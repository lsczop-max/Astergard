from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from math import isfinite
from time import monotonic
from typing import Any

from websockets.exceptions import ConnectionClosed
from websockets.legacy.server import WebSocketServerProtocol

from astergard.application.session_transport import (
    SessionCapability,
    SessionEvent,
    SessionInput,
    SessionInputKind,
    SessionTransportKind,
)
from astergard.protocol.web_v1 import (
    COMMAND_LENGTH_LIMIT,
    WebProtocolError,
    build_web_envelope,
    parse_web_envelope,
    serialize_web_envelope,
    WEB_MESSAGE_MAX_BYTES,
)


@dataclass(frozen=True, slots=True)
class WebSocketTransportLimits:
    message_max_bytes: int = WEB_MESSAGE_MAX_BYTES
    hello_timeout_seconds: float = 10.0
    login_timeout_seconds: float = 30.0
    max_protocol_errors: int = 3
    message_rate_limit_count: int = 24
    message_rate_limit_window_seconds: float = 10.0
    command_rate_limit_count: int = 12
    command_rate_limit_window_seconds: float = 10.0


def _validate_positive_timeout(value: float | None, field_name: str) -> float | None:
    if value is None:
        return None
    if type(value) is bool or type(value) not in {int, float}:
        raise ValueError(f"{field_name} must be a positive finite number or None.")
    numeric = float(value)
    if not isfinite(numeric) or numeric <= 0:
        raise ValueError(f"{field_name} must be a positive finite number or None.")
    return numeric


@dataclass(slots=True)
class _SlidingWindowLimiter:
    max_events: int
    window_seconds: float
    timestamps: deque[float] = field(default_factory=deque)

    def allow(self, now: float) -> bool:
        cutoff = now - self.window_seconds
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_events:
            return False
        self.timestamps.append(now)
        return True


@dataclass(slots=True, eq=False)
class WebSocketSessionTransport:
    websocket: WebSocketServerProtocol
    limits: WebSocketTransportLimits = field(default_factory=WebSocketTransportLimits)
    kind: SessionTransportKind = SessionTransportKind.WEB
    capabilities: frozenset[SessionCapability] = frozenset(
        {
            SessionCapability.RAW_TEXT,
            SessionCapability.PROMPT,
            SessionCapability.STRUCTURED_EVENTS,
            SessionCapability.WEB_JSON,
        }
    )
    _sequence: int = 0
    _closed: bool = False
    _protocol_error_count: int = 0
    _deadline_kind: SessionInputKind | None = None
    _deadline_at: float | None = None
    _message_limiter: _SlidingWindowLimiter = field(init=False)
    _command_limiter: _SlidingWindowLimiter = field(init=False)

    def __post_init__(self) -> None:
        self._validate_limits()
        self._message_limiter = _SlidingWindowLimiter(
            self.limits.message_rate_limit_count,
            self.limits.message_rate_limit_window_seconds,
        )
        self._command_limiter = _SlidingWindowLimiter(
            self.limits.command_rate_limit_count,
            self.limits.command_rate_limit_window_seconds,
        )

    def _validate_limits(self) -> None:
        _validate_positive_timeout(self.limits.hello_timeout_seconds, "hello_timeout_seconds")
        _validate_positive_timeout(self.limits.login_timeout_seconds, "login_timeout_seconds")
        _validate_positive_timeout(self.limits.message_rate_limit_window_seconds, "message_rate_limit_window_seconds")
        _validate_positive_timeout(self.limits.command_rate_limit_window_seconds, "command_rate_limit_window_seconds")

    def _deadline_for(self, expected: SessionInputKind) -> float | None:
        if expected == SessionInputKind.HELLO and self._deadline_kind == SessionInputKind.HELLO and self._deadline_at is not None:
            return self._deadline_at
        if expected == SessionInputKind.CREDENTIALS and self._deadline_kind == SessionInputKind.CREDENTIALS and self._deadline_at is not None:
            return self._deadline_at
        if expected == SessionInputKind.HELLO:
            timeout = self.limits.hello_timeout_seconds
        elif expected == SessionInputKind.CREDENTIALS:
            timeout = self.limits.login_timeout_seconds
        else:
            self._deadline_kind = None
            self._deadline_at = None
            return None
        if self._deadline_kind != expected or self._deadline_at is None:
            self._deadline_kind = expected
            self._deadline_at = monotonic() + timeout
        return self._deadline_at

    def _next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    def _allowed_request_type(self, expected: SessionInputKind, message_type: str) -> bool:
        if message_type == "connection.ping":
            return expected != SessionInputKind.HELLO
        if expected == SessionInputKind.HELLO:
            return message_type == "session.hello"
        if expected == SessionInputKind.CREDENTIALS:
            return message_type in {"auth.login", "creator.start"}
        if expected == SessionInputKind.CREATOR:
            return message_type in {"creator.submit", "creator.back", "creator.cancel"}
        if expected == SessionInputKind.CREATOR_START:
            return message_type == "creator.start"
        if expected == SessionInputKind.CREATOR_SUBMIT:
            return message_type == "creator.submit"
        if expected == SessionInputKind.CREATOR_BACK:
            return message_type == "creator.back"
        if expected == SessionInputKind.CREATOR_CANCEL:
            return message_type == "creator.cancel"
        if expected == SessionInputKind.COMMAND:
            return message_type == "command.execute"
        return False

    def _remaining_deadline(self, expected: SessionInputKind) -> float | None:
        deadline = self._deadline_for(expected)
        if deadline is None:
            return None
        remaining = deadline - monotonic()
        return remaining

    async def _send_envelope(
        self,
        message_type: str,
        payload: dict[str, Any],
        *,
        request_id: str | None = None,
    ) -> None:
        if self._closed:
            raise EOFError
        envelope = build_web_envelope(
            message_type,
            payload,
            request_id=request_id,
            sequence=self._next_sequence(),
        )
        await self.websocket.send(serialize_web_envelope(envelope))

    async def _send_protocol_error(self, code: str, message: str, request_id: str | None = None) -> None:
        if self._closed:
            return
        try:
            await self._send_envelope(
                "protocol.error",
                {"code": code, "message": message},
                request_id=request_id,
            )
        finally:
            self._protocol_error_count += 1

    async def _close_with_protocol_error(
        self,
        code: str,
        message: str,
        *,
        request_id: str | None = None,
        close_code: int = 1008,
        close_reason: str = "protocol error",
    ) -> None:
        await self._send_protocol_error(code, message, request_id=request_id)
        await self.close(close_code=close_code, reason=close_reason)

    def _should_close_after_error(self, code: str) -> bool:
        if code in {
            "invalid_binary",
            "message_too_large",
            "timeout_hello",
            "timeout_login",
            "unsupported_version",
        }:
            return True
        if code == "rate_limited":
            return self._protocol_error_count >= 2
        return self._protocol_error_count >= self.limits.max_protocol_errors

    async def _handle_protocol_error(
        self,
        error: WebProtocolError,
        request_id: str | None,
    ) -> None:
        if self._closed:
            return
        await self._send_protocol_error(error.code, error.message, request_id=request_id)
        if self._should_close_after_error(error.code):
            await self.close(close_code=1008, reason="protocol violation")

    async def _handle_binary_message(self) -> None:
        await self._close_with_protocol_error(
            "invalid_binary",
            "Binary websocket messages are not supported.",
            close_code=1003,
            close_reason="binary frame not supported",
        )

    def _consume_rate_limit(self, *, command: bool) -> bool:
        now = monotonic()
        if not self._message_limiter.allow(now):
            return False
        if command and not self._command_limiter.allow(now):
            return False
        return True

    async def read_input(
        self,
        expected: SessionInputKind,
        *,
        deadline: float | None = None,
    ) -> SessionInput:
        if self._closed:
            raise EOFError
        if deadline is not None:
            self._deadline_kind = expected
            self._deadline_at = deadline
        while not self._closed:
            timeout = self._remaining_deadline(expected)
            if timeout is not None and timeout <= 0:
                await self._close_with_protocol_error(
                    "timeout_hello" if expected == SessionInputKind.HELLO else "timeout_login",
                    "Timed out waiting for the next websocket message.",
                )
                raise EOFError
            try:
                if timeout is None:
                    raw = await self.websocket.recv()
                else:
                    raw = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            except asyncio.TimeoutError:
                await self._close_with_protocol_error(
                    "timeout_hello" if expected == SessionInputKind.HELLO else "timeout_login",
                    "Timed out waiting for the next websocket message.",
                )
                raise EOFError
            except ConnectionClosed:
                self._closed = True
                raise EOFError
            if isinstance(raw, bytes):
                await self._handle_binary_message()
                raise EOFError
            if not self._consume_rate_limit(command=expected == SessionInputKind.COMMAND):
                await self._send_protocol_error(
                    "rate_limited",
                    "Too many websocket messages or commands were received in a short period of time.",
                )
                if self._should_close_after_error("rate_limited"):
                    await self.close(close_code=1008, reason="rate limited")
                    raise EOFError
                continue
            try:
                envelope = parse_web_envelope(raw, max_bytes=self.limits.message_max_bytes)
            except WebProtocolError as exc:
                await self._handle_protocol_error(exc, None)
                if self._closed:
                    raise EOFError
                continue
            if not self._allowed_request_type(expected, envelope.type):
                await self._handle_protocol_error(
                    WebProtocolError("invalid_state", "Unexpected websocket message for the current session state."),
                    envelope.request_id,
                )
                if self._closed:
                    raise EOFError
                continue
            if envelope.type == "connection.ping":
                return SessionInput(SessionInputKind.PING, dict(envelope.payload), envelope.request_id)
            if envelope.type == "session.hello":
                return SessionInput(SessionInputKind.HELLO, dict(envelope.payload), envelope.request_id)
            if envelope.type == "auth.login":
                return SessionInput(SessionInputKind.CREDENTIALS, dict(envelope.payload), envelope.request_id)
            if envelope.type == "creator.start":
                return SessionInput(SessionInputKind.CREATOR_START, dict(envelope.payload), envelope.request_id)
            if envelope.type == "creator.submit":
                return SessionInput(SessionInputKind.CREATOR_SUBMIT, dict(envelope.payload), envelope.request_id)
            if envelope.type == "creator.back":
                return SessionInput(SessionInputKind.CREATOR_BACK, dict(envelope.payload), envelope.request_id)
            if envelope.type == "creator.cancel":
                return SessionInput(SessionInputKind.CREATOR_CANCEL, dict(envelope.payload), envelope.request_id)
            if envelope.type == "command.execute":
                command = envelope.payload.get("command", "")
                if isinstance(command, str) and len(command.encode("utf-8")) > COMMAND_LENGTH_LIMIT:
                    await self._handle_protocol_error(
                        WebProtocolError("message_too_large", "Command exceeds the transport limit."),
                        envelope.request_id,
                    )
                    if self._closed:
                        raise EOFError
                    continue
                return SessionInput(SessionInputKind.COMMAND, dict(envelope.payload), envelope.request_id)
        raise EOFError

    async def send_text(self, text: str) -> None:
        await self._send_envelope("output.text", {"text": text})

    async def send_prompt(self, prompt: str) -> None:
        await self._send_envelope("output.prompt", {"prompt": prompt})

    async def send_event(self, event: SessionEvent) -> None:
        if self._closed:
            raise EOFError
        await self._send_envelope(
            event.type,
            dict(event.payload),
            request_id=event.request_id,
        )

    async def close(self, close_code: int = 1000, reason: str = "session closed") -> None:
        if self._closed:
            return
        self._closed = True
        try:
            await self.websocket.close(code=close_code, reason=reason)
        except Exception:
            pass

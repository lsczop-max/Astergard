from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from astergard.gmcp import (
    ROOM_INFO_PACKAGE,
    core_hello_packet,
    gmcp_negotiation_packet,
    gmcp_payload,
    room_info_payload,
)
from astergard.protocol.web_v1 import COMMAND_LENGTH_LIMIT
from astergard.utils import send_prompt, send_text


class SessionTransportKind(str, Enum):
    TCP = "tcp"
    WEB = "web"


class SessionCapability(str, Enum):
    RAW_TEXT = "raw_text"
    PROMPT = "prompt"
    STRUCTURED_EVENTS = "structured_events"
    GMCP = "gmcp"
    WEB_JSON = "web_json"
    DEBUG_MAP = "debug_map"


class SessionInputKind(str, Enum):
    HELLO = "session.hello"
    CREDENTIALS = "auth.login"
    RESPONSE = "session.response"
    COMMAND = "command.execute"
    PING = "connection.ping"
    DISCONNECT = "connection.disconnect"


@dataclass(frozen=True, slots=True)
class SessionInput:
    kind: SessionInputKind
    payload: dict[str, Any]
    request_id: str | None = None

    def __repr__(self) -> str:
        return (
            "SessionInput("
            f"kind={self.kind.value!r}, payload_keys={sorted(self.payload.keys())!r}, "
            f"request_id={self.request_id!r})"
        )


@dataclass(frozen=True, slots=True)
class SessionEvent:
    type: str
    payload: dict[str, Any]
    request_id: str | None = None
    sequence: int | None = None

    def __repr__(self) -> str:
        return (
            "SessionEvent("
            f"type={self.type!r}, payload_keys={sorted(self.payload.keys())!r}, "
            f"request_id={self.request_id!r}, sequence={self.sequence!r})"
        )


@runtime_checkable
class SessionTransport(Protocol):
    kind: SessionTransportKind
    capabilities: frozenset[SessionCapability]

    async def read_input(self, expected: SessionInputKind) -> SessionInput: ...
    async def send_text(self, text: str) -> None: ...
    async def send_prompt(self, prompt: str) -> None: ...
    async def send_event(self, event: SessionEvent) -> None: ...
    async def close(self) -> None: ...


def is_debug_map_allowed(transport: SessionTransport) -> bool:
    return (
        transport.kind == SessionTransportKind.TCP
        and SessionCapability.DEBUG_MAP in transport.capabilities
    )


@dataclass(slots=True, eq=False)
class TcpSessionTransport:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    max_input_length: int = COMMAND_LENGTH_LIMIT
    kind: SessionTransportKind = SessionTransportKind.TCP
    capabilities: frozenset[SessionCapability] = frozenset(
        {
            SessionCapability.RAW_TEXT,
            SessionCapability.PROMPT,
            SessionCapability.STRUCTURED_EVENTS,
            SessionCapability.GMCP,
            SessionCapability.DEBUG_MAP,
        }
    )
    _credential_stage: str = "username"
    _closed: bool = False

    async def _read_line(self) -> str:
        raw = await self.reader.readline()
        if raw == b"":
            raise EOFError
        if len(raw) > self.max_input_length + 2:
            raise ValueError("Input exceeds the transport limit.")
        try:
            return raw.decode("utf-8").rstrip("\r\n")
        except UnicodeDecodeError as exc:
            raise ValueError("Input is not valid UTF-8.") from exc

    async def read_input(self, expected: SessionInputKind) -> SessionInput:
        if expected == SessionInputKind.HELLO:
            return SessionInput(SessionInputKind.HELLO, {"transport": self.kind.value}, None)
        if expected == SessionInputKind.DISCONNECT:
            return SessionInput(SessionInputKind.DISCONNECT, {"reason": "client_disconnect"}, None)
        if expected == SessionInputKind.PING:
            raw = await self._read_line()
            return SessionInput(SessionInputKind.PING, {"nonce": raw} if raw else {}, None)
        if expected == SessionInputKind.COMMAND:
            raw = await self._read_line()
            if raw.lower() == "ping":
                return SessionInput(SessionInputKind.PING, {"nonce": raw}, None)
            if raw.lower() == "disconnect":
                return SessionInput(SessionInputKind.DISCONNECT, {"reason": raw.lower()}, None)
            return SessionInput(SessionInputKind.COMMAND, {"command": raw}, None)
        if expected == SessionInputKind.RESPONSE:
            raw = await self._read_line()
            return SessionInput(SessionInputKind.RESPONSE, {"text": raw}, None)
        if expected == SessionInputKind.CREDENTIALS:
            raw = await self._read_line()
            if self._credential_stage == "username":
                self._credential_stage = "password"
                return SessionInput(SessionInputKind.CREDENTIALS, {"username": raw}, None)
            self._credential_stage = "username"
            return SessionInput(SessionInputKind.CREDENTIALS, {"password": raw}, None)
        raise ValueError(f"Unsupported expected input kind: {expected!r}")

    async def send_text(self, text: str) -> None:
        await send_text(self.writer, text)

    async def send_prompt(self, prompt: str) -> None:
        await send_prompt(self.writer, prompt)

    async def send_event(self, event: SessionEvent) -> None:
        if event.type == "gmcp.negotiation":
            await self._send_packet(gmcp_negotiation_packet())
            return
        if event.type == "gmcp.core_hello":
            await self._send_packet(core_hello_packet())
            return
        if event.type == "room.info":
            packet = gmcp_payload(ROOM_INFO_PACKAGE, event.payload)
            await self._send_packet(packet)
            return

    async def _send_packet(self, packet: bytes) -> None:
        self.writer.write(packet)
        await self.writer.drain()

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            pass


def make_room_info_event(location: Any, world: Any, *, sequence: int | None = None) -> SessionEvent:
    return SessionEvent("room.info", room_info_payload(location, world), sequence=sequence)


def make_gmcp_negotiation_event() -> SessionEvent:
    return SessionEvent("gmcp.negotiation", {})


def make_core_hello_event() -> SessionEvent:
    return SessionEvent("gmcp.core_hello", {})


def make_session_ready_event(
    transport: SessionTransportKind,
    username: str | None = None,
    *,
    sequence: int | None = None,
) -> SessionEvent:
    payload: dict[str, Any] = {"transport": transport.value}
    if username is not None:
        payload["username"] = username
    return SessionEvent("session.ready", payload, sequence=sequence)


def make_auth_result_event(
    success: bool,
    username: str,
    *,
    reason: str | None = None,
    request_id: str | None = None,
    sequence: int | None = None,
) -> SessionEvent:
    payload: dict[str, Any] = {"success": success, "username": username}
    if reason is not None:
        payload["reason"] = reason
    return SessionEvent("auth.result", payload, request_id=request_id, sequence=sequence)


def make_command_result_event(
    command: str,
    *,
    success: bool,
    request_id: str | None = None,
    sequence: int | None = None,
) -> SessionEvent:
    payload: dict[str, Any] = {"command": command, "success": success}
    return SessionEvent("command.result", payload, request_id=request_id, sequence=sequence)


def make_protocol_error_event(
    code: str,
    message: str,
    *,
    request_id: str | None = None,
    sequence: int | None = None,
) -> SessionEvent:
    payload = {"code": code, "message": message}
    return SessionEvent("protocol.error", payload, request_id=request_id, sequence=sequence)


def make_connection_pong_event(
    request_id: str | None = None,
    *,
    sequence: int | None = None,
) -> SessionEvent:
    return SessionEvent("connection.pong", {}, request_id=request_id, sequence=sequence)


def next_sequence(current: int) -> int:
    return current + 1

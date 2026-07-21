from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque

from astergard.application.session_transport import (
    SessionCapability,
    SessionEvent,
    SessionInput,
    SessionInputKind,
    SessionTransportKind,
)


@dataclass(eq=False)
class MemorySessionTransport:
    kind: SessionTransportKind = SessionTransportKind.WEB
    capabilities: frozenset[SessionCapability] = frozenset(
        {
            SessionCapability.RAW_TEXT,
            SessionCapability.PROMPT,
            SessionCapability.STRUCTURED_EVENTS,
            SessionCapability.WEB_JSON,
        }
    )
    inbound: Deque[SessionInput] = field(default_factory=deque)
    outbound_text: list[str] = field(default_factory=list)
    outbound_prompts: list[str] = field(default_factory=list)
    outbound_events: list[SessionEvent] = field(default_factory=list)
    closed: bool = False

    def queue_input(
        self,
        kind: SessionInputKind,
        payload: Any | None = None,
        request_id: str | None = None,
    ) -> None:
        if payload is None:
            payload_dict: dict[str, Any] = {}
        elif isinstance(payload, dict):
            payload_dict = dict(payload)
        elif kind == SessionInputKind.CREDENTIALS:
            payload_dict = {"username": str(payload)}
        elif kind == SessionInputKind.COMMAND:
            payload_dict = {"command": str(payload)}
        elif kind == SessionInputKind.RESPONSE:
            payload_dict = {"text": str(payload)}
        elif kind == SessionInputKind.PING:
            payload_dict = {"nonce": str(payload)}
        else:
            payload_dict = {"value": payload}
        self.inbound.append(SessionInput(kind, payload_dict, request_id))

    async def read_input(
        self,
        expected: SessionInputKind,
        *,
        deadline: float | None = None,
    ) -> SessionInput:
        if not self.inbound:
            raise EOFError
        message = self.inbound.popleft()
        if expected in {SessionInputKind.CREDENTIALS, SessionInputKind.CREATOR} and message.kind in {
            SessionInputKind.CREATOR_START,
            SessionInputKind.CREATOR_SUBMIT,
            SessionInputKind.CREATOR_BACK,
            SessionInputKind.CREATOR_CANCEL,
        }:
            return message
        if message.kind != expected and message.kind not in {SessionInputKind.PING, SessionInputKind.DISCONNECT}:
            raise ValueError(f"Unexpected input kind: {message.kind.value}")
        return message

    async def send_text(self, text: str) -> None:
        self.outbound_text.append(text)

    async def send_prompt(self, prompt: str) -> None:
        self.outbound_prompts.append(prompt)

    async def send_event(self, event: SessionEvent) -> None:
        self.outbound_events.append(event)

    def emit_event(self, event: SessionEvent) -> None:
        self.outbound_events.append(event)

    async def close(self) -> None:
        self.closed = True

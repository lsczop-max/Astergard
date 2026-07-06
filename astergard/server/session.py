from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from astergard.characters.models import Character
from astergard.state import SESSION_STATE_MACHINE, SessionState, parse_session_state

@dataclass
class ClientConnection:
    reader: Any
    writer: Any
    username: str | None = None
    state: str = SessionState.CONNECTED.value
    character: Character | None = None

    def transition_state(self, target: str | SessionState) -> None:
        current = parse_session_state(self.state)
        next_state = parse_session_state(target)
        self.state = SESSION_STATE_MACHINE.validate(current, next_state).value

    async def disconnect(self) -> None:
        if self.state != SessionState.DISCONNECTED.value:
            try:
                self.transition_state(SessionState.DISCONNECTED)
            except Exception:
                self.state = SessionState.DISCONNECTED.value
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            pass

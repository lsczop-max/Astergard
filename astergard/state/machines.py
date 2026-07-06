from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StateTransitionError(ValueError):
    """Raised when an entity attempts an invalid state transition."""


class SessionState(StrEnum):
    CONNECTED = "CONNECTED"
    ENTER_PASSWORD = "ENTER_PASSWORD"
    IN_GAME = "IN_GAME"
    DISCONNECTED = "DISCONNECTED"


class CharacterState(StrEnum):
    ALIVE = "ALIVE"
    IN_COMBAT = "IN_COMBAT"
    DEAD = "DEAD"


class NPCState(StrEnum):
    IDLE = "IDLE"
    PATROL = "PATROL"
    AGGRESSIVE = "AGGRESSIVE"
    GUARD = "GUARD"
    DEAD = "DEAD"


class CombatState(StrEnum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


@dataclass(frozen=True, slots=True)
class StateMachine[T: StrEnum]:
    allowed: dict[T, frozenset[T]]

    def validate(self, current: T, target: T) -> T:
        if target == current:
            return target
        allowed_targets = self.allowed.get(current, frozenset())
        if target not in allowed_targets:
            raise StateTransitionError(f"Invalid transition: {current.value} -> {target.value}")
        return target


SESSION_STATE_MACHINE = StateMachine[SessionState](
    {
        SessionState.CONNECTED: frozenset({SessionState.ENTER_PASSWORD, SessionState.IN_GAME, SessionState.DISCONNECTED}),
        SessionState.ENTER_PASSWORD: frozenset({SessionState.IN_GAME, SessionState.DISCONNECTED}),
        SessionState.IN_GAME: frozenset({SessionState.DISCONNECTED}),
        SessionState.DISCONNECTED: frozenset(),
    }
)

CHARACTER_STATE_MACHINE = StateMachine[CharacterState](
    {
        CharacterState.ALIVE: frozenset({CharacterState.IN_COMBAT, CharacterState.DEAD}),
        CharacterState.IN_COMBAT: frozenset({CharacterState.ALIVE, CharacterState.DEAD}),
        CharacterState.DEAD: frozenset(),
    }
)

NPC_STATE_MACHINE = StateMachine[NPCState](
    {
        NPCState.IDLE: frozenset({NPCState.PATROL, NPCState.AGGRESSIVE, NPCState.GUARD, NPCState.DEAD}),
        NPCState.PATROL: frozenset({NPCState.IDLE, NPCState.AGGRESSIVE, NPCState.GUARD, NPCState.DEAD}),
        NPCState.AGGRESSIVE: frozenset({NPCState.IDLE, NPCState.PATROL, NPCState.GUARD, NPCState.DEAD}),
        NPCState.GUARD: frozenset({NPCState.IDLE, NPCState.PATROL, NPCState.AGGRESSIVE, NPCState.DEAD}),
        NPCState.DEAD: frozenset({NPCState.IDLE}),
    }
)

COMBAT_STATE_MACHINE = StateMachine[CombatState](
    {
        CombatState.IDLE: frozenset({CombatState.ACTIVE}),
        CombatState.ACTIVE: frozenset({CombatState.ENDED}),
        CombatState.ENDED: frozenset({CombatState.IDLE}),
    }
)


def parse_session_state(value: str | SessionState) -> SessionState:
    return value if isinstance(value, SessionState) else SessionState(value)


def parse_character_state(value: str | CharacterState) -> CharacterState:
    return value if isinstance(value, CharacterState) else CharacterState(value)


def parse_npc_state(value: str | NPCState) -> NPCState:
    return value if isinstance(value, NPCState) else NPCState(value)


def parse_combat_state(value: str | CombatState) -> CombatState:
    return value if isinstance(value, CombatState) else CombatState(value)

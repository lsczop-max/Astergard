from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class DomainEventType(StrEnum):
    """Canonical domain event names used by the engine and game systems."""

    ENGINE_STARTED = "engine.started"
    ENGINE_STOPPED = "engine.stopped"
    ENGINE_TICK_STARTED = "engine.tick_started"
    ENGINE_TICK_COMPLETED = "engine.tick_completed"
    ENGINE_TICK_FAILED = "engine.tick_failed"
    ENGINE_SHUTDOWN_REQUESTED = "engine.shutdown_requested"
    ENGINE_PLAYERS_FLUSHED = "engine.players_flushed"
    ENGINE_WORLD_FLUSHED = "engine.world_flushed"

    SERVER_STARTED = "server.started"
    SESSION_CHARACTER_SAVED = "session.character_saved"

    CHARACTER_TICK_COMPLETED = "character.tick_completed"
    CHARACTER_MOVED = "character.moved"
    CHARACTER_SPOKE = "character.spoke"
    CHARACTER_EMOTED = "character.emoted"
    CHARACTER_SHOUTED = "character.shouted"
    CHARACTER_SAVED = "character.saved"

    ITEM_PICKED_UP = "item.picked_up"
    ITEM_DROPPED = "item.dropped"
    ITEM_EQUIPPED = "item.equipped"
    ITEM_UNEQUIPPED = "item.unequipped"
    ITEM_CONSUMED = "item.consumed"

    COMBAT_ATTACKED = "combat.attacked"
    COMBAT_FLED = "combat.fled"
    COMBATANT_DIED = "combatant.died"
    NPC_DIED = "npc.died"
    WORLD_RESPAWN_TICK_COMPLETED = "world.respawn_tick_completed"

    QUEST_ACCEPTED = "quest.accepted"
    QUEST_PROGRESS_UPDATED = "quest.progress_updated"
    QUEST_COMPLETED = "quest.completed"
    REPUTATION_CHANGED = "reputation.changed"

    ECONOMY_ITEM_BOUGHT = "economy.item_bought"
    ECONOMY_ITEM_SOLD = "economy.item_sold"

    MAGIC_CAST = "magic.cast"
    CRAFTING_ATTEMPTED = "crafting.attempted"


@dataclass(frozen=True, slots=True)
class EngineEvent:
    """Immutable event emitted by the MUD engine.

    ``type`` remains a string for backwards compatibility with D19 tests and
    existing audit rows. ``DomainEventType`` is accepted by ``emit`` and
    normalized to its canonical string value.
    """

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def actor(self) -> str:
        return str(self.payload.get("username") or self.payload.get("actor") or "system")


EventHandler = Callable[[EngineEvent], None]


class EventBus:
    """Deterministic domain event bus with wildcard routing and failure isolation."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[EngineEvent] = []
        self._errors: list[tuple[EngineEvent, str]] = []

    def subscribe(self, event_type: str | DomainEventType, handler: EventHandler) -> None:
        key = self._normalize_type(event_type)
        if handler not in self._subscribers[key]:
            self._subscribers[key].append(handler)

    def subscribe_many(self, event_types: Iterable[str | DomainEventType], handler: EventHandler) -> None:
        for event_type in event_types:
            self.subscribe(event_type, handler)

    def unsubscribe(self, event_type: str | DomainEventType, handler: EventHandler) -> None:
        key = self._normalize_type(event_type)
        if handler in self._subscribers[key]:
            self._subscribers[key].remove(handler)

    def publish(self, event: EngineEvent) -> None:
        self._history.append(event)
        handlers = list(self._subscribers.get(event.type, [])) + list(self._subscribers.get("*", []))
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # event subscribers must not kill the tick loop
                self._errors.append((event, f"{type(exc).__name__}: {exc}"))

    def emit(self, event_type: str | DomainEventType, **payload: Any) -> None:
        self.publish(EngineEvent(self._normalize_type(event_type), payload))

    @property
    def history(self) -> tuple[EngineEvent, ...]:
        return tuple(self._history)

    @property
    def errors(self) -> tuple[tuple[EngineEvent, str], ...]:
        return tuple(self._errors)

    @staticmethod
    def _normalize_type(event_type: str | DomainEventType) -> str:
        return event_type.value if isinstance(event_type, DomainEventType) else event_type

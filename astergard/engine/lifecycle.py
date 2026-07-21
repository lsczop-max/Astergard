from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Awaitable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from astergard.application.bootstrap import GameServices
from astergard.characters.models import Character
from astergard.engine.events import EngineEvent, EventBus
from astergard.engine.scheduler import Scheduler


@dataclass(slots=True)
class EngineLifecycle:
    """Owns engine tick lifecycle, save lifecycle and shutdown flushing."""

    services: "GameServices"
    players: Callable[[], list[Character]]
    event_bus: EventBus
    scheduler: Scheduler
    tick_interval_seconds: float = 4.0
    tick_count: int = 0
    is_running: bool = False
    shutdown_requested: bool = False

    def __post_init__(self) -> None:
        self.scheduler.every("autosave_world", 15, self.flush_world_state)
        self.scheduler.every("autosave_players", 15, self.flush_player_states)
        self.scheduler.every("audit_tick", 60, self.audit_tick)
        self.event_bus.subscribe("*", self._audit_engine_event)

    async def run_forever(
        self,
        tick_once: Callable[[], Any],
        after_tick: Callable[[Any], Awaitable[None]] | None = None,
    ) -> None:
        self.is_running = True
        self.event_bus.emit("engine.started")
        try:
            while not self.shutdown_requested:
                await asyncio.sleep(self.tick_interval_seconds)
                tick_result = self.tick(tick_once)
                if after_tick is not None:
                    await after_tick(tick_result)
        finally:
            self.is_running = False
            self.flush_all("run_forever_exit")
            self.event_bus.emit("engine.stopped")

    def tick(self, tick_once: Callable[[], Any]) -> Any:
        self.event_bus.emit("engine.tick_started", tick=self.tick_count)
        start = perf_counter()
        ok = False
        error: str | None = None
        tick_result: Any = None
        try:
            tick_result = tick_once()
            self.scheduler.run_due(self.tick_count)
            ok = True
            self.event_bus.emit("engine.tick_completed", tick=self.tick_count)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            self.event_bus.emit("engine.tick_failed", tick=self.tick_count, error=error)
            self.flush_all("tick_failure")
            raise
        finally:
            observability = getattr(self.services, "observability", None)
            if observability is not None:
                observability.record_tick(self.tick_count, (perf_counter() - start) * 1000.0, ok, error)
            self.tick_count += 1
        return tick_result

    def request_shutdown(self, reason: str = "manual") -> None:
        self.shutdown_requested = True
        self.event_bus.emit("engine.shutdown_requested", reason=reason)
        self.flush_all(reason)

    def flush_player_states(self) -> None:
        result = self.services.save_load.flush_all(self.players(), "autosave_players")
        self.event_bus.emit("engine.players_flushed", count=result.saved_characters, errors=list(result.errors))

    def flush_world_state(self) -> None:
        result = self.services.save_load.save_world("autosave_world")
        self.event_bus.emit("engine.world_flushed", save_version=self.services.repo.world_state.save_version(), errors=list(result.errors))

    def flush_all(self, reason: str) -> None:
        result = self.services.save_load.flush_all(self.players(), reason)
        self.services.repo.audit.record("system", "engine_flush", json.dumps({"reason": reason, "ok": result.ok, "errors": result.errors}, ensure_ascii=False))

    def audit_tick(self) -> None:
        self.services.repo.audit.record("system", "engine_tick", json.dumps({"tick": self.tick_count}, ensure_ascii=False))

    def _audit_engine_event(self, event: EngineEvent) -> None:
        if event.type.startswith("engine.tick_"):
            return
        try:
            self.services.repo.audit.record("system", event.type, json.dumps(event.payload, ensure_ascii=False, default=str))
        except Exception:
            # Audit must never break event dispatch or the server lifecycle.
            return

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from time import monotonic
from typing import Any, Deque

from astergard.engine.events import EngineEvent, EventBus
from astergard.engine.scheduler import Scheduler


@dataclass(frozen=True, slots=True)
class CommandMetric:
    command: str
    actor: str
    duration_ms: float
    ok: bool
    error: str | None = None


@dataclass(frozen=True, slots=True)
class TickMetric:
    tick: int
    duration_ms: float
    ok: bool
    error: str | None = None


@dataclass(frozen=True, slots=True)
class DiagnosticSnapshot:
    uptime_seconds: float
    event_count: int
    event_errors: int
    command_count: int
    command_errors: int
    average_command_ms: float
    max_command_ms: float
    tick_count: int
    average_tick_ms: float
    max_tick_ms: float
    scheduler_tasks: int
    scheduler_errors: int


class ObservabilityService:
    """Central in-memory observability for diagnostics, tests and GM commands.

    This is intentionally standard-library only. It provides bounded metrics,
    event counters and human-readable diagnostics without pulling in an external
    telemetry stack.
    """

    def __init__(self, event_bus: EventBus, scheduler: Scheduler, *, history_limit: int = 500) -> None:
        self.event_bus = event_bus
        self.scheduler = scheduler
        self.started_at = monotonic()
        self.history_limit = history_limit
        self.event_counts: Counter[str] = Counter()
        self.event_samples: Deque[EngineEvent] = deque(maxlen=history_limit)
        self.command_metrics: Deque[CommandMetric] = deque(maxlen=history_limit)
        self.tick_metrics: Deque[TickMetric] = deque(maxlen=history_limit)
        event_bus.subscribe("*", self.record_event)

    def record_event(self, event: EngineEvent) -> None:
        self.event_counts[event.type] += 1
        self.event_samples.append(event)

    def record_command(self, command: str, actor: str, duration_ms: float, ok: bool, error: str | None = None) -> None:
        self.command_metrics.append(CommandMetric(command=command, actor=actor, duration_ms=duration_ms, ok=ok, error=error))

    def record_tick(self, tick: int, duration_ms: float, ok: bool, error: str | None = None) -> None:
        self.tick_metrics.append(TickMetric(tick=tick, duration_ms=duration_ms, ok=ok, error=error))

    def snapshot(self) -> DiagnosticSnapshot:
        commands = list(self.command_metrics)
        ticks = list(self.tick_metrics)
        command_errors = sum(1 for metric in commands if not metric.ok)
        command_durations = [metric.duration_ms for metric in commands]
        tick_durations = [metric.duration_ms for metric in ticks]
        return DiagnosticSnapshot(
            uptime_seconds=monotonic() - self.started_at,
            event_count=sum(self.event_counts.values()),
            event_errors=len(self.event_bus.errors),
            command_count=len(commands),
            command_errors=command_errors,
            average_command_ms=(sum(command_durations) / len(command_durations)) if command_durations else 0.0,
            max_command_ms=max(command_durations) if command_durations else 0.0,
            tick_count=len(ticks),
            average_tick_ms=(sum(tick_durations) / len(tick_durations)) if tick_durations else 0.0,
            max_tick_ms=max(tick_durations) if tick_durations else 0.0,
            scheduler_tasks=len(self.scheduler.tasks),
            scheduler_errors=len(self.scheduler.errors),
        )

    def render_metrics(self) -> str:
        snap = self.snapshot()
        return "\n".join(
            [
                "Jak pracuje świat:",
                f"Czas działania: {snap.uptime_seconds:.2f}s",
                f"Wydarzenia: {snap.event_count} (błędy: {snap.event_errors})",
                f"Ruch graczy: {snap.command_count} (błędy: {snap.command_errors})",
                f"Średni czas komendy: {snap.average_command_ms:.3f} ms",
                f"Najdłuższa komenda: {snap.max_command_ms:.3f} ms",
                f"Ticki świata: {snap.tick_count}",
                f"Średni czas ticka: {snap.average_tick_ms:.3f} ms",
                f"Najdłuższy tick: {snap.max_tick_ms:.3f} ms",
                f"Zegar świata: {snap.scheduler_tasks} zadań (błędy: {snap.scheduler_errors})",
            ]
        )

    def render_events(self, limit: int = 20) -> str:
        limit = max(1, min(limit, 100))
        if not self.event_counts:
            return "Brak eventów."
        lines = ["Najczęstsze zdarzenia:"]
        for event_type, count in self.event_counts.most_common(limit):
            lines.append(f"{event_type}: {count}")
        return "\n".join(lines)

    def render_lag(self) -> str:
        ticks = list(self.tick_metrics)
        if not ticks:
            return "Brak danych ticków."
        slowest = max(ticks, key=lambda metric: metric.duration_ms)
        latest = ticks[-1]
        return "\n".join(
            [
                "Rytm świata:",
                f"Ostatni tick: {latest.tick} / {latest.duration_ms:.3f} ms / {'OK' if latest.ok else 'BŁĄD'}",
                f"Najwolniejszy tick: {slowest.tick} / {slowest.duration_ms:.3f} ms / {'OK' if slowest.ok else 'BŁĄD'}",
                f"Błędy zegara: {len(self.scheduler.errors)}",
            ]
        )

    def render_diagnostics(self) -> str:
        lines = [self.render_metrics(), "", self.render_lag(), "", self.render_events(10)]
        return "\n".join(lines)

    def export_dict(self) -> dict[str, Any]:
        snap = self.snapshot()
        return {
            "uptime_seconds": snap.uptime_seconds,
            "event_count": snap.event_count,
            "event_errors": snap.event_errors,
            "command_count": snap.command_count,
            "command_errors": snap.command_errors,
            "average_command_ms": snap.average_command_ms,
            "max_command_ms": snap.max_command_ms,
            "tick_count": snap.tick_count,
            "average_tick_ms": snap.average_tick_ms,
            "max_tick_ms": snap.max_tick_ms,
            "scheduler_tasks": snap.scheduler_tasks,
            "scheduler_errors": snap.scheduler_errors,
            "event_counts": dict(self.event_counts),
        }

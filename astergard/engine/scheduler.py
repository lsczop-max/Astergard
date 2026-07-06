from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


TaskCallback = Callable[[], Any]


@dataclass(slots=True)
class ScheduledTask:
    name: str
    interval_ticks: int
    callback: TaskCallback
    run_on_tick_zero: bool = False
    enabled: bool = True
    last_run_tick: int = -1

    def should_run(self, tick: int) -> bool:
        if not self.enabled:
            return False
        if tick == 0:
            return self.run_on_tick_zero
        return tick % self.interval_ticks == 0 and self.last_run_tick != tick


class Scheduler:
    """Deterministic tick scheduler used by the engine lifecycle."""

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._errors: list[tuple[str, str]] = []

    def every(self, name: str, interval_ticks: int, callback: TaskCallback, *, run_on_tick_zero: bool = False) -> None:
        if interval_ticks <= 0:
            raise ValueError("interval_ticks must be positive")
        self._tasks[name] = ScheduledTask(name, interval_ticks, callback, run_on_tick_zero)

    def disable(self, name: str) -> None:
        self._tasks[name].enabled = False

    def enable(self, name: str) -> None:
        self._tasks[name].enabled = True

    def run_due(self, tick: int) -> None:
        for task in list(self._tasks.values()):
            if not task.should_run(tick):
                continue
            try:
                task.callback()
                task.last_run_tick = tick
            except Exception as exc:
                self._errors.append((task.name, f"{type(exc).__name__}: {exc}"))

    @property
    def tasks(self) -> tuple[ScheduledTask, ...]:
        return tuple(self._tasks.values())

    @property
    def errors(self) -> tuple[tuple[str, str], ...]:
        return tuple(self._errors)

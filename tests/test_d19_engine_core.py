from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.application.bootstrap import GameBootstrapper
from astergard.characters.models import Character
from astergard.engine.events import EngineEvent, EventBus
from astergard.engine.lifecycle import EngineLifecycle
from astergard.engine.scheduler import Scheduler
from astergard.server.game import GameServer


class EngineCoreD19Tests(unittest.TestCase):
    def test_event_bus_isolates_failing_subscribers(self) -> None:
        bus = EventBus()
        seen: list[str] = []

        def fail(_: EngineEvent) -> None:
            raise RuntimeError("boom")

        def ok(event: EngineEvent) -> None:
            seen.append(event.type)

        bus.subscribe("x", fail)
        bus.subscribe("x", ok)
        bus.emit("x", value=1)
        self.assertEqual(seen, ["x"])
        self.assertEqual(len(bus.errors), 1)
        self.assertEqual(bus.history[0].payload["value"], 1)

    def test_scheduler_runs_due_tasks_without_repeating_same_tick(self) -> None:
        scheduler = Scheduler()
        calls: list[int] = []
        scheduler.every("two", 2, lambda: calls.append(1))
        for tick in range(5):
            scheduler.run_due(tick)
            scheduler.run_due(tick)
        self.assertEqual(len(calls), 2)

    def test_lifecycle_flush_all_persists_character_and_world(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "mud.db"
            services = GameBootstrapper(str(db)).build()
            player = Character("tester")
            services.repo.register("tester", "secret")
            player.gold = 42
            players = [player]
            lifecycle = EngineLifecycle(services, lambda: players, services.event_bus, services.scheduler)
            lifecycle.flush_all("unit_test")
            loaded = services.repo.load("tester")
            self.assertEqual(loaded.gold, 42)
            self.assertGreaterEqual(services.repo.world_state.save_version(), 1)
            audit = services.repo.audit.recent("system", 10)
            self.assertTrue(any(event.event_type == "engine_flush" for event in audit))

    def test_game_server_shutdown_requests_lifecycle_flush(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            server = GameServer(str(Path(tmp) / "mud.db"))
            server.shutdown("unit_test")
            self.assertTrue(server.lifecycle.shutdown_requested)
            self.assertGreaterEqual(server.repo.world_state.save_version(), 1)


if __name__ == "__main__":
    unittest.main()

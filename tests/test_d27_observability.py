from __future__ import annotations

import asyncio
import unittest

from astergard.engine.events import DomainEventType
from astergard.testing import TestGameHarness


class D27ObservabilityTests(unittest.TestCase):
    def test_observability_records_command_metrics(self) -> None:
        async def scenario() -> None:
            with TestGameHarness() as harness:
                helper = harness.create_character("observer")
                helper.admin_role = "helper"
                await harness.execute(helper, "cechy")
                metrics = await harness.execute(helper, "metrics")
                self.assertIn("Metryki silnika", metrics.output)
                self.assertIn("Komendy:", metrics.output)
                snapshot = harness.require_server().services.observability.snapshot()
                self.assertGreaterEqual(snapshot.command_count, 2)

        asyncio.run(scenario())

    def test_observability_records_domain_event_counters(self) -> None:
        async def scenario() -> None:
            with TestGameHarness() as harness:
                helper = harness.create_character("eventer")
                helper.admin_role = "helper"
                server = harness.require_server()
                server.services.event_bus.emit(DomainEventType.CHARACTER_SPOKE, username="eventer", room_id=0)
                events = await harness.execute(helper, "events 5")
                self.assertIn("Event counters", events.output)
                self.assertIn("character.spoke", events.output)

        asyncio.run(scenario())

    def test_lag_command_reports_tick_metrics_after_lifecycle_tick(self) -> None:
        async def scenario() -> None:
            with TestGameHarness() as harness:
                helper = harness.create_character("ticker")
                helper.admin_role = "helper"
                server = harness.require_server()
                server.lifecycle.tick(server.heartbeat.tick_once)
                lag = await harness.execute(helper, "lag")
                self.assertIn("Diagnostyka ticków", lag.output)
                self.assertIn("Ostatni tick", lag.output)

        asyncio.run(scenario())

    def test_player_cannot_read_diagnostics(self) -> None:
        async def scenario() -> None:
            with TestGameHarness() as harness:
                player = harness.create_character("plain_diag")
                result = await harness.execute(player, "diagnostics")
                self.assertIn("Nie masz uprawnień", result.output)

        asyncio.run(scenario())

    def test_diagnostics_command_combines_metrics_lag_and_events(self) -> None:
        async def scenario() -> None:
            with TestGameHarness() as harness:
                helper = harness.create_character("diag")
                helper.admin_role = "helper"
                server = harness.require_server()
                server.lifecycle.tick(server.heartbeat.tick_once)
                output = await harness.execute(helper, "diagnostics")
                self.assertIn("Metryki silnika", output.output)
                self.assertIn("Diagnostyka ticków", output.output)
                self.assertIn("Event counters", output.output)

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from astergard.characters.models import Character
from astergard.engine.events import DomainEventType, EventBus
from astergard.items.models import Item
from astergard.server.game import GameServer


class DomainEventD20Tests(unittest.TestCase):
    def test_event_bus_accepts_typed_domain_event_names(self) -> None:
        bus = EventBus()
        seen: list[str] = []
        bus.subscribe(DomainEventType.CHARACTER_MOVED, lambda event: seen.append(event.type))
        bus.emit(DomainEventType.CHARACTER_MOVED, username="arek", from_room_id=1, to_room_id=2)
        self.assertEqual(seen, ["character.moved"])
        self.assertEqual(bus.history[0].actor, "arek")

    def test_movement_emits_domain_event_and_audit_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            server = GameServer(str(Path(tmp) / "mud.db"))
            char = Character("tester")
            start_room = char.room_id
            start_location = server.world.get_location(start_room)
            assert start_location is not None
            direction = next(iter(start_location.exits))
            server.move_direct(char, direction)
            events = [event for event in server.services.event_bus.history if event.type == DomainEventType.CHARACTER_MOVED.value]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].payload["username"], "tester")
            self.assertEqual(events[0].payload["from_room_id"], start_room)
            self.assertEqual(events[0].payload["to_room_id"], char.room_id)
            audit = server.repo.audit.recent("system", 20)
            self.assertTrue(any(row.event_type == DomainEventType.CHARACTER_MOVED.value for row in audit))

    def test_inventory_events_are_emitted_by_command_path(self) -> None:
        async def scenario() -> None:
            with tempfile.TemporaryDirectory() as tmp:
                server = GameServer(str(Path(tmp) / "mud.db"))
                char = Character("tester")
                loc = server.world.get_location(char.room_id)
                assert loc is not None
                loc.items.append(Item("żelazny klucz", "Ciężki klucz.", 0.1, 1, "iron_key"))
                ctx = server.make_context(char)
                response = await server.dispatcher.execute_line(ctx, "wez klucz")
                self.assertIn("Podnosisz", response)
                events = [event.type for event in server.services.event_bus.history]
                self.assertIn(DomainEventType.ITEM_PICKED_UP.value, events)
        asyncio.run(scenario())

    def test_failing_domain_event_subscriber_is_audited_as_bus_error_only(self) -> None:
        bus = EventBus()
        bus.subscribe(DomainEventType.ECONOMY_ITEM_BOUGHT, lambda event: (_ for _ in ()).throw(RuntimeError("broken")))
        bus.emit(DomainEventType.ECONOMY_ITEM_BOUGHT, username="tester", item="chleb", price=2)
        self.assertEqual(len(bus.errors), 1)
        self.assertEqual(bus.history[0].type, DomainEventType.ECONOMY_ITEM_BOUGHT.value)


if __name__ == "__main__":
    unittest.main()

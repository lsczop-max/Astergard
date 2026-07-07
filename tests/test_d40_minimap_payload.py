from __future__ import annotations

import asyncio
import json
import unittest
from typing import Any, cast

from astergard.testing import FakeReader, FakeWriter, TestGameHarness


class MinimapPayloadTests(unittest.TestCase):
    def test_payload_contains_all_world_rooms(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            payload = server.services.minimap_service.build_payload(
                character,
                server.world,
            )
            self.assertEqual(payload["type"], "full_map_debug")
            self.assertEqual(len(payload["rooms"]), len(server.world.locations))

    def test_payload_contains_current_location(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            location = server.world.get_location(60)
            self.assertIsNotNone(location)
            assert location is not None
            payload = server.services.minimap_service.build_payload(
                character,
                server.world,
            )
            self.assertEqual(payload["current_room_id"], 60)
            self.assertEqual(payload["current_room_name"], location.name)
            self.assertEqual(payload["current_zone"], location.zone)

    def test_payload_contains_exits_for_rooms(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            payload = server.services.minimap_service.build_payload(
                character,
                server.world,
            )
            room = payload["rooms"]["60"]
            self.assertIn("exits", room)
            self.assertIsInstance(room["exits"], dict)

    def test_payload_is_valid_json(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            payload = server.services.minimap_service.build_payload(
                character,
                server.world,
            )
            serialized = server.services.minimap_service.serialize_payload(payload)
            self.assertTrue(serialized.startswith("<MAP_JSON>"))
            self.assertTrue(serialized.endswith("</MAP_JSON>"))
            decoded = json.loads(
                serialized.removeprefix("<MAP_JSON>").removesuffix("</MAP_JSON>")
            )
            self.assertEqual(decoded["type"], "full_map_debug")

    def test_payload_is_sent_on_entry_and_move(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("entry", "secret"))
            character = server.repo.load("entry")
            character.room_id = 60
            server.repo.save(character)

            reader = FakeReader.from_text_lines(["entry", "secret"])
            writer = FakeWriter()
            login = asyncio.run(
                server.session_flow.login(cast(Any, reader), cast(Any, writer))
            )
            self.assertIsNotNone(login.character)
            assert login.character is not None

            asyncio.run(
                server.session_flow.send_initial_view(
                    cast(Any, writer),
                    server.make_context(login.character),
                )
            )
            initial_text = writer.text()
            self.assertIn("<MAP_JSON>", initial_text)
            self.assertIn("Widoczne wyjścia", initial_text)

            writer.clear()
            move_reader = FakeReader.from_text_lines(["poludnie"])
            asyncio.run(
                server.session_flow.command_loop(
                    cast(Any, move_reader),
                    cast(Any, writer),
                    server.make_context(login.character),
                )
            )
            moved_text = writer.text()
            self.assertIn("Wychodzisz na poludnie.", moved_text)
            self.assertIn("<MAP_JSON>", moved_text)

    def test_look_and_move_still_work(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("runner", room_id=60)
            async def run_look() -> str:
                return await server.services.dispatcher.commands["look"](
                    server.make_context(character),
                    None,
                    1,
                )

            self.assertIn("Widoczne wyjścia", asyncio.run(run_look()))
            output = server.services.exploration_service.move_direct(
                server.make_context(character).exploration(),
                character,
                "poludnie",
            )
            self.assertIn("Wychodzisz", output)


if __name__ == "__main__":
    unittest.main()

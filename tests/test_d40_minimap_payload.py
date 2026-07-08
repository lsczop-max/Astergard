from __future__ import annotations

import asyncio
import json
import os
import unittest
from typing import Any, cast
from unittest.mock import patch

from astergard.testing import FakeReader, FakeWriter, TestGameHarness
from astergard.utils import send_to_client


class MinimapPayloadTests(unittest.TestCase):
    def test_full_payload_contains_all_world_rooms(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            payload = server.services.minimap_service.build_payload(
                character,
                server.world,
            )
            self.assertEqual(payload["type"], "full_map_debug")
            self.assertEqual(len(payload["rooms"]), len(server.world.locations))

    def test_update_payload_is_minimal(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            payload = server.services.minimap_service.build_update_payload(
                character,
                server.world,
            )
            self.assertEqual(payload["type"], "map_update")
            self.assertIn("current_room_id", payload)
            self.assertIn("current_room_name", payload)
            self.assertIn("current_zone", payload)
            self.assertIn("exits", payload)
            self.assertIn("nearby_rooms", payload)
            self.assertNotIn("rooms", payload)

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

    def test_send_to_client_uses_utf8_and_crlf(self) -> None:
        writer = FakeWriter()
        asyncio.run(
            send_to_client(
                cast(Any, writer),
                "Żołnierz Kuźnia Brama Dymnych Chorągwi",
                "[w pełni sił] [Stan: zdrowy] [Złoto: bez pieniędzy] > ",
            )
        )
        self.assertEqual(
            writer.chunks[0],
            "Żołnierz Kuźnia Brama Dymnych Chorągwi\r\n".encode("utf-8"),
        )
        self.assertEqual(writer.chunks[1], "[w pełni sił] [Stan: zdrowy] [Złoto: bez pieniędzy] > ".encode("utf-8"))

    def test_map_payload_is_off_by_default(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertFalse(server.mudlet_map_enabled)
            self.assertFalse(server.services.minimap_service.enabled)
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
            self.assertNotIn("<MAP_JSON>", initial_text)
            self.assertEqual(initial_text.count("[w pełni sił]"), 1)

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
            self.assertNotIn("<MAP_JSON>", moved_text)
            self.assertEqual(moved_text.count("[w pełni sił]"), 1)

    def test_map_payload_is_enabled_via_env(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_MUDLET_MAP": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.mudlet_map_enabled)
                self.assertTrue(server.services.minimap_service.enabled)
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
                self.assertIn('"type":"full_map_debug"', initial_text)
                self.assertEqual(initial_text.count("[w pełni sił]"), 1)
                self.assertLess(initial_text.index("<MAP_JSON>"), initial_text.index("[w pełni sił]"))

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
                self.assertIn('"type":"map_update"', moved_text)
                self.assertNotIn('"type":"full_map_debug"', moved_text)
                self.assertEqual(moved_text.count("[w pełni sił]"), 1)

    def test_debug_map_command_sends_full_payload_only_when_enabled(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_MUDLET_MAP": "1"}, clear=False):
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
                assert login.character is not None
                login.character.admin_role = "helper"
                writer.clear()

                debug_reader = FakeReader.from_text_lines(["debug_map"])
                asyncio.run(
                    server.session_flow.command_loop(
                        cast(Any, debug_reader),
                        cast(Any, writer),
                        server.make_context(login.character),
                    )
                )
                debug_text = writer.text()
                self.assertIn("Wysyłam pełny podgląd mapy.", debug_text)
                self.assertIn("<MAP_JSON>", debug_text)
                self.assertIn('"type":"full_map_debug"', debug_text)


if __name__ == "__main__":
    unittest.main()

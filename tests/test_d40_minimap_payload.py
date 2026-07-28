from __future__ import annotations

import asyncio
import json
import os
import re
import unittest
from typing import Any, cast
from unittest.mock import patch

from astergard.application.session_transport import TcpSessionTransport
from astergard.gmcp import POLISH_TO_MUDLET_DIRECTION
from astergard.protocol.web_v1 import WEB_MESSAGE_MAX_BYTES, build_web_envelope, serialize_web_envelope
from astergard.testing import FakeReader, FakeWriter, TestGameHarness
from astergard.world.models import Exit
from astergard.utils import send_to_client


class MinimapPayloadTests(unittest.TestCase):
    def _map_payloads(self, text: str) -> list[dict[str, Any]]:
        return [json.loads(match) for match in re.findall(r"<MAP_JSON>(.*?)</MAP_JSON>", text)]

    def _snapshot_exits(self, *locations: Any) -> dict[int, dict[str, Exit]]:
        return {location.id: dict(location.exits) for location in locations}

    def _restore_exits(self, server: Any, snapshots: dict[int, dict[str, Exit]]) -> None:
        for room_id, exits in snapshots.items():
            location = server.world.get_location(room_id)
            if location is None:
                continue
            location.exits.clear()
            location.exits.update(exits)

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
                "w pełni sił, jest w pełni sił, bez pieniędzy. > ",
            )
        )
        self.assertEqual(
            writer.chunks[0],
            "Żołnierz Kuźnia Brama Dymnych Chorągwi\r\n".encode("utf-8"),
        )
        self.assertEqual(writer.chunks[1], "w pełni sił, jest w pełni sił, bez pieniędzy. > ".encode("utf-8"))

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
            transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
            login = asyncio.run(server.session_flow.login(transport))
            self.assertIsNotNone(login.character)
            assert login.character is not None

            asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
            initial_text = writer.text()
            expected_prompt = server.prompt(login.character)
            self.assertNotIn("<MAP_JSON>", initial_text)
            self.assertEqual(initial_text.count(expected_prompt), 1)

            writer.clear()
            move_reader = FakeReader.from_text_lines(["ne"])
            move_transport = TcpSessionTransport(cast(Any, move_reader), cast(Any, writer))
            server.clients[move_transport] = login.character
            asyncio.run(server.session_flow.command_loop(move_transport, server.make_context(login.character)))
            moved_text = writer.text()
            self.assertIn("Kierujesz się na północny wschód.", moved_text)
            self.assertNotIn("<MAP_JSON>", moved_text)
            self.assertEqual(moved_text.count(expected_prompt), 1)

    def test_map_payload_omits_hidden_exits_in_full_and_incremental_updates(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_MUDLET_MAP": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.mudlet_map_enabled)
                self.assertTrue(server.services.minimap_service.enabled)
                self.assertTrue(server.repo.register("entry", "secret"))
                character = server.repo.load("entry")
                location = server.world.get_location(0)
                assert location is not None
                location.exits["sekretny-most"] = Exit(61, is_door=True, kind="most", description="Jawny most", visible=True)
                location.exits["gora"] = Exit(987654, is_door=True, is_locked=True, kind="Wieża Magów", description="Sekretna brama", visible=False)
                snapshot = {
                    direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible)
                    for direction, exit_ in location.exits.items()
                }
                character.room_id = location.id
                server.repo.save(character)

                reader = FakeReader.from_text_lines(["entry", "secret", "look", "wschod"])
                writer = FakeWriter()
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                login = asyncio.run(server.session_flow.login(transport))
                self.assertIsNotNone(login.character)
                assert login.character is not None

                asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
                initial_text = writer.text()
                initial_payloads = [json.loads(match) for match in re.findall(r"<MAP_JSON>(.*?)</MAP_JSON>", initial_text)]
                self.assertEqual(len(initial_payloads), 1)
                self.assertEqual(initial_payloads[0]["type"], "full_map_debug")
                expected_exits = {
                    POLISH_TO_MUDLET_DIRECTION[direction]: target
                    for direction, (target, _is_door, _is_locked, _kind, _description, visible) in snapshot.items()
                    if visible and direction in POLISH_TO_MUDLET_DIRECTION
                }
                self.assertEqual(
                    initial_payloads[0]["rooms"][str(location.id)]["exits"],
                    expected_exits,
                )
                self.assertNotIn("Wieża Magów", initial_text)
                self.assertNotIn("987654", initial_text)
                self.assertNotIn("gora", initial_text)
                self.assertEqual(
                    {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                    snapshot,
                )

                writer.clear()
                server.clients[transport] = login.character
                asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))
                command_text = writer.text()
                command_payloads = [json.loads(match) for match in re.findall(r"<MAP_JSON>(.*?)</MAP_JSON>", command_text)]
                self.assertEqual([payload["type"] for payload in command_payloads], ["map_update", "map_update"])
                self.assertEqual(command_payloads[0]["exits"], expected_exits)
                moved_location = server.world.get_location(login.character.room_id)
                self.assertIsNotNone(moved_location)
                assert moved_location is not None
                expected_moved_exits = {
                    POLISH_TO_MUDLET_DIRECTION[direction]: exit_.target_room
                    for direction, exit_ in moved_location.exits.items()
                    if exit_.visible and direction in POLISH_TO_MUDLET_DIRECTION
                }
                self.assertEqual(command_payloads[1]["exits"], expected_moved_exits)
                self.assertIn("Kierujesz się na wschód.", command_text)
                self.assertNotIn("Wieża Magów", command_text)
                self.assertNotIn("987654", command_text)
                self.assertNotIn("gora", command_text)
                self.assertEqual(
                    {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                    snapshot,
                )

    def test_map_payload_handles_room_without_public_exits(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_MUDLET_MAP": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("entry", "secret"))
                character = server.repo.load("entry")
                location = next(loc for loc in server.world.locations.values() if loc.id != 14)
                original_exits = dict(location.exits)
                location.exits.clear()
                location.exits["sekretny-most"] = Exit(
                    987654,
                    is_door=True,
                    kind="most",
                    description="Jawny most",
                    visible=False,
                )
                snapshot = {
                    direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible)
                    for direction, exit_ in location.exits.items()
                }
                character.room_id = location.id
                server.repo.save(character)

                reader = FakeReader.from_text_lines(["entry", "secret", "look"])
                writer = FakeWriter()
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                login = asyncio.run(server.session_flow.login(transport))
                self.assertIsNotNone(login.character)
                assert login.character is not None

                asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
                initial_text = writer.text()
                initial_payloads = [json.loads(match) for match in re.findall(r"<MAP_JSON>(.*?)</MAP_JSON>", initial_text)]
                self.assertEqual(len(initial_payloads), 1)
                self.assertEqual(initial_payloads[0]["type"], "full_map_debug")
                self.assertNotIn("sekretny-most", initial_text)
                self.assertNotIn("987654", initial_text)
                self.assertEqual(initial_payloads[0]["rooms"][str(location.id)]["exits"], {})
                self.assertEqual(
                    {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                    snapshot,
                )

                writer.clear()
                server.clients[transport] = login.character
                asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))
                command_text = writer.text()
                command_payloads = [json.loads(match) for match in re.findall(r"<MAP_JSON>(.*?)</MAP_JSON>", command_text)]
                self.assertEqual([payload["type"] for payload in command_payloads], ["map_update"])
                self.assertNotIn("sekretny-most", command_text)
                self.assertNotIn("987654", command_text)
                self.assertEqual(command_payloads[0]["exits"], {})
                self.assertEqual(
                    {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                    snapshot,
                )
                location.exits.clear()
                location.exits.update(original_exits)

    def test_map_update_uses_visible_graph_for_nearby_rooms(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_MUDLET_MAP": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("entry", "secret"))
                character = server.repo.load("entry")

                origin = server.world.get_location(60)
                hidden_target = server.world.get_location(61)
                move_target = server.world.get_location(62)
                hidden_continuation = server.world.get_location(63)
                self.assertIsNotNone(origin)
                self.assertIsNotNone(hidden_target)
                self.assertIsNotNone(move_target)
                self.assertIsNotNone(hidden_continuation)
                assert origin is not None and hidden_target is not None and move_target is not None and hidden_continuation is not None

                snapshots = self._snapshot_exits(origin, hidden_target, move_target, hidden_continuation)
                try:
                    for room in (origin, hidden_target, move_target, hidden_continuation):
                        room.exits.clear()

                    origin.exits["gora"] = Exit(hidden_target.id, kind="Wieża Magów", description="Sekretne przejście", visible=False)
                    hidden_target.exits["wschod"] = Exit(hidden_continuation.id, kind="most", description="Jawny pomost", visible=True)
                    move_target.exits.clear()
                    origin.exits["poludnie"] = Exit(move_target.id, kind="droga", description="Jawna droga na południe", visible=True)
                    character.room_id = origin.id
                    server.repo.save(character)

                    reader = FakeReader.from_text_lines(["entry", "secret", "look", "poludnie"])
                    writer = FakeWriter()
                    transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                    login = asyncio.run(server.session_flow.login(transport))
                    self.assertIsNotNone(login.character)
                    assert login.character is not None

                    asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
                    writer.clear()
                    server.clients[transport] = login.character
                    asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))
                    command_text = writer.text()
                    payloads = self._map_payloads(command_text)
                    self.assertEqual([payload["type"] for payload in payloads], ["map_update", "map_update"])

                    look_payload = payloads[0]
                    move_payload = payloads[1]
                    self.assertEqual(look_payload["current_room_id"], origin.id)
                    self.assertEqual(look_payload["exits"], {"s": move_target.id})
                    self.assertEqual(set(look_payload["nearby_rooms"]), {str(origin.id), str(move_target.id)})
                    self.assertNotIn("Wieża Magów", command_text)
                    self.assertNotIn("gora", command_text)

                    self.assertEqual(move_payload["current_room_id"], move_target.id)
                    self.assertEqual(move_payload["exits"], {})
                    self.assertEqual(set(move_payload["nearby_rooms"]), {str(move_target.id)})
                    self.assertNotIn("Wieża Magów", command_text)
                    self.assertNotIn("gora", command_text)
                    self.assertEqual(
                        {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in origin.exits.items()},
                        {
                            "gora": (hidden_target.id, False, False, "Wieża Magów", "Sekretne przejście", False),
                            "poludnie": (move_target.id, False, False, "droga", "Jawna droga na południe", True),
                        },
                    )
                finally:
                    self._restore_exits(server, snapshots)

    def test_map_update_uses_alternative_visible_routes_and_handles_graph_edges(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_MUDLET_MAP": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("entry", "secret"))
                character = server.repo.load("entry")

                origin = server.world.get_location(70)
                hidden_mid = server.world.get_location(71)
                target = server.world.get_location(72)
                one_way_source = server.world.get_location(73)
                one_way_target = server.world.get_location(74)
                missing_source = server.world.get_location(75)
                cycle_source = server.world.get_location(76)
                cycle_target = server.world.get_location(77)
                self.assertIsNotNone(origin)
                self.assertIsNotNone(hidden_mid)
                self.assertIsNotNone(target)
                self.assertIsNotNone(one_way_source)
                self.assertIsNotNone(one_way_target)
                self.assertIsNotNone(missing_source)
                self.assertIsNotNone(cycle_source)
                self.assertIsNotNone(cycle_target)
                assert (
                    origin is not None
                    and hidden_mid is not None
                    and target is not None
                    and one_way_source is not None
                    and one_way_target is not None
                    and missing_source is not None
                    and cycle_source is not None
                    and cycle_target is not None
                )

                snapshots = self._snapshot_exits(origin, hidden_mid, target, one_way_source, one_way_target, missing_source, cycle_source, cycle_target)
                try:
                    for room in (origin, hidden_mid, target, one_way_source, one_way_target, missing_source, cycle_source, cycle_target):
                        room.exits.clear()

                    origin.exits["gora"] = Exit(hidden_mid.id, kind="Wieża Magów", description="Sekretne przejście", visible=False)
                    hidden_mid.exits["wschod"] = Exit(target.id, kind="most", description="Jawny most", visible=True)
                    character.room_id = origin.id
                    server.repo.save(character)

                    reader = FakeReader.from_text_lines(["entry", "secret", "look"])
                    writer = FakeWriter()
                    transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                    login = asyncio.run(server.session_flow.login(transport))
                    self.assertIsNotNone(login.character)
                    assert login.character is not None
                    asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
                    writer.clear()
                    server.clients[transport] = login.character
                    asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))
                    payload = self._map_payloads(writer.text())[0]
                    self.assertEqual(set(payload["nearby_rooms"]), {str(origin.id)})

                    origin.exits["poludnie"] = Exit(target.id, kind="droga", description="Jawna droga", visible=True)
                    server.repo.save(character)
                    second_reader = FakeReader.from_text_lines(["look"])
                    second_writer = FakeWriter()
                    second_transport = TcpSessionTransport(cast(Any, second_reader), cast(Any, second_writer))
                    server.clients[second_transport] = login.character
                    asyncio.run(server.session_flow.command_loop(second_transport, server.make_context(login.character)))
                    second_payload = self._map_payloads(second_writer.text())[0]
                    self.assertEqual(set(second_payload["nearby_rooms"]), {str(origin.id), str(target.id)})
                    self.assertIn(str(target.id), second_writer.text())

                    one_way_source.exits["poludnie"] = Exit(one_way_target.id, kind="droga", description="Jednostronna droga", visible=True)
                    login.character.room_id = one_way_source.id
                    server.repo.save(login.character)
                    one_way_reader = FakeReader.from_text_lines(["look"])
                    one_way_writer = FakeWriter()
                    one_way_transport = TcpSessionTransport(cast(Any, one_way_reader), cast(Any, one_way_writer))
                    server.clients[one_way_transport] = login.character
                    asyncio.run(server.session_flow.command_loop(one_way_transport, server.make_context(login.character)))
                    one_way_payload = self._map_payloads(one_way_writer.text())[0]
                    self.assertEqual(set(one_way_payload["nearby_rooms"]), {str(one_way_source.id), str(one_way_target.id)})

                    missing_source.exits["poludnie"] = Exit(999999, kind="droga", description="Zaginiona droga", visible=True)
                    login.character.room_id = missing_source.id
                    server.repo.save(login.character)
                    missing_reader = FakeReader.from_text_lines(["look"])
                    missing_writer = FakeWriter()
                    missing_transport = TcpSessionTransport(cast(Any, missing_reader), cast(Any, missing_writer))
                    server.clients[missing_transport] = login.character
                    asyncio.run(server.session_flow.command_loop(missing_transport, server.make_context(login.character)))
                    missing_payload = self._map_payloads(missing_writer.text())[0]
                    self.assertEqual(set(missing_payload["nearby_rooms"]), {str(missing_source.id)})

                    cycle_source.exits["wschod"] = Exit(cycle_target.id, kind="droga", description="Pętla 1", visible=True)
                    cycle_target.exits["zachod"] = Exit(cycle_source.id, kind="droga", description="Pętla 2", visible=True)
                    login.character.room_id = cycle_source.id
                    server.repo.save(login.character)
                    cycle_reader = FakeReader.from_text_lines(["look"])
                    cycle_writer = FakeWriter()
                    cycle_transport = TcpSessionTransport(cast(Any, cycle_reader), cast(Any, cycle_writer))
                    server.clients[cycle_transport] = login.character
                    asyncio.run(server.session_flow.command_loop(cycle_transport, server.make_context(login.character)))
                    cycle_payload = self._map_payloads(cycle_writer.text())[0]
                    self.assertEqual(set(cycle_payload["nearby_rooms"]), {str(cycle_source.id), str(cycle_target.id)})
                finally:
                    self._restore_exits(server, snapshots)

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
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                login = asyncio.run(server.session_flow.login(transport))
                self.assertIsNotNone(login.character)
                assert login.character is not None

                asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
                initial_text = writer.text()
                expected_prompt = server.prompt(login.character)
                self.assertIn("<MAP_JSON>", initial_text)
                self.assertIn('"type":"full_map_debug"', initial_text)
                self.assertEqual(initial_text.count(expected_prompt), 1)
                self.assertLess(initial_text.index("<MAP_JSON>"), initial_text.index(expected_prompt))

                writer.clear()
                move_reader = FakeReader.from_text_lines(["ne"])
                move_transport = TcpSessionTransport(cast(Any, move_reader), cast(Any, writer))
                server.clients[move_transport] = login.character
                asyncio.run(server.session_flow.command_loop(move_transport, server.make_context(login.character)))
                moved_text = writer.text()
                self.assertIn("Kierujesz się na północny wschód.", moved_text)
                self.assertIn("<MAP_JSON>", moved_text)
                self.assertIn('"type":"map_update"', moved_text)
                self.assertNotIn('"type":"full_map_debug"', moved_text)
                self.assertEqual(moved_text.count(expected_prompt), 1)

    def test_web_map_snapshot_uses_visited_rooms_by_default(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("mapper", room_id=60)
            character.visited_room_ids = {60}

            payloads = server.services.minimap_service.build_web_snapshot_payloads(character, server.world, starting_sequence=999)
            self.assertEqual({room["room_id"] for payload in payloads for room in payload["rooms"]}, {60})
            self.assertEqual(character.visited_room_ids, {60})
            self.assertTrue(all(
                len(serialize_web_envelope(build_web_envelope("map.snapshot", payload, sequence=999 + index)).encode("utf-8")) <= WEB_MESSAGE_MAX_BYTES
                for index, payload in enumerate(payloads)
            ))

    def test_web_map_reveal_all_includes_every_room_but_keeps_hidden_exits_hidden(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_WEB_MAP_REVEAL_ALL": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.services.minimap_service.reveal_all_web_map)
                character = harness.create_character("mapper", room_id=60)
                character.visited_room_ids = {60}
                original_visited = set(character.visited_room_ids)
                room = server.world.get_location(60)
                hidden_target = server.world.get_location(62)
                assert room is not None
                assert hidden_target is not None
                snapshots = self._snapshot_exits(room, hidden_target)
                room.exits["ukryte_przejscie"] = Exit(hidden_target.id, kind="przejście", description="Ukryty skrót", visible=False)
                try:
                    payloads = server.services.minimap_service.build_web_snapshot_payloads(character, server.world, starting_sequence=999)
                    all_room_ids = {room["room_id"] for payload in payloads for room in payload["rooms"]}
                    self.assertEqual(all_room_ids, set(server.world.locations))
                    self.assertEqual(character.visited_room_ids, original_visited)
                    self.assertTrue(all(
                        len(serialize_web_envelope(build_web_envelope("map.snapshot", payload, sequence=999 + index)).encode("utf-8")) <= WEB_MESSAGE_MAX_BYTES
                        for index, payload in enumerate(payloads)
                    ))
                    self.assertFalse(
                        any(
                            edge["from_room_id"] == room.id and edge["to_room_id"] == hidden_target.id
                            for payload in payloads
                            for edge in payload["edges"]
                        )
                    )
                finally:
                    self._restore_exits(server, snapshots)

    def test_web_map_reveal_all_update_tracks_current_room_without_resending_world(self) -> None:
        with patch.dict(os.environ, {"ASTERGARD_WEB_MAP_REVEAL_ALL": "1"}, clear=False):
            with TestGameHarness() as harness:
                server = harness.require_server()
                character = harness.create_character("mapper", room_id=60)
                character.visited_room_ids = {60}
                first = server.services.minimap_service.build_web_update_payload(
                    character,
                    server.world,
                    sync_id="sync-1",
                    previous_visited_room_ids={60},
                )
                self.assertEqual(first["current_room_id"], 60)
                self.assertEqual(first["rooms"], [])
                self.assertEqual(first["edges"], [])
                character.room_id = 61
                second = server.services.minimap_service.build_web_update_payload(
                    character,
                    server.world,
                    sync_id="sync-1",
                    previous_visited_room_ids={60},
                )
                self.assertEqual(second["current_room_id"], 61)
                self.assertEqual(second["rooms"], [])
                self.assertEqual(second["edges"], [])

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
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                login = asyncio.run(server.session_flow.login(transport))
                assert login.character is not None
                login.character.admin_role = "helper"
                writer.clear()

                debug_reader = FakeReader.from_text_lines(["debug_map"])
                debug_transport = TcpSessionTransport(cast(Any, debug_reader), cast(Any, writer))
                asyncio.run(server.session_flow.command_loop(debug_transport, server.make_context(login.character)))
                debug_text = writer.text()
                self.assertIn("Wysyłam podgląd mapy.", debug_text)
                self.assertIn("<MAP_JSON>", debug_text)
                self.assertIn('"type":"full_map_debug"', debug_text)


if __name__ == "__main__":
    unittest.main()

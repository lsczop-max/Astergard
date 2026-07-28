from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Any, cast

from astergard.application.session_transport import TcpSessionTransport
from astergard.gmcp import IAC, POLISH_TO_MUDLET_DIRECTION, SE, SB, room_info_packet, room_info_payload
from astergard.testing import FakeReader, FakeWriter, TestGameHarness
from astergard.world.models import Exit
from tools.build_mudlet_package import main as build_mudlet_package
from tools.lua_syntax import validate_lua_structure
from tools.mudlet_support import (
    MAP_FILENAME,
    compare_versions,
    export_map_file,
    load_manifest,
    mudlet_paths,
    validate_manifest_data,
    validate_world_map,
    world_map_payload,
)


class MudletClientTests(unittest.TestCase):
    def test_manifest_is_valid(self) -> None:
        manifest_path = Path("client/mudlet/manifest.json")
        manifest = load_manifest(manifest_path)
        errors = validate_manifest_data(manifest)
        self.assertEqual(errors, [])
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["map_version"], "0.1.0")

    def test_version_compare(self) -> None:
        self.assertEqual(compare_versions("4.12.0", "4.12.0"), 0)
        self.assertEqual(compare_versions("4.13.0", "4.12.9"), 1)
        self.assertEqual(compare_versions("4.11.9", "4.12.0"), -1)

    def test_world_map_payload_is_consistent(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            world = server.world
            errors = validate_world_map(world)
            self.assertEqual(errors, [])
            payload = world_map_payload(world)
            self.assertEqual(payload["package"], "Astergard")
            self.assertEqual(payload["map_version"], "0.1.0")
            self.assertEqual(len(payload["rooms"]), len(world.locations))
            first = payload["rooms"][0]
            self.assertIn("coords", first)
            self.assertIn("exits", first)

    def test_export_map_file_writes_json(self) -> None:
        with TestGameHarness() as harness, tempfile.TemporaryDirectory() as tmp:
            server = harness.require_server()
            output = Path(tmp) / MAP_FILENAME
            export_map_file(server.world, output)
            decoded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(decoded["package"], "Astergard")
            self.assertEqual(decoded["version"], "0.1.0")
            self.assertEqual(len(decoded["rooms"]), len(server.world.locations))

    def test_export_map_file_omits_hidden_special_exits(self) -> None:
        with TestGameHarness() as harness, tempfile.TemporaryDirectory() as tmp:
            server = harness.require_server()
            location = next(loc for loc in server.world.locations.values() if "gora" not in loc.exits)
            location.exits["sekretny-most"] = Exit(61, is_door=True, kind="most", description="Jawny most", visible=True)
            location.exits["gora"] = Exit(987654, is_door=True, is_locked=True, kind="Wieża Magów", description="Sekretna brama", visible=False)
            snapshot = {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()}

            output = Path(tmp) / MAP_FILENAME
            export_map_file(server.world, output)
            decoded = json.loads(output.read_text(encoding="utf-8"))
            room = next(room for room in decoded["rooms"] if room["num"] == location.id)
            serialized = output.read_text(encoding="utf-8")
            self.assertNotIn("Wieża Magów", serialized)
            self.assertNotIn("987654", serialized)
            self.assertNotIn("gora", serialized)
            special_exits = room.get("special_exits", [])
            injected = next(entry for entry in special_exits if entry["direction"] == "sekretny-most")
            self.assertEqual(injected["target"], 61)
            self.assertEqual(injected["kind"], "most")
            self.assertTrue(injected["visible"])
            self.assertTrue(injected["door"])
            self.assertFalse(injected["locked"])
            self.assertNotIn("gora", {entry["direction"] for entry in special_exits})
            self.assertEqual(
                {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                snapshot,
            )

    def test_build_release_archive_contains_client_files(self) -> None:
        with tempfile.TemporaryDirectory():
            paths = mudlet_paths()
            build_mudlet_package()
            self.assertTrue((paths.releases_dir / "Astergard.mpackage").exists())
            with zipfile.ZipFile(paths.releases_dir / "Astergard.mpackage", "r") as archive:
                names = set(archive.namelist())
                self.assertIn("main.lua", names)
                self.assertIn("manifest.json", names)
                self.assertIn("src/bootstrap.lua", names)
                self.assertIn("maps/astergard_map.json", names)

    def test_lua_files_have_balanced_blocks(self) -> None:
        for lua_file in sorted(Path("client/mudlet").rglob("*.lua")):
            errors = validate_lua_structure(lua_file.read_text(encoding="utf-8"))
            self.assertEqual(errors, [], msg=f"{lua_file}: {errors}")

    def test_room_info_packet_is_gmcp_frame(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            location = server.world.get_location(14)
            assert location is not None
            packet = room_info_packet(location, server.world)
            self.assertTrue(packet.startswith(bytes([IAC, SB])))
            self.assertTrue(packet.endswith(bytes([IAC, SE])))
            self.assertIn(b"Room.Info", packet)

    def test_room_info_packet_omits_hidden_special_exits(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            location = next(loc for loc in server.world.locations.values() if "gora" not in loc.exits)
            location.exits["sekretny-most"] = Exit(61, is_door=True, kind="most", description="Jawny most", visible=True)
            location.exits["gora"] = Exit(987654, is_door=True, is_locked=True, kind="Wieża Magów", description="Sekretna brama", visible=False)
            snapshot = {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()}

            payload = room_info_payload(location, server.world)
            packet = room_info_packet(location, server.world)
            text = packet.decode("utf-8", errors="ignore")
            self.assertNotIn("Wieża Magów", text)
            self.assertNotIn("987654", text)
            self.assertNotIn("gora", text)

            expected_exits = {
                POLISH_TO_MUDLET_DIRECTION[direction]: target
                for direction, (target, _is_door, _is_locked, _kind, _description, visible) in snapshot.items()
                if visible and direction in POLISH_TO_MUDLET_DIRECTION
            }
            self.assertEqual(payload["exits"], expected_exits)
            self.assertEqual(
                {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                snapshot,
            )
            self.assertTrue(
                any(
                    entry["direction"] == "sekretny-most"
                    and entry["target"] == 61
                    and entry["kind"] == "most"
                    and entry["visible"] is True
                    and entry["door"] is True
                    and entry["locked"] is False
                    for entry in payload.get("special_exits", [])
                )
            )
            self.assertFalse(any(entry["direction"] == "up" and entry["target"] == 987654 for entry in payload.get("special_exits", [])))

    def test_initial_view_sends_room_info(self) -> None:
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
            asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
            payload = b"".join(writer.chunks)
            self.assertIn(b"Core.Hello", payload)
            self.assertIn(b"Room.Info", payload)
            self.assertIn(bytes([IAC, 251, 201]), payload)

    def test_room_info_is_sent_after_movement(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("entry", "secret"))
            character = server.repo.load("entry")
            character.room_id = 60
            server.repo.save(character)

            reader = FakeReader.from_text_lines(["entry", "secret", "ne"])
            writer = FakeWriter()
            transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
            login = asyncio.run(server.session_flow.login(transport))
            assert login.character is not None
            asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
            writer.clear()
            server.clients[transport] = login.character
            asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))
            payload = b"".join(writer.chunks)
            self.assertIn(b"Room.Info", payload)
            self.assertIn(b"Kierujesz si", payload)
            self.assertTrue(any(chunk.startswith(bytes([IAC, SB])) for chunk in writer.chunks))

    def test_session_loop_sends_room_info_on_room_change(self) -> None:
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
            self.assertIsNotNone(login.character)
            assert login.character is not None

            asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
            writer.clear()
            move_reader = FakeReader.from_text_lines(["ne"])
            move_transport = TcpSessionTransport(cast(Any, move_reader), cast(Any, writer))
            server.clients[move_transport] = login.character
            asyncio.run(server.session_flow.command_loop(move_transport, server.make_context(login.character)))
            payload = b"".join(writer.chunks)
            self.assertIn(b"Room.Info", payload)
            self.assertIn(b"Kierujesz si", payload)


if __name__ == "__main__":
    unittest.main()

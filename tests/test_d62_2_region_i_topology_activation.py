from __future__ import annotations

import unittest

from astergard.gmcp import room_info_payload
from astergard.testing import TestGameHarness
from astergard.world.manager import STARTING_ROOM_ID, WorldManager
from astergard.world.region_i_loader import load_region_i_data


class RegionITopologyActivationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load_region_i_data()
        self.room_ids = {room.id for room in self.data.rooms}
        self.deprecated_room_ids = set(range(2, 14)) | set(range(15, 20))

    def test_runtime_contains_canonical_region_i_rooms_and_omits_deprecated_ids(self) -> None:
        world = WorldManager()
        world.generate_world()

        for room_id in self.room_ids:
            self.assertIsNotNone(world.get_location(room_id), msg=f"missing room {room_id}")
        for room_id in self.deprecated_room_ids:
            self.assertIsNone(world.get_location(room_id), msg=f"deprecated room {room_id} still present")

    def test_runtime_room_metadata_matches_json(self) -> None:
        world = WorldManager()
        world.generate_world()

        for room in self.data.rooms:
            location = world.get_location(room.id)
            self.assertIsNotNone(location, msg=f"missing room {room.id}")
            assert location is not None
            self.assertEqual(location.name, room.name)
            self.assertEqual(location.zone, room.region_id)
            self.assertEqual((location.map_x, location.map_y, location.map_z), (room.x, room.y, room.z))

    def test_runtime_has_exactly_219_logical_connections_for_region_i(self) -> None:
        world = WorldManager()
        world.generate_world()

        pairs: set[tuple[int, int]] = set()
        for room_id in self.room_ids:
            location = world.get_location(room_id)
            self.assertIsNotNone(location, msg=f"missing room {room_id}")
            assert location is not None
            for exit_ in location.exits.values():
                self.assertIn(exit_.target_room, self.room_ids, msg=f"room {room_id} still exits to {exit_.target_room}")
                pair = (room_id, exit_.target_room)
                pairs.add(pair if pair[0] <= pair[1] else (pair[1], pair[0]))

        self.assertEqual(len(pairs), 219)
        self.assertEqual(pairs, self.data.edge_pairs)

    def test_region_i_is_fully_reachable_from_start(self) -> None:
        world = WorldManager()
        world.generate_world()

        visited: set[int] = set()
        queue = [STARTING_ROOM_ID]
        while queue:
            room_id = queue.pop()
            if room_id in visited:
                continue
            visited.add(room_id)
            location = world.get_location(room_id)
            self.assertIsNotNone(location, msg=f"missing room {room_id}")
            assert location is not None
            for exit_ in location.exits.values():
                if exit_.target_room in self.room_ids and exit_.target_room not in visited:
                    queue.append(exit_.target_room)

        self.assertEqual(visited, self.room_ids)

    def test_region_i_entry_points_and_no_external_exits(self) -> None:
        world = WorldManager()
        world.generate_world()

        room_62 = world.get_location(62)
        room_84 = world.get_location(84)
        room_76 = world.get_location(76)
        room_86 = world.get_location(86)
        self.assertIsNotNone(room_62)
        self.assertIsNotNone(room_84)
        self.assertIsNotNone(room_76)
        self.assertIsNotNone(room_86)
        assert room_62 is not None and room_84 is not None and room_76 is not None and room_86 is not None

        self.assertIn("wschod", room_62.exits)
        self.assertEqual(room_62.exits["wschod"].target_room, 87)
        self.assertIn("poludnie", room_84.exits)
        self.assertEqual(room_84.exits["poludnie"].target_room, 157)

        self.assertTrue(all(exit_.target_room in self.room_ids for exit_ in room_76.exits.values()))
        self.assertTrue(all(exit_.target_room in self.room_ids for exit_ in room_86.exits.values()))

        for room_id in self.room_ids:
            location = world.get_location(room_id)
            assert location is not None
            for exit_ in location.exits.values():
                self.assertIn(exit_.target_room, self.room_ids)

    def test_gmcp_room_info_serializes_new_region_i_room(self) -> None:
        world = WorldManager()
        world.generate_world()
        room = world.get_location(STARTING_ROOM_ID)
        self.assertIsNotNone(room)
        assert room is not None

        payload = room_info_payload(room, world)
        self.assertEqual(payload["num"], STARTING_ROOM_ID)
        self.assertEqual(payload["name"], room.name)
        self.assertEqual(payload["area"], room.zone)
        self.assertEqual(payload["coords"], {"x": room.map_x, "y": room.map_y, "z": room.map_z})
        self.assertTrue(payload["exits"])

    def test_web_map_snapshot_reveals_full_region_i_topology(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            server.services.minimap_service.reveal_all_web_map = True
            character = harness.create_character("mapper", room_id=STARTING_ROOM_ID)

            payloads = server.services.minimap_service.build_web_snapshot_payloads(
                character,
                server.world,
                max_bytes=10_000_000,
            )
            self.assertEqual(len(payloads), 1)
            payload = payloads[0]
            self.assertEqual(payload["current_room_id"], STARTING_ROOM_ID)

            rooms = {int(room["room_id"]): room for room in payload["rooms"]}
            self.assertTrue(all(room_id in rooms for room_id in self.room_ids))
            self.assertTrue(all(room_id not in rooms for room_id in self.deprecated_room_ids))

            snapshot_pairs: set[tuple[int, int]] = set()
            for edge in payload["edges"]:
                left = int(edge["from_room_id"])
                right = int(edge["to_room_id"])
                if left not in self.room_ids or right not in self.room_ids:
                    continue
                snapshot_pairs.add((left, right) if left <= right else (right, left))
            self.assertEqual(snapshot_pairs, self.data.edge_pairs)


if __name__ == "__main__":
    unittest.main()

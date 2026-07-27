from __future__ import annotations

import json
import unittest

from astergard.world.manager import STARTING_ROOM_ID, WorldManager
from astergard.world.region_i_loader import (
    JSON_TO_RUNTIME_DIRECTION,
    REGION_I_ASSET_PATH,
    RegionIDataError,
    load_region_i_data,
)


class RegionIDataLoaderTests(unittest.TestCase):
    def test_loader_parses_canonical_asset(self) -> None:
        data = load_region_i_data()

        self.assertEqual(data.schema_version, 1)
        self.assertTrue(data.name.startswith("Region I"))
        self.assertEqual(len(data.rooms), 170)
        self.assertEqual(len(data.edges), 219)

        room_ids = {room.id for room in data.rooms}
        expected_ids = {0, 1, 14, 20} | set(range(21, 187))
        expected_ids -= set(range(2, 14))
        expected_ids -= set(range(15, 20))
        self.assertEqual(room_ids, expected_ids)
        self.assertNotIn(2, room_ids)
        self.assertNotIn(13, room_ids)
        self.assertNotIn(15, room_ids)
        self.assertNotIn(19, room_ids)
        self.assertIn(STARTING_ROOM_ID, room_ids)
        self.assertEqual(data.room_ids, room_ids)

        self.assertTrue(all(edge.bidirectional for edge in data.edges))
        self.assertTrue(all(edge.direction in JSON_TO_RUNTIME_DIRECTION.values() for edge in data.edges))
        self.assertEqual(len(data.edge_pairs), 219)
        self.assertEqual({room.id for room in data.rooms if room.id == STARTING_ROOM_ID}, {STARTING_ROOM_ID})

    def test_loader_rejects_unknown_or_broken_payloads(self) -> None:
        raw = json.loads(REGION_I_ASSET_PATH.read_text(encoding="utf-8"))
        raw["rooms"][0]["id"] = 999
        raw["edges"][0]["direction"] = "Q"
        # A direct parse of the broken payload should fail even before reachability.
        from astergard.world.region_i_loader import _parse_region_i_payload

        with self.assertRaises(RegionIDataError):
            _parse_region_i_payload(raw, require_unique_coords=True)

    def test_loader_does_not_modify_runtime_world(self) -> None:
        world = WorldManager()
        world.generate_world()
        start_room = world.get_location(STARTING_ROOM_ID)
        assert start_room is not None
        before = {
            "room_count": len(world.locations),
            "start_room_name": start_room.name,
            "zone": start_room.zone,
        }

        data = load_region_i_data()
        self.assertEqual(len(data.rooms), 170)
        start_room_after = world.get_location(STARTING_ROOM_ID)
        assert start_room_after is not None
        after = {
            "room_count": len(world.locations),
            "start_room_name": start_room_after.name,
            "zone": start_room_after.zone,
        }
        self.assertEqual(before, after)

    def test_runtime_direction_translation_covers_all_edges(self) -> None:
        data = load_region_i_data()
        translated = {edge.direction for edge in data.edges}
        self.assertTrue(translated)
        self.assertEqual(translated, set(JSON_TO_RUNTIME_DIRECTION.values()).intersection(translated))


if __name__ == "__main__":
    unittest.main()

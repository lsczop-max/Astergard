from __future__ import annotations

import unittest

from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


D351B_RANGES = {
    "Podgrodzie": range(60, 80),
    "Haldun": range(80, 95),
    "Osada_Mysliwych": range(95, 110),
    "Forteca_Dungrim": range(110, 125),
    "Trakty": range(135, 180),
    "Boczne_Drogi": range(180, 210),
}


class D351BOuterRegionWorldRewriteTests(unittest.TestCase):
    def test_d351b_authors_outer_settlements_and_roads(self) -> None:
        pack = make_content_pack()
        authored = {content.room_id: content for content in pack}
        for zone, room_range in D351B_RANGES.items():
            for room_id in room_range:
                self.assertIn(room_id, authored, f"missing authored content for {zone} room {room_id}")
                self.assertIsNotNone(authored[room_id].name)
                self.assertIsNotNone(authored[room_id].description)
                self.assertGreaterEqual(len(authored[room_id].inspectables), 3)

    def test_d351b_replaces_placeholder_text(self) -> None:
        world = WorldManager()
        world.generate_world()
        forbidden = ("czeka na ręczne opracowanie", "placeholder", "procedural")
        for zone, room_range in D351B_RANGES.items():
            for room_id in room_range:
                loc = world.locations[room_id]
                self.assertEqual(loc.zone, zone)
                text = f"{loc.name}\n{loc.description}".lower()
                for marker in forbidden:
                    self.assertNotIn(marker, text)

    def test_d351b_graph_is_connected_and_not_full_grid(self) -> None:
        world = WorldManager()
        world.generate_world()
        for room_range in D351B_RANGES.values():
            exits_per_room = [len(world.locations[room_id].exits) for room_id in room_range]
            self.assertGreaterEqual(min(exits_per_room), 1)
            self.assertLess(sum(exits_per_room) / len(exits_per_room), 4.5)
        self.assertEqual(world.locations[56].exits["poludnie"].target_room, 60)
        self.assertEqual(world.locations[70].exits["poludnie"].target_room, 135)
        self.assertEqual(world.locations[84].exits["poludniowy-wschod"].target_room, 140)
        self.assertEqual(world.locations[109].exits["wschod"].target_room, 210)
        self.assertEqual(world.locations[124].exits["poludnie"].target_room, 180)

    def test_all_exits_stay_symmetric_after_d351b(self) -> None:
        world = WorldManager()
        world.generate_world()
        for loc in world.locations.values():
            for direction, exit_ in loc.exits.items():
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                self.assertIn(opposite, target.exits, f"{loc.id} {direction} -> {target.id}")
                self.assertEqual(target.exits[opposite].target_room, loc.id)


if __name__ == "__main__":
    unittest.main()

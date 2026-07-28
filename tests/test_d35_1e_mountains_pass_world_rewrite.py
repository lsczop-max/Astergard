from __future__ import annotations

import unittest

from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


PASS_RANGE = range(125, 135)
MOUNTAIN_RANGE = range(335, 390)
D351E_RANGE = tuple(PASS_RANGE) + tuple(MOUNTAIN_RANGE)


class D351EMountainsPassWorldRewriteTests(unittest.TestCase):
    def test_d351e_authors_all_pass_and_mountain_rooms(self) -> None:
        authored = {content.room_id: content for content in make_content_pack()}
        for room_id in D351E_RANGE:
            self.assertIn(room_id, authored)
            content = authored[room_id]
            self.assertIsNotNone(content.name)
            self.assertIsNotNone(content.description)
            self.assertGreaterEqual(len(content.inspectables), 3)
        names = [authored[room_id].name for room_id in D351E_RANGE]
        self.assertEqual(len(set(names)), 65)

    def test_d351e_replaces_pass_and_mountain_placeholder_text(self) -> None:
        world = WorldManager()
        world.generate_world()
        forbidden = ("czeka na ręczne opracowanie", "placeholder", "procedural")
        for room_id in D351E_RANGE:
            loc = world.locations[room_id]
            if room_id in PASS_RANGE:
                self.assertEqual(loc.zone, "polnocny-las")
            else:
                self.assertEqual(loc.zone, "Gory_Mekhara")
            text = f"{loc.name}\n{loc.description}".lower()
            for marker in forbidden:
                self.assertNotIn(marker, text)

    def test_d351e_graph_is_sparse_connected_and_has_expected_chokepoints(self) -> None:
        world = WorldManager()
        world.generate_world()
        exits_per_room = [len(world.locations[room_id].exits) for room_id in D351E_RANGE]
        self.assertGreaterEqual(min(exits_per_room), 1)
        self.assertLess(sum(exits_per_room) / len(exits_per_room), 4.0)
        self.assertEqual(world.locations[125].exits["wschod"].target_room, 132)
        self.assertEqual(world.locations[129].exits["wschod"].target_room, 136)
        self.assertEqual(world.locations[134].exits["wschod"].target_room, 141)
        self.assertEqual(world.locations[334].exits["polnocny-wschod"].target_room, 335)
        self.assertEqual(world.locations[389].exits["poludniowy-wschod"].target_room, 390)

    def test_all_exits_stay_symmetric_after_d351e(self) -> None:
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

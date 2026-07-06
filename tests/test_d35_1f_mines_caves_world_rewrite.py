from __future__ import annotations

import unittest

from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


MINE_RANGE = range(390, 425)
CAVE_RANGE = range(455, 475)
D351F_RANGE = tuple(MINE_RANGE) + tuple(CAVE_RANGE)


class D351FMinesCavesWorldRewriteTests(unittest.TestCase):
    def test_d351f_authors_all_mine_and_cave_rooms(self) -> None:
        authored = {content.room_id: content for content in make_content_pack()}
        for room_id in D351F_RANGE:
            self.assertIn(room_id, authored)
            content = authored[room_id]
            self.assertIsNotNone(content.name)
            self.assertIsNotNone(content.description)
            self.assertGreaterEqual(len(content.inspectables), 3)
        names = [authored[room_id].name for room_id in D351F_RANGE]
        self.assertEqual(len(set(names)), 55)

    def test_d351f_replaces_placeholder_text(self) -> None:
        world = WorldManager()
        world.generate_world()
        forbidden = ("czeka na ręczne opracowanie", "placeholder", "procedural")
        for room_id in D351F_RANGE:
            loc = world.locations[room_id]
            self.assertIn(loc.zone, {"Kopalnia_Zelaza", "Jaskinie_Wilkow"})
            text = f"{loc.name}\n{loc.description}".lower()
            for marker in forbidden:
                self.assertNotIn(marker, text)

    def test_d351f_graph_has_vertical_mine_and_organic_caves(self) -> None:
        world = WorldManager()
        world.generate_world()
        mine_exits = [len(world.locations[room_id].exits) for room_id in MINE_RANGE]
        cave_exits = [len(world.locations[room_id].exits) for room_id in CAVE_RANGE]
        self.assertGreaterEqual(min(mine_exits), 2)
        self.assertGreaterEqual(min(cave_exits), 1)
        self.assertLess(sum(mine_exits) / len(mine_exits), 4.5)
        self.assertLess(sum(cave_exits) / len(cave_exits), 4.0)
        self.assertEqual(world.locations[389].exits["poludniowy-wschod"].target_room, 390)
        self.assertEqual(world.locations[394].exits["dol"].target_room, 395)
        self.assertEqual(world.locations[404].exits["dol"].target_room, 405)
        self.assertEqual(world.locations[416].exits["dol"].target_room, 417)
        self.assertEqual(world.locations[424].exits["zachod"].target_room, 455)

    def test_all_exits_stay_symmetric_after_d351f(self) -> None:
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

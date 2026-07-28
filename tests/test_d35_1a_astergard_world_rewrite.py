from __future__ import annotations

import unittest

from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


class D351AAstergardWorldRewriteTests(unittest.TestCase):
    def test_astergard_has_exactly_sixty_authored_city_rooms(self) -> None:
        pack = make_content_pack()
        city_ids = {content.room_id for content in pack if 0 <= content.room_id <= 59}
        self.assertEqual(len(city_ids), 60)
        self.assertEqual(min(city_ids), 0)
        self.assertEqual(max(city_ids), 59)

    def test_no_magic_tower_remains_in_authored_city_content(self) -> None:
        names = "\n".join(content.name or "" for content in make_content_pack()).lower()
        descriptions = "\n".join(content.description or "" for content in make_content_pack()).lower()
        self.assertNotIn("wieża magów", names)
        self.assertNotIn("wieza magow", names)
        self.assertNotIn("wieża magów", descriptions)
        self.assertNotIn("wieza magow", descriptions)

    def test_astergard_graph_is_organic_not_full_grid(self) -> None:
        world = WorldManager()
        world.generate_world()
        city_ids = [room_id for room_id, loc in world.locations.items() if loc.zone == "centrum"]
        city = [world.locations[i] for i in city_ids]
        self.assertEqual(len(city), 45)
        exits_per_room = [len(loc.exits) for loc in city]
        self.assertLess(sum(exits_per_room) / len(exits_per_room), 4.0)
        self.assertTrue(any("polnocny-wschod" in loc.exits or "poludniowy-wschod" in loc.exits for loc in city))
        self.assertEqual(world.locations[0].exits["wschod"].target_room, 20)
        self.assertEqual(world.locations[1].exits["polnoc"].target_room, 21)
        self.assertEqual(world.locations[14].exits["wschod"].target_room, 1)

    def test_all_generated_exits_are_symmetric_in_full_wind_rose(self) -> None:
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

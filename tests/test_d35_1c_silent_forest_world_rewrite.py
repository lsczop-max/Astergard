from __future__ import annotations

import unittest

from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


PUSZCZA_RANGE = range(210, 280)


class D351CSilentForestWorldRewriteTests(unittest.TestCase):
    def test_d351c_authors_all_silent_forest_rooms(self) -> None:
        authored = {content.room_id: content for content in make_content_pack()}
        for room_id in PUSZCZA_RANGE:
            self.assertIn(room_id, authored)
            content = authored[room_id]
            self.assertIsNotNone(content.name)
            self.assertIsNotNone(content.description)
            self.assertGreaterEqual(len(content.inspectables), 3)
        names = [authored[room_id].name for room_id in PUSZCZA_RANGE]
        self.assertEqual(len(set(names)), 70)

    def test_d351c_replaces_forest_placeholder_text(self) -> None:
        world = WorldManager()
        world.generate_world()
        forbidden = ("czeka na ręczne opracowanie", "placeholder", "procedural")
        for room_id in PUSZCZA_RANGE:
            loc = world.locations[room_id]
            self.assertEqual(loc.zone, "Puszcza_Ciszy")
            text = f"{loc.name}\n{loc.description}".lower()
            for marker in forbidden:
                self.assertNotIn(marker, text)

    def test_d351c_forest_graph_is_connected_organic_and_has_transitions(self) -> None:
        world = WorldManager()
        world.generate_world()
        exits_per_room = [len(world.locations[room_id].exits) for room_id in PUSZCZA_RANGE]
        self.assertGreaterEqual(min(exits_per_room), 1)
        self.assertLess(sum(exits_per_room) / len(exits_per_room), 4.0)
        self.assertTrue(any("poludniowy-wschod" in world.locations[room_id].exits for room_id in PUSZCZA_RANGE))
        self.assertEqual(world.locations[109].exits["wschod"].target_room, 210)
        self.assertEqual(world.locations[179].exits["polnocny-zachod"].target_room, 210)
        self.assertEqual(world.locations[279].exits["polnocny-wschod"].target_room, 280)

    def test_all_exits_stay_symmetric_after_d351c(self) -> None:
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

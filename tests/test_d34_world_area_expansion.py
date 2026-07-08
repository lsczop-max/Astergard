from __future__ import annotations

import asyncio
import unittest

from astergard.testing import TestGameHarness
from astergard.npcs.manager import NPCManager
from astergard.world.content import make_content_pack
from astergard.world.manager import WorldManager


class D34WorldAreaExpansionTests(unittest.TestCase):
    def test_first_district_has_at_least_sixty_authored_rooms(self) -> None:
        pack = make_content_pack()
        self.assertGreaterEqual(len(pack), 60)
        room_ids = {content.room_id for content in pack}
        self.assertIn(0, room_ids)
        self.assertIn(59, room_ids)

    def test_authored_rooms_keep_world_graph_size_and_have_inspectables(self) -> None:
        world = WorldManager()
        world.generate_world()
        self.assertEqual(len(world.locations), 500)
        authored = [loc for loc in world.locations.values() if loc.inspectables]
        self.assertGreaterEqual(len(authored), 90)
        self.assertEqual(world.locations[15].name, "Tyły Karczmy")
        self.assertIn("ludzie przechodnie mieszkancy mieszkańcy", world.locations[15].inspectables)
        self.assertTrue(world.locations[15].description.startswith("Tyły Karczmy należy"))

    def test_player_can_travel_into_expanded_area_and_inspect_generic_detail(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("d34_travel")
                char.room_id = 3
                transcript = await harness.execute(char, "spojrz")
                self.assertIn("Boczne Uliczki Placu", transcript.output)
                self.assertNotIn("Możesz obejrzeć", transcript.output)
                detail = await harness.execute(char, "obejrzyj okiennice")
                self.assertIn("uchylają się", detail.output)

        asyncio.run(run())

    def test_key_city_landmarks_have_descriptions_and_links(self) -> None:
        world = WorldManager()
        world.generate_world()
        for room_id, expected in {
            21: "Studnia Miejska",
            22: "Jatki Rzeźników",
            23: "Targ Rybny",
            25: "Dziedziniec Straży",
            35: "Ogród Ziół Kapłanów",
            41: "Pomosty",
            48: "Warsztat Cieśli",
            59: "Kapliczka Przydrożna",
        }.items():
            loc = world.locations[room_id]
            self.assertEqual(loc.name, expected)
            self.assertGreaterEqual(len(loc.description.split(".")), 2)
        self.assertEqual(world.locations[25].exits["wschod"].target_room, 26)
        self.assertEqual(world.locations[26].exits["zachod"].target_room, 25)
        self.assertEqual(world.locations[41].exits["polnoc"].target_room, 42)
        self.assertEqual(world.locations[42].exits["poludnie"].target_room, 41)

    def test_hidden_items_exist_in_expanded_content(self) -> None:
        world = WorldManager()
        world.generate_world()
        hidden = [element for loc in world.locations.values() for element in loc.hidden_elements]
        self.assertGreaterEqual(len(hidden), 5)

    def test_starting_population_respects_room_caps_with_new_npcs(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()
        self.assertGreaterEqual(len(npcs.npcs), 10)
        self.assertTrue(any(npc.vnum == "watch_sergeant" for npc in npcs.npcs.values()))
        self.assertTrue(any(npc.vnum == "carpenter" for npc in npcs.npcs.values()))
        self.assertLessEqual(max(len(loc.npc_ids) for loc in world.locations.values()), NPCManager.MAX_NPCS_PER_ROOM)


if __name__ == "__main__":
    unittest.main()

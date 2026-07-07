from __future__ import annotations

import unittest
from collections import Counter, deque

from astergard.npcs.manager import NPCManager
from astergard.quests.manager import QUESTS
from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


AUDITED_EMPTY_ZONES = {
    "Boczne_Drogi",
    "Knieja_Cichych_Sciezek",
    "Gory_Mekhara",
    "Ruiny_Karshold",
    "Jaskinie_Wilkow",
}


class D351RWorldAuditTests(unittest.TestCase):
    def test_world_graph_content_and_population_are_consistent(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        self.assertEqual(len(world.locations), 500)
        self.assertTrue(all(loc.description.strip() for loc in world.locations.values()))

        content = make_content_pack()
        room_ids = [entry.room_id for entry in content]
        self.assertEqual(len(room_ids), len(set(room_ids)))

        seen = {0}
        queue: deque[int] = deque([0])
        wrong_exits: list[tuple[int, str, int]] = []
        one_way: list[tuple[int, str, int]] = []

        while queue:
            room_id = queue.popleft()
            loc = world.locations[room_id]
            for direction, exit_ in loc.exits.items():
                self.assertIn(exit_.target_room, world.locations, (room_id, direction))
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                if opposite not in target.exits or target.exits[opposite].target_room != room_id:
                    one_way.append((room_id, direction, exit_.target_room))
                if exit_.target_room not in seen:
                    seen.add(exit_.target_room)
                    queue.append(exit_.target_room)
        self.assertEqual(len(seen), len(world.locations))
        self.assertFalse(wrong_exits)
        self.assertFalse(one_way)

        zone_counts = Counter(loc.zone for loc in world.locations.values() if loc.npc_ids)
        for zone in AUDITED_EMPTY_ZONES:
            self.assertGreater(zone_counts[zone], 0, zone)

        self.assertTrue(all(npc.dialogue_tree for npc in npcs.npcs.values()))
        self.assertFalse([npc for npc in npcs.npcs.values() if npc.is_merchant and not npc.shop_inventory])
        self.assertFalse([npc for npc in npcs.npcs.values() if npc.is_merchant and npc.merchant_gold <= 0])

        quest_npcs = {npc.vnum for npc in npcs.npcs.values()}
        for quest in QUESTS.values():
            self.assertIn(quest.start_npc, quest_npcs, quest.id)
            self.assertIn(quest.completion_npc, quest_npcs, quest.id)


if __name__ == "__main__":
    unittest.main()

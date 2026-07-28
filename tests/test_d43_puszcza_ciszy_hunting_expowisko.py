from __future__ import annotations

import unittest
from unittest.mock import patch
from typing import cast

from astergard.application.services.animal_loot_service import AnimalLootService
from astergard.application.services.quest_service import QuestApplicationService
from astergard.application.use_case_contexts import QuestContext
from astergard.characters.models import Character
from astergard.engine.events import EventBus
from astergard.factions.reputation import FactionManager
from astergard.npcs.manager import NPCManager
from astergard.npcs.models import NPCFactory
from astergard.quests.manager import QuestManager
from astergard.world.manager import WorldManager


class PuszczaCiszyHuntingExpowiskoTests(unittest.TestCase):
    def test_beginner_road_rooms_spawn_new_animals(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        self.assertEqual({npc.vnum for npc in npcs.by_room(183)}, {"puszcza_szczur"})
        self.assertEqual({npc.zone for npc in npcs.by_room(183)}, {"nadrzeczne-mokradla"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(185)}, {"puszcza_mysliwy"})
        self.assertEqual({npc.zone for npc in npcs.by_room(185)}, {"nadrzeczne-mokradla"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(190)}, {"puszcza_zielarz"})
        self.assertEqual({npc.zone for npc in npcs.by_room(190)}, {"Boczne_Drogi"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(196)}, {"puszcza_kruk"})
        self.assertEqual({npc.zone for npc in npcs.by_room(196)}, {"Boczne_Drogi"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(200)}, {"puszcza_pies_dziki"})
        self.assertEqual({npc.zone for npc in npcs.by_room(200)}, {"Boczne_Drogi"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(201)}, {"puszcza_lis"})
        self.assertEqual({npc.zone for npc in npcs.by_room(201)}, {"Boczne_Drogi"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(203)}, {"puszcza_wilk_mlody"})
        self.assertEqual({npc.zone for npc in npcs.by_room(203)}, {"Boczne_Drogi"})
        self.assertEqual({npc.vnum for npc in npcs.by_room(206)}, {"puszcza_wilk"})
        self.assertEqual({npc.zone for npc in npcs.by_room(206)}, {"Boczne_Drogi"})

    def test_new_forest_animals_have_ai_schedule_and_respawn(self) -> None:
        factory = NPCFactory()
        expectations = {
            "puszcza_szczur": "PATROL",
            "puszcza_kruk": "PATROL",
            "puszcza_lis": "PATROL",
            "puszcza_pies_dziki": "AGGRESSIVE",
            "puszcza_wilk_mlody": "PATROL",
            "puszcza_wilk": "AGGRESSIVE",
        }

        for vnum, ai_state in expectations.items():
            npc = factory.create(vnum, 185)
            self.assertEqual(npc.ai_state, ai_state)
            self.assertGreater(npc.respawn_delay_seconds, 0)
            self.assertTrue(npc.daily_schedule)

    def test_new_forest_loot_tables_are_sellable_and_itemized(self) -> None:
        factory = NPCFactory()
        loot_service = AnimalLootService()
        vnums = [
            "puszcza_szczur",
            "puszcza_kruk",
            "puszcza_lis",
            "puszcza_pies_dziki",
            "puszcza_wilk_mlody",
            "puszcza_wilk",
        ]

        with patch("astergard.application.services.animal_loot_service.random.random", return_value=0.0):
            for vnum in vnums:
                loot = loot_service.build_loot(factory.create(vnum, 230))
                self.assertTrue(loot, msg=vnum)
                self.assertTrue(all(item.weight > 0 for item in loot), msg=vnum)
                self.assertTrue(all(item.value > 0 for item in loot), msg=vnum)
                self.assertTrue(all(item.can_be_sold_to_merchants for item in loot), msg=vnum)

    def test_beginner_hunting_quest_can_be_taken_and_completed(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()
        quests = QuestManager()
        factions = FactionManager()
        service = QuestApplicationService(quests, factions)
        character = Character("hunter")
        character.room_id = 185
        ctx = QuestContext(character=character, event_bus=EventBus(), npcs=npcs, quests=quests)

        accepted = service.talk(ctx, "myśliwy szczury")
        self.assertIn("Otrzymujesz nowe zadanie", accepted)
        self.assertIn("Szczury przy obozie", accepted)
        self.assertIn("puszcza_szczury", character.active_quests)

        quests.progress(character, "kill", "puszcza_szczur", 3)
        completed = service.talk(ctx, "myśliwy szczury")
        self.assertIn("Kończysz zadanie", completed)
        self.assertIn("puszcza_szczury", character.completed_quests)
        self.assertNotIn("puszcza_szczury", character.active_quests)

    def test_remove_dead_queues_respawn_for_new_forest_mobs(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("puszcza_wilk", 206, "Boczne_Drogi")
        self.assertIsNotNone(npc)
        assert npc is not None
        self.assertEqual(npc.zone, "Boczne_Drogi")

        npcs.remove_dead(npc)

        self.assertTrue(world.respawn_queue)
        queued = world.respawn_queue[-1]
        self.assertEqual(queued["vnum"], "puszcza_wilk")
        self.assertEqual(queued["room_id"], 206)
        self.assertGreater(int(cast(int | float | str, queued["delay"])), 0)

    def test_existing_biome_wolf_remains_available(self) -> None:
        wolf = NPCFactory().create("wolf", 455)
        self.assertEqual(wolf.vnum, "wolf")
        self.assertEqual(wolf.room_id, 455)
        self.assertEqual(wolf.zone, "Zachod_Las")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from collections import Counter
import unittest

from astergard.application.services.quest_service import QuestApplicationService
from astergard.application.use_case_contexts import QuestContext
from astergard.characters.models import Character
from astergard.engine.events import EventBus
from astergard.factions.reputation import FactionManager
from astergard.npcs.manager import NPCManager
from astergard.quests.manager import QuestManager
from astergard.items.models import Item
from astergard.world.manager import WorldManager


class PuszczaCiszyExpansionTests(unittest.TestCase):
    def test_forest_population_matches_expected_distribution(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        expected_rooms: dict[int, set[str]] = {
            216: {"puszcza_mysliwy", "puszcza_szczur", "puszcza_pajak"},
            223: {"puszcza_zielarz", "puszcza_kruk", "puszcza_lis"},
            229: {"puszcza_wilk_mlody", "puszcza_pajak_lesny"},
            234: {"puszcza_wilk", "puszcza_wilk_stary", "puszcza_wataha_wilkow"},
            241: {"puszcza_jelen", "puszcza_niedzwiedz", "puszcza_niedzwiedzica"},
            246: {"puszcza_drwal", "puszcza_bandyta"},
            252: {"puszcza_pustelnik", "puszcza_bandyta_zwiadowca", "puszcza_lowca"},
            258: {"puszcza_lowczy", "puszcza_pajak_duzy"},
            267: {"puszcza_dzik", "puszcza_bandycki_naczelnik", "puszcza_niedzwiedzi_olbrzym"},
            274: {"puszcza_troll"},
        }
        expected_combat_vnums = {
            "puszcza_szczur",
            "puszcza_pajak",
            "puszcza_kruk",
            "puszcza_lis",
            "puszcza_wilk_mlody",
            "puszcza_pajak_lesny",
            "puszcza_wilk",
            "puszcza_wilk_stary",
            "puszcza_wataha_wilkow",
            "puszcza_niedzwiedz",
            "puszcza_niedzwiedzica",
            "puszcza_bandyta",
            "puszcza_bandyta_zwiadowca",
            "puszcza_lowca",
            "puszcza_lowczy",
            "puszcza_pajak_duzy",
            "puszcza_bandycki_naczelnik",
            "puszcza_niedzwiedzi_olbrzym",
            "puszcza_troll",
        }
        tier_counts: Counter[str] = Counter()
        for room_id, expected_vnums in expected_rooms.items():
            room_npcs = npcs.by_room(room_id)
            self.assertLessEqual(len(room_npcs), NPCManager.MAX_NPCS_PER_ROOM)
            self.assertEqual({npc.vnum for npc in room_npcs}, expected_vnums)
            self.assertTrue(all(npc.zone == "Puszcza_Ciszy" for npc in room_npcs))
            tier_counts.update(npc.threat_tier for npc in room_npcs if npc.vnum in expected_combat_vnums)

        self.assertEqual(sum(tier_counts.values()), 19)
        self.assertEqual(tier_counts["trash"], 5)
        self.assertEqual(tier_counts["standard"], 11)
        self.assertEqual(tier_counts["elite"], 2)
        self.assertEqual(tier_counts["boss"], 1)

    def test_hidden_chests_exist_in_forest_content(self) -> None:
        world = WorldManager()
        world.generate_world()

        for room_id in (218, 234, 248, 259, 273):
            location = world.get_location(room_id)
            self.assertIsNotNone(location)
            assert location is not None
            hidden_items = [hidden for hidden in location.hidden_elements if hidden["type"] == "item"]
            self.assertTrue(hidden_items, msg=f"room {room_id}")
            chest = hidden_items[0]["data"]
            assert isinstance(chest, Item)
            self.assertTrue(chest.is_container)
            self.assertGreaterEqual(chest.capacity, 6.0)
            self.assertTrue(chest.contains)
            self.assertTrue(chest.vnum and chest.vnum.startswith("forest_hidden_chest_"))

    def test_new_forest_quests_can_be_accepted_and_completed(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()
        quests = QuestManager()
        factions = FactionManager()
        service = QuestApplicationService(quests, factions)
        character = Character("hunter")
        character.room_id = 216
        ctx = QuestContext(character=character, event_bus=EventBus(), npcs=npcs, quests=quests)

        accepted_bandits = service.talk(ctx, "myśliwy bandyci")
        self.assertIn("Leśni bandyci", accepted_bandits)
        self.assertIn("puszcza_bandyci", character.active_quests)
        quests.progress(character, "kill", "puszcza_bandyta", 3)
        completed_bandits = service.talk(ctx, "myśliwy bandyci")
        self.assertIn("Kończysz zadanie", completed_bandits)
        self.assertIn("puszcza_bandyci", character.completed_quests)

        accepted_spiders = service.talk(ctx, "myśliwy pajaki")
        self.assertIn("Pajęcze zasadzki", accepted_spiders)
        self.assertIn("puszcza_pajaki", character.active_quests)
        quests.progress(character, "kill", "puszcza_pajak", 2)
        completed_spiders = service.talk(ctx, "myśliwy pajaki")
        self.assertIn("Kończysz zadanie", completed_spiders)
        self.assertIn("puszcza_pajaki", character.completed_quests)

        accepted_bears = service.talk(ctx, "myśliwy niedzwiedzie")
        self.assertIn("Ślad niedźwiedzi", accepted_bears)
        self.assertIn("puszcza_niedzwiedzie", character.active_quests)
        quests.progress(character, "kill", "puszcza_niedzwiedz", 1)
        completed_bears = service.talk(ctx, "myśliwy niedzwiedzie")
        self.assertIn("Kończysz zadanie", completed_bears)
        self.assertIn("puszcza_niedzwiedzie", character.completed_quests)


if __name__ == "__main__":
    unittest.main()

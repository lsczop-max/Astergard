from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.content import make_content_pack
from astergard.world.manager import OPPOSITE, WorldManager


WILD_ROOM_IDS = range(210, 280)
SWAMP_ROOM_IDS = range(475, 500)


class D351ODzikaStrefaProductionTests(unittest.TestCase):
    def test_populate_spawns_wild_npcs_with_dialogues_equipment_and_schedules(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        expected = {
            ("puszcza_mysliwy", 216, "Puszcza_Ciszy"),
            ("puszcza_zielarz", 223, "Puszcza_Ciszy"),
            ("puszcza_jelen", 241, "Puszcza_Ciszy"),
            ("puszcza_drwal", 246, "Puszcza_Ciszy"),
            ("puszcza_pustelnik", 252, "Puszcza_Ciszy"),
            ("puszcza_dzik", 267, "Puszcza_Ciszy"),
            ("bagna_zielarz", 478, "Bagna_Hookri"),
            ("bagna_zaba", 481, "Bagna_Hookri"),
            ("bagna_mysliwy", 488, "Bagna_Hookri"),
            ("bagna_pustelnik", 493, "Bagna_Hookri"),
        }

        for vnum, room_id, zone in expected:
            npc = next(candidate for candidate in npcs.by_room(room_id) if candidate.vnum == vnum)
            self.assertEqual(npc.zone, zone, vnum)
            self.assertEqual(npc.faction, "REBELS", vnum)
            self.assertTrue({"default", "praca", "miejsce", "plotki"}.issubset(npc.dialogue_tree.keys()), vnum)
            self.assertTrue({"świt", "dzień", "wieczór", "noc"}.issubset(npc.daily_schedule.keys()), vnum)
            self.assertTrue(npc.character.equipment, vnum)
            self.assertTrue(npc.threat_tier, vnum)
            self.assertTrue(npc.character.combat_style, vnum)

        self.assertLessEqual(max(len(world.locations[room_id].npc_ids) for room_id in (*WILD_ROOM_IDS, *SWAMP_ROOM_IDS)), NPCManager.MAX_NPCS_PER_ROOM)

    def test_wild_schedule_phases_and_route_moves_stay_local(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        hermit = next(npc for npc in npcs.by_room(493) if npc.vnum == "bagna_pustelnik")
        npcs.ai_tick(hour=6)
        self.assertEqual(hermit.daily_phase, "świt")
        self.assertIn("ślad", hermit.daily_activity.lower())
        npcs.ai_tick(hour=19)
        self.assertEqual(hermit.daily_phase, "wieczór")
        self.assertIn("kaplic", hermit.daily_activity.lower())

    def test_search_finds_exploration_items_and_quests_complete_through_real_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("wild_explorer", room_id=223)
                char.gold = 120

                start_herbs = await harness.execute(char, "rozmawiaj zielarz zioła")
                self.assertIn("Leśne zioła", start_herbs.output)
                self.assertIn("puszcza_herbs", char.active_quests)

                char.room_id = 230
                with patch("random.randint", return_value=10):
                    found_herbs = await harness.execute(char, "szukaj")
                self.assertIn("Odkrywasz: garść leśnych ziół", found_herbs.output)
                await asyncio.sleep(0.6)
                pickup_herbs = await harness.execute(char, "weź garść leśnych ziół")
                self.assertIn("Podnosisz garść leśnych ziół", pickup_herbs.output)
                await asyncio.sleep(0.6)
                char.room_id = 223
                herbs_done = await harness.execute(char, "daj garść leśnych ziół zielarz")
                self.assertIn("Kończysz zadanie: Leśne zioła", herbs_done.output)
                self.assertIn("puszcza_herbs", char.completed_quests)

                char.room_id = 252
                await asyncio.sleep(0.6)
                camp_start = await harness.execute(char, "rozmawiaj pustelnik obóz")
                self.assertIn("Ślad obozu", camp_start.output)
                self.assertIn("puszcza_camp_token", char.active_quests)

                char.room_id = 274
                await asyncio.sleep(0.6)
                with patch("random.randint", return_value=10):
                    camp_found = await harness.execute(char, "szukaj")
                self.assertIn("Odkrywasz: znacznik obozu", camp_found.output)
                await asyncio.sleep(0.6)
                camp_pickup = await harness.execute(char, "weź znacznik obozu")
                self.assertIn("Podnosisz znacznik obozu", camp_pickup.output)
                await asyncio.sleep(0.6)
                char.room_id = 252
                camp_done = await harness.execute(char, "daj znacznik obozu pustelnik")
                self.assertIn("Kończysz zadanie: Ślad obozu", camp_done.output)
                self.assertIn("puszcza_camp_token", char.completed_quests)

                char.room_id = 478
                await asyncio.sleep(0.6)
                swamp_start = await harness.execute(char, "rozmawiaj zielarka torf")
                self.assertIn("Torfowe zioła", swamp_start.output)
                self.assertIn("bagna_herbs", char.active_quests)

                char.room_id = 475
                await asyncio.sleep(0.6)
                with patch("random.randint", return_value=10):
                    swamp_found = await harness.execute(char, "szukaj")
                self.assertIn("Odkrywasz: zestaw torfowych ziół", swamp_found.output)
                await asyncio.sleep(0.6)
                swamp_pickup = await harness.execute(char, "weź zestaw torfowych ziół")
                self.assertIn("Podnosisz zestaw torfowych ziół", swamp_pickup.output)
                await asyncio.sleep(0.6)
                char.room_id = 478
                swamp_done = await harness.execute(char, "daj zestaw torfowych ziół zielarka")
                self.assertIn("Kończysz zadanie: Torfowe zioła", swamp_done.output)
                self.assertIn("bagna_herbs", char.completed_quests)

                char.room_id = 493
                await asyncio.sleep(0.6)
                stone_start = await harness.execute(char, "rozmawiaj pustelnik kamień")
                self.assertIn("Kamień z ołtarza", stone_start.output)
                self.assertIn("bagna_stone", char.active_quests)

                char.room_id = 499
                await asyncio.sleep(0.6)
                with patch("random.randint", return_value=10):
                    stone_found = await harness.execute(char, "szukaj")
                self.assertIn("Odkrywasz: czarny kamyk bagienny", stone_found.output)
                await asyncio.sleep(0.6)
                stone_pickup = await harness.execute(char, "weź czarny kamyk bagienny")
                self.assertIn("Podnosisz czarny kamyk bagienny", stone_pickup.output)
                await asyncio.sleep(0.6)
                char.room_id = 493
                stone_done = await harness.execute(char, "daj czarny kamyk bagienny pustelnik")
                self.assertIn("Kończysz zadanie: Kamień z ołtarza", stone_done.output)
                self.assertIn("bagna_stone", char.completed_quests)

                char.room_id = 493
                await asyncio.sleep(0.6)
                tracks_start = await harness.execute(char, "rozmawiaj pustelnik tropy")
                self.assertIn("Bagienne tropy", tracks_start.output)
                self.assertIn("bagna_tracks", char.active_quests)

                char.room_id = 488
                await asyncio.sleep(0.6)
                tracks_progress = await harness.execute(char, "rozmawiaj myśliwy")
                self.assertIn("Cel osiągnięty", tracks_progress.output)

                char.room_id = 493
                await asyncio.sleep(0.6)
                tracks_done = await harness.execute(char, "rozmawiaj pustelnik")
                self.assertIn("Kończysz zadanie: Bagienne tropy", tracks_done.output)
                self.assertIn("bagna_tracks", char.completed_quests)

        asyncio.run(run())

    def test_shops_offer_wild_goods(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("wild_shop", room_id=223)
                forest_offer = await harness.execute(char, "oferta")
                self.assertIn("wiązka leśnych ziół", forest_offer.output)
                self.assertIn("suszone grzyby", forest_offer.output)

                char.room_id = 478
                await asyncio.sleep(0.6)
                swamp_offer = await harness.execute(char, "oferta")
                self.assertIn("torfowe ziele", swamp_offer.output)
                self.assertIn("maść przeciw wilgoci", swamp_offer.output)

                char.room_id = 488
                await asyncio.sleep(0.6)
                hunter_offer = await harness.execute(char, "oferta")
                self.assertIn("kołczan strzał", hunter_offer.output)
                self.assertIn("sidła leśne", hunter_offer.output)

        asyncio.run(run())

    def test_region_content_and_graph_remain_consistent(self) -> None:
        world = WorldManager()
        world.generate_world()
        authored = {content.room_id: content for content in make_content_pack()}

        for room_id in (*WILD_ROOM_IDS, *SWAMP_ROOM_IDS):
            content = authored[room_id]
            self.assertIsNotNone(content.name)
            self.assertIsNotNone(content.description)
            self.assertGreaterEqual(len(content.inspectables), 3)
            self.assertNotIn("czeka na ręczne opracowanie", f"{content.name}\n{content.description}".lower())
            loc = world.locations[room_id]
            for direction, exit_ in loc.exits.items():
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                self.assertIn(opposite, target.exits, f"{room_id} {direction} -> {target.id}")
                self.assertEqual(target.exits[opposite].target_room, room_id)


if __name__ == "__main__":
    unittest.main()

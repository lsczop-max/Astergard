from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import OPPOSITE, WorldManager


HALDUN_ROOM_IDS = range(80, 95)
HALDUN_NPCS: dict[str, int] = {
    "haldun_farmer": 82,
    "haldun_wellkeeper": 83,
    "haldun_farmerka": 84,
    "haldun_solt": 85,
    "haldun_miller": 87,
    "haldun_blacksmith": 88,
    "haldun_merchant": 89,
    "haldun_pasterz": 92,
    "haldun_wartownik": 94,
}


class D351KHaldunProductionTests(unittest.TestCase):
    def test_populate_places_haldun_npcs_with_schedules_and_equipment(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        expected_zones = {
            80: "centrum",
            81: "centrum",
            82: "trakt-nadrzeczny",
            83: "trakt-nadrzeczny",
            84: "trakt-nadrzeczny",
            85: "trakt-nadrzeczny",
            86: "trakt-nadrzeczny",
            87: "polnocny-las",
            88: "polnocny-las",
            89: "polnocny-las",
            90: "polnocny-las",
            91: "polnocny-las",
            92: "polnocny-las",
            93: "polnocny-las",
            94: "polnocny-las",
        }
        for vnum, room_id in HALDUN_NPCS.items():
            npc = next(candidate for candidate in npcs.by_room(room_id) if candidate.vnum == vnum)
            self.assertEqual(npc.zone, expected_zones[room_id], vnum)
            self.assertTrue({"default", "praca", "miejsce", "plotki"}.issubset(npc.dialogue_tree.keys()), vnum)
            self.assertIn("świt", npc.daily_schedule, vnum)
            self.assertIn("noc", npc.daily_schedule, vnum)
            self.assertTrue(npc.character.equipment, vnum)
            self.assertTrue(npc.threat_tier, vnum)
            self.assertTrue(npc.character.combat_style, vnum)

        self.assertLessEqual(max(len(world.locations[room_id].npc_ids) for room_id in HALDUN_ROOM_IDS), NPCManager.MAX_NPCS_PER_ROOM)

    def test_haldun_region_has_specific_descriptions_items_and_symmetric_exits(self) -> None:
        world = WorldManager()
        world.generate_world()

        expected_names = {
            80: "Piwnica pod Żurawiem",
            81: "Izby Gościnne pod Żurawiem",
            82: "Wysoki Brzeg",
            83: "Zakole Rzeki",
            84: "Mokre Łąki",
            85: "Pierwsze Sieci",
            86: "Skraj Osady Rybackiej",
            87: "Wejście między Leszczyny",
            88: "Ścieżka Młodych Brzóz",
            89: "Piaszczysty Przesmyk",
            90: "Polana Zajęczych Traw",
            91: "Gęstwina Niskich Sosen",
            92: "Jar Suchego Potoku",
            93: "Kępa Krzywych Brzóz",
            94: "Skraj Jasnego Lasu",
        }
        expected_zones = {
            80: "centrum",
            81: "centrum",
            82: "trakt-nadrzeczny",
            83: "trakt-nadrzeczny",
            84: "trakt-nadrzeczny",
            85: "trakt-nadrzeczny",
            86: "trakt-nadrzeczny",
            87: "polnocny-las",
            88: "polnocny-las",
            89: "polnocny-las",
            90: "polnocny-las",
            91: "polnocny-las",
            92: "polnocny-las",
            93: "polnocny-las",
            94: "polnocny-las",
        }
        for room_id in HALDUN_ROOM_IDS:
            loc = world.locations[room_id]
            self.assertEqual(loc.zone, expected_zones[room_id])
            self.assertEqual(loc.name, expected_names[room_id])
            self.assertGreaterEqual(len(loc.description.split(".")), 2)
            self.assertGreaterEqual(len(loc.inspectables), 3)

        for room_id in HALDUN_ROOM_IDS:
            for direction, exit_ in world.locations[room_id].exits.items():
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                self.assertIn(opposite, target.exits, f"{room_id} {direction} -> {target.id}")
                self.assertEqual(target.exits[opposite].target_room, room_id)

    def test_haldun_dialogues_quests_and_shops_work_through_real_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("haldun_production", room_id=85)
                char.gold = 80

                start = await harness.execute(char, "rozmawiaj sołtys zadanie")
                self.assertIn("Wiadro do studni", start.output)
                self.assertIn("haldun_well_bucket", char.active_quests)

                char.room_id = 83
                pickup = await harness.execute(char, "weź wiadro studzienne")
                self.assertIn("Podnosisz wiadro studzienne", pickup.output)
                complete = await harness.execute(char, "daj wiadro studzienne studniarz")
                self.assertIn("Kończysz zadanie: Wiadro do studni", complete.output)
                self.assertIn("haldun_well_bucket", char.completed_quests)

                await asyncio.sleep(0.6)
                char.room_id = 85
                watch_start = await harness.execute(char, "rozmawiaj sołtys obchód")
                self.assertIn("Obchód drogi", watch_start.output)
                self.assertIn("haldun_watch_round", char.active_quests)

                await asyncio.sleep(0.6)
                char.room_id = 94
                watch_progress = await harness.execute(char, "rozmawiaj wartownik")
                self.assertIn("Cel osiągnięty", watch_progress.output)
                self.assertEqual(char.active_quests["haldun_watch_round"]["current"], 1)

                await asyncio.sleep(0.6)
                char.room_id = 85
                watch_complete = await harness.execute(char, "rozmawiaj sołtys")
                self.assertIn("Kończysz zadanie: Obchód drogi", watch_complete.output)
                self.assertIn("haldun_watch_round", char.completed_quests)

                char.room_id = 83
                offer = await harness.execute(char, "oferta")
                self.assertIn("gliniany dzban", offer.output)
                gold_before = char.gold
                buy = await harness.execute(char, "kup gliniany dzban")
                self.assertIn("Kupujesz gliniany dzban", buy.output)
                self.assertLess(char.gold, gold_before)

        asyncio.run(run())

    def test_haldun_daily_routines_keep_npcs_in_region(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("haldun_farmer", 82)
        self.assertIsNotNone(npc)
        assert npc is not None

        npcs.ai_tick(hour=6)
        self.assertEqual(npc.daily_phase, "świt")
        self.assertEqual(npc.daily_activity, "Przygotowuje narzędzia i zaczyna dzień pracy.")
        morning_room = npc.room_id

        npcs.ai_tick(hour=19)
        self.assertEqual(npc.daily_phase, "wieczór")
        self.assertEqual(npc.daily_activity, "Zamyka robotę i wraca do domu.")
        self.assertEqual(world.locations[npc.room_id].zone, "trakt-nadrzeczny")
        self.assertTrue(world.locations[npc.room_id].zone == world.locations[morning_room].zone)


if __name__ == "__main__":
    unittest.main()

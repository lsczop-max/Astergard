from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import OPPOSITE, WorldManager


FORTRESS_ROOM_IDS = range(110, 125)
FORTRESS_NPCS: tuple[tuple[str, int], ...] = (
    ("dungrim_guard", 110),
    ("dungrim_patrol_guard", 112),
    ("dungrim_stablemaster", 114),
    ("dungrim_cook", 115),
    ("dungrim_sergeant", 116),
    ("dungrim_military_blacksmith", 117),
    ("dungrim_lieutenant", 118),
    ("dungrim_patrol_guard", 119),
    ("dungrim_commander", 120),
    ("dungrim_armorer", 121),
    ("dungrim_quartermaster", 122),
    ("dungrim_storekeeper", 123),
    ("dungrim_guard", 124),
)


class FixedRng:
    def random(self) -> float:
        return 0.0

    def choice(self, seq: list[tuple[str, int]]) -> tuple[str, int]:
        return seq[0]


class D351LFortecaDungrimProductionTests(unittest.TestCase):
    def test_populate_places_dungrim_npcs_with_schedules_dialogues_and_equipment(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        for room_id in FORTRESS_ROOM_IDS:
            loc = world.locations[room_id]
            self.assertEqual(loc.zone, "Forteca_Dungrim")
            self.assertGreaterEqual(len(loc.description.split(".")), 1)
            self.assertGreaterEqual(len(loc.inspectables), 3)

        for vnum, room_id in FORTRESS_NPCS:
            candidates = [npc for npc in npcs.by_room(room_id) if npc.vnum == vnum]
            self.assertTrue(candidates, vnum)
            npc = candidates[0]
            self.assertEqual(npc.zone, "Forteca_Dungrim", vnum)
            self.assertEqual(npc.faction, "MEEKHAN", vnum)
            self.assertTrue({"default", "praca", "miejsce", "plotki"}.issubset(npc.dialogue_tree), vnum)
            self.assertTrue({"świt", "dzień", "wieczór", "noc"}.issubset(npc.daily_schedule), vnum)
            self.assertTrue(npc.character.equipment, vnum)
            self.assertTrue(npc.character.combat_style, vnum)
            self.assertTrue(npc.threat_tier, vnum)

        self.assertLessEqual(max(len(world.locations[room_id].npc_ids) for room_id in FORTRESS_ROOM_IDS), NPCManager.MAX_NPCS_PER_ROOM)

    def test_dungrim_patrols_use_existing_schedule_and_patrol_state(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        patrol = next(npc for npc in npcs.by_room(112) if npc.vnum == "dungrim_patrol_guard")
        patrol.ai_state = "PATROL"
        start_room = patrol.room_id

        events = npcs.ai_tick(rng=FixedRng(), hour=12)

        self.assertNotEqual(patrol.room_id, start_room)
        self.assertTrue(any(event.kind in {"move", "patrol"} and event.npc_id == patrol.id for event in events))
        self.assertEqual(world.locations[patrol.room_id].zone, "Forteca_Dungrim")

    def test_dungrim_dialogues_and_quests_work_through_real_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("dungrim_quests", room_id=116)
                char.gold = 120

                patrol_start = await harness.execute(char, "rozmawiaj sierżant raport")
                self.assertIn("Raport z obchodu", patrol_start.output)
                self.assertIn("dungrim_patrol_report", char.active_quests)

                char.room_id = 112
                await asyncio.sleep(0.6)
                patrol_progress = await harness.execute(char, "rozmawiaj patrolowy")
                self.assertIn("Cel osiągnięty", patrol_progress.output)
                self.assertEqual(char.active_quests["dungrim_patrol_report"]["current"], 1)

                char.room_id = 116
                await asyncio.sleep(0.6)
                patrol_finish = await harness.execute(char, "rozmawiaj sierżant")
                self.assertIn("Kończysz zadanie: Raport z obchodu", patrol_finish.output)
                self.assertIn("dungrim_patrol_report", char.completed_quests)

                await asyncio.sleep(0.6)
                char.room_id = 120
                armory_start = await harness.execute(char, "rozmawiaj dowódca nity")
                self.assertIn("Nity do zbrojowni", armory_start.output)
                self.assertIn("dungrim_armory_rivets", char.active_quests)

                char.room_id = 121
                pickup = await harness.execute(char, "weź pęk nitów")
                self.assertIn("Podnosisz pęk nitów", pickup.output)
                armory_finish = await harness.execute(char, "daj pęk nitów zbrojmistrz")
                self.assertIn("Kończysz zadanie: Nity do zbrojowni", armory_finish.output)
                self.assertIn("dungrim_armory_rivets", char.completed_quests)

        asyncio.run(run())

    def test_dungrim_shops_offer_military_goods(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("dungrim_shops", room_id=122)
                char.gold = 100

                quartermaster_offer = await harness.execute(char, "oferta")
                self.assertIn("racja żołnierska", quartermaster_offer.output)
                self.assertIn("oliwa do lamp", quartermaster_offer.output)

                char.room_id = 121
                armory_offer = await harness.execute(char, "oferta")
                self.assertIn("hełm garnizonowy", armory_offer.output)
                self.assertIn("miecz wartowniczy", armory_offer.output)

                char.room_id = 115
                kitchen_offer = await harness.execute(char, "oferta")
                self.assertIn("gulasz garnizonowy", kitchen_offer.output)

        asyncio.run(run())

    def test_dungrim_region_has_symmetric_exits_and_working_schedule(self) -> None:
        world = WorldManager()
        world.generate_world()

        for room_id in FORTRESS_ROOM_IDS:
            loc = world.locations[room_id]
            self.assertEqual(loc.zone, "Forteca_Dungrim")
            self.assertGreaterEqual(len(loc.inspectables), 3)
            for direction, exit_ in loc.exits.items():
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                self.assertIn(opposite, target.exits, f"{room_id} {direction} -> {target.id}")
                self.assertEqual(target.exits[opposite].target_room, room_id)

        npcs = NPCManager(world)
        npcs.populate()
        commander = next(npc for npc in npcs.by_room(120) if npc.vnum == "dungrim_commander")
        npcs.ai_tick(hour=6)
        self.assertEqual(commander.daily_phase, "świt")
        self.assertIn("Zmienia wartę", commander.daily_activity)
        npcs.ai_tick(hour=19)
        self.assertEqual(commander.daily_phase, "wieczór")
        self.assertIn("Obchodzi posterunek", commander.daily_activity)


if __name__ == "__main__":
    unittest.main()

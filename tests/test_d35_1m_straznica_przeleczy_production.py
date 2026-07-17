from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import OPPOSITE, WorldManager


PASS_ROOM_IDS = range(125, 135)
PASS_NPCS: tuple[tuple[str, int], ...] = (
    ("straznica_dowodca", 125),
    ("straznica_wartownik", 126),
    ("straznica_zwiadowca", 127),
    ("straznica_przewodnik", 128),
    ("straznica_karawanowy", 129),
    ("straznica_woznica", 130),
    ("straznica_podrozny", 131),
    ("straznica_pielgrzym", 132),
    ("straznica_mysliwy", 133),
    ("straznica_wartownik", 134),
)


class FixedRng:
    def random(self) -> float:
        return 0.0

    def choice(self, seq: list[tuple[str, int]]) -> tuple[str, int]:
        return seq[0]


class D351MStraznicaPrzeleczyProductionTests(unittest.TestCase):
    def test_populate_places_pass_npcs_with_equipment_dialogues_and_schedules(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        for room_id in PASS_ROOM_IDS:
            loc = world.locations[room_id]
            self.assertEqual(loc.zone, "Straznica_Przeleczy")
            self.assertGreaterEqual(len(loc.description.split(".")), 2)
            self.assertGreaterEqual(len(loc.inspectables), 3)

        for vnum, room_id in PASS_NPCS:
            npc = next(candidate for candidate in npcs.by_room(room_id) if candidate.vnum == vnum)
            self.assertEqual(npc.zone, "Straznica_Przeleczy", vnum)
            self.assertEqual(npc.faction, "MEEKHAN", vnum)
            self.assertTrue({"default", "praca", "miejsce", "plotki"}.issubset(npc.dialogue_tree.keys()), vnum)
            self.assertTrue({"świt", "dzień", "wieczór", "noc"}.issubset(npc.daily_schedule.keys()), vnum)
            self.assertTrue(npc.character.equipment, vnum)
            self.assertTrue(npc.threat_tier, vnum)
            self.assertTrue(npc.character.combat_style, vnum)

        self.assertLessEqual(max(len(world.locations[room_id].npc_ids) for room_id in PASS_ROOM_IDS), NPCManager.MAX_NPCS_PER_ROOM)

    def test_patrols_move_existing_patrol_npc_inside_pass_zone(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        scout = next(npc for npc in npcs.by_room(127) if npc.vnum == "straznica_zwiadowca")
        scout.ai_state = "PATROL"
        start_room = scout.room_id

        events = npcs.ai_tick(rng=FixedRng(), hour=12)

        self.assertNotEqual(scout.room_id, start_room)
        self.assertTrue(any(event.kind in {"move", "patrol"} and event.npc_id == scout.id for event in events))
        self.assertEqual(world.locations[scout.room_id].zone, "Straznica_Przeleczy")

    def test_dialogues_quests_and_shops_work_through_real_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("pass_production", room_id=125)
                char.gold = 120

                start = await harness.execute(char, "rozmawiaj komendant zadanie")
                self.assertIn("Meldunek z wieży", start.output)
                self.assertIn("straznica_meldunek", char.active_quests)

                char.room_id = 127
                await asyncio.sleep(0.6)
                progress = await harness.execute(char, "rozmawiaj zwiadowca")
                self.assertIn("Cel osiągnięty", progress.output)
                self.assertEqual(char.active_quests["straznica_meldunek"]["current"], 1)

                char.room_id = 125
                await asyncio.sleep(0.6)
                finish = await harness.execute(char, "rozmawiaj komendant")
                self.assertIn("Kończysz zadanie: Meldunek z wieży", finish.output)
                self.assertIn("straznica_meldunek", char.completed_quests)

                char.room_id = 128
                await asyncio.sleep(0.6)
                lamp_start = await harness.execute(char, "rozmawiaj przewodnik olej")
                self.assertIn("Olej do lamp", lamp_start.output)
                self.assertIn("straznica_lamp_oil", char.active_quests)

                await asyncio.sleep(0.6)
                pickup = await harness.execute(char, "weź olej do lamp")
                self.assertIn("Podnosisz olej do lamp", pickup.output)
                await asyncio.sleep(0.6)
                lamp_finish = await harness.execute(char, "daj olej do lamp przewodnik")
                self.assertIn("Kończysz zadanie: Olej do lamp", lamp_finish.output)
                self.assertIn("straznica_lamp_oil", char.completed_quests)

                char.room_id = 129
                await asyncio.sleep(0.6)
                manifest_start = await harness.execute(char, "rozmawiaj kupiec karawan manifest")
                self.assertIn("Manifest karawany", manifest_start.output)
                self.assertIn("straznica_manifest", char.active_quests)

                await asyncio.sleep(0.6)
                manifest_pickup = await harness.execute(char, "weź list przewozowy")
                self.assertIn("Podnosisz list przewozowy", manifest_pickup.output)
                await asyncio.sleep(0.6)
                manifest_finish = await harness.execute(char, "daj list przewozowy dla kupca karawan")
                self.assertIn("Kończysz zadanie: Manifest karawany", manifest_finish.output)
                self.assertIn("straznica_manifest", char.completed_quests)

        asyncio.run(run())

    def test_shops_offer_local_pass_goods(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("pass_shops", room_id=128)
                guide_offer = await harness.execute(char, "oferta")
                self.assertIn("olej do lamp", guide_offer.output)
                self.assertIn("zwój mapy", guide_offer.output)

                char.room_id = 129
                await asyncio.sleep(0.6)
                caravan_offer = await harness.execute(char, "oferta")
                self.assertIn("list przewozowy", caravan_offer.output)
                self.assertIn("smar do osi", caravan_offer.output)

                char.room_id = 133
                await asyncio.sleep(0.6)
                hunter_offer = await harness.execute(char, "oferta")
                self.assertIn("futro z kozicy", hunter_offer.output)
                self.assertIn("zestaw linek", hunter_offer.output)

        asyncio.run(run())

    def test_schedule_and_region_consistency_stay_symmetric(self) -> None:
        world = WorldManager()
        world.generate_world()

        for room_id in PASS_ROOM_IDS:
            loc = world.locations[room_id]
            self.assertEqual(loc.zone, "Straznica_Przeleczy")
            self.assertGreaterEqual(len(loc.inspectables), 3)
            self.assertNotIn("czeka na ręczne opracowanie", f"{loc.name}\n{loc.description}".lower())
            for direction, exit_ in loc.exits.items():
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                self.assertIn(opposite, target.exits, f"{room_id} {direction} -> {target.id}")
                self.assertEqual(target.exits[opposite].target_room, room_id)

        npcs = NPCManager(world)
        npcs.populate()
        commander = next(npc for npc in npcs.by_room(125) if npc.vnum == "straznica_dowodca")
        npcs.ai_tick(hour=6)
        self.assertEqual(commander.daily_phase, "świt")
        self.assertIn("meldunki", commander.daily_activity.lower())
        npcs.ai_tick(hour=19)
        self.assertEqual(commander.daily_phase, "wieczór")
        self.assertIn("raporty", commander.daily_activity.lower())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import OPPOSITE, WorldManager
from astergard.world.region_i_content import load_region_i_cards


TRACT_ROOM_IDS = range(135, 180)
TRACT_SPAWNS: tuple[tuple[str, int], ...] = (
    ("trakty_przewodnik", 135),
    ("trakty_pielgrzym", 136),
    ("trakty_karawaniarz", 138),
    ("trakty_kurier", 140),
    ("trakty_woznica", 141),
    ("trakty_podrozny", 145),
    ("trakty_zebrak", 156),
    ("trakty_mysliwy", 165),
    ("trakty_drwal", 166),
    ("trakty_straznik", 172),
    ("trakty_handlarz", 176),
)


class FixedRng:
    def random(self) -> float:
        return 0.0

    def choice(self, seq):
        return seq[0]


CARD_BY_ID = {card.id: card for card in load_region_i_cards()}


class D351NTraktyProductionTests(unittest.TestCase):
    def test_populate_spawns_road_npcs_with_equipment_dialogues_and_schedules(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()
        for room_id in TRACT_ROOM_IDS:
            loc = world.locations[room_id]
            card = CARD_BY_ID[room_id]
            self.assertEqual(loc.zone, card.region_id)
            self.assertEqual(loc.name, card.name)
            self.assertIsNotNone(loc.name)
            self.assertIsNotNone(loc.description)
            self.assertGreaterEqual(len(loc.inspectables), 3)

        for vnum, room_id in TRACT_SPAWNS:
            npc = next(candidate for candidate in npcs.by_room(room_id) if candidate.vnum == vnum)
            self.assertEqual(npc.zone, CARD_BY_ID[room_id].region_id, vnum)
            self.assertEqual(npc.faction, "MEEKHAN", vnum)
            self.assertTrue({"default", "praca", "miejsce", "plotki"}.issubset(npc.dialogue_tree.keys()), vnum)
            self.assertTrue({"świt", "dzień", "wieczór", "noc"}.issubset(npc.daily_schedule.keys()), vnum)
            self.assertTrue(npc.character.equipment, vnum)
            self.assertTrue(npc.threat_tier, vnum)
            self.assertTrue(npc.character.combat_style, vnum)

        self.assertLessEqual(max(len(world.locations[room_id].npc_ids) for room_id in TRACT_ROOM_IDS), NPCManager.MAX_NPCS_PER_ROOM)

    def test_patrols_and_schedules_keep_guard_on_route(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        guard = next(npc for npc in npcs.by_room(172) if npc.vnum == "trakty_straznik")
        guard.ai_state = "PATROL"
        start_room = guard.room_id

        events = npcs.ai_tick(rng=FixedRng(), hour=12)

        self.assertNotEqual(guard.room_id, start_room)
        self.assertTrue(any(event.kind in {"move", "patrol"} and event.npc_id == guard.id for event in events))
        self.assertEqual(world.locations[guard.room_id].zone, world.locations[start_room].zone)

    def test_dialogues_quests_and_deliveries_work_through_real_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                def current_strażnik_room() -> int:
                    return next(npc.room_id for npc in server.services.npcs.npcs.values() if npc.vnum == "trakty_straznik")
                char = harness.create_character("tract_production", room_id=140)
                char.gold = 150

                start = await harness.execute(char, "rozmawiaj kurier zadanie")
                self.assertIn("List kuriera", start.output)
                self.assertIn("trakty_kurier_note", char.active_quests)

                await asyncio.sleep(0.6)
                pickup_note = await harness.execute(char, "weź zapieczętowany list")
                self.assertIn("Podnosisz zapieczętowany list", pickup_note.output)

                char.room_id = 135
                await asyncio.sleep(0.6)
                finish_note = await harness.execute(char, "daj zapieczętowany list dla przewodnik")
                self.assertIn("Kończysz zadanie: List kuriera", finish_note.output)
                self.assertIn("trakty_kurier_note", char.completed_quests)

                char.room_id = 138
                await asyncio.sleep(0.6)
                manifest_start = await harness.execute(char, "rozmawiaj karawaniarz manifest")
                self.assertIn("Manifest karawany", manifest_start.output)
                self.assertIn("trakty_manifest", char.active_quests)

                await asyncio.sleep(0.6)
                pickup_manifest = await harness.execute(char, "weź list przewozowy")
                self.assertIn("Podnosisz list przewozowy", pickup_manifest.output)
                await asyncio.sleep(0.6)
                finish_manifest = await harness.execute(char, "daj list przewozowy dla karawaniarz")
                self.assertIn("Kończysz zadanie: Manifest karawany", finish_manifest.output)
                self.assertIn("trakty_manifest", char.completed_quests)

                char.room_id = current_strażnik_room()
                await asyncio.sleep(0.6)
                hunter_start = await harness.execute(char, "rozmawiaj strażnik zadanie")
                self.assertIn("Ślad myśliwego", hunter_start.output)
                self.assertIn("trakty_hunter_report", char.active_quests)

                char.room_id = 165
                await asyncio.sleep(0.6)
                hunter_progress = await harness.execute(char, "rozmawiaj myśliwy")
                self.assertIn("Cel osiągnięty", hunter_progress.output)

                char.room_id = current_strażnik_room()
                await asyncio.sleep(0.6)
                hunter_finish = await harness.execute(char, "rozmawiaj strażnik")
                self.assertIn("Kończysz zadanie: Ślad myśliwego", hunter_finish.output)
                self.assertIn("trakty_hunter_report", char.completed_quests)

        asyncio.run(run())

    def test_shops_offer_route_goods(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("tract_shop", room_id=135)
                guide_offer = await harness.execute(char, "oferta")
                self.assertIn("olej do lamp", guide_offer.output)
                self.assertIn("zwój mapy", guide_offer.output)

                char.room_id = 138
                await asyncio.sleep(0.6)
                caravan_offer = await harness.execute(char, "oferta")
                self.assertIn("list przewozowy", caravan_offer.output)
                self.assertIn("klin pod koło", caravan_offer.output)

                char.room_id = 165
                await asyncio.sleep(0.6)
                hunter_offer = await harness.execute(char, "oferta")
                self.assertIn("futro z kozicy", hunter_offer.output)
                self.assertIn("zestaw linek", hunter_offer.output)

                char.room_id = 166
                await asyncio.sleep(0.6)
                lumber_offer = await harness.execute(char, "oferta")
                self.assertIn("topór rozłupujący", lumber_offer.output)
                self.assertIn("klin do drewna", lumber_offer.output)

        asyncio.run(run())

    def test_region_content_and_symmetry_stay_coherent(self) -> None:
        world = WorldManager()
        world.generate_world()
        for room_id in TRACT_ROOM_IDS:
            loc = world.locations[room_id]
            card = CARD_BY_ID[room_id]
            self.assertEqual(loc.zone, card.region_id)
            self.assertIsNotNone(loc.name)
            self.assertIsNotNone(loc.description)
            self.assertGreaterEqual(len(loc.inspectables), 3)
            self.assertNotIn("czeka na ręczne opracowanie", f"{loc.name}\n{loc.description}".lower())
            for direction, exit_ in loc.exits.items():
                opposite = OPPOSITE[direction]
                target = world.locations[exit_.target_room]
                self.assertIn(opposite, target.exits, f"{room_id} {direction} -> {target.id}")
                self.assertEqual(target.exits[opposite].target_room, room_id)


if __name__ == "__main__":
    unittest.main()

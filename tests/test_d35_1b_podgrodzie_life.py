from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.manager import NPCManager
from astergard.npcs.combat_profiles import combat_style_for_vnum
from astergard.npcs.threat import threat_for_vnum
from astergard.testing import TestGameHarness
from astergard.world.manager import WorldManager


PODGRODZIE_SPAWNS: dict[str, int] = {
    "podgrodzie_woznica": 60,
    "podgrodzie_karczmarz": 62,
    "podgrodzie_karczmarka": 62,
    "podgrodzie_pielgrzym": 62,
    "podgrodzie_piekarz": 63,
    "podgrodzie_handlarz": 63,
    "podgrodzie_przekupka": 76,
    "podgrodzie_kowal": 66,
    "podgrodzie_pomocnik_kowala": 66,
    "podgrodzie_straznik_miejski": 66,
    "podgrodzie_rybak": 69,
    "podgrodzie_dziecko": 72,
    "podgrodzie_zebrak": 75,
    "podgrodzie_chlop": 77,
    "podgrodzie_chlopka": 78,
}


class D351BPodgrodzieLifeTests(unittest.TestCase):
    def test_podgrodzie_is_not_empty(self) -> None:
        world = WorldManager()
        world.generate_world()
        podgrodzie = [world.locations[room_id] for room_id in range(60, 80)]
        self.assertGreater(sum(len(loc.items) for loc in podgrodzie), 0)
        self.assertGreater(sum(len(loc.inspectables) for loc in podgrodzie), 0)

    def test_new_npc_vnums_have_threat_and_combat_profiles(self) -> None:
        for vnum, expected_tier, expected_style in [
            ("podgrodzie_woznica", "trash", "zrownowazony"),
            ("podgrodzie_karczmarz", "trash", "ostrozny"),
            ("podgrodzie_kowal", "standard", "defensywny"),
            ("podgrodzie_straznik_miejski", "standard", "defensywny"),
            ("podgrodzie_chlopka", "trash", "zrownowazony"),
        ]:
            self.assertEqual(threat_for_vnum(vnum).tier, expected_tier)
            self.assertEqual(combat_style_for_vnum(vnum), expected_style)

    def test_spawn_places_new_npcs_in_expected_rooms(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        for vnum, room_id in PODGRODZIE_SPAWNS.items():
            npc = npcs.spawn(vnum, room_id)
            self.assertIsNotNone(npc, vnum)
            assert npc is not None
            self.assertEqual(npc.room_id, room_id)
            self.assertEqual(world.locations[room_id].zone, "Podgrodzie")
            self.assertIn(npc.id, world.locations[room_id].npc_ids)

    def test_populate_places_new_podgrodzie_civilians(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        spawned_vnums = {npc.vnum for npc in npcs.npcs.values() if npc.vnum in PODGRODZIE_SPAWNS}
        self.assertEqual(spawned_vnums, set(PODGRODZIE_SPAWNS))
        for vnum, room_id in PODGRODZIE_SPAWNS.items():
            self.assertTrue(any(npc.vnum == vnum for npc in npcs.by_room(room_id)), vnum)
        self.assertLessEqual(max(len(world.locations[room_id].npc_ids) for room_id in range(60, 80)), NPCManager.MAX_NPCS_PER_ROOM)

    def test_npc_schedule_updates_look_output(self) -> None:
        with TestGameHarness() as harness:
            char = harness.create_character("d35_living_world", room_id=66)
            server = harness.require_server()
            moving = next(npc for npc in server.services.npcs.by_room(66) if npc.vnum == "podgrodzie_kowal")

            server.services.npcs.ai_tick(hour=2)
            self.assertEqual(moving.daily_phase, "noc")
            self.assertEqual(moving.daily_activity, "Wraca do domu z zapachem dymu i metalu.")

            reply = asyncio.run(harness.execute(char, "spojrz"))
            self.assertIn("Kowal wraca do domu z zapachem dymu i metalu.", reply.output)
            self.assertIn("Kowal", reply.output)

    def test_npc_moves_within_zone_using_existing_exit(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("podgrodzie_kowal", 66)
        self.assertIsNotNone(npc)
        assert npc is not None
        start_room = npc.room_id
        start_exits = {exit_.target_room for exit_ in world.locations[start_room].exits.values()}
        npcs.ai_tick(hour=12)
        self.assertNotEqual(npc.room_id, start_room)
        self.assertIn(npc.room_id, start_exits)
        self.assertEqual(world.locations[npc.room_id].zone, "Podgrodzie")

    def test_npc_schedule_does_not_remove_npc_from_world(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("podgrodzie_rybak", 69)
        self.assertIsNotNone(npc)
        assert npc is not None
        before = len(npcs.npcs)
        npcs.ai_tick(hour=6)
        npcs.ai_tick(hour=12)
        npcs.ai_tick(hour=19)
        self.assertEqual(len(npcs.npcs), before)
        self.assertIn(npc.id, npcs.npcs)
        self.assertEqual(world.locations[npc.room_id].zone, "Podgrodzie")


if __name__ == "__main__":
    unittest.main()

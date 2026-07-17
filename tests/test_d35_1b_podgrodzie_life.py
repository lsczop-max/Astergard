from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.combat_profiles import combat_style_for_vnum
from astergard.npcs.manager import NPCManager
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

LIVING_WORLD_SCHEDULED_VNUMS: tuple[str, ...] = (
    "astergard_guard",
    "watch_sergeant",
    "innkeeper",
    "merchant",
    "customs_clerk",
    "dockhand",
    "fishmonger",
    "fisherman",
    "beggar",
    "traveler",
    "child",
    "urchin",
    "priest_aide",
    "carpenter",
    "tanner",
    "armorer",
    "woodcutter",
    "podgrodzie_woznica",
    "podgrodzie_karczmarz",
    "podgrodzie_karczmarka",
    "podgrodzie_pielgrzym",
    "podgrodzie_piekarz",
    "podgrodzie_handlarz",
    "podgrodzie_przekupka",
    "podgrodzie_kowal",
    "podgrodzie_pomocnik_kowala",
    "podgrodzie_straznik_miejski",
    "podgrodzie_rybak",
    "podgrodzie_dziecko",
    "podgrodzie_zebrak",
    "podgrodzie_chlop",
    "podgrodzie_chlopka",
)


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

    def test_scheduler_assigns_many_daily_schedules(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        scheduled = [npc for npc in npcs.npcs.values() if npc.daily_schedule]
        self.assertGreaterEqual(len(scheduled), 30)
        self.assertTrue(all(npc.daily_schedule for npc in scheduled))

    def test_npc_schedule_updates_look_output(self) -> None:
        with TestGameHarness() as harness:
            char = harness.create_character("d35_living_world", room_id=66)
            server = harness.require_server()
            moving = next(npc for npc in server.services.npcs.by_room(66) if npc.vnum == "podgrodzie_kowal")

            server.services.npcs.ai_tick(hour=2)
            self.assertEqual(moving.daily_phase, "noc")
            self.assertEqual(moving.daily_activity, "Liczy zamówienia i siedzi przy osmolonym stole.")

            reply = asyncio.run(harness.execute(char, "spojrz"))
            self.assertIn("Kowal liczy zamówienia i siedzi przy osmolonym stole.", reply.output)
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

    def test_npc_returns_home_and_stays_in_zone(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("podgrodzie_rybak", 69)
        self.assertIsNotNone(npc)
        assert npc is not None
        home_room = npc.home_room_id
        npcs.ai_tick(hour=12)
        self.assertEqual(world.locations[npc.room_id].zone, "Podgrodzie")
        npcs.ai_tick(hour=2)
        self.assertEqual(npc.room_id, home_room)
        self.assertEqual(world.locations[npc.room_id].zone, "Podgrodzie")

    def test_scheduler_does_not_leave_map(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        tracked = [
            npcs.spawn("astergard_guard", 0),
            npcs.spawn("podgrodzie_woznica", 60),
            npcs.spawn("podgrodzie_karczmarz", 62),
        ]
        self.assertTrue(all(npc is not None for npc in tracked))

        for hour in [6, 12, 19, 2]:
            npcs.ai_tick(hour=hour)
            for npc in tracked:
                assert npc is not None
                self.assertIn(npc.room_id, world.locations)
                self.assertEqual(world.locations[npc.room_id].zone, npc.zone)

    def test_populate_still_builds_living_scheduler_cast(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        present = {npc.vnum for npc in npcs.npcs.values() if npc.vnum in LIVING_WORLD_SCHEDULED_VNUMS and npc.daily_schedule}
        self.assertEqual(present, set(LIVING_WORLD_SCHEDULED_VNUMS))
        self.assertEqual(len(present), len(LIVING_WORLD_SCHEDULED_VNUMS))


if __name__ == "__main__":
    unittest.main()

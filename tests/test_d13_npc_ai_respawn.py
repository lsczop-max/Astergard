from __future__ import annotations

import unittest

from astergard.characters.models import Character
from astergard.combat.manager import CombatManager
from astergard.factions.reputation import FactionManager
from astergard.npcs.manager import NPCManager
from astergard.world.manager import WorldManager


class AlwaysPatrolRandom:
    def random(self) -> float:
        return 0.0

    def choice(self, seq):
        return seq[0]


class D13NPCAITests(unittest.TestCase):
    def test_patrol_moves_only_inside_same_zone_and_emits_event(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("meekhan_soldier", 0)
        self.assertIsNotNone(npc)
        assert npc is not None
        npc.ai_state = "PATROL"
        events = npcs.ai_tick(rng=AlwaysPatrolRandom())
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].kind, "patrol")
        self.assertNotEqual(npc.room_id, 0)
        self.assertEqual(world.locations[npc.room_id].zone, npc.zone)
        self.assertIn(npc.id, world.locations[npc.room_id].npc_ids)
        self.assertNotIn(npc.id, world.locations[0].npc_ids)

    def test_aggressive_npc_initiates_combat_with_player_in_room(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("wolf", 101)
        self.assertIsNotNone(npc)
        assert npc is not None
        player = Character("Tester")
        player.room_id = 101
        combat = CombatManager()
        events = npcs.ai_tick([player], combat=combat)
        self.assertEqual(events[0].kind, "aggression")
        self.assertTrue(player.in_combat)
        self.assertTrue(npc.character.in_combat)
        self.assertIn((npc.id, "Tester"), combat.active_fights)

    def test_guard_attacks_player_hostile_to_meekhan(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        guard = npcs.spawn("meekhan_soldier", 0)
        self.assertIsNotNone(guard)
        player = Character("Bandzior")
        player.room_id = 0
        player.reputation["MEEKHAN"] = -600
        combat = CombatManager()
        factions = FactionManager()
        events = npcs.ai_tick([player], combat=combat, factions=factions)
        self.assertEqual(events[0].kind, "guard_aggression")
        self.assertIn((guard.id, "Bandzior"), combat.active_fights)  # type: ignore[union-attr]

    def test_respawn_waits_for_delay_and_respects_room_population_limit(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npc = npcs.spawn("wolf", 101)
        self.assertIsNotNone(npc)
        assert npc is not None
        npc.respawn_delay_seconds = 10
        npcs.remove_dead(npc)
        self.assertEqual(len(world.respawn_queue), 1)
        early = npcs.respawn_tick(now=float(world.respawn_queue[0]["time"]) + 9)
        self.assertEqual(early, [])
        self.assertEqual(len(world.respawn_queue), 1)
        late = npcs.respawn_tick(now=float(world.respawn_queue[0]["time"]) + 11)
        self.assertEqual(len(late), 1)
        self.assertEqual(late[0].kind, "respawn")
        self.assertEqual(len(world.respawn_queue), 0)

        world.locations[125].npc_ids.clear()
        npcs.npcs.clear()
        for _ in range(NPCManager.MAX_NPCS_PER_ROOM):
            self.assertIsNotNone(npcs.spawn("wolf", 125))
        blocked = npcs.spawn("wolf", 125)
        self.assertIsNone(blocked)
        self.assertEqual(len(world.locations[125].npc_ids), NPCManager.MAX_NPCS_PER_ROOM)


if __name__ == "__main__":
    unittest.main()

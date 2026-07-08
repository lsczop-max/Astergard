from __future__ import annotations

import asyncio
import unittest

from astergard.npcs.manager import NPCManager
from astergard.world.manager import WorldManager
from astergard.testing import TestGameHarness


class PatrolRandom:
    def __init__(self, value: float = 0.2) -> None:
        self.value = value

    def random(self) -> float:
        return self.value

    def choice(self, seq):
        return seq[0]


class D351JWorldReactionTests(unittest.TestCase):
    def test_helping_podgrodzie_raises_reputation(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("reaction_quest", room_id=14)
                start = await harness.execute(char, "rozmawiaj karczmarz zadanie")
                self.assertIn("Dostawa z targu", start.output)
                rep_before = char.reputation.get("MEEKHAN", 0)

                char.room_id = 47
                await asyncio.sleep(0.6)
                await harness.execute(char, "wez kosz targowy")
                char.room_id = 14
                await asyncio.sleep(0.6)
                finish = await harness.execute(char, "daj kosz targowy karczmarz")

                self.assertIn("Kończysz zadanie: Dostawa z targu", finish.output)
                self.assertGreater(char.reputation.get("MEEKHAN", 0), rep_before)
                self.assertIn("market_delivery", char.completed_quests)

        asyncio.run(run())

    def test_bad_weather_slows_patrol_npcs(self) -> None:
        world = WorldManager()
        world.generate_world()

        clear_npcs = NPCManager(world)
        clear_guard = clear_npcs.spawn("dungrim_patrol_guard", 112)
        self.assertIsNotNone(clear_guard)
        assert clear_guard is not None
        clear_events = clear_npcs.ai_tick(rng=PatrolRandom(0.2), weather_by_zone={clear_guard.zone: "slonecznie"})
        self.assertTrue(any(event.kind == "patrol" for event in clear_events))

        bad_world = WorldManager()
        bad_world.generate_world()
        bad_npcs = NPCManager(bad_world)
        bad_guard = bad_npcs.spawn("dungrim_patrol_guard", 112)
        self.assertIsNotNone(bad_guard)
        assert bad_guard is not None
        bad_events = bad_npcs.ai_tick(rng=PatrolRandom(0.2), weather_by_zone={bad_guard.zone: "mgla"})
        self.assertFalse(any(event.kind == "patrol" for event in bad_events))

    def test_bad_reputation_triggers_guard_aggression(self) -> None:
        with TestGameHarness() as harness:
            char = harness.create_character("reaction_guard", room_id=25)
            char.reputation["MEEKHAN"] = -600
            server = harness.require_server()
            events = server.services.npcs.ai_tick(players=[char], combat=server.services.combat, factions=server.services.factions, hour=12)
            self.assertTrue(any(event.kind == "guard_aggression" for event in events))
            self.assertTrue(char.in_combat)

    def test_dialogue_changes_with_reputation(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("reaction_dialogue", room_id=25)
                char.reputation["MEEKHAN"] = -600
                response = await harness.execute(char, "rozmawiaj sierżant o brama")
                self.assertIn("Z taką reputacją", response.output)

        asyncio.run(run())

    def test_completed_quest_unlocks_better_offer(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("reaction_offer", room_id=14)
                before = await harness.execute(char, "oferta")
                self.assertNotIn("gorący posiłek", before.output)

                await asyncio.sleep(0.6)
                await harness.execute(char, "rozmawiaj karczmarz zadanie")
                char.room_id = 47
                await asyncio.sleep(0.6)
                await harness.execute(char, "wez kosz targowy")
                char.room_id = 14
                await asyncio.sleep(0.6)
                await harness.execute(char, "daj kosz targowy karczmarz")

                after = await harness.execute(char, "oferta")
                self.assertIn("gorący posiłek", after.output)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

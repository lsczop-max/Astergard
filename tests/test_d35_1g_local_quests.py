from __future__ import annotations

import asyncio
import unittest

from astergard.testing import TestGameHarness


class D351GLocalQuestTests(unittest.TestCase):
    def test_delivery_quest_starts_completes_and_rewards(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("quest_delivery", room_id=14)
                start = await harness.execute(char, "rozmawiaj karczmarz zadanie")
                self.assertIn("Otrzymujesz nowe zadanie: Dostawa z targu", start.output)
                self.assertIn("market_delivery", char.active_quests)

                char.room_id = 47
                pickup = await harness.execute(char, "weź kosz targowy")
                self.assertIn("Podnosisz kosz targowy", pickup.output)

                char.room_id = 14
                gold_before = char.gold
                rep_before = char.reputation.get("MEEKHAN", 0)
                finish = await harness.execute(char, "daj kosz targowy karczmarz")
                self.assertIn("Kończysz zadanie: Dostawa z targu", finish.output)
                self.assertNotIn("market_delivery", char.active_quests)
                self.assertIn("market_delivery", char.completed_quests)
                self.assertGreater(char.gold, gold_before)
                self.assertGreater(char.reputation.get("MEEKHAN", 0), rep_before)

        asyncio.run(run())

    def test_talk_quest_progresses_and_completes(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("quest_guard", room_id=25)
                start = await harness.execute(char, "rozmawiaj sierżant zadanie")
                self.assertIn("Otrzymujesz nowe zadanie: Podejrzany włóczęga", start.output)
                self.assertIn("guard_vagrant", char.active_quests)

                char.room_id = 56
                await asyncio.sleep(0.6)
                progress = await harness.execute(char, "rozmawiaj włóczęga")
                self.assertIn("Cel osiągnięty", progress.output)
                self.assertEqual(char.active_quests["guard_vagrant"]["current"], 1)

                char.room_id = 25
                await asyncio.sleep(0.6)
                gold_before = char.gold
                rep_before = char.reputation.get("MEEKHAN", 0)
                finish = await harness.execute(char, "rozmawiaj sierżant")
                self.assertIn("Kończysz zadanie: Podejrzany włóczęga", finish.output)
                self.assertNotIn("guard_vagrant", char.active_quests)
                self.assertIn("guard_vagrant", char.completed_quests)
                self.assertGreater(char.gold, gold_before)
                self.assertGreater(char.reputation.get("MEEKHAN", 0), rep_before)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

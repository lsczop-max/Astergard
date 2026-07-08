from __future__ import annotations

import asyncio
import tempfile
import unittest
from typing import cast

from astergard.quests.manager import QUESTS
from astergard.testing import TestGameHarness


NEW_LOCAL_QUEST_IDS: tuple[str, ...] = (
    "city_ring_search",
    "merchant_price_check",
    "dockside_rumor",
    "pilgrim_escort",
    "wheel_repair",
    "shield_repair",
    "wolf_watch",
    "fish_delivery",
    "grain_delivery",
    "wood_delivery",
    "candles_gather",
    "well_water_delivery",
)


class D351QLocalQuestExpansionTests(unittest.TestCase):
    def test_new_local_quests_have_complete_dialogue_metadata(self) -> None:
        self.assertEqual(len(NEW_LOCAL_QUEST_IDS), 12)
        for quest_id in NEW_LOCAL_QUEST_IDS:
            quest = QUESTS[quest_id]
            self.assertTrue(quest.description, quest_id)
            self.assertTrue(quest.offer_text, quest_id)
            self.assertTrue(quest.completion_text, quest_id)
            self.assertTrue(quest.start_npc, quest_id)
            self.assertTrue(quest.completion_npc, quest_id)
            self.assertTrue(quest.objectives, quest_id)
            self.assertGreaterEqual(quest.rewards.get("gold", 0), 8, quest_id)

    def test_new_quests_start_progress_and_complete_through_real_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("quest_flow", room_id=25)
                char.gold = 20

                ring_start = await harness.execute(char, "rozmawiaj sierżant pierścień")
                self.assertIn("Zaginiony pierścień", ring_start.output)
                self.assertIn("city_ring_search", char.active_quests)

                char.room_id = 1
                await asyncio.sleep(0.6)
                search = await harness.execute(char, "szukaj")
                self.assertIn("srebrny pierścień", search.output)
                await asyncio.sleep(0.6)
                pickup_ring = await harness.execute(char, "weź srebrny pierścień")
                self.assertIn("Podnosisz srebrny pierścień", pickup_ring.output)

                char.room_id = 0
                gold_before_ring = char.gold
                await asyncio.sleep(0.6)
                finish_ring = await harness.execute(char, "daj srebrny pierścień kupiec")
                self.assertIn("Kończysz zadanie: Zaginiony pierścień", finish_ring.output)
                self.assertIn("city_ring_search", char.completed_quests)
                self.assertGreater(char.gold, gold_before_ring)

                char.room_id = 66
                await asyncio.sleep(0.6)
                wheel_start = await harness.execute(char, "rozmawiaj kowal naprawa")
                self.assertIn("Naprawa koła", wheel_start.output)
                self.assertIn("wheel_repair", char.active_quests)

                char.room_id = 60
                await asyncio.sleep(0.6)
                pickup_wheel = await harness.execute(char, "weź złamane koło wozu")
                self.assertIn("Podnosisz złamane koło wozu", pickup_wheel.output)
                gold_before_wheel = char.gold
                await asyncio.sleep(0.6)
                finish_wheel = await harness.execute(char, "daj złamane koło wozu woźnica")
                self.assertIn("Kończysz zadanie: Naprawa koła", finish_wheel.output)
                self.assertIn("wheel_repair", char.completed_quests)
                self.assertGreater(char.gold, gold_before_wheel)

                char.room_id = 63
                await asyncio.sleep(0.6)
                grain_start = await harness.execute(char, "rozmawiaj piekarz zboże")
                self.assertIn("Worek zboża", grain_start.output)
                self.assertIn("grain_delivery", char.active_quests)

                await asyncio.sleep(0.6)
                pickup_grain = await harness.execute(char, "weź worek zboża")
                self.assertIn("Podnosisz worek zboża", pickup_grain.output)
                char.room_id = 62
                gold_before_grain = char.gold
                await asyncio.sleep(0.6)
                finish_grain = await harness.execute(char, "daj worek zboża karczmarz")
                self.assertIn("Kończysz zadanie: Worek zboża", finish_grain.output)
                self.assertIn("grain_delivery", char.completed_quests)
                self.assertGreater(char.gold, gold_before_grain)

        asyncio.run(run())

    def test_quest_state_survives_save_and_load(self) -> None:
        async def run() -> None:
            with tempfile.NamedTemporaryFile() as tmp, TestGameHarness(db_path=tmp.name) as harness:
                char = harness.create_character("quest_save", room_id=0)
                server = harness.require_server()

                start = await harness.execute(char, "rozmawiaj kupiec ceny")
                self.assertIn("Targowe ceny", start.output)
                self.assertIn("merchant_price_check", char.active_quests)

                char.room_id = 76
                await asyncio.sleep(0.6)
                progress = await harness.execute(char, "rozmawiaj przekupka")
                self.assertIn("Cel osiągnięty", progress.output)
                server.repo.save(char)

                loaded = server.repo.load("quest_save")
                server.clients[cast(asyncio.StreamWriter, harness.writers["quest_save"])] = loaded
                self.assertIn("merchant_price_check", loaded.active_quests)
                self.assertEqual(loaded.active_quests["merchant_price_check"]["current"], 1)

                loaded.room_id = 0
                gold_before = loaded.gold
                rep_before = loaded.reputation.get("MEEKHAN", 0)
                await asyncio.sleep(0.6)
                finish = await harness.execute(loaded, "rozmawiaj kupiec")
                self.assertIn("Kończysz zadanie: Targowe ceny", finish.output)
                self.assertIn("merchant_price_check", loaded.completed_quests)
                self.assertGreater(loaded.gold, gold_before)
                self.assertGreater(loaded.reputation.get("MEEKHAN", 0), rep_before)

                server.repo.save(loaded)
                reloaded = server.repo.load("quest_save")
                self.assertIn("merchant_price_check", reloaded.completed_quests)
                self.assertNotIn("merchant_price_check", reloaded.active_quests)
                self.assertEqual(reloaded.gold, loaded.gold)

        asyncio.run(run())

    def test_branching_quest_can_use_alternative_targets_and_return_to_turn_in(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("quest_branch", room_id=0)
                server = harness.require_server()

                start = await harness.execute(char, "rozmawiaj kupiec ceny")
                self.assertIn("Targowe ceny", start.output)
                self.assertIn("merchant_price_check", char.active_quests)

                quest_log = server.services.quests.render(char)
                self.assertIn("Cele:", quest_log)
                self.assertIn("jedno z:", quest_log)

                char.room_id = 42
                await asyncio.sleep(0.6)
                progress = await harness.execute(char, "rozmawiaj rybaczka")
                self.assertIn("Cel osiągnięty", progress.output)
                self.assertEqual(char.active_quests["merchant_price_check"]["current"], 1)

                char.room_id = 0
                await asyncio.sleep(0.6)
                finish = await harness.execute(char, "rozmawiaj kupiec")
                self.assertIn("Kończysz zadanie: Targowe ceny", finish.output)
                self.assertIn("merchant_price_check", char.completed_quests)
                self.assertNotIn("merchant_price_check", char.active_quests)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

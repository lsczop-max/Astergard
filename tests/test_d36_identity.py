from __future__ import annotations

import asyncio
import tempfile
import unittest

from astergard.testing import TestGameHarness


class D36IdentityTests(unittest.TestCase):
    def test_quest_completion_updates_reputation_renown_and_title(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("identity_quest", room_id=14)
                char.renown = 49
                start = await harness.execute(char, "rozmawiaj karczmarz zadanie")
                self.assertIn("Dostawa z targu", start.output)
                global_before = char.global_reputation
                renown_before = char.renown

                char.room_id = 47
                await asyncio.sleep(0.6)
                await harness.execute(char, "wez kosz targowy")
                char.room_id = 14
                await asyncio.sleep(0.6)
                finish = await harness.execute(char, "daj kosz targowy karczmarz")

                self.assertIn("Kończysz zadanie: Dostawa z targu", finish.output)
                self.assertGreater(char.global_reputation, global_before)
                self.assertGreater(char.renown, renown_before)
                self.assertEqual(char.title, "Rozpoznawalny")
                self.assertGreater(char.local_reputation.get("Centrum_Twierdza", 0), 0)

        asyncio.run(run())

    def test_bad_reputation_blocks_guard_and_merchant_reactions(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("identity_bad", room_id=25)
                rules = harness.require_server().services.factions.rules
                char.global_reputation = -220
                char.reputation["MEEKHAN"] = -600
                char.wanted_level = 2
                char.sync_identity(title=rules.title_for(char.renown, char.wanted_level), wanted_level=char.wanted_level)

                guard = await harness.execute(char, "rozmawiaj sierżant zadanie")
                self.assertIn("napraw swoje sprawy", guard.output)

                char.room_id = 14
                await asyncio.sleep(0.6)
                merchant_offer = await harness.execute(char, "oferta")
                self.assertIn("Nie handluję z taką reputacją", merchant_offer.output)

                await asyncio.sleep(0.6)
                merchant_dialog = await harness.execute(char, "rozmawiaj karczmarz plotki")
                self.assertIn("Z taką reputacją", merchant_dialog.output)

        asyncio.run(run())

    def test_crime_is_recorded_and_survives_save_load(self) -> None:
        async def run() -> None:
            with tempfile.NamedTemporaryFile() as tmp, TestGameHarness(db_path=tmp.name) as harness:
                char = harness.create_character("identity_crime", room_id=14)
                server = harness.require_server()

                await asyncio.sleep(0.6)
                theft = await harness.execute(char, "weź miska gulaszu")
                self.assertIn("Podnosisz miska gulaszu", theft.output)
                self.assertGreaterEqual(char.crimes.get("kradzież", 0), 1)
                self.assertGreaterEqual(char.wanted_level, 1)
                self.assertTrue(char.wanted_posts)

                char.renown = 151
                char.wanted_level = 2
                char.sync_identity(title=server.services.factions.rules.title_for(char.renown, char.wanted_level), wanted_level=char.wanted_level)
                server.repo.save(char)

                loaded = server.repo.load("identity_crime")
                self.assertGreaterEqual(loaded.crimes.get("kradzież", 0), 1)
                self.assertGreaterEqual(loaded.wanted_level, 1)
                self.assertTrue(loaded.wanted_posts)
                self.assertEqual(loaded.title, "Poszukiwany")
                self.assertEqual(loaded.renown, 151)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

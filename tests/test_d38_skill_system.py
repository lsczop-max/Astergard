from __future__ import annotations

import tempfile
import unittest

from astergard.characters.creation import CharacterCreationProfile
from astergard.characters.models import CharacterSkills
from astergard.database.repository import PlayerRepository


class SkillSystemTests(unittest.TestCase):
    def test_professions_grant_starting_skills(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            profile = CharacterCreationProfile.build(
                name="Mira",
                gender_id="f",
                age="27",
                origin="uczeń rzemieślnika",
                childhood="miasto",
                birth_region="Astergard",
                main_profession="szermierz",
                secondary_profession="bard",
                appearance="Szczupła kobieta z prostym mieczem przy pasie.",
            )
            self.assertTrue(repo.register("mira", "secret", profile))
            char = repo.load("mira")
            self.assertGreaterEqual(char.skills.level("bron_jednoraczna"), 3)
            self.assertGreaterEqual(char.skills.level("obserwacja"), 1)
            self.assertGreaterEqual(char.skills.level("perswazja"), 3)
            self.assertIn("bron_jednoraczna", char.skills.values)
            self.assertIn("muzyka", char.skills.values)

    def test_skill_training_by_use_advances_progress_and_levels(self) -> None:
        skills = CharacterSkills()
        self.assertFalse(skills.train("obserwacja", 9))
        self.assertEqual(skills.level("obserwacja"), 1)
        self.assertEqual(skills.progress("obserwacja"), 9)

        self.assertTrue(skills.train("obserwacja", 2))
        self.assertEqual(skills.level("obserwacja"), 2)
        self.assertEqual(skills.progress("obserwacja"), 1)

    def test_skill_training_stops_at_limit(self) -> None:
        skills = CharacterSkills()
        skills.values["handel"]["level"] = 20
        skills.values["handel"]["progress"] = 7
        self.assertFalse(skills.train("handel", 100))
        self.assertEqual(skills.level("handel"), 20)
        self.assertEqual(skills.progress("handel"), 0)

    def test_skill_save_and_load_roundtrip_preserves_progress(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("round", "secret"))
            char = repo.load("round")
            char.skills.train("bron_cieta", 11)
            char.skills.train("pierwsza_pomoc", 13)
            repo.save(char)

            loaded = repo.load("round")
            self.assertEqual(loaded.skills.level("bron_jednoraczna"), char.skills.level("bron_jednoraczna"))
            self.assertEqual(loaded.skills.progress("bron_jednoraczna"), char.skills.progress("bron_jednoraczna"))
            self.assertEqual(loaded.skills.level("pierwsza_pomoc"), char.skills.level("pierwsza_pomoc"))
            self.assertEqual(loaded.skills.progress("pierwsza_pomoc"), char.skills.progress("pierwsza_pomoc"))

    def test_legacy_skill_model_remains_compatible(self) -> None:
        skills = CharacterSkills(
            {
                "bron_cieta": {"level": 4, "progress": 3},
                "spostrzegawczosc": {"level": 2, "progress": 5},
            }
        )
        self.assertEqual(skills.level("bron_jednoraczna"), 4)
        self.assertEqual(skills.level("bron_cieta"), 4)
        self.assertEqual(skills.level("obserwacja"), 2)
        self.assertIs(skills.values["bron_jednoraczna"], skills.values["bron_cieta"])
        self.assertIs(skills.values["obserwacja"], skills.values["spostrzegawczosc"])


if __name__ == "__main__":
    unittest.main()

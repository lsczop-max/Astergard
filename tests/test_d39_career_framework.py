from __future__ import annotations

import json
import tempfile
import unittest
import warnings

from astergard.characters.careers import (
    CareerUserProfile,
    all_careers,
    all_organizations,
    all_schools,
    can_join_career,
    join_career,
    join_organization,
    join_school,
    leave_career,
    leave_organization,
    leave_school,
    resolve_career,
    resolve_organization,
    resolve_school,
    validate_career_integrity,
)
from astergard.characters.models import Character, CharacterSkills
from astergard.database.repository import PlayerRepository
from astergard.rules.combat_specialization import all_master_trainers


def _career_character() -> Character:
    char = Character(username="career")
    char.skills = CharacterSkills()
    return char


class CareerFrameworkTests(unittest.TestCase):
    def test_character_starts_without_career(self) -> None:
        char = _career_character()
        self.assertIsNone(char.career_id)
        self.assertIsNone(char.organization_id)
        self.assertIsNone(char.school_id)
        self.assertIsNone(char.organization_rank)

    def test_catalog_contains_expected_careers(self) -> None:
        careers = {career.id for career in all_careers()}
        self.assertTrue({"zolnierz", "lowca", "kupiec", "rzemieslnik", "rzezimieszek"}.issubset(careers))
        self.assertEqual(resolve_career("Żołnierz").id, "zolnierz")

    def test_catalog_contains_expected_organizations_and_schools(self) -> None:
        organizations = {organization.id for organization in all_organizations()}
        schools = {school.id for school in all_schools()}
        self.assertIn("legion", organizations)
        self.assertIn("szkola_kuzni", schools)
        self.assertEqual(resolve_organization("Legion").career_id, "zolnierz")
        self.assertEqual(resolve_school("Szkoła Kuźni").organization, "cech_kowali")

    def test_selecting_career_is_allowed_once(self) -> None:
        profile = CareerUserProfile()
        result = can_join_career(profile, "zolnierz")
        self.assertTrue(result.allowed)
        self.assertEqual(result.reason_code, "OK")
        char = _career_character()
        join_result = join_career(char, "zolnierz")
        self.assertTrue(join_result.allowed)
        self.assertEqual(char.career_id, "zolnierz")
        self.assertFalse(join_career(char, "kupiec").allowed)

    def test_joining_organization_requires_career(self) -> None:
        char = _career_character()
        self.assertFalse(join_organization(char, "legion").allowed)
        self.assertEqual(validate_career_integrity(char.career_profile()).reason_code, "OK")

    def test_joining_school_requires_organization(self) -> None:
        char = _career_character()
        join_career(char, "zolnierz")
        self.assertFalse(join_school(char, "szkola_strazy").allowed)
        result = validate_career_integrity(char.career_profile())
        self.assertTrue(result.valid)

    def test_joining_school_requires_matching_organization(self) -> None:
        char = _career_character()
        join_career(char, "zolnierz")
        join_organization(char, "straz_miejska")
        result = join_school(char, "szkola_kuzni")
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "ORGANIZATION_MISMATCH")

    def test_joining_organization_resets_school_and_rank(self) -> None:
        char = _career_character()
        join_career(char, "zolnierz")
        join_organization(char, "legion")
        join_school(char, "szkola_legionu")
        char.organization_rank = 3
        result = join_organization(char, "straz_miejska")
        self.assertTrue(result.allowed)
        self.assertEqual(char.organization_id, "straz_miejska")
        self.assertIsNone(char.school_id)
        self.assertIsNone(char.organization_rank)

    def test_leave_operations_clear_state(self) -> None:
        char = _career_character()
        join_career(char, "zolnierz")
        join_organization(char, "legion")
        join_school(char, "szkola_legionu")
        char.organization_rank = 4
        leave_school(char)
        self.assertIsNone(char.school_id)
        leave_organization(char)
        self.assertIsNone(char.organization_id)
        self.assertIsNone(char.organization_rank)
        leave_career(char)
        self.assertIsNone(char.career_id)

    def test_learning_hierarchy_matches_master_trainers(self) -> None:
        trainers = all_master_trainers()
        trainer_school_ids = {trainer.school_id for trainer in trainers if trainer.school_id}
        self.assertIn("szkola_strazy", trainer_school_ids)
        self.assertIn("szkola_kuzni", trainer_school_ids)
        self.assertIn("szkola_najemna", trainer_school_ids)

    def test_serialization_roundtrip_preserves_career_path(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("career", "secret"))
            char = repo.load("career")
            join_career(char, "rzemieslnik")
            join_organization(char, "cech_kowali")
            join_school(char, "szkola_kuzni")
            char.organization_rank = 2
            repo.save(char)

            loaded = repo.load("career")
            self.assertEqual(loaded.career_id, "rzemieslnik")
            self.assertEqual(loaded.organization_id, "cech_kowali")
            self.assertEqual(loaded.school_id, "szkola_kuzni")
            self.assertEqual(loaded.organization_rank, 2)

    def test_legacy_records_keep_empty_career_path(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("legacy", "secret"))
            with repo.connection() as con:
                row = con.execute(
                    """
                    SELECT room_id,gold,stats_json,skills_json,wounds_json,reputation_json,global_reputation,local_reputation_json,
                           renown,title,crimes_json,wanted_level,wanted_posts_json,quests_json,completed_json,inventory_json,equipment_json,effects_json,combat_style
                    FROM players WHERE username=?
                    """,
                    ("legacy",),
                ).fetchone()
            assert row is not None
            loaded = repo.characters.serializer.hydrate("legacy", row)
            self.assertIsNone(loaded.career_id)
            self.assertIsNone(loaded.organization_id)
            self.assertIsNone(loaded.school_id)
            self.assertIsNone(loaded.organization_rank)

    def test_unknown_ids_are_safely_cleared_on_hydration(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("bad", "secret"))
            creator_json = {
                "name": "bad",
                "career_path": {
                    "career_id": "nieistniejace",
                    "organization_id": "nieistniejaca",
                    "school_id": "nieistniejaca",
                    "organization_rank": 7,
                },
            }
            with repo.connection() as con:
                con.execute(
                    "UPDATE players SET creator_json=? WHERE username=?",
                    (json.dumps(creator_json, ensure_ascii=False), "bad"),
                )
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                loaded = repo.load("bad")
            self.assertGreaterEqual(len(captured), 1)
            self.assertIsNone(loaded.career_id)
            self.assertIsNone(loaded.organization_id)
            self.assertIsNone(loaded.school_id)
            self.assertIsNone(loaded.organization_rank)

    def test_profile_validation_catches_invalid_states(self) -> None:
        result = validate_career_integrity(CareerUserProfile(organization_id="legion"))
        self.assertFalse(result.valid)
        self.assertEqual(result.reason_code, "ORGANIZATION_WITHOUT_CAREER")
        result = validate_career_integrity(CareerUserProfile(career_id="zolnierz", school_id="szkola_strazy"))
        self.assertFalse(result.valid)
        self.assertEqual(result.reason_code, "SCHOOL_WITHOUT_ORGANIZATION")


if __name__ == "__main__":
    unittest.main()

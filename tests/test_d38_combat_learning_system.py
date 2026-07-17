from __future__ import annotations

import tempfile
import unittest

from astergard.characters.models import Character, CharacterSkills
from astergard.database.repository import PlayerRepository
from astergard.rules.combat_specialization import (
    CombatSpecializationLoadout,
    MASTER_TRAINERS,
    MasterTrainer,
    TechniqueUserProfile,
    can_learn_technique,
    learn_specialization,
    learn_technique,
)


def _learning_character() -> Character:
    char = Character(username="learner")
    char.skills = CharacterSkills()
    return char


class CombatLearningSystemTests(unittest.TestCase):
    def test_learn_riposte(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
            additional_skills=(),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        char.skills.values["parowanie"]["level"] = 12
        trainer = MASTER_TRAINERS[0]

        result = learn_technique(char, "riposte", trainer)

        self.assertTrue(result.allowed)
        self.assertIn("riposte", char.known_techniques)
        self.assertFalse(learn_technique(char, "riposte", trainer).allowed)

    def test_missing_required_specialization_blocks_learning(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=(),
            additional_skills=(),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        char.skills.values["parowanie"]["level"] = 12
        trainer = MASTER_TRAINERS[0]

        result = can_learn_technique(
            TechniqueUserProfile(
                known_weapon_specializations=char.combat_specializations.weapon_specializations,
                known_defense_specializations=char.combat_specializations.defense_specializations,
                known_techniques=char.known_techniques,
                weapon_skill_percent={"miecze": 60},
                defense_skill_percent={"parowanie": 60},
            ),
            "riposte",
            trainer,
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "REQUIRED_DEFENSE_NOT_LEARNED")

    def test_missing_required_level_blocks_learning(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
            additional_skills=(),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        char.skills.values["parowanie"]["level"] = 11
        trainer = MASTER_TRAINERS[0]

        result = learn_technique(char, "riposte", trainer)

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "SKILL_LEVEL_TOO_LOW")
        self.assertNotIn("riposte", char.known_techniques)

    def test_mistrz_does_not_teach_technique(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
            additional_skills=(),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        char.skills.values["parowanie"]["level"] = 12
        trainer = MasterTrainer(
            id="fake",
            name="Fałszywy Mistrz",
            description="Nie uczy techniki.",
            location_id="fake_room",
            taught_specializations=("miecze",),
            taught_techniques=("disarm",),
        )

        result = learn_technique(char, "riposte", trainer)

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "TRAINER_CANNOT_TEACH")
        self.assertNotIn("riposte", char.known_techniques)

    def test_repeat_learning_is_blocked(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
            additional_skills=(),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        char.skills.values["parowanie"]["level"] = 12
        trainer = MASTER_TRAINERS[0]

        first = learn_technique(char, "riposte", trainer)
        second = learn_technique(char, "riposte", trainer)

        self.assertTrue(first.allowed)
        self.assertFalse(second.allowed)
        self.assertEqual(second.reason_code, "TECHNIQUE_ALREADY_KNOWN")

    def test_learn_weapon_specialization(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=(),
            defense_specializations=(),
            additional_skills=(),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        trainer = MASTER_TRAINERS[0]

        result = learn_specialization(char, "weapon", "miecze", trainer)

        self.assertTrue(result.allowed)
        self.assertIn("miecze", char.combat_specializations.weapon_specializations)

    def test_limit_specialization_is_enforced(self) -> None:
        char = _learning_character()
        char.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze", "szable"),
            defense_specializations=("parowanie",),
            additional_skills=("tropienie",),
        )
        char.skills.values["bron_jednoraczna"]["level"] = 12
        trainer = MASTER_TRAINERS[0]

        result = learn_specialization(char, "weapon", "sztylety", trainer)

        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "SPECIALIZATION_LIMIT_REACHED")

    def test_serialization_roundtrip_preserves_learning(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("learner", "secret"))
            char = repo.load("learner")
            char.combat_specializations = CombatSpecializationLoadout(
                weapon_specializations=("miecze",),
                defense_specializations=("parowanie",),
                additional_skills=("tropienie",),
            )
            char.known_techniques = ("riposte", "disarm")
            repo.save(char)

            loaded = repo.load("learner")
            self.assertEqual(loaded.combat_specializations.weapon_specializations, ("miecze",))
            self.assertEqual(loaded.combat_specializations.defense_specializations, ("parowanie",))
            self.assertEqual(loaded.known_techniques, ("riposte", "disarm"))

    def test_odczyt_preserves_empty_learning_state(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("empty", "secret"))
            loaded = repo.load("empty")
            self.assertEqual(loaded.combat_specializations.weapon_specializations, ())
            self.assertEqual(loaded.combat_specializations.defense_specializations, ())
            self.assertEqual(loaded.known_techniques, ())


if __name__ == "__main__":
    unittest.main()

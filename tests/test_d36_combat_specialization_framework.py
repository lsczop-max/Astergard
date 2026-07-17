from __future__ import annotations

import json
import unittest

from astergard.rules.combat_specialization import (
    ADDITIONAL_SKILLS,
    DEFENSE_SPECIALIZATIONS,
    TRAINING_STAGES,
    WEAPON_SPECIALIZATIONS,
    CombatSpecializationLimitError,
    CombatSpecializationLoadout,
    CombatSpecializationRules,
    AdditionalSkillDefinition,
    DefenseSpecializationDefinition,
    WeaponSpecializationDefinition,
    combat_specialization_menu_text,
    default_combat_specialization_rules,
    resolve_additional_skill,
    resolve_defense_specialization,
    resolve_weapon_specialization,
    validate_combat_specialization_loadout,
)


class CombatSpecializationFrameworkTests(unittest.TestCase):
    def test_catalog_contains_requested_weapon_definitions(self) -> None:
        self.assertEqual(
            [definition.id for definition in WEAPON_SPECIALIZATIONS],
            ["miecze", "szable", "sztylety", "topory", "mloty", "bulawy", "wlocznie", "halabardy", "cepy", "kije_bojowe"],
        )
        self.assertIsInstance(WEAPON_SPECIALIZATIONS[0], WeaponSpecializationDefinition)
        self.assertEqual(WEAPON_SPECIALIZATIONS[0].techniques, ())
        self.assertEqual(WEAPON_SPECIALIZATIONS[0].master_trainers, ())
        self.assertEqual(WEAPON_SPECIALIZATIONS[0].allowed_actions, ())
        self.assertEqual(WEAPON_SPECIALIZATIONS[0].future_balance, {})

    def test_catalog_contains_requested_defense_definitions(self) -> None:
        self.assertEqual([definition.id for definition in DEFENSE_SPECIALIZATIONS], ["tarcze", "parowanie", "uniki"])
        self.assertIsInstance(DEFENSE_SPECIALIZATIONS[0], DefenseSpecializationDefinition)
        self.assertEqual(DEFENSE_SPECIALIZATIONS[0].techniques, ())

    def test_additional_skills_have_three_training_stages(self) -> None:
        self.assertEqual(len(ADDITIONAL_SKILLS), 12)
        self.assertIsInstance(ADDITIONAL_SKILLS[0], AdditionalSkillDefinition)
        self.assertEqual([stage.id for stage in TRAINING_STAGES], ["trainer", "academy", "master"])
        self.assertEqual([stage.minimum_percent for stage in TRAINING_STAGES], [0, 30, 60])
        self.assertEqual([stage.maximum_percent for stage in TRAINING_STAGES], [30, 60, 100])
        self.assertEqual(ADDITIONAL_SKILLS[0].training_stages, TRAINING_STAGES)

    def test_lookup_resolves_by_id_and_label(self) -> None:
        self.assertEqual(resolve_weapon_specialization("MIECZE").id, "miecze")
        self.assertEqual(resolve_defense_specialization("Parowanie").id, "parowanie")
        self.assertEqual(resolve_additional_skill("pierwsza pomoc").id, "pierwsza_pomoc")

    def test_limits_allow_valid_loadout(self) -> None:
        loadout = CombatSpecializationLoadout(
            weapon_specializations=("miecze", "sztylety"),
            defense_specializations=("tarcze", "uniki"),
            additional_skills=("tropienie", "orientacja", "pierwsza_pomoc", "skradanie"),
        )
        validate_combat_specialization_loadout(loadout)
        self.assertEqual(loadout.weapon_specializations, ("miecze", "sztylety"))

    def test_limit_two_weapons_is_enforced(self) -> None:
        loadout = CombatSpecializationLoadout(
            weapon_specializations=("miecze", "sztylety", "topory"),
            defense_specializations=("tarcze",),
            additional_skills=("tropienie",),
        )
        with self.assertRaises(CombatSpecializationLimitError):
            validate_combat_specialization_loadout(loadout)

    def test_limit_two_defenses_is_enforced(self) -> None:
        loadout = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("tarcze", "parowanie", "uniki"),
            additional_skills=("tropienie",),
        )
        with self.assertRaises(CombatSpecializationLimitError):
            validate_combat_specialization_loadout(loadout)

    def test_limit_four_additional_skills_is_enforced(self) -> None:
        loadout = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("tarcze",),
            additional_skills=("tropienie", "orientacja", "pierwsza_pomoc", "skradanie", "wspinaczka"),
        )
        with self.assertRaises(CombatSpecializationLimitError):
            validate_combat_specialization_loadout(loadout)

    def test_duplicate_specializations_are_rejected(self) -> None:
        loadout = CombatSpecializationLoadout(
            weapon_specializations=("miecze", "miecze"),
            defense_specializations=("tarcze",),
            additional_skills=("tropienie",),
        )
        with self.assertRaises(CombatSpecializationLimitError):
            validate_combat_specialization_loadout(loadout)

    def test_json_roundtrip_preserves_loadout(self) -> None:
        original = CombatSpecializationLoadout(
            weapon_specializations=("szable", "cepy"),
            defense_specializations=("parowanie", "uniki"),
            additional_skills=("targowanie", "kowalstwo", "wspinaczka"),
        )
        payload = json.loads(json.dumps(original.to_dict(), ensure_ascii=False))
        restored = CombatSpecializationLoadout.from_dict(payload)
        self.assertEqual(restored, original)

    def test_rules_roundtrip_preserves_limits(self) -> None:
        rules = CombatSpecializationRules(max_weapon_specializations=2, max_defense_specializations=2, max_additional_skills=4)
        restored = CombatSpecializationRules.from_dict(json.loads(json.dumps(rules.to_dict(), ensure_ascii=False)))
        self.assertEqual(restored, rules)
        self.assertEqual(default_combat_specialization_rules(), rules)

    def test_menu_text_lists_all_sections(self) -> None:
        menu = combat_specialization_menu_text()
        self.assertIn("Specjalizacje broni:", menu)
        self.assertIn("Specjalizacje obrony:", menu)
        self.assertIn("Umiejętności dodatkowe:", menu)


if __name__ == "__main__":
    unittest.main()

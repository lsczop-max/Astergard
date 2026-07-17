from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from astergard.rules.combat_specialization import (
    CombatTechnique,
    CombatTechniqueCatalog,
    CombatTechniqueConfigurationError,
    TechniqueEligibilityResult,
    TechniqueUserProfile,
    WeaponClass,
    can_use_technique,
    default_combat_technique_catalog,
    load_combat_technique_catalog,
)


class CombatTechniquesFrameworkTests(unittest.TestCase):
    def test_loader_loads_default_catalog(self) -> None:
        catalog = default_combat_technique_catalog()
        self.assertIsInstance(catalog, CombatTechniqueCatalog)
        self.assertEqual(catalog.names(), ("riposte", "disarm", "stun", "guard_break", "armor_pierce", "counterattack"))

    def test_loader_rejects_unknown_weapon_class(self) -> None:
        payload = {
            "techniques": [
                {
                    "id": "bad",
                    "name": "Bad",
                    "description": "x",
                    "required_weapon_classes": ["GIGANTIC"],
                    "required_weapon_specializations": [],
                    "required_defense_specializations": [],
                    "required_skill_percent": 10,
                    "required_skill_source": "WEAPON_SPECIALIZATION",
                    "enabled": True,
                    "stamina_cost": 0,
                    "cooldown_seconds": 0,
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            tmp_path = Path(handle.name)
        try:
            with self.assertRaises(CombatTechniqueConfigurationError):
                load_combat_technique_catalog(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_loader_rejects_unknown_weapon_specialization(self) -> None:
        payload = {
            "techniques": [
                {
                    "id": "bad",
                    "name": "Bad",
                    "description": "x",
                    "required_weapon_classes": ["LIGHT"],
                    "required_weapon_specializations": ["nieznane"],
                    "required_defense_specializations": [],
                    "required_skill_percent": 10,
                    "required_skill_source": "WEAPON_SPECIALIZATION",
                    "enabled": True,
                    "stamina_cost": 0,
                    "cooldown_seconds": 0,
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            tmp_path = Path(handle.name)
        try:
            with self.assertRaises(CombatTechniqueConfigurationError):
                load_combat_technique_catalog(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_loader_rejects_unknown_defense_specialization(self) -> None:
        payload = {
            "techniques": [
                {
                    "id": "bad",
                    "name": "Bad",
                    "description": "x",
                    "required_weapon_classes": ["LIGHT"],
                    "required_weapon_specializations": ["miecze"],
                    "required_defense_specializations": ["nieznane"],
                    "required_skill_percent": 10,
                    "required_skill_source": "DEFENSE_SPECIALIZATION",
                    "enabled": True,
                    "stamina_cost": 0,
                    "cooldown_seconds": 0,
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            tmp_path = Path(handle.name)
        try:
            with self.assertRaises(CombatTechniqueConfigurationError):
                load_combat_technique_catalog(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_loader_rejects_duplicate_identifier(self) -> None:
        payload = {
            "techniques": [
                {
                    "id": "dup",
                    "name": "One",
                    "description": "x",
                    "required_weapon_classes": ["LIGHT"],
                    "required_weapon_specializations": ["miecze"],
                    "required_defense_specializations": [],
                    "required_skill_percent": 10,
                    "required_skill_source": "WEAPON_SPECIALIZATION",
                    "enabled": True,
                    "stamina_cost": 0,
                    "cooldown_seconds": 0,
                },
                {
                    "id": "dup",
                    "name": "Two",
                    "description": "y",
                    "required_weapon_classes": ["LIGHT"],
                    "required_weapon_specializations": ["szable"],
                    "required_defense_specializations": [],
                    "required_skill_percent": 10,
                    "required_skill_source": "WEAPON_SPECIALIZATION",
                    "enabled": True,
                    "stamina_cost": 0,
                    "cooldown_seconds": 0,
                },
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            tmp_path = Path(handle.name)
        try:
            with self.assertRaises(CombatTechniqueConfigurationError):
                load_combat_technique_catalog(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_loader_rejects_negative_required_skill_percent(self) -> None:
        technique = {
            "id": "bad",
            "name": "Bad",
            "description": "x",
            "required_weapon_classes": ["LIGHT"],
            "required_weapon_specializations": ["miecze"],
            "required_defense_specializations": [],
            "required_skill_percent": -1,
            "required_skill_source": "WEAPON_SPECIALIZATION",
            "enabled": True,
            "stamina_cost": 0,
            "cooldown_seconds": 0,
        }
        with self.assertRaises(CombatTechniqueConfigurationError):
            CombatTechniqueCatalog.from_dict({"techniques": [technique]})

    def test_loader_rejects_too_high_required_skill_percent(self) -> None:
        technique = {
            "id": "bad",
            "name": "Bad",
            "description": "x",
            "required_weapon_classes": ["LIGHT"],
            "required_weapon_specializations": ["miecze"],
            "required_defense_specializations": [],
            "required_skill_percent": 101,
            "required_skill_source": "WEAPON_SPECIALIZATION",
            "enabled": True,
            "stamina_cost": 0,
            "cooldown_seconds": 0,
        }
        with self.assertRaises(CombatTechniqueConfigurationError):
            CombatTechniqueCatalog.from_dict({"techniques": [technique]})

    def test_technique_serialization_roundtrip(self) -> None:
        technique = CombatTechnique(
            id="example",
            name="Przykład",
            description="Test",
            required_weapon_classes=(WeaponClass.LIGHT, WeaponClass.MEDIUM),
            required_weapon_specializations=("miecze", "szable"),
            required_defense_specializations=("parowanie",),
            required_skill_percent=60,
            enabled=True,
            stamina_cost=0,
            cooldown_seconds=0,
        )
        restored = CombatTechnique.from_dict(json.loads(json.dumps(technique.to_dict(), ensure_ascii=False)))
        self.assertEqual(restored, technique)

    def test_riposte_is_allowed_for_sword_parry_60(self) -> None:
        catalog = default_combat_technique_catalog()
        riposte = catalog.by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="miecze",
            known_weapon_specializations=("miecze",),
            known_defense_specializations=("parowanie",),
            weapon_skill_percent={"miecze": 60},
            defense_skill_percent={"parowanie": 60},
        )
        result = can_use_technique(profile, riposte)
        self.assertTrue(result.allowed)
        self.assertEqual(result.reason_code, "OK")
        self.assertIsInstance(result, TechniqueEligibilityResult)

    def test_riposte_is_allowed_for_sabre_parry_60(self) -> None:
        riposte = default_combat_technique_catalog().by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="szable",
            known_weapon_specializations=("szable",),
            known_defense_specializations=("parowanie",),
            weapon_skill_percent={"szable": 60},
            defense_skill_percent={"parowanie": 60},
        )
        self.assertTrue(can_use_technique(profile, riposte).allowed)

    def test_riposte_is_allowed_for_dagger_parry_60(self) -> None:
        riposte = default_combat_technique_catalog().by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="sztylety",
            known_weapon_specializations=("sztylety",),
            known_defense_specializations=("parowanie",),
            weapon_skill_percent={"sztylety": 60},
            defense_skill_percent={"parowanie": 60},
        )
        self.assertTrue(can_use_technique(profile, riposte).allowed)

    def test_riposte_is_denied_below_threshold(self) -> None:
        riposte = default_combat_technique_catalog().by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="miecze",
            known_weapon_specializations=("miecze",),
            known_defense_specializations=("parowanie",),
            weapon_skill_percent={"miecze": 59},
            defense_skill_percent={"parowanie": 59},
        )
        self.assertFalse(can_use_technique(profile, riposte).allowed)

    def test_riposte_is_denied_without_parry(self) -> None:
        riposte = default_combat_technique_catalog().by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="miecze",
            known_weapon_specializations=("miecze",),
            known_defense_specializations=(),
            weapon_skill_percent={"miecze": 100},
            defense_skill_percent={},
        )
        result = can_use_technique(profile, riposte)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "REQUIRED_DEFENSE_NOT_LEARNED")

    def test_riposte_is_denied_for_incompatible_weapon(self) -> None:
        riposte = default_combat_technique_catalog().by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="mloty",
            known_weapon_specializations=("miecze", "mloty"),
            known_defense_specializations=("parowanie",),
            weapon_skill_percent={"mloty": 100},
            defense_skill_percent={"parowanie": 100},
        )
        result = can_use_technique(profile, riposte)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "INCOMPATIBLE_WEAPON_CLASS")

    def test_riposte_is_denied_when_active_weapon_differs_from_known_requirement(self) -> None:
        riposte = default_combat_technique_catalog().by_id("riposte")
        profile = TechniqueUserProfile(
            active_weapon_specialization="mloty",
            known_weapon_specializations=("miecze", "mloty"),
            known_defense_specializations=("parowanie",),
            weapon_skill_percent={"mloty": 100},
            defense_skill_percent={"parowanie": 100},
        )
        self.assertFalse(can_use_technique(profile, riposte).allowed)

    def test_stun_allows_heavy_weapons_only(self) -> None:
        stun = default_combat_technique_catalog().by_id("stun")
        for weapon in ("mloty", "bulawy", "cepy"):
            profile = TechniqueUserProfile(
                active_weapon_specialization=weapon,
                known_weapon_specializations=(weapon,),
                known_defense_specializations=(),
                weapon_skill_percent={weapon: 60},
                defense_skill_percent={},
            )
            self.assertTrue(can_use_technique(profile, stun).allowed)
        profile = TechniqueUserProfile(
            active_weapon_specialization="miecze",
            known_weapon_specializations=("miecze",),
            known_defense_specializations=(),
            weapon_skill_percent={"miecze": 100},
            defense_skill_percent={},
        )
        self.assertFalse(can_use_technique(profile, stun).allowed)

    def test_disarm_allows_matching_weapons(self) -> None:
        disarm = default_combat_technique_catalog().by_id("disarm")
        for weapon in ("miecze", "włócznie", "halabardy"):
            profile = TechniqueUserProfile(
                active_weapon_specialization=weapon,
                known_weapon_specializations=(weapon,),
                known_defense_specializations=(),
                weapon_skill_percent={weapon: 60},
                defense_skill_percent={},
            )
            self.assertTrue(can_use_technique(profile, disarm).allowed)
        profile = TechniqueUserProfile(
            active_weapon_specialization="mloty",
            known_weapon_specializations=("mloty",),
            known_defense_specializations=(),
            weapon_skill_percent={"mloty": 100},
            defense_skill_percent={},
        )
        self.assertFalse(can_use_technique(profile, disarm).allowed)

    def test_disabled_technique_is_always_denied(self) -> None:
        technique = CombatTechnique(
            id="disabled",
            name="Wyłączona",
            description="x",
            required_weapon_classes=(WeaponClass.LIGHT,),
            required_weapon_specializations=("miecze",),
            required_defense_specializations=(),
            required_skill_percent=10,
            enabled=False,
            stamina_cost=0,
            cooldown_seconds=0,
        )
        profile = TechniqueUserProfile(
            active_weapon_specialization="miecze",
            known_weapon_specializations=("miecze",),
            known_defense_specializations=(),
            weapon_skill_percent={"miecze": 100},
            defense_skill_percent={},
        )
        self.assertFalse(can_use_technique(profile, technique).allowed)

    def test_missing_active_weapon_is_denied(self) -> None:
        technique = default_combat_technique_catalog().by_id("disarm")
        profile = TechniqueUserProfile(
            active_weapon_specialization=None,
            known_weapon_specializations=("miecze",),
            known_defense_specializations=(),
            weapon_skill_percent={"miecze": 100},
            defense_skill_percent={},
        )
        result = can_use_technique(profile, technique)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "NO_ACTIVE_WEAPON")

    def test_unknown_active_weapon_is_denied(self) -> None:
        technique = default_combat_technique_catalog().by_id("disarm")
        profile = TechniqueUserProfile(
            active_weapon_specialization="nieznana",
            known_weapon_specializations=("nieznana",),
            known_defense_specializations=(),
            weapon_skill_percent={"nieznana": 100},
            defense_skill_percent={},
        )
        result = can_use_technique(profile, technique)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "INCOMPATIBLE_WEAPON_SPECIALIZATION")

    def test_global_catalog_remains_immutable(self) -> None:
        catalog = default_combat_technique_catalog()
        self.assertIsInstance(catalog.techniques, tuple)
        snapshot = catalog.names()
        local_copy = list(catalog.techniques)
        local_copy.pop()
        self.assertEqual(default_combat_technique_catalog().names(), snapshot)


if __name__ == "__main__":
    unittest.main()

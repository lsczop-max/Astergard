from __future__ import annotations

import dataclasses
import json
import tempfile
import unittest
import warnings
from collections import deque
from pathlib import Path

import pytest

from astergard.combat.actions import DefenseResolution
from astergard.combat.defense import DefenseType
from astergard.combat.defense import DefenseContext, resolve_defense
from astergard.combat.weapons import (
    HandRequirement,
    WeaponProfileCatalog,
    WeaponProfileConfigurationError,
    active_combat_weapon_and_shield,
    load_default_weapon_profile_catalog,
    resolve_weapon_profile,
    snapshot_weapon_profile,
)
from astergard.items.models import Item, starter_items
from astergard.testing import TestGameHarness


class ScriptedRng:
    def __init__(self, randint_values: list[int] | None = None, random_values: list[float] | None = None) -> None:
        self.randint_values = deque(randint_values or [])
        self.random_values = deque(random_values or [])

    def randint(self, a: int, b: int) -> int:
        if self.randint_values:
            return self.randint_values.popleft()
        return a

    def random(self) -> float:
        if self.random_values:
            return self.random_values.popleft()
        return 1.0


def _clear_combat_slots(character) -> None:
    for slot in ("bron_glowna", "bron_pomocnicza", "tarcza", "prawa_reka", "lewa_reka"):
        character.equipment[slot] = None


class D44WeaponProfileTests(unittest.TestCase):
    def test_default_catalog_loads_and_is_immutable(self) -> None:
        catalog = load_default_weapon_profile_catalog()
        self.assertGreaterEqual(len(catalog.profiles), 10)
        self.assertEqual(catalog.get("garrison_short_sword").id, "garrison_short_sword")  # type: ignore[union-attr]
        with self.assertRaises(dataclasses.FrozenInstanceError):
            catalog.profiles = ()  # type: ignore[misc]
        with self.assertRaises(TypeError):
            catalog.profiles_by_id["x"] = catalog.profiles[0]  # type: ignore[index]

    def test_loader_rejects_invalid_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid_profiles.json"
            base = {
                "id": "test_profile",
                "name": "test profile",
                "specialization_id": "miecze",
                "weapon_class": "MEDIUM",
                "tags": ["blade", "one_handed"],
                "hand_requirement": "ONE_HANDED",
                "damage_types": ["SLASH"],
                "base_speed": 1.0,
                "base_accuracy": 1.0,
                "base_damage": 1.0,
                "armor_penetration": 1.0,
                "reach": 1.0,
                "enabled": True,
            }

            def write(payload: list[dict[str, object]]) -> None:
                path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            write([{**base, "weapon_class": "UNKNOWN"}])
            with self.assertRaises(WeaponProfileConfigurationError):
                WeaponProfileCatalog.from_json(path)

            write([{**base, "specialization_id": "nieznana"}])
            with self.assertRaises(WeaponProfileConfigurationError):
                WeaponProfileCatalog.from_json(path)

            write([{**base, "tags": ["blade", "unknown_tag"]}])
            with self.assertRaises(WeaponProfileConfigurationError):
                WeaponProfileCatalog.from_json(path)

            write([{**base, "damage_types": ["SLASH", "INVALID"]}])
            with self.assertRaises(WeaponProfileConfigurationError):
                WeaponProfileCatalog.from_json(path)

            write([{**base}, {**base}])
            with self.assertRaises(WeaponProfileConfigurationError):
                WeaponProfileCatalog.from_json(path)

    def test_profiles_match_expected_tags(self) -> None:
        catalog = load_default_weapon_profile_catalog()
        self.assertIn("parry_capable", catalog.get("garrison_short_sword").tags)  # type: ignore[union-attr]
        self.assertIn("parry_capable", catalog.get("court_sabre").tags)  # type: ignore[union-attr]
        self.assertIn("parry_capable", catalog.get("duelist_dagger").tags)  # type: ignore[union-attr]
        self.assertNotIn("parry_capable", catalog.get("war_hammer").tags)  # type: ignore[union-attr]
        self.assertNotIn("parry_capable", catalog.get("war_mace").tags)  # type: ignore[union-attr]
        self.assertNotIn("parry_capable", catalog.get("war_flail").tags)  # type: ignore[union-attr]
        self.assertIn("reach", catalog.get("watch_halberd").tags)  # type: ignore[union-attr]
        self.assertIn("hooked", catalog.get("watch_halberd").tags)  # type: ignore[union-attr]
        self.assertIn("parry_capable", catalog.get("war_staff").tags)  # type: ignore[union-attr]

    def test_legacy_profile_snapshot_is_empty_and_resolution_is_safe(self) -> None:
        item = Item("stary miecz", "Stara broń.", 1.0, 1, "legacy_sword", item_type="weapon", slot="bron_glowna")
        profile = resolve_weapon_profile(item)
        snapshot = snapshot_weapon_profile(item)
        self.assertIsNotNone(profile)
        self.assertTrue(profile.legacy)  # type: ignore[union-attr]
        self.assertIsNone(snapshot.weapon_profile_id)
        self.assertEqual(snapshot.weapon_tags, ())
        self.assertIsNone(snapshot.hand_requirement)

    def test_item_serialization_preserves_weapon_profile_id(self) -> None:
        item = Item(
            "prosty miecz",
            "Broń.",
            1.0,
            10,
            "profiled_sword",
            item_type="weapon",
            slot="bron_glowna",
            weapon_profile_id="garrison_short_sword",
        )
        restored = Item.from_dict(item.to_dict())
        self.assertEqual(restored.weapon_profile_id, "garrison_short_sword")

    def test_combat_action_snapshots_profile_data_from_active_weapon_only(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("profile_actor", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            inventory_weapon = Item(
                "miecz w plecaku",
                "Nieaktywny.",
                1.0,
                1,
                "inventory_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_profile_id="garrison_short_sword",
            )
            equipped_weapon = Item(
                "sztylet aktywny",
                "Założony.",
                0.4,
                1,
                "equipped_dagger",
                item_type="weapon",
                slot="bron_glowna",
                weapon_profile_id="duelist_dagger",
            )
            hero.inventory.append(inventory_weapon)
            hero.equipment["bron_glowna"] = equipped_weapon

            action = server.combat.build_basic_attack_action(hero, npc.character)

            self.assertEqual(action.weapon_id, equipped_weapon.id)
            self.assertEqual(action.weapon_profile_id, "duelist_dagger")
            self.assertIn("parry_capable", action.weapon_tags)
            self.assertEqual(action.hand_requirement, HandRequirement.ONE_HANDED)
            self.assertIsNone(action.technique_id)
            hero.equipment["bron_glowna"] = inventory_weapon
            self.assertEqual(action.weapon_profile_id, "duelist_dagger")
            with self.assertRaises(dataclasses.FrozenInstanceError):
                action.weapon_tags = ()  # type: ignore[misc]

    def test_hand_requirements_normalize_two_handed_and_versatile(self) -> None:
        catalog = load_default_weapon_profile_catalog()
        self.assertEqual(catalog.get("war_hammer").hand_requirement, HandRequirement.TWO_HANDED)  # type: ignore[union-attr]
        self.assertEqual(catalog.get("war_staff").hand_requirement, HandRequirement.VERSATILE)  # type: ignore[union-attr]

    def test_parry_capable_profiles_allow_parry_and_non_parry_profiles_do_not(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("attacker", room_id=101)
            defender = harness.create_character("defender", room_id=101)
            _clear_combat_slots(defender)
            defender.inventory.clear()
            attacker.inventory.clear()

            parry_weapon = Item(
                "miecz profilowany",
                "",
                1.0,
                10,
                "parry_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_profile_id="garrison_short_sword",
                weapon_type="miecz",
                parry_bonus=80,
            )
            defender.equipment["bron_glowna"] = parry_weapon
            outcome = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(outcome.resolution, DefenseResolution.PARRIED)
            self.assertTrue(outcome.attempts[-1].available)
            self.assertTrue(outcome.attempts[-1].attempted)

            no_parry_weapon = Item(
                "młot profilowany",
                "",
                1.0,
                10,
                "no_parry_hammer",
                item_type="weapon",
                slot="bron_glowna",
                weapon_profile_id="war_hammer",
                weapon_type="młot",
                parry_bonus=80,
            )
            defender.equipment["bron_glowna"] = no_parry_weapon
            outcome = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(outcome.resolution, DefenseResolution.DODGED)
            self.assertEqual([attempt.defense_type for attempt in outcome.attempts], [DefenseType.DODGE])
            self.assertTrue(outcome.attempts[0].available)
            self.assertTrue(outcome.attempts[0].attempted)

            legacy_weapon = Item("stary miecz", "", 1.0, 10, "legacy_sword", item_type="weapon", slot="bron_glowna", weapon_type="miecz", parry_bonus=80)
            defender.equipment["bron_glowna"] = legacy_weapon
            outcome = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(outcome.resolution, DefenseResolution.PARRIED)
            self.assertTrue(outcome.attempts[-1].available)

    def test_two_handed_profile_blocks_shield_in_combat_resolution(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("attacker2", room_id=101)
            defender = harness.create_character("defender2", room_id=101)
            _clear_combat_slots(defender)
            defender.inventory.clear()
            two_handed = Item(
                "halabarda profilowana",
                "",
                1.0,
                10,
                "halberd_profiled",
                item_type="weapon",
                slot="bron_glowna",
                weapon_profile_id="watch_halberd",
                weapon_type="halabarda",
                parry_bonus=10,
            )
            shield = Item(
                "tarcza profilowana",
                "",
                1.0,
                10,
                "shield_profiled",
                item_type="shield",
                slot="tarcza",
                shield_block=10,
            )
            defender.equipment["bron_glowna"] = two_handed
            defender.equipment["tarcza"] = shield
            with pytest.warns(UserWarning, match="Tarcza nie bierze udziału w obronie"):
                outcome = resolve_defense(
                    DefenseContext(
                        attacker=attacker,
                        defender=defender,
                        hit_score=60,
                        dodge_score=1,
                        rng=ScriptedRng(randint_values=[1]),
                        rules=server.combat.rules,
                    )
                )
            shield_attempt = next(attempt for attempt in outcome.attempts if attempt.defense_type == DefenseType.SHIELD_BLOCK)
            self.assertFalse(shield_attempt.available)
            self.assertFalse(shield_attempt.attempted)
            self.assertEqual(shield_attempt.reason_code, "INCOMPATIBLE_WEAPON_STATE")

    def test_unknown_profile_is_fallback_safe(self) -> None:
        item = Item(
            "broń z błędnym profilem",
            "",
            1.0,
            1,
            "broken_profile_weapon",
            item_type="weapon",
            slot="bron_glowna",
            weapon_profile_id="missing_profile",
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            profile = resolve_weapon_profile(item)
        self.assertIsNotNone(profile)
        self.assertTrue(profile.legacy)  # type: ignore[union-attr]
        self.assertTrue(caught)

    def test_active_combat_equipment_helper_ignores_inventory(self) -> None:
        with TestGameHarness() as harness:
            harness.require_server()
            hero = harness.create_character("equip_helper", room_id=101)
            _clear_combat_slots(hero)
            equipped = Item("miecz aktywny", "", 1.0, 1, "equipped_weapon", item_type="weapon", slot="bron_glowna", weapon_profile_id="garrison_short_sword")
            inventory = Item("miecz w plecaku", "", 1.0, 1, "inventory_weapon", item_type="weapon", slot="bron_glowna", weapon_profile_id="court_sabre")
            shield = Item("tarcza aktywna", "", 1.0, 1, "equipped_shield", item_type="shield", slot="tarcza")
            hero.equipment["bron_glowna"] = equipped
            hero.equipment["tarcza"] = shield
            hero.inventory.append(inventory)
            weapon, resolved_shield, profile = active_combat_weapon_and_shield(hero)
            assert weapon is not None
            assert resolved_shield is not None
            assert profile is not None
            self.assertEqual(weapon.id, equipped.id)
            self.assertEqual(resolved_shield.id, shield.id)
            self.assertFalse(profile.legacy)

    def test_combat_action_and_defense_remain_compatible_with_existing_flow(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("flow_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            hero.inventory.clear()
            npc.character.inventory.clear()
            hero.equipment["bron_glowna"] = Item(
                "prosty miecz",
                "Broń testowa.",
                1.0,
                10,
                "flow_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_type="miecz",
                weapon_profile_id="garrison_short_sword",
                base_damage=6,
                parry_bonus=2,
            )
            hero.skills.values["bron_jednoraczna"]["level"] = 20
            server.combat.rng = ScriptedRng(randint_values=[20, 1, 1], random_values=[1.0, 1.0, 1.0])

            result = server.combat.attack(hero, npc.character)

            self.assertIsNotNone(result.combat_action)
            self.assertIsNotNone(result.combat_outcome)
            assert result.combat_action is not None
            assert result.combat_outcome is not None
            self.assertEqual(result.combat_action.action_id, result.combat_outcome.action_id)
            self.assertIsNotNone(result.combat_action.weapon_profile_id)
            self.assertEqual(result.combat_outcome.defense_result, result.combat_outcome.defense_outcome.resolution if result.combat_outcome.defense_outcome else result.combat_outcome.defense_result)

    def test_current_starter_weapon_has_profile(self) -> None:
        starter = starter_items()[0]
        self.assertEqual(starter.weapon_profile_id, "garrison_short_sword")


if __name__ == "__main__":
    unittest.main()

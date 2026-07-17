from __future__ import annotations

import unittest
from collections import deque

import pytest

from astergard.characters.models import Character
from astergard.combat.actions import DefenseType
from astergard.combat.defense import DefenseContext, build_defense_candidates
from astergard.items.models import Item
from astergard.rules.combat_specialization import ActiveDefenseStyle, CombatSpecializationLoadout
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


def _weapon(profile_id: str, vnum: str, name: str, *, weapon_type: str = "miecz") -> Item:
    return Item(
        name,
        "",
        1.0,
        10,
        vnum,
        item_type="weapon",
        slot="bron_glowna",
        weapon_profile_id=profile_id,
        weapon_type=weapon_type,
        parry_bonus=10,
    )


def _shield(profile_id: str, vnum: str, name: str) -> Item:
    return Item(
        name,
        "",
        1.0,
        10,
        vnum,
        item_type="shield",
        slot="tarcza",
        shield_profile_id=profile_id,
        shield_block=10,
    )


def _armor(profile_id: str, vnum: str, name: str, *, weight: float = 10.0) -> Item:
    return Item(
        name,
        "",
        weight,
        10,
        vnum,
        item_type="armor",
        slot="korpus",
        armor_profile_id=profile_id,
        protection=1,
        armor_value=1,
    )


def _clear_combat_slots(character: Character) -> None:
    for slot in ("bron_glowna", "bron_pomocnicza", "tarcza", "prawa_reka", "lewa_reka", "korpus"):
        character.equipment[slot] = None


class D47DynamicDefenseEvaluationTests(unittest.TestCase):
    def _build_context(self, defender: Character, attacker: Character, *, hit_score: int = 60, dodge_score: int = 1, server=None) -> DefenseContext:
        assert server is not None
        return DefenseContext(
            attacker=attacker,
            defender=defender,
            hit_score=hit_score,
            dodge_score=dodge_score,
            rng=ScriptedRng(randint_values=[1, 1, 1, 1, 1]),
            rules=server.combat.rules,
        )

    def test_order_prefers_shield_then_dodge_then_parry_for_well_protected_character(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("order_attacker", room_id=101)
            defender = harness.create_character("order_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            defender.skills.values["tarcze"]["level"] = 90
            defender.skills.values["uniki"]["level"] = 60
            defender.skills.values["parowanie"]["level"] = 50
            defender.equipment["korpus"] = _armor("light_armor", "light_armor", "lekki pancerz")
            defender.equipment["tarcza"] = _shield("small_shield", "small_shield", "mała tarcza")
            defender.equipment["bron_glowna"] = _weapon("garrison_short_sword", "sword", "miecz")
            defender.active_defense_style = ActiveDefenseStyle.DODGE.value

            candidates = build_defense_candidates(self._build_context(defender, attacker, server=server))

            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.SHIELD_BLOCK, DefenseType.DODGE, DefenseType.PARRY])
            self.assertGreater(candidates[0].effective_value, candidates[1].effective_value)
            self.assertGreater(candidates[1].effective_value, candidates[2].effective_value)

    def test_heavy_armor_pushes_dodge_to_the_bottom(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("heavy_attacker", room_id=101)
            defender = harness.create_character("heavy_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            defender.skills.values["tarcze"]["level"] = 90
            defender.skills.values["uniki"]["level"] = 60
            defender.skills.values["parowanie"]["level"] = 50
            defender.equipment["korpus"] = _armor("heavy_armor", "heavy_armor", "ciężki pancerz")
            defender.equipment["tarcza"] = _shield("small_shield", "small_shield", "mała tarcza")
            defender.equipment["bron_glowna"] = _weapon("garrison_short_sword", "sword", "miecz")

            candidates = build_defense_candidates(self._build_context(defender, attacker, server=server))

            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.SHIELD_BLOCK, DefenseType.PARRY, DefenseType.DODGE])
            self.assertFalse(candidates[-1].available)

    def test_hammer_reduces_parry_to_zero_effectiveness(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("hammer_attacker", room_id=101)
            defender = harness.create_character("hammer_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            defender.skills.values["tarcze"]["level"] = 90
            defender.skills.values["uniki"]["level"] = 60
            defender.skills.values["parowanie"]["level"] = 50
            defender.equipment["korpus"] = _armor("light_armor", "light_armor", "lekki pancerz")
            defender.equipment["tarcza"] = _shield("small_shield", "small_shield", "mała tarcza")
            defender.equipment["bron_glowna"] = _weapon("war_hammer", "war_hammer", "młot", weapon_type="młot")

            with pytest.warns(UserWarning, match="Tarcza nie bierze udziału w obronie"):
                candidates = build_defense_candidates(self._build_context(defender, attacker, server=server))

            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.SHIELD_BLOCK, DefenseType.DODGE, DefenseType.PARRY])
            parry_candidate = next(candidate for candidate in candidates if candidate.defense_type == DefenseType.PARRY)
            self.assertFalse(parry_candidate.available)
            self.assertEqual(parry_candidate.effective_value, 0.0)

    def test_rapier_is_better_at_parrying_than_sword(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("rapier_attacker", room_id=101)
            rapier_fighter = harness.create_character("rapier_defender", room_id=101)
            sword_fighter = harness.create_character("sword_defender", room_id=101)
            for character in (rapier_fighter, sword_fighter):
                _clear_combat_slots(character)
                character.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
                character.skills.values["parowanie"]["level"] = 60
                character.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie")

            rapier_fighter.equipment["bron_glowna"] = _weapon("duelist_rapier", "rapier", "rapier", weapon_type="szpada")
            sword_fighter.equipment["bron_glowna"] = _weapon("garrison_short_sword", "sword", "miecz", weapon_type="miecz")

            rapier_candidates = build_defense_candidates(self._build_context(rapier_fighter, attacker, server=server))
            sword_candidates = build_defense_candidates(self._build_context(sword_fighter, attacker, server=server))

            rapier_parry = next(candidate for candidate in rapier_candidates if candidate.defense_type == DefenseType.PARRY)
            sword_parry = next(candidate for candidate in sword_candidates if candidate.defense_type == DefenseType.PARRY)
            self.assertGreater(rapier_parry.effective_value, sword_parry.effective_value)

    def test_axe_is_worse_at_parrying_than_sword(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("axe_attacker", room_id=101)
            axe_fighter = harness.create_character("axe_defender", room_id=101)
            sword_fighter = harness.create_character("sword_defender_2", room_id=101)
            for character in (axe_fighter, sword_fighter):
                _clear_combat_slots(character)
                character.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
                character.skills.values["parowanie"]["level"] = 60
                character.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie")

            axe_fighter.equipment["bron_glowna"] = _weapon("battle_axe", "battle_axe", "topór", weapon_type="topór")
            sword_fighter.equipment["bron_glowna"] = _weapon("garrison_short_sword", "sword_2", "miecz", weapon_type="miecz")

            axe_candidates = build_defense_candidates(self._build_context(axe_fighter, attacker, server=server))
            sword_candidates = build_defense_candidates(self._build_context(sword_fighter, attacker, server=server))

            axe_parry = next(candidate for candidate in axe_candidates if candidate.defense_type == DefenseType.PARRY)
            sword_parry = next(candidate for candidate in sword_candidates if candidate.defense_type == DefenseType.PARRY)
            self.assertLess(axe_parry.effective_value, sword_parry.effective_value)

    def test_missing_shield_and_weapon_skip_their_candidates(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("bare_attacker", room_id=101)
            defender = harness.create_character("bare_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki",))
            defender.skills.values["uniki"]["level"] = 40
            defender.skills.values["tarcze"]["level"] = 0
            defender.skills.values["parowanie"]["level"] = 0

            candidates = build_defense_candidates(self._build_context(defender, attacker, server=server))

            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.DODGE])

    def test_when_everything_is_disabled_the_attack_goes_through(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("attack_attacker", room_id=101)
            defender = harness.create_character("attack_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            defender.skills.values["uniki"]["level"] = 0
            defender.skills.values["tarcze"]["level"] = 0
            defender.skills.values["parowanie"]["level"] = 0
            attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", "attacker_sword", "miecz")
            attacker.skills.values["bron_jednoraczna"]["level"] = 20

            result = server.combat.attack(attacker, defender)

            self.assertIsNotNone(result.combat_outcome)
            assert result.combat_outcome is not None
            self.assertIn(result.combat_outcome.result_type.value, {"HIT", "TARGET_DEFEATED"})

    def test_sorting_is_stable_for_equal_values(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("stable_attacker", room_id=101)
            defender = harness.create_character("stable_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            defender.skills.values["uniki"]["level"] = 50
            defender.skills.values["tarcze"]["level"] = 50
            defender.skills.values["parowanie"]["level"] = 50
            defender.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie", weight=0.0)
            defender.equipment["tarcza"] = _shield("medium_shield", "medium_shield", "średnia tarcza")
            defender.equipment["bron_glowna"] = _weapon("garrison_short_sword", "stable_sword", "miecz")

            candidates = build_defense_candidates(self._build_context(defender, attacker, server=server))

            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.SHIELD_BLOCK, DefenseType.PARRY, DefenseType.DODGE])

    def test_active_style_no_longer_changes_defense_result(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker_a = harness.create_character("style_attacker_a", room_id=101)
            attacker_b = harness.create_character("style_attacker_b", room_id=101)
            defender_a = harness.create_character("style_defender_a", room_id=101)
            defender_b = harness.create_character("style_defender_b", room_id=101)
            for attacker in (attacker_a, attacker_b):
                attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", f"{attacker.username}_sword", "miecz")
                attacker.skills.values["bron_jednoraczna"]["level"] = 20
            for defender in (defender_a, defender_b):
                _clear_combat_slots(defender)
                defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
                defender.skills.values["uniki"]["level"] = 40
                defender.skills.values["tarcze"]["level"] = 0
                defender.skills.values["parowanie"]["level"] = 0
                defender.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie")
            defender_a.active_defense_style = ActiveDefenseStyle.DODGE.value
            defender_b.active_defense_style = ActiveDefenseStyle.PARRY.value
            server.combat.rng = ScriptedRng(randint_values=[1, 1, 1, 1, 1], random_values=[1.0, 1.0, 1.0])
            result_a = server.combat.attack(attacker_a, defender_a)
            server.combat.rng = ScriptedRng(randint_values=[1, 1, 1, 1, 1], random_values=[1.0, 1.0, 1.0])
            result_b = server.combat.attack(attacker_b, defender_b)

            self.assertIsNotNone(result_a.combat_outcome)
            self.assertIsNotNone(result_b.combat_outcome)
            assert result_a.combat_outcome is not None
            assert result_b.combat_outcome is not None
            self.assertEqual(result_a.combat_outcome.result_type, result_b.combat_outcome.result_type)
            self.assertEqual(result_a.combat_outcome.damage, result_b.combat_outcome.damage)
            self.assertEqual(result_a.combat_outcome.wound_ids, result_b.combat_outcome.wound_ids)


if __name__ == "__main__":
    unittest.main()

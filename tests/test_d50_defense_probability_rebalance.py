from __future__ import annotations

import unittest
from collections import deque

from astergard.characters.models import Character
from astergard.combat.actions import CombatActionType, DefenseResolution, DefenseType
from astergard.combat.defense import DefenseContext, build_defense_candidates, resolve_defense
from astergard.combat.defense_balance import default_defense_probability_policy
from astergard.items.models import Item
from astergard.rules.combat_specialization import CombatSpecializationLoadout
from astergard.testing import TestGameHarness


class ScriptedRng:
    def __init__(self, randint_values: list[int] | None = None) -> None:
        self.randint_values = deque(randint_values or [])

    def randint(self, a: int, b: int) -> int:
        if self.randint_values:
            return self.randint_values.popleft()
        return a

    def random(self) -> float:
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


def _armor(profile_id: str, vnum: str, name: str) -> Item:
    return Item(
        name,
        "",
        1.0,
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


class D50DefenseProbabilityRebalanceTests(unittest.TestCase):
    def test_curve_is_monotonic_and_capped(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("curve_attacker", room_id=101)
            defender = harness.create_character("curve_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki",))
            defender.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie")
            policy = default_defense_probability_policy()

            # Rebuild explicit levels to compare the curve directly.
            defender.skills.values["uniki"]["level"] = 0
            zero = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))[0]
            defender.skills.values["uniki"]["level"] = 30
            low = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))[0]
            defender.skills.values["uniki"]["level"] = 100
            high = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))[0]

            self.assertEqual(zero.final_probability, 0.0)
            self.assertGreater(low.final_probability, 0.0)
            self.assertLess(low.final_probability, high.final_probability)
            self.assertLess(high.final_probability, 1.0)
            self.assertLessEqual(high.final_probability, policy.maximum_probability)

    def test_attack_pressure_reduces_probability_without_breaking_specialists(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("pressure_attacker", room_id=101)
            defender = harness.create_character("pressure_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki",))
            defender.skills.values["uniki"]["level"] = 100
            defender.equipment["korpus"] = _armor("light_armor", "light_armor", "lekki pancerz")

            low_pressure = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=20, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))[0]
            high_pressure = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=120, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))[0]

            self.assertGreater(low_pressure.final_probability, high_pressure.final_probability)
            self.assertGreater(low_pressure.final_probability, 0.1)
            self.assertGreaterEqual(high_pressure.final_probability, 0.0)

    def test_sequence_multipliers_apply_and_respect_tie_break(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("sequence_attacker", room_id=101)
            defender = harness.create_character("sequence_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            defender.skills.values["tarcze"]["level"] = 90
            defender.skills.values["uniki"]["level"] = 90
            defender.skills.values["parowanie"]["level"] = 90
            defender.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie")
            defender.equipment["tarcza"] = _shield("medium_shield", "medium_shield", "średnia tarcza")
            defender.equipment["bron_glowna"] = _weapon("garrison_short_sword", "sword", "miecz")

            candidates = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1, 1, 1]), rules=server.combat.rules))
            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.SHIELD_BLOCK, DefenseType.PARRY, DefenseType.DODGE])
            self.assertEqual(candidates[0].sequence_multiplier, 1.0)
            self.assertEqual(candidates[1].sequence_multiplier, 0.5)
            self.assertEqual(candidates[2].sequence_multiplier, 0.25)
            self.assertLess(candidates[1].final_probability, candidates[1].base_probability)
            self.assertLess(candidates[2].final_probability, candidates[2].base_probability)

            outcome = resolve_defense(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1000, 1]), rules=server.combat.rules))
            self.assertEqual(outcome.resolution, DefenseResolution.PARRIED)
            self.assertEqual([attempt.defense_type for attempt in outcome.attempts], [DefenseType.SHIELD_BLOCK, DefenseType.PARRY])

    def test_equipment_modifiers_follow_profiles(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("equipment_attacker", room_id=101)
            defender = harness.create_character("equipment_defender", room_id=101)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))

            _clear_combat_slots(defender)
            defender.skills.values["uniki"]["level"] = 100
            defender.equipment["korpus"] = _armor("heavy_armor", "heavy_armor", "ciężki pancerz")
            heavy = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))
            heavy_dodge = next(candidate for candidate in heavy if candidate.defense_type == DefenseType.DODGE)
            self.assertFalse(heavy_dodge.available)
            self.assertEqual(heavy_dodge.final_probability, 0.0)

            _clear_combat_slots(defender)
            defender.skills.values["uniki"]["level"] = 60
            defender.equipment["korpus"] = _armor("medium_armor", "medium_armor", "średni pancerz")
            medium = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))
            medium_dodge = next(candidate for candidate in medium if candidate.defense_type == DefenseType.DODGE)
            self.assertGreater(medium_dodge.final_probability, 0.0)
            self.assertLess(medium_dodge.final_probability, 1.0)

            _clear_combat_slots(defender)
            defender.skills.values["parowanie"]["level"] = 80
            defender.equipment["bron_glowna"] = _weapon("battle_axe", "battle_axe", "topór", weapon_type="topór")
            axe = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))
            axe_parry = next(candidate for candidate in axe if candidate.defense_type == DefenseType.PARRY)
            self.assertGreater(axe_parry.final_probability, 0.0)

            _clear_combat_slots(defender)
            defender.skills.values["tarcze"]["level"] = 80
            defender.equipment["tarcza"] = _shield("medium_shield", "medium_shield", "średnia tarcza")
            defender.equipment["korpus"] = _armor("unarmored", "unarmored", "ubranie")
            shield_candidates = build_defense_candidates(DefenseContext(attacker=attacker, defender=defender, hit_score=60, dodge_score=1, rng=ScriptedRng([1]), rules=server.combat.rules))
            shield = next(candidate for candidate in shield_candidates if candidate.defense_type == DefenseType.SHIELD_BLOCK)
            self.assertGreater(shield.final_probability, 0.0)

    def test_integration_riposte_can_still_fire_without_loops(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("integrated_attacker", room_id=101)
            defender = harness.create_character("integrated_defender", room_id=101)
            defender.combat_specializations = CombatSpecializationLoadout(weapon_specializations=("miecze",), defense_specializations=("parowanie",))
            defender.known_techniques = ("riposte",)
            defender.skills.values["parowanie"]["level"] = 100
            defender.skills.values["bron_jednoraczna"]["level"] = 100
            defender.equipment["bron_glowna"] = _weapon("garrison_short_sword", "defender_sword", "miecz")
            attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", "attacker_sword", "miecz")
            attacker.skills.values["bron_jednoraczna"]["level"] = 20
            server.combat.start_fight(attacker, defender)
            server.combat.rng = ScriptedRng([1] * 20)

            result = server.combat.attack(attacker, defender)

            self.assertIsNotNone(result.combat_outcome)
            assert result.combat_outcome is not None
            self.assertIsNotNone(result.reaction_discovery)
            self.assertIsNotNone(result.reaction_execution)
            if result.reaction_execution is not None:
                self.assertTrue(result.reaction_execution.executed)
                self.assertIsNotNone(result.reaction_execution.reaction_result)
                if result.reaction_execution.reaction_result is not None:
                    self.assertEqual(result.reaction_execution.reaction_result.combat_action.action_type, CombatActionType.REACTION)
                    self.assertEqual(result.reaction_execution.reaction_result.combat_action.reaction_depth, 1)
                    self.assertEqual(result.reaction_execution.reaction_result.combat_action.technique_id, "riposte")

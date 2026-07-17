from __future__ import annotations

import random
import unittest
from collections import Counter, deque

from astergard.characters.models import Character
from astergard.combat.actions import CombatAction, CombatOutcome, CombatOutcomeType, DefenseOutcome, DefenseResolution
from astergard.combat.hit_locations import (
    ArmorCoverageOutcome,
    AttackType,
    BodyLocation,
    BodyLocationGroup,
    HitQuality,
    load_default_armor_coverage_catalog,
    load_default_hit_location_catalog,
    resolve_armor_coverage,
    resolve_hit_location,
)
from astergard.combat.manager import CombatManager
from astergard.combat.weapons import resolve_weapon_profile
from astergard.items.models import Item
from astergard.rules.combat_specialization import CombatSpecializationLoadout


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


def _weapon(profile_id: str, *, name: str, weapon_type: str, damage_type: str, base_damage: int = 5) -> Item:
    return Item(
        name,
        "",
        1.0,
        10,
        profile_id,
        item_type="weapon",
        slot="bron_glowna",
        wearable=True,
        weapon_type=weapon_type,
        damage_type=damage_type,
        base_damage=base_damage,
        parry_bonus=5,
        weapon_profile_id=profile_id,
    )


def _armor(profile_id: str, *, slot: str = "korpus", name: str | None = None) -> Item:
    return Item(
        name or profile_id,
        "",
        2.0,
        12,
        f"{profile_id}_{slot}",
        item_type="armor",
        slot=slot,
        wearable=True,
        armor_value=2,
        protection=2,
        id=f"{profile_id}_{slot}",
        armor_profile_id=profile_id,
    )


def _shield(profile_id: str, *, name: str | None = None) -> Item:
    return Item(
        name or profile_id,
        "",
        2.0,
        12,
        f"{profile_id}_shield",
        item_type="shield",
        slot="tarcza",
        wearable=True,
        shield_block=5,
        id=f"{profile_id}_shield",
        shield_profile_id=profile_id,
    )


class D52BodyLocationsAndArmorCoverageTests(unittest.TestCase):
    def test_hit_location_catalog_is_deterministic_for_a_seed(self) -> None:
        catalog = load_default_hit_location_catalog()
        weapon = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta")
        action = CombatAction(actor_id="attacker", target_id="defender")

        first = resolve_hit_location(
            resolve_weapon_profile(weapon),
            action,
            HitQuality.CLEAN,
            None,
            None,
            random.Random(17),
            attack_type=AttackType.SLASH,
        )
        second = resolve_hit_location(
            resolve_weapon_profile(weapon),
            action,
            HitQuality.CLEAN,
            None,
            None,
            random.Random(17),
            attack_type=AttackType.SLASH,
        )

        self.assertEqual(first.location, second.location)
        self.assertEqual(first.location_group, second.location_group)
        self.assertGreater(len(catalog.rules), 0)

    def test_slash_thrust_and_overhead_prefer_expected_regions(self) -> None:
        weapon = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta")
        action = CombatAction(actor_id="attacker", target_id="defender")
        profile = resolve_weapon_profile(weapon)

        def sample(attack_type: AttackType) -> Counter[BodyLocationGroup]:
            rng = random.Random(2026)
            counts: Counter[BodyLocationGroup] = Counter()
            for _ in range(400):
                outcome = resolve_hit_location(profile, action, HitQuality.CLEAN, None, None, rng, attack_type=attack_type)
                counts[outcome.location_group] += 1
            return counts

        slash = sample(AttackType.SLASH)
        thrust = sample(AttackType.THRUST)
        overhead = sample(AttackType.OVERHEAD)

        self.assertGreater(slash[BodyLocationGroup.ARM_GROUP] + slash[BodyLocationGroup.TORSO_GROUP], slash[BodyLocationGroup.FOOT_GROUP])
        self.assertGreater(thrust[BodyLocationGroup.TORSO_GROUP], thrust[BodyLocationGroup.FOOT_GROUP])
        self.assertGreater(overhead[BodyLocationGroup.HEAD_GROUP] + overhead[BodyLocationGroup.ARM_GROUP], overhead[BodyLocationGroup.FOOT_GROUP])

    def test_high_quality_does_not_force_vital_locations(self) -> None:
        weapon = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta")
        action = CombatAction(actor_id="attacker", target_id="defender")
        profile = resolve_weapon_profile(weapon)
        rng = random.Random(999)

        outcomes = [
            resolve_hit_location(profile, action, HitQuality.DEVASTATING, None, None, rng, attack_type=AttackType.STANDARD)
            for _ in range(200)
        ]

        self.assertTrue(any(outcome.location not in {BodyLocation.HEAD, BodyLocation.NECK} for outcome in outcomes))

    def test_active_armor_is_detected_and_inventory_only_is_ignored(self) -> None:
        target = Character("obronca")
        target.skills.values["uniki"]["level"] = 0
        target.skills.values["parowanie"]["level"] = 0
        target.skills.values["tarcze"]["level"] = 0

        inventory_armor = _armor("medium_armor", name="środkowy pancerz")
        target.inventory.append(inventory_armor)
        inventory_only = resolve_armor_coverage(target, BodyLocation.CHEST, ScriptedRng(random_values=[0.0]), load_default_armor_coverage_catalog())
        self.assertTrue(inventory_only.fully_unarmored)

        target.equipment["korpus"] = inventory_armor
        equipped = resolve_armor_coverage(target, BodyLocation.CHEST, ScriptedRng(random_values=[0.0]), load_default_armor_coverage_catalog())
        self.assertFalse(equipped.fully_unarmored)
        self.assertTrue(equipped.covering_layers)
        self.assertFalse(equipped.partial_coverage)

    def test_partial_coverage_is_probabilistic_and_layers_are_sorted(self) -> None:
        target = Character("obronca")
        target.equipment["tarcza"] = _shield("small_shield", name="mała tarcza")

        covered = resolve_armor_coverage(target, BodyLocation.CHEST, ScriptedRng(random_values=[0.0]), load_default_armor_coverage_catalog())
        uncovered = resolve_armor_coverage(target, BodyLocation.CHEST, ScriptedRng(random_values=[0.99]), load_default_armor_coverage_catalog())
        self.assertTrue(covered.partial_coverage)
        self.assertTrue(covered.covering_layers)
        self.assertTrue(uncovered.partial_coverage)
        self.assertFalse(uncovered.covering_layers)
        self.assertTrue(uncovered.fully_unarmored)

        target.equipment["korpus"] = _armor("medium_armor", name="średni pancerz")
        layered = resolve_armor_coverage(target, BodyLocation.CHEST, ScriptedRng(random_values=[0.0, 0.0]), load_default_armor_coverage_catalog())
        self.assertEqual([layer.item_id for layer in layered.covering_layers], ["small_shield_shield", "medium_armor_korpus"])

    def test_hit_resolution_populates_body_location_and_coverage(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[10, 1], random_values=[0.0, 0.0, 0.0, 0.0]))
        attacker = Character("atakujacy")
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        attacker.skills.values["bron_jednoraczna"]["level"] = 20
        defender = Character("obronca")
        defender.skills.values["uniki"]["level"] = 0
        defender.skills.values["parowanie"]["level"] = 0
        defender.skills.values["tarcze"]["level"] = 0

        result = manager.attack(attacker, defender)

        self.assertIsNotNone(result.combat_outcome)
        assert result.combat_outcome is not None
        self.assertTrue(result.hit)
        self.assertIsNotNone(result.body_location)
        self.assertIsNotNone(result.body_location_group)
        self.assertIsNotNone(result.hit_quality)
        self.assertIsNotNone(result.combat_outcome.body_location)
        self.assertIsNotNone(result.combat_outcome.body_location_group)
        self.assertIsNotNone(result.combat_outcome.hit_quality)
        self.assertIsNotNone(result.combat_outcome.armor_coverage_outcome)
        armor_coverage = result.combat_outcome.armor_coverage_outcome
        assert armor_coverage is not None
        self.assertIsInstance(armor_coverage, ArmorCoverageOutcome)
        self.assertTrue(armor_coverage.fully_unarmored)

    def test_defended_attack_does_not_assign_body_location(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[1, 1, 1], random_values=[0.0, 0.0, 0.0, 0.0]))
        attacker = Character("atakujacy")
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=6)
        attacker.skills.values["bron_jednoraczna"]["level"] = 0
        defender = Character("obronca")
        defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki",))
        defender.skills.values["uniki"]["level"] = 100
        defender.skills.values["parowanie"]["level"] = 0
        defender.skills.values["tarcze"]["level"] = 0

        result = manager.attack(attacker, defender)

        self.assertIsNotNone(result.combat_outcome)
        assert result.combat_outcome is not None
        self.assertEqual(result.combat_outcome.result_type, CombatOutcomeType.DEFENDED)
        self.assertIsNone(result.body_location)
        self.assertIsNone(result.combat_outcome.body_location)
        self.assertIsNone(result.combat_outcome.body_location_group)

    def test_miss_outcome_has_no_body_location(self) -> None:
        outcome = CombatOutcome(
            action_id="miss-1",
            actor_id="attacker",
            target_id="defender",
            result_type=CombatOutcomeType.MISS,
            hit=False,
            defense_result=DefenseResolution.NONE,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.NONE,
                successful_defense=False,
                attempts=(),
                selected_defense=None,
                reason_code="MISS",
            ),
            damage=0,
            target_defeated=False,
            combat_ended=False,
            reason_code="MISS",
        )
        self.assertIsNone(outcome.body_location)
        self.assertIsNone(outcome.body_location_group)

    def test_riposte_can_receive_a_body_location(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[1] * 20, random_values=[0.0] * 20))
        attacker = Character("atakujacy", room_id=1)
        defender = Character("obronca", room_id=1)
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=6)
        attacker.skills.values["bron_jednoraczna"]["level"] = 5
        attacker.skills.values["uniki"]["level"] = 0
        attacker.skills.values["parowanie"]["level"] = 0
        attacker.skills.values["tarcze"]["level"] = 0

        defender.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
        )
        defender.known_techniques = ("riposte",)
        defender.equipment["bron_glowna"] = _weapon("court_sabre", name="szabla", weapon_type="szabla", damage_type="cieta", base_damage=4)
        defender.skills.values["bron_jednoraczna"]["level"] = 100
        defender.skills.values["parowanie"]["level"] = 100
        defender.skills.values["uniki"]["level"] = 0
        defender.skills.values["tarcze"]["level"] = 0
        manager.start_fight(attacker, defender)

        result = manager.attack(attacker, defender)

        self.assertIsNotNone(result.reaction_execution)
        assert result.reaction_execution is not None
        self.assertTrue(result.reaction_execution.executed)
        self.assertIsNotNone(result.reaction_execution.reaction_result)
        assert result.reaction_execution.reaction_result is not None
        self.assertIsNotNone(result.reaction_execution.reaction_result.combat_outcome.body_location)
        self.assertIsNotNone(result.reaction_execution.reaction_result.combat_outcome.body_location_group)

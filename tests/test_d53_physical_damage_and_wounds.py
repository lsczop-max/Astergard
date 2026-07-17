from __future__ import annotations

import unittest
from collections import deque
from unittest.mock import patch

from astergard.characters.models import Character, CharacterStats
from astergard.combat.actions import DefenseOutcome, DefenseResolution, DefenseType
from astergard.combat.hit_locations import (
    ArmorCoverageOutcome,
    AttackType,
    BodyLocation,
    BodyLocationGroup,
    HitQuality,
    legacy_body_part_for_location,
    resolve_armor_coverage,
    resolve_hit_location,
)
from astergard.combat.manager import CombatManager
from astergard.combat.physical_damage import WoundSeverity, resolve_attack_physical_damage
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


def _failed_defense() -> DefenseOutcome:
    return DefenseOutcome(
        resolution=DefenseResolution.NONE,
        successful_defense=False,
        attempts=(),
        selected_defense=None,
        reason_code="NONE",
    )


class D53PhysicalDamageTests(unittest.TestCase):
    def test_hit_location_and_armor_coverage_are_consumed_once_and_snapshot_is_stable(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[10, 1], random_values=[0.0, 0.0, 0.0, 0.0]))
        attacker = Character("atakujacy", room_id=1)
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        attacker.skills.values["bron_jednoraczna"]["level"] = 20
        defender = Character("obronca", room_id=1)
        defender.skills.values["uniki"]["level"] = 0
        defender.skills.values["parowanie"]["level"] = 0
        defender.skills.values["tarcze"]["level"] = 0
        defender.equipment["korpus"] = _armor("light_armor", name="lekki pancerz")

        with patch("astergard.combat.manager.resolve_defense", return_value=_failed_defense()), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver, patch(
            "astergard.combat.manager.resolve_armor_coverage",
            wraps=resolve_armor_coverage,
        ) as armor_coverage_resolver, patch(
            "astergard.combat.manager.resolve_attack_physical_damage",
            wraps=resolve_attack_physical_damage,
        ) as physical_resolver:
            result = manager.attack(attacker, defender)

        self.assertEqual(hit_location_resolver.call_count, 1)
        self.assertEqual(armor_coverage_resolver.call_count, 1)
        self.assertEqual(physical_resolver.call_count, 1)
        self.assertIsNotNone(result.combat_outcome)
        self.assertIsNotNone(result.combat_event)
        self.assertIsNotNone(result.physical_outcome)
        self.assertIsNotNone(result.wound_outcome)
        assert result.combat_outcome is not None
        assert result.combat_event is not None
        assert result.physical_outcome is not None
        assert result.wound_outcome is not None
        assert result.combat_outcome.armor_coverage_outcome is not None
        self.assertEqual(result.combat_outcome.hit_location, result.combat_event.hit_location)
        self.assertEqual(result.combat_outcome.body_location, result.combat_outcome.armor_coverage_outcome.body_location)
        self.assertEqual(result.combat_outcome.body_location, result.physical_outcome.body_location)
        self.assertEqual(result.combat_outcome.body_location, result.wound_outcome.source_body_location)
        self.assertEqual(result.combat_event.hit_location, result.physical_outcome.body_location.value)
        self.assertEqual(result.wound_outcome.legacy_body_part, legacy_body_part_for_location(result.physical_outcome.body_location))

        original_layers = tuple(result.combat_outcome.armor_coverage_outcome.covering_layers)
        defender.equipment["korpus"] = None
        self.assertEqual(tuple(result.combat_outcome.armor_coverage_outcome.covering_layers), original_layers)
        self.assertEqual(tuple(result.physical_outcome.armor_layers), original_layers)

    def test_riposte_and_npc_share_the_same_physical_pipeline(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[10, 10, 10, 10], random_values=[0.0] * 20))
        attacker = Character("atakujacy", room_id=1)
        defender = Character("obronca", room_id=1)
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        attacker.skills.values["bron_jednoraczna"]["level"] = 20
        defender.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
        )
        defender.known_techniques = ("riposte",)
        defender.equipment["bron_glowna"] = _weapon("court_sabre", name="szabla", weapon_type="szabla", damage_type="cieta", base_damage=4)
        defender.skills.values["bron_jednoraczna"]["level"] = 100
        defender.skills.values["parowanie"]["level"] = 100
        manager.start_fight(attacker, defender)

        calls = {"count": 0}

        def _resolve_defense_side_effect(*args: object, **kwargs: object) -> DefenseOutcome:
            calls["count"] += 1
            if calls["count"] == 1:
                return DefenseOutcome(
                    resolution=DefenseResolution.PARRIED,
                    successful_defense=True,
                    attempts=(),
                    selected_defense=DefenseType.PARRY,
                    reason_code="PARRIED",
                )
            return _failed_defense()

        with patch("astergard.combat.manager.resolve_defense", side_effect=_resolve_defense_side_effect), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver, patch(
            "astergard.combat.manager.resolve_armor_coverage",
            wraps=resolve_armor_coverage,
        ) as armor_coverage_resolver, patch(
            "astergard.combat.manager.resolve_attack_physical_damage",
            wraps=resolve_attack_physical_damage,
        ) as physical_resolver:
            result = manager.attack(attacker, defender)

        self.assertEqual(hit_location_resolver.call_count, 2)
        self.assertEqual(armor_coverage_resolver.call_count, 2)
        self.assertEqual(physical_resolver.call_count, 2)
        self.assertIsNotNone(result.reaction_execution)
        assert result.reaction_execution is not None
        self.assertIsNotNone(result.reaction_execution.reaction_result)
        assert result.reaction_execution.reaction_result is not None
        self.assertIsNotNone(result.reaction_execution.reaction_result.physical_outcome)
        self.assertIsNotNone(result.reaction_execution.reaction_result.wound_outcome)
        assert result.reaction_execution.reaction_result.physical_outcome is not None
        assert result.reaction_execution.reaction_result.wound_outcome is not None
        assert result.reaction_execution.reaction_result.combat_outcome is not None
        assert result.reaction_execution.reaction_result.combat_event is not None
        self.assertEqual(
            result.reaction_execution.reaction_result.combat_outcome.hit_location,
            result.reaction_execution.reaction_result.combat_event.hit_location,
        )
        self.assertEqual(
            result.reaction_execution.reaction_result.physical_outcome.body_location,
            result.reaction_execution.reaction_result.wound_outcome.source_body_location,
        )

        npc = Character("wilk", room_id=1)
        npc.combat_identity = "npc:wolf"
        npc.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        with patch("astergard.combat.manager.resolve_defense", return_value=_failed_defense()), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as npc_hit_location_resolver, patch(
            "astergard.combat.manager.resolve_attack_physical_damage",
            wraps=resolve_attack_physical_damage,
        ) as npc_physical_resolver:
            npc_result = manager.attack(npc, defender)

        self.assertEqual(npc_hit_location_resolver.call_count, 1)
        self.assertEqual(npc_physical_resolver.call_count, 1)
        self.assertIsNotNone(npc_result.combat_outcome)
        self.assertIsNotNone(npc_result.physical_outcome)
        self.assertIsNotNone(npc_result.wound_outcome)
        assert npc_result.combat_outcome is not None
        assert npc_result.physical_outcome is not None
        assert npc_result.wound_outcome is not None
        assert npc_result.combat_event is not None
        self.assertEqual(npc_result.combat_outcome.hit_location, npc_result.combat_event.hit_location)
        self.assertEqual(npc_result.physical_outcome.body_location, npc_result.wound_outcome.source_body_location)

    def test_weapon_profiles_change_physical_channels_without_using_skill_as_raw_multiplier(self) -> None:
        attacker = Character("atakujacy", room_id=1)
        attacker.stats = CharacterStats(sila=12, zrecznosc=12, wytrzymalosc=12, percepcja=10, sila_woli=10, kondycja=120)
        defender = Character("cel", room_id=1)
        armor_coverage = ArmorCoverageOutcome(
            body_location=BodyLocation.CHEST,
            covering_layers=(),
            fully_unarmored=True,
            partial_coverage=False,
            total_coverage_indicator=0.0,
        )
        rapier = _weapon("duelist_rapier", name="rapier", weapon_type="szpada", damage_type="cieta", base_damage=4)
        hammer = _weapon("war_hammer", name="młot", weapon_type="młot", damage_type="obuchowa", base_damage=5)
        rapier_profile = resolve_weapon_profile(rapier)
        hammer_profile = resolve_weapon_profile(hammer)
        rapier_outcome, _ = resolve_attack_physical_damage(
            action_id="rapier",
            attacker=attacker,
            defender=defender,
            weapon=rapier,
            weapon_profile=rapier_profile,
            attack_type=AttackType.THRUST,
            hit_quality=HitQuality.CLEAN,
            body_location=BodyLocation.CHEST,
            body_location_group=BodyLocationGroup.TORSO_GROUP,
            armor_coverage=armor_coverage,
            style_damage=0.0,
            profession_damage=0.0,
        )
        hammer_outcome, _ = resolve_attack_physical_damage(
            action_id="hammer",
            attacker=attacker,
            defender=defender,
            weapon=hammer,
            weapon_profile=hammer_profile,
            attack_type=AttackType.BLUNT_STRIKE,
            hit_quality=HitQuality.CLEAN,
            body_location=BodyLocation.CHEST,
            body_location_group=BodyLocationGroup.TORSO_GROUP,
            armor_coverage=armor_coverage,
            style_damage=0.0,
            profession_damage=0.0,
        )
        self.assertGreater(hammer_outcome.effective_impact, rapier_outcome.effective_impact)
        self.assertGreater(rapier_outcome.effective_piercing, hammer_outcome.effective_piercing)
        self.assertEqual(rapier_outcome.body_location, BodyLocation.CHEST)
        self.assertEqual(hammer_outcome.body_location, BodyLocation.CHEST)
        self.assertIn(rapier_outcome.severity, {WoundSeverity.MINOR, WoundSeverity.MODERATE, WoundSeverity.SERIOUS, WoundSeverity.SEVERE, WoundSeverity.CRITICAL})


if __name__ == "__main__":
    unittest.main()

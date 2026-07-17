from __future__ import annotations

import unittest
from collections import deque
from unittest.mock import patch

from astergard.characters.models import Character
from astergard.combat.actions import CombatOutcomeType, DefenseOutcome, DefenseResolution, DefenseType
from astergard.combat.hit_locations import (
    BodyLocation,
    legacy_body_part_for_location,
    resolve_armor_coverage,
    resolve_hit_location,
)
from astergard.combat.manager import CombatManager
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


def _successful_defense(resolution: DefenseResolution, selected_defense: DefenseType | None = None) -> DefenseOutcome:
    return DefenseOutcome(
        resolution=resolution,
        successful_defense=True,
        attempts=(),
        selected_defense=selected_defense,
        reason_code=resolution.value,
    )


def _failed_defense() -> DefenseOutcome:
    return DefenseOutcome(
        resolution=DefenseResolution.NONE,
        successful_defense=False,
        attempts=(),
        selected_defense=None,
        reason_code="NONE",
    )


class D521AuthoritativeHitLocationTests(unittest.TestCase):
    def test_hit_resolver_runs_once_and_shared_location_is_used_everywhere(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[10, 1], random_values=[0.0, 0.0, 0.0, 0.0]))
        attacker = Character("atakujacy")
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        attacker.skills.values["bron_jednoraczna"]["level"] = 20
        defender = Character("obronca")
        defender.skills.values["uniki"]["level"] = 0
        defender.skills.values["parowanie"]["level"] = 0
        defender.skills.values["tarcze"]["level"] = 0
        defender.equipment["korpus"] = _armor("light_armor", name="lekki pancerz")

        with patch("astergard.combat.manager.resolve_defense", return_value=_failed_defense()), patch.object(CombatManager, "choose_body_part", wraps=manager.choose_body_part) as legacy_choice, patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver, patch(
            "astergard.combat.manager.resolve_armor_coverage",
            wraps=resolve_armor_coverage,
        ) as armor_coverage_resolver:
            result = manager.attack(attacker, defender)

        self.assertEqual(hit_location_resolver.call_count, 1)
        self.assertEqual(legacy_choice.call_count, 0)
        self.assertEqual(armor_coverage_resolver.call_count, 1)
        self.assertIsNotNone(result.combat_outcome)
        self.assertIsNotNone(result.combat_event)
        assert result.combat_outcome is not None
        assert result.combat_event is not None
        self.assertIsNotNone(result.combat_outcome.armor_coverage_outcome)
        assert result.combat_outcome.armor_coverage_outcome is not None
        self.assertIsNotNone(result.combat_outcome.body_location)
        assert result.combat_outcome.body_location is not None
        self.assertEqual(result.combat_outcome.hit_location, result.combat_event.hit_location)
        self.assertEqual(result.combat_outcome.body_location, result.combat_outcome.armor_coverage_outcome.body_location)
        self.assertEqual(result.body_part, result.combat_outcome.legacy_body_part)
        self.assertEqual(result.body_part, legacy_body_part_for_location(result.combat_outcome.body_location))
        self.assertIn(result.combat_outcome.result_type, {CombatOutcomeType.HIT, CombatOutcomeType.TARGET_DEFEATED})
        self.assertEqual(result.combat_outcome.hit_location, result.combat_outcome.body_location.value)
        self.assertEqual(result.combat_event.body_location, result.combat_outcome.body_location.value)

    def test_miss_and_defense_outcomes_do_not_resolve_hit_location(self) -> None:
        attacker = Character("atakujacy")
        defender = Character("obronca")
        manager = CombatManager(rng=ScriptedRng(randint_values=[1, 1], random_values=[0.0, 0.0]))

        attacker.die()
        with patch("astergard.combat.manager.resolve_hit_location", wraps=resolve_hit_location) as hit_location_resolver:
            outcome = manager.attack(attacker, defender)
        self.assertIsNotNone(outcome.combat_outcome)
        assert outcome.combat_outcome is not None
        self.assertEqual(outcome.combat_outcome.result_type, CombatOutcomeType.INVALID)
        self.assertEqual(hit_location_resolver.call_count, 0)

        attacker = Character("atakujacy")
        defender = Character("obronca")
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta")
        with patch("astergard.combat.manager.resolve_defense", return_value=_successful_defense(DefenseResolution.DODGED, DefenseType.DODGE)), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver:
            outcome = manager.attack(attacker, defender)
        self.assertIsNotNone(outcome.combat_outcome)
        assert outcome.combat_outcome is not None
        self.assertEqual(outcome.combat_outcome.result_type, CombatOutcomeType.DEFENDED)
        self.assertEqual(hit_location_resolver.call_count, 0)

        with patch("astergard.combat.manager.resolve_defense", return_value=_successful_defense(DefenseResolution.PARRIED, DefenseType.PARRY)), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver:
            outcome = manager.attack(attacker, defender)
        self.assertIsNotNone(outcome.combat_outcome)
        assert outcome.combat_outcome is not None
        self.assertEqual(outcome.combat_outcome.result_type, CombatOutcomeType.DEFENDED)
        self.assertEqual(hit_location_resolver.call_count, 0)

        with patch("astergard.combat.manager.resolve_defense", return_value=_successful_defense(DefenseResolution.BLOCKED, DefenseType.SHIELD_BLOCK)), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver:
            outcome = manager.attack(attacker, defender)
        self.assertIsNotNone(outcome.combat_outcome)
        assert outcome.combat_outcome is not None
        self.assertEqual(outcome.combat_outcome.result_type, CombatOutcomeType.DEFENDED)
        self.assertEqual(hit_location_resolver.call_count, 0)

    def test_legacy_adapter_is_deterministic_and_complete(self) -> None:
        seen = {legacy_body_part_for_location(location) for location in BodyLocation}
        self.assertTrue(seen.issubset({"glowa", "korpus", "lewa_reka", "prawa_reka", "lewa_noga", "prawa_noga"}))
        for location in BodyLocation:
            first = legacy_body_part_for_location(location)
            second = legacy_body_part_for_location(location)
            self.assertEqual(first, second)
            self.assertTrue(first)

    def test_riposte_and_npc_use_same_hit_location_path(self) -> None:
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
                return _successful_defense(DefenseResolution.PARRIED, DefenseType.PARRY)
            return _failed_defense()

        with patch("astergard.combat.manager.resolve_defense", side_effect=_resolve_defense_side_effect), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as hit_location_resolver, patch.object(CombatManager, "choose_body_part", wraps=manager.choose_body_part) as legacy_choice:
            result = manager.attack(attacker, defender)

        self.assertEqual(hit_location_resolver.call_count, 2)
        self.assertEqual(legacy_choice.call_count, 0)
        self.assertIsNotNone(result.reaction_execution)
        assert result.reaction_execution is not None
        reaction_result = result.reaction_execution.reaction_result
        self.assertIsNotNone(reaction_result)
        assert reaction_result is not None
        self.assertIsNotNone(reaction_result.combat_outcome)
        self.assertIsNotNone(reaction_result.combat_event)
        assert reaction_result.combat_outcome is not None
        assert reaction_result.combat_event is not None
        self.assertIsNotNone(reaction_result.combat_outcome.body_location)
        self.assertIsNotNone(reaction_result.combat_outcome.armor_coverage_outcome)
        assert reaction_result.combat_outcome.armor_coverage_outcome is not None
        assert reaction_result.combat_outcome.body_location is not None
        self.assertEqual(reaction_result.combat_outcome.hit_location, reaction_result.combat_event.hit_location)
        self.assertEqual(
            reaction_result.combat_outcome.legacy_body_part,
            legacy_body_part_for_location(reaction_result.combat_outcome.body_location),
        )
        self.assertEqual(reaction_result.combat_outcome.armor_coverage_outcome.body_location, reaction_result.combat_outcome.body_location)

        npc = Character("wilk", room_id=1)
        npc.combat_identity = "npc:wolf"
        npc.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        with patch("astergard.combat.manager.resolve_defense", return_value=_failed_defense()), patch(
            "astergard.combat.manager.resolve_hit_location",
            wraps=resolve_hit_location,
        ) as npc_hit_location_resolver:
            npc_result = manager.attack(npc, defender)
        self.assertIsNotNone(npc_result.combat_outcome)
        self.assertIsNotNone(npc_result.combat_event)
        assert npc_result.combat_outcome is not None
        assert npc_result.combat_event is not None
        self.assertEqual(npc_hit_location_resolver.call_count, 1)
        self.assertIsNotNone(npc_result.combat_outcome.body_location)
        assert npc_result.combat_outcome.body_location is not None
        self.assertEqual(npc_result.combat_outcome.hit_location, npc_result.combat_event.hit_location)
        self.assertEqual(
            npc_result.combat_outcome.legacy_body_part,
            legacy_body_part_for_location(npc_result.combat_outcome.body_location),
        )

    def test_partial_coverage_is_resolved_once_and_preserved(self) -> None:
        manager = CombatManager(rng=ScriptedRng(randint_values=[10, 1], random_values=[0.0, 0.0, 0.0, 0.0]))
        attacker = Character("atakujacy")
        attacker.equipment["bron_glowna"] = _weapon("garrison_short_sword", name="miecz", weapon_type="miecz", damage_type="cieta", base_damage=8)
        attacker.skills.values["bron_jednoraczna"]["level"] = 20
        defender = Character("obronca")
        defender.skills.values["uniki"]["level"] = 0
        defender.skills.values["parowanie"]["level"] = 0
        defender.skills.values["tarcze"]["level"] = 0
        defender.equipment["tarcza"] = _shield("small_shield", name="mała tarcza")

        with patch("astergard.combat.manager.resolve_defense", return_value=_failed_defense()), patch(
            "astergard.combat.manager.resolve_armor_coverage",
            wraps=resolve_armor_coverage,
        ) as armor_coverage_resolver:
            result = manager.attack(attacker, defender)

        self.assertEqual(armor_coverage_resolver.call_count, 1)
        self.assertIsNotNone(result.combat_outcome)
        self.assertIsNotNone(result.combat_event)
        assert result.combat_outcome is not None
        assert result.combat_event is not None
        self.assertIsNotNone(result.combat_outcome.armor_coverage_outcome)
        assert result.combat_outcome.armor_coverage_outcome is not None
        self.assertIsNotNone(result.combat_outcome.body_location)
        assert result.combat_outcome.body_location is not None
        self.assertEqual(result.combat_outcome.armor_coverage_outcome.body_location, result.combat_outcome.body_location)
        self.assertEqual(result.combat_event.body_location, result.combat_outcome.body_location.value)


if __name__ == "__main__":
    unittest.main()

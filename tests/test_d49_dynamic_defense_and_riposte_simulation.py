from __future__ import annotations

import unittest

from astergard.characters.models import Character
from astergard.combat.actions import CombatAction, CombatOutcome, CombatOutcomeType, DefenseAttempt, DefenseOutcome, DefenseResolution, DefenseType
from astergard.combat.d49_simulation import BUILD_PRESETS, simulate_single_attacks
from astergard.combat.reactions import CombatReactionExecutor, ReactionTriggerContext, build_reaction_user_profile, default_combat_reaction_catalog, find_available_reactions
from astergard.items.models import EQUIPMENT_SLOTS, EquipmentSet, dueling_blade
from astergard.rules.combat_specialization import CombatSpecializationLoadout
from astergard.testing import TestGameHarness


def _clear_equipment(character: Character) -> None:
    character.equipment = EquipmentSet.default()
    for slot in EQUIPMENT_SLOTS:
        character.equipment[slot] = None


def _parried_outcome(action: CombatAction) -> CombatOutcome:
    return CombatOutcome(
        action_id=action.action_id,
        actor_id=action.actor_id,
        target_id=action.target_id,
        result_type=CombatOutcomeType.DEFENDED,
        hit=False,
        defense_result=DefenseResolution.PARRIED,
        defense_outcome=DefenseOutcome(
            resolution=DefenseResolution.PARRIED,
            successful_defense=True,
            attempts=(
                DefenseAttempt(
                    defense_type=DefenseType.PARRY,
                    available=True,
                    attempted=True,
                    success=True,
                    reason_code="PARRIED",
                ),
            ),
            selected_defense=DefenseType.PARRY,
            reason_code="PARRIED",
        ),
        damage=0,
        target_defeated=False,
        combat_ended=False,
        reason_code="DEFENDED",
    )


class D49DynamicDefenseAndRiposteSimulationTests(unittest.TestCase):
    def test_single_attack_simulation_is_deterministic_for_same_seed(self) -> None:
        preset = next(preset for preset in BUILD_PRESETS if preset.key == "D")
        first = simulate_single_attacks(preset, 8)
        second = simulate_single_attacks(preset, 8)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_executor_revalidates_runtime_state_before_riposte(self) -> None:
        with TestGameHarness() as harness:
            harness.require_server()
            attacker = harness.create_character("d49_attacker", room_id=101)
            reactor = harness.create_character("d49_reactor", room_id=101)

            _clear_equipment(reactor)
            reactor.combat_specializations = CombatSpecializationLoadout(
                weapon_specializations=("miecze",),
                defense_specializations=("parowanie",),
            )
            reactor.known_techniques = ("riposte",)
            reactor.skills.values["parowanie"]["level"] = 12
            reactor.skills.values["bron_jednoraczna"]["level"] = 12
            reactor.in_combat = True
            reactor.is_alive = True
            reactor.equipment["bron_glowna"] = dueling_blade()

            source_action = CombatAction(action_id="source-action", actor_id=attacker.username, target_id=reactor.username)
            source_outcome = _parried_outcome(source_action)
            catalog = default_combat_reaction_catalog()
            cases = (
                ("skill", 11, None, False, "SKILL_LEVEL_TOO_LOW"),
                ("location", None, 102, False, "NOT_IN_SAME_LOCATION"),
                ("weapon", None, None, True, "ACTIVE_WEAPON_MISSING"),
            )
            for label, skill_level, room_id, clear_weapon, expected_reason in cases:
                with self.subTest(case=label):
                    _clear_equipment(reactor)
                    reactor.equipment["bron_glowna"] = dueling_blade()
                    reactor.room_id = 101
                    reactor.skills.values["parowanie"]["level"] = 12
                    reactor.in_combat = True
                    discovery = find_available_reactions(
                        ReactionTriggerContext(
                            source_action=source_action,
                            source_outcome=source_outcome,
                            reactor_profile=build_reaction_user_profile(reactor),
                            opponent_profile=build_reaction_user_profile(attacker),
                        ),
                        catalog,
                    )
                    self.assertTrue(discovery.available_reactions)
                    executor = CombatReactionExecutor(catalog)
                    if skill_level is not None:
                        reactor.skills.values["parowanie"]["level"] = skill_level
                    if room_id is not None:
                        reactor.room_id = room_id
                    if clear_weapon:
                        reactor.equipment["bron_glowna"] = None
                    result = executor.execute_reaction(
                        discovery,
                        source_action,
                        source_outcome,
                        reactor,
                        attacker,
                        lambda *args, **kwargs: None,
                    )
                    self.assertFalse(result.executed)
                    self.assertEqual(result.reason_code, expected_reason)

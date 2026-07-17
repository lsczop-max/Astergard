from __future__ import annotations

import dataclasses
import json
import tempfile
import unittest
from collections import deque
from pathlib import Path

from astergard.combat.actions import (
    CombatAction,
    CombatActionType,
    CombatOutcome,
    CombatOutcomeType,
    DefenseAttempt,
    DefenseOutcome,
    DefenseResolution,
    DefenseType,
)
from astergard.combat.reactions import (
    CombatReactionConfigurationError,
    CombatReactionType,
    ReactionTriggerContext,
    ReactionTriggerType,
    REACTION_POLICY,
    build_reaction_user_profile,
    default_combat_reaction_catalog,
    evaluate_reaction,
    find_available_reactions,
    load_combat_reaction_catalog,
    reaction_trigger_types_from_outcome,
)
from astergard.characters.models import Character
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


def _clear_combat_slots(character: Character) -> None:
    for slot in ("bron_glowna", "bron_pomocnicza", "tarcza", "prawa_reka", "lewa_reka"):
        character.equipment[slot] = None


def _parry_weapon(profile_id: str = "garrison_short_sword", *, vnum: str = "parry_weapon", weapon_type: str = "miecz") -> Item:
    return Item(
        "broń profilowana",
        "",
        1.0,
        10,
        vnum,
        item_type="weapon",
        slot="bron_glowna",
        weapon_profile_id=profile_id,
        weapon_type=weapon_type,
        parry_bonus=80,
    )


def _parry_outcome(action: CombatAction) -> CombatOutcome:
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


class D46CombatReactionsFrameworkTests(unittest.TestCase):
    def test_trigger_mapping_distinguishes_parry_dodge_block_miss_and_failed_parry(self) -> None:
        action = CombatAction(action_id="a1", actor_id="hero", target_id="wolf", action_type=CombatActionType.BASIC_ATTACK)

        self.assertEqual(
            reaction_trigger_types_from_outcome(_parry_outcome(action)),
            (ReactionTriggerType.SUCCESSFUL_PARRY,),
        )

        dodge_outcome = CombatOutcome(
            action_id="a2",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.DEFENDED,
            hit=False,
            defense_result=DefenseResolution.DODGED,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.DODGED,
                successful_defense=True,
                attempts=(),
                selected_defense=DefenseType.DODGE,
                reason_code="DODGED",
            ),
            damage=0,
            target_defeated=False,
            combat_ended=False,
            reason_code="DODGED",
        )
        block_outcome = CombatOutcome(
            action_id="a3",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.DEFENDED,
            hit=False,
            defense_result=DefenseResolution.BLOCKED,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.BLOCKED,
                successful_defense=True,
                attempts=(),
                selected_defense=DefenseType.SHIELD_BLOCK,
                reason_code="BLOCKED",
            ),
            damage=0,
            target_defeated=False,
            combat_ended=False,
            reason_code="BLOCKED",
        )
        miss_outcome = CombatOutcome(
            action_id="a4",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.MISS,
            hit=False,
            defense_result=DefenseResolution.NONE,
            damage=0,
            target_defeated=False,
            combat_ended=False,
            reason_code="MISS",
        )
        failed_parry = CombatOutcome(
            action_id="a5",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.HIT,
            hit=True,
            defense_result=DefenseResolution.NONE,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.NONE,
                successful_defense=False,
                attempts=(
                    DefenseAttempt(
                        defense_type=DefenseType.PARRY,
                        available=True,
                        attempted=True,
                        success=False,
                        reason_code="FAILED",
                    ),
                ),
                selected_defense=None,
                reason_code="FAILED",
            ),
            damage=1,
            target_defeated=False,
            combat_ended=False,
            reason_code="HIT",
        )

        self.assertEqual(reaction_trigger_types_from_outcome(dodge_outcome), (ReactionTriggerType.SUCCESSFUL_DODGE,))
        self.assertEqual(reaction_trigger_types_from_outcome(block_outcome), (ReactionTriggerType.SUCCESSFUL_SHIELD_BLOCK,))
        self.assertEqual(reaction_trigger_types_from_outcome(miss_outcome), (ReactionTriggerType.ATTACK_MISSED,))
        self.assertEqual(reaction_trigger_types_from_outcome(failed_parry), (ReactionTriggerType.ACTOR_HIT,))

    def test_catalog_loader_validates_data_and_is_immutable(self) -> None:
        catalog = default_combat_reaction_catalog()
        self.assertGreaterEqual(len(catalog.definitions), 1)
        self.assertEqual(catalog.by_id("riposte_reaction").reaction_type, CombatReactionType.RIPOSTE)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            catalog.definitions = ()  # type: ignore[misc]
        with self.assertRaises(TypeError):
            catalog.definitions_by_id["x"] = catalog.definitions[0]  # type: ignore[index]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid_reactions.json"
            base = {
                "id": "riposte_reaction",
                "name": "Riposta",
                "reaction_type": "RIPOSTE",
                "trigger_types": ["SUCCESSFUL_PARRY"],
                "required_technique_id": "riposte",
                "required_defense_style": "PARRY",
                "required_weapon_tags": ["parry_capable", "agile"],
                "required_weapon_specializations": [],
                "enabled": True,
                "priority": 100,
                "consumes_reaction_window": True,
            }

            def write(payload: list[dict[str, object]]) -> None:
                path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            write([{**base, "reaction_type": "UNKNOWN"}])
            with self.assertRaises(CombatReactionConfigurationError):
                load_combat_reaction_catalog(path)

            write([{**base, "trigger_types": ["BROKEN"]}])
            with self.assertRaises(CombatReactionConfigurationError):
                load_combat_reaction_catalog(path)

            write([{**base, "required_defense_style": "BROKEN"}])
            with self.assertRaises(CombatReactionConfigurationError):
                load_combat_reaction_catalog(path)

            write([{**base, "required_weapon_tags": ["parry_capable", "BROKEN"]}])
            with self.assertRaises(CombatReactionConfigurationError):
                load_combat_reaction_catalog(path)

            write([{**base, "required_technique_id": "missing_technique"}])
            with self.assertRaises(CombatReactionConfigurationError):
                load_combat_reaction_catalog(path)

            write([{**base}, {**base}])
            with self.assertRaises(CombatReactionConfigurationError):
                load_combat_reaction_catalog(path)

    def test_riposte_is_available_only_with_matching_parry_setup(self) -> None:
        with TestGameHarness() as harness:
            hero = harness.create_character("reacter", room_id=101)
            attacker = harness.create_character("aggressor", room_id=101)
            hero.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
            hero.known_techniques = ("riposte",)
            hero.active_defense_style = ActiveDefenseStyle.PARRY.value
            hero.in_combat = True
            hero.is_alive = True
            attacker.in_combat = True
            attacker.is_alive = True
            hero.stats.zrecznosc = 20
            hero.skills.values["parowanie"]["level"] = 20

            action = CombatAction(action_id="action-1", actor_id=attacker.username, target_id=hero.username, action_type=CombatActionType.BASIC_ATTACK)
            outcome = _parry_outcome(action)
            hero.equipment["bron_glowna"] = _parry_weapon("garrison_short_sword")

            context = ReactionTriggerContext(
                source_action=action,
                source_outcome=outcome,
                reactor_profile=build_reaction_user_profile(hero),
                opponent_profile=build_reaction_user_profile(attacker),
            )
            discovery = find_available_reactions(context, default_combat_reaction_catalog())

            self.assertEqual(len(discovery.available_reactions), 1)
            reaction = discovery.available_reactions[0]
            self.assertEqual(reaction.reaction_type, CombatReactionType.RIPOSTE)
            self.assertEqual(reaction.trigger_type, ReactionTriggerType.SUCCESSFUL_PARRY)
            self.assertEqual(reaction.technique_id, "riposte")
            self.assertTrue(reaction.automatic)
            self.assertEqual(discovery.reaction_window.source_action_id, action.action_id)
            self.assertEqual(discovery.reaction_window.reactor_id, hero.username)
            self.assertEqual(discovery.reaction_window.available_reaction_ids, (reaction.reaction_id,))
            with self.assertRaises(dataclasses.FrozenInstanceError):
                reaction.automatic = True  # type: ignore[misc]

    def test_riposte_is_denied_when_conditions_do_not_match(self) -> None:
        with TestGameHarness() as harness:
            hero = harness.create_character("reacter_denied", room_id=101)
            attacker = harness.create_character("aggressor_denied", room_id=101)
            hero.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
            hero.known_techniques = ()
            hero.active_defense_style = ActiveDefenseStyle.PARRY.value
            hero.in_combat = True
            hero.is_alive = True
            attacker.in_combat = True
            attacker.is_alive = True
            action = CombatAction(action_id="action-2", actor_id=attacker.username, target_id=hero.username, action_type=CombatActionType.BASIC_ATTACK)
            outcome = _parry_outcome(action)
            riposte = default_combat_reaction_catalog().by_id("riposte_reaction")

            cases = [
                ("TECHNIQUE_NOT_KNOWN", ()),
            ]
            for expected_reason, known_techniques in cases:
                with self.subTest(expected_reason=expected_reason):
                    hero.known_techniques = known_techniques
                    hero.active_defense_style = ActiveDefenseStyle.PARRY.value
                    hero.equipment["bron_glowna"] = _parry_weapon("garrison_short_sword")
                    profile = build_reaction_user_profile(hero)
                    result = evaluate_reaction(
                        ReactionTriggerContext(
                            source_action=action,
                            source_outcome=outcome,
                            reactor_profile=profile,
                            opponent_profile=build_reaction_user_profile(attacker),
                        ),
                        riposte,
                    )
                    self.assertFalse(result.allowed)
                    self.assertEqual(result.reason_code, expected_reason)

            for expected_reason, weapon in [
                ("INCOMPATIBLE_WEAPON_TAGS", Item("młot", "", 1.0, 10, "war_hammer", item_type="weapon", slot="bron_glowna", weapon_profile_id="war_hammer", weapon_type="młot")),
                ("INCOMPATIBLE_WEAPON_TAGS", Item("buława", "", 1.0, 10, "war_mace", item_type="weapon", slot="bron_glowna", weapon_profile_id="war_mace", weapon_type="buława")),
                ("INCOMPATIBLE_WEAPON_TAGS", Item("cep", "", 1.0, 10, "war_flail", item_type="weapon", slot="bron_glowna", weapon_profile_id="war_flail", weapon_type="cep")),
                ("INCOMPATIBLE_WEAPON_TAGS", Item("legacy sword", "", 1.0, 10, "legacy_sword", item_type="weapon", slot="bron_glowna", weapon_type="miecz")),
            ]:
                with self.subTest(weapon=weapon.vnum):
                    hero.known_techniques = ("riposte",)
                    hero.active_defense_style = ActiveDefenseStyle.PARRY.value
                    hero.equipment["bron_glowna"] = weapon
                    hero.in_combat = True
                    hero.is_alive = True
                    profile = build_reaction_user_profile(hero)
                    result = evaluate_reaction(
                        ReactionTriggerContext(
                            source_action=action,
                            source_outcome=outcome,
                            reactor_profile=profile,
                            opponent_profile=build_reaction_user_profile(attacker),
                        ),
                        riposte,
                    )
                    self.assertFalse(result.allowed)
                    self.assertEqual(result.reason_code, expected_reason)

            hero.known_techniques = ("riposte",)
            hero.active_defense_style = ActiveDefenseStyle.PARRY.value
            hero.equipment["bron_glowna"] = _parry_weapon("garrison_short_sword")
            hero.is_alive = False
            profile = build_reaction_user_profile(hero)
            result = evaluate_reaction(
                ReactionTriggerContext(
                    source_action=action,
                    source_outcome=outcome,
                    reactor_profile=profile,
                    opponent_profile=build_reaction_user_profile(attacker),
                ),
                riposte,
            )
            self.assertFalse(result.allowed)
            self.assertEqual(result.reason_code, "REACTOR_DEAD")

    def test_reaction_window_and_depth_limit_are_explicit(self) -> None:
        with TestGameHarness() as harness:
            hero = harness.create_character("window_hero", room_id=101)
            attacker = harness.create_character("window_attacker", room_id=101)
            hero.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
            hero.known_techniques = ("riposte",)
            hero.active_defense_style = ActiveDefenseStyle.PARRY.value
            hero.in_combat = True
            hero.is_alive = True
            hero.equipment["bron_glowna"] = _parry_weapon("garrison_short_sword")
            action = CombatAction(action_id="action-3", actor_id=attacker.username, target_id=hero.username, action_type=CombatActionType.BASIC_ATTACK)
            outcome = _parry_outcome(action)

            open_discovery = find_available_reactions(
                ReactionTriggerContext(
                    source_action=action,
                    source_outcome=outcome,
                    reactor_profile=build_reaction_user_profile(hero),
                    opponent_profile=build_reaction_user_profile(attacker),
                    reaction_depth=0,
                ),
                default_combat_reaction_catalog(),
            )
            self.assertFalse(open_discovery.reaction_window.consumed)
            self.assertEqual(open_discovery.reaction_window.available_reaction_ids, tuple(reaction.reaction_id for reaction in open_discovery.available_reactions))

            closed_discovery = find_available_reactions(
                ReactionTriggerContext(
                    source_action=action,
                    source_outcome=outcome,
                    reactor_profile=build_reaction_user_profile(hero),
                    opponent_profile=build_reaction_user_profile(attacker),
                    reaction_depth=REACTION_POLICY.max_reaction_depth,
                ),
                default_combat_reaction_catalog(),
            )
            self.assertTrue(closed_discovery.reaction_window.consumed)
            self.assertFalse(closed_discovery.available_reactions)

    def test_manager_attaches_reaction_discovery_without_changing_primary_attack(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("reaction_attacker", room_id=101)
            defender = harness.create_character("reaction_defender", room_id=101)
            attacker.inventory.clear()
            defender.inventory.clear()
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
            defender.known_techniques = ("riposte",)
            defender.active_defense_style = ActiveDefenseStyle.PARRY.value
            defender.in_combat = True
            defender.equipment["bron_glowna"] = _parry_weapon("garrison_short_sword")
            defender.skills.values["parowanie"]["level"] = 20
            attacker.equipment["bron_glowna"] = Item(
                "miecz atakującego",
                "",
                1.0,
                10,
                "attacker_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_profile_id="garrison_short_sword",
                weapon_type="miecz",
                base_damage=6,
            )
            attacker.skills.values["bron_jednoraczna"]["level"] = 20
            attacker.in_combat = True
            server.combat.rng = ScriptedRng(randint_values=[20, 1, 1, 1, 1, 1], random_values=[1.0, 1.0, 1.0])

            result = server.combat.attack(attacker, defender)

            self.assertIsNotNone(result.combat_outcome)
            self.assertIsNotNone(result.reaction_discovery)
            combat_outcome = result.combat_outcome
            reaction_discovery = result.reaction_discovery
            assert combat_outcome is not None
            assert reaction_discovery is not None
            self.assertEqual(combat_outcome.result_type, CombatOutcomeType.DEFENDED)
            self.assertEqual(reaction_discovery.available_reactions[0].reaction_type, CombatReactionType.RIPOSTE)
            self.assertEqual(result.effective_damage, 0)
            self.assertFalse(result.defender_dead)
            self.assertEqual(combat_outcome.damage, 0)
            self.assertIsNotNone(combat_outcome.defense_outcome)
            assert combat_outcome.defense_outcome is not None
            self.assertEqual(combat_outcome.defense_outcome.resolution, DefenseResolution.PARRIED)


if __name__ == "__main__":
    unittest.main()

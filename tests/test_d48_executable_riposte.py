from __future__ import annotations

import unittest
from collections import deque
from types import SimpleNamespace
from unittest.mock import patch

from astergard.characters.models import Character
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
    CombatReactionExecutor,
    ReactionTriggerContext,
    build_reaction_user_profile,
    default_combat_reaction_catalog,
    evaluate_reaction,
    find_available_reactions,
)
from astergard.engine.events import DomainEventType
from astergard.items.models import EQUIPMENT_SLOTS, EquipmentSet, Item, dueling_blade
from astergard.rules.combat_specialization import CombatSpecializationLoadout
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


def _clear_equipment(character: Character) -> None:
    character.equipment = EquipmentSet.default()
    for slot in EQUIPMENT_SLOTS:
        character.equipment[slot] = None


def _configure_riposte_defender(character: Character) -> None:
    _clear_equipment(character)
    character.combat_specializations = CombatSpecializationLoadout(
        weapon_specializations=("szable",),
        defense_specializations=("parowanie",),
    )
    character.known_techniques = ("riposte",)
    character.skills.values["parowanie"]["level"] = 12
    character.skills.values["bron_jednoraczna"]["level"] = 12
    character.skills.values["uniki"]["level"] = 0
    character.equipment["bron_glowna"] = dueling_blade()


def _configure_riposte_attacker(character: Character) -> None:
    _clear_equipment(character)
    character.skills.values["bron_jednoraczna"]["level"] = 1
    character.skills.values["uniki"]["level"] = 0


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


def _dodge_outcome(action: CombatAction) -> CombatOutcome:
    return CombatOutcome(
        action_id=action.action_id,
        actor_id=action.actor_id,
        target_id=action.target_id,
        result_type=CombatOutcomeType.DEFENDED,
        hit=False,
        defense_result=DefenseResolution.DODGED,
        defense_outcome=DefenseOutcome(
            resolution=DefenseResolution.DODGED,
            successful_defense=True,
            attempts=(
                DefenseAttempt(
                    defense_type=DefenseType.DODGE,
                    available=True,
                    attempted=True,
                    success=True,
                    reason_code="DODGED",
                ),
            ),
            selected_defense=DefenseType.DODGE,
            reason_code="DODGED",
        ),
        damage=0,
        target_defeated=False,
        combat_ended=False,
        reason_code="DODGED",
    )


def _blocked_outcome(action: CombatAction) -> CombatOutcome:
    return CombatOutcome(
        action_id=action.action_id,
        actor_id=action.actor_id,
        target_id=action.target_id,
        result_type=CombatOutcomeType.DEFENDED,
        hit=False,
        defense_result=DefenseResolution.BLOCKED,
        defense_outcome=DefenseOutcome(
            resolution=DefenseResolution.BLOCKED,
            successful_defense=True,
            attempts=(
                DefenseAttempt(
                    defense_type=DefenseType.SHIELD_BLOCK,
                    available=True,
                    attempted=True,
                    success=True,
                    reason_code="BLOCKED",
                ),
            ),
            selected_defense=DefenseType.SHIELD_BLOCK,
            reason_code="BLOCKED",
        ),
        damage=0,
        target_defeated=False,
        combat_ended=False,
        reason_code="BLOCKED",
    )


class D48ExecutableRiposteTests(unittest.IsolatedAsyncioTestCase):
    def test_reaction_discovery_only_appears_after_successful_parry(self) -> None:
        attacker = Character("atakujacy")
        defender = Character("obronca")
        defender.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze",),
            defense_specializations=("parowanie",),
        )
        defender.known_techniques = ("riposte",)
        defender.skills.values["parowanie"]["level"] = 12
        defender.skills.values["bron_jednoraczna"]["level"] = 12
        _clear_equipment(defender)
        defender.equipment["bron_glowna"] = dueling_blade()
        defender.in_combat = True
        defender.is_alive = True

        source_action = CombatAction(action_id="action-1", actor_id=attacker.username, target_id=defender.username)
        catalog = default_combat_reaction_catalog()

        for outcome in (_dodge_outcome(source_action), _blocked_outcome(source_action), CombatOutcome(
            action_id=source_action.action_id,
            actor_id=source_action.actor_id,
            target_id=source_action.target_id,
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
        )):
            with self.subTest(result=outcome.result_type.value):
                discovery = find_available_reactions(
                    ReactionTriggerContext(
                        source_action=source_action,
                        source_outcome=outcome,
                        reactor_profile=build_reaction_user_profile(defender),
                        opponent_profile=build_reaction_user_profile(attacker),
                    ),
                    catalog,
                )
                self.assertFalse(discovery.available_reactions)

    def test_reaction_requires_skill_and_supported_weapon_profile(self) -> None:
        attacker = Character("atakujacy")
        reactor = Character("reaktor")
        reactor.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=("miecze", "szable", "sztylety"),
            defense_specializations=("parowanie",),
        )
        reactor.known_techniques = ("riposte",)
        reactor.skills.values["parowanie"]["level"] = 12
        reactor.skills.values["bron_jednoraczna"]["level"] = 12
        reactor.in_combat = True
        reactor.is_alive = True

        source_action = CombatAction(action_id="action-2", actor_id=attacker.username, target_id=reactor.username)
        source_outcome = _parried_outcome(source_action)
        catalog = default_combat_reaction_catalog()

        cases = [
            ("garrison_short_sword", "miecz", True),
            ("court_sabre", "szpada", True),
            ("duelist_dagger", "sztylet", True),
            ("war_hammer", "młot", False),
            ("war_mace", "buława", False),
            ("war_flail", "cep", False),
            ("legacy_weapon", "miecz", False),
        ]

        for profile_id, weapon_type, expected in cases:
            with self.subTest(profile_id=profile_id):
                _clear_equipment(reactor)
                reactor.equipment["bron_glowna"] = Item(
                    f"broń {profile_id}",
                    "",
                    1.0,
                    10,
                    profile_id,
                    item_type="weapon",
                    slot="bron_glowna",
                    weapon_type=weapon_type,
                    parry_bonus=50,
                    weapon_profile_id=None if profile_id == "legacy_weapon" else profile_id,
                )
                discovery = find_available_reactions(
                    ReactionTriggerContext(
                        source_action=source_action,
                        source_outcome=source_outcome,
                        reactor_profile=build_reaction_user_profile(reactor),
                        opponent_profile=build_reaction_user_profile(attacker),
                    ),
                    catalog,
                )
                allowed = bool(discovery.available_reactions)
                self.assertEqual(allowed, expected)
                validation = evaluate_reaction(
                    ReactionTriggerContext(
                        source_action=source_action,
                        source_outcome=source_outcome,
                        reactor_profile=build_reaction_user_profile(reactor),
                        opponent_profile=build_reaction_user_profile(attacker),
                    ),
                    catalog.by_id("riposte_reaction"),
                )
                self.assertEqual(validation.allowed, expected)

    def test_reaction_window_is_consumed_and_blocks_second_execution(self) -> None:
        attacker = Character("atakujacy")
        reactor = Character("reaktor")
        _configure_riposte_defender(reactor)
        reactor.in_combat = True
        source_action = CombatAction(action_id="action-3", actor_id=attacker.username, target_id=reactor.username)
        source_outcome = _parried_outcome(source_action)
        catalog = default_combat_reaction_catalog()
        executor = CombatReactionExecutor(catalog)
        discovery = find_available_reactions(
            ReactionTriggerContext(
                source_action=source_action,
                source_outcome=source_outcome,
                reactor_profile=build_reaction_user_profile(reactor),
                opponent_profile=build_reaction_user_profile(attacker),
            ),
            catalog,
        )
        dummy_result = SimpleNamespace(combat_outcome=source_outcome)

        first = executor.execute_reaction(
            discovery,
            source_action,
            source_outcome,
            reactor,
            attacker,
            lambda reaction_action, reactor_character, target_character: dummy_result,
        )
        second = executor.execute_reaction(
            discovery,
            source_action,
            source_outcome,
            reactor,
            attacker,
            lambda reaction_action, reactor_character, target_character: dummy_result,
        )

        self.assertTrue(first.executed)
        self.assertTrue(first.window_consumed)
        self.assertFalse(second.executed)
        self.assertEqual(second.reason_code, "REACTION_WINDOW_CONSUMED")

    async def test_kill_command_executes_riposte_with_separate_events_and_stops_followup_tick(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("riposte_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")

            _clear_equipment(hero)
            hero.skills.values["bron_jednoraczna"]["level"] = 1
            hero.skills.values["uniki"]["level"] = 0
            hero.wounds["korpus"] = 3

            _clear_equipment(npc.character)
            _configure_riposte_defender(npc.character)
            npc.character.skills.values["uniki"]["level"] = 0
            npc.character.wounds["korpus"] = 0

            server.combat.rng = ScriptedRng(randint_values=[1, 1, 20, 20, 1, 20], random_values=[1.0])

            with patch("astergard.combat.manager.legacy_body_part_for_location", return_value="korpus"):
                transcript = await harness.execute(hero, f"zabij {npc.name}")

            attack_events = [event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED]
            self.assertEqual(len(attack_events), 2)
            primary, riposte = attack_events
            self.assertEqual(primary.payload["action_type"], CombatActionType.BASIC_ATTACK.value)
            self.assertEqual(riposte.payload["action_type"], CombatActionType.REACTION.value)
            self.assertEqual(riposte.payload["parent_action_id"], primary.payload["action_id"])
            self.assertEqual(riposte.payload["technique_id"], "riposte")
            self.assertTrue(riposte.payload["reaction_id"])
            self.assertEqual(riposte.payload["reaction_depth"], 1)
            self.assertFalse(hero.is_alive)
            self.assertFalse(server.combat.has_fight(hero.username, npc.character.combat_identity or npc.character.username))
            self.assertIn("ripost", transcript.output.lower())

            before_tick = len([event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED])
            harness.tick_once()
            after_tick = len([event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED])
            self.assertEqual(before_tick, after_tick)

from __future__ import annotations

import asyncio
import dataclasses
import unittest
from collections import deque

from astergard.combat.actions import (
    CombatOutcome,
    CombatOutcomeType,
    DefenseAttempt,
    DefenseOutcome,
    DefenseResolution,
    DefenseType,
)
from astergard.combat.defense import DefenseContext, resolve_defense
from astergard.combat.events import CombatEvent
from astergard.characters.models import Character
from astergard.combat.narration import CombatNarrator
from astergard.engine.events import DomainEventType
from astergard.items.models import Item
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


class D43ExplicitDefenseResolutionTests(unittest.TestCase):
    def _clear_combat_slots(self, character: Character) -> None:
        combatant = character
        for slot in ("bron_glowna", "bron_pomocnicza", "prawa_reka", "lewa_reka", "tarcza"):
            combatant.equipment[slot] = None

    def test_defense_models_are_immutable_and_serializable(self) -> None:
        attempt = DefenseAttempt(
            defense_type=DefenseType.PARRY,
            available=True,
            attempted=True,
            success=False,
            chance=12,
            roll=9,
            reason_code="FAILED",
        )
        outcome = DefenseOutcome(
            resolution=DefenseResolution.NONE,
            successful_defense=False,
            attempts=(attempt,),
            selected_defense=None,
            reason_code="NONE",
        )

        payload = outcome.to_dict()
        restored = DefenseOutcome.from_dict(payload)

        self.assertEqual(restored.resolution, DefenseResolution.NONE)
        self.assertEqual(restored.attempts[0].defense_type, DefenseType.PARRY)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            attempt.success = True  # type: ignore[misc]

    def test_resolve_defense_reports_dodge_block_parry_and_unavailable_attempts(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("defense_attacker", room_id=101)
            defender = next(npc.character for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            self._clear_combat_slots(defender)

            dodge = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=1,
                    dodge_score=50,
                    rng=ScriptedRng(),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(dodge.resolution, DefenseResolution.DODGED)
            self.assertTrue(dodge.successful_defense)
            self.assertEqual(len(dodge.attempts), 1)
            self.assertTrue(dodge.attempts[0].available)
            self.assertTrue(dodge.attempts[0].attempted)
            self.assertTrue(dodge.attempts[0].success)

            shield = Item(
                "tarcza testowa",
                "Tarcza testowa.",
                3.0,
                10,
                "test_shield",
                item_type="shield",
                slot="tarcza",
                shield_block=80,
            )
            defender.inventory.clear()
            self._clear_combat_slots(defender)
            defender.equipment["tarcza"] = shield
            block = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(block.resolution, DefenseResolution.BLOCKED)
            self.assertTrue(block.successful_defense)
            self.assertEqual([attempt.defense_type for attempt in block.attempts], [DefenseType.SHIELD_BLOCK])
            self.assertTrue(block.attempts[0].available)
            self.assertTrue(block.attempts[0].attempted)
            self.assertTrue(block.attempts[0].success)

            weapon = Item(
                "miecz testowy",
                "Miecz testowy.",
                1.0,
                10,
                "test_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_type="miecz",
                parry_bonus=80,
            )
            self._clear_combat_slots(defender)
            defender.equipment["bron_glowna"] = weapon
            parry = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(parry.resolution, DefenseResolution.PARRIED)
            self.assertTrue(parry.successful_defense)
            self.assertEqual([attempt.defense_type for attempt in parry.attempts], [DefenseType.PARRY])
            self.assertTrue(parry.attempts[0].available)
            self.assertTrue(parry.attempts[0].attempted)
            self.assertTrue(parry.attempts[0].success)

            defender.inventory.append(Item("zapasowa tarcza", "Nieaktywna.", 2.0, 1, "backup_shield", item_type="shield", slot="tarcza", shield_block=80))
            self._clear_combat_slots(defender)
            unavailable = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(unavailable.resolution, DefenseResolution.DODGED)
            self.assertTrue(unavailable.successful_defense)
            self.assertEqual([attempt.defense_type for attempt in unavailable.attempts], [DefenseType.DODGE])
            self.assertEqual([attempt.available for attempt in unavailable.attempts], [True])
            self.assertEqual([attempt.attempted for attempt in unavailable.attempts], [True])

    def test_attack_populates_explicit_defense_outcome(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("explicit_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            self._clear_combat_slots(npc.character)
            hero.equipment["bron_glowna"] = Item(
                "miecz testowy",
                "Miecz testowy.",
                1.0,
                10,
                "explicit_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_type="miecz",
                base_damage=7,
            )
            hero.skills.values["bron_jednoraczna"]["level"] = 20
            npc.character.inventory.clear()
            self._clear_combat_slots(npc.character)
            server.combat.rng = ScriptedRng(randint_values=[20, 1, 1], random_values=[1.0, 1.0, 1.0])

            result = server.combat.attack(hero, npc.character)

            self.assertIsNotNone(result.combat_outcome)
            assert result.combat_outcome is not None
            self.assertIsNotNone(result.combat_outcome.defense_outcome)
            assert result.combat_outcome.defense_outcome is not None
            self.assertEqual(result.combat_outcome.defense_outcome.resolution, DefenseResolution.NONE)
            self.assertEqual(result.combat_outcome.defense_result, DefenseResolution.NONE)
            self.assertFalse(result.combat_outcome.defense_outcome.successful_defense)
            self.assertEqual([attempt.defense_type for attempt in result.combat_outcome.defense_outcome.attempts], [DefenseType.DODGE])
            self.assertTrue(result.hit)
            self.assertIn(result.combat_outcome.result_type, {CombatOutcomeType.HIT, CombatOutcomeType.TARGET_DEFEATED})
            self.assertEqual(result.effective_damage, result.combat_outcome.damage)
            self.assertGreaterEqual(result.combat_outcome.damage, 0)

    def test_narrator_uses_explicit_defense_outcome(self) -> None:
        narrator = CombatNarrator()
        dodge_event = CombatEvent(
            action_id="action-1",
            attacker_id="hero",
            attacker_name="Hero",
            defender_id="wolf",
            defender_name="Wilk",
            technique="precyzyjny cios",
            result="dodge",
            defense="dodge",
            weapon_family="miecze",
        )
        block_event = CombatEvent(
            action_id="action-2",
            attacker_id="hero",
            attacker_name="Hero",
            defender_id="wolf",
            defender_name="Wilk",
            technique="precyzyjny cios",
            result="block",
            defense="block",
            weapon_family="miecze",
        )
        parry_event = CombatEvent(
            action_id="action-3",
            attacker_id="hero",
            attacker_name="Hero",
            defender_id="wolf",
            defender_name="Wilk",
            technique="precyzyjny cios",
            result="parry",
            defense="parry",
            weapon_family="miecze",
        )
        miss_event = CombatEvent(
            action_id="action-4",
            attacker_id="hero",
            attacker_name="Hero",
            defender_id="wolf",
            defender_name="Wilk",
            technique="precyzyjny cios",
            result="miss",
            defense="none",
            weapon_family="miecze",
        )

        dodge_outcome = CombatOutcome(
            action_id="action-1",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.DEFENDED,
            hit=False,
            defense_result=DefenseResolution.DODGED,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.DODGED,
                successful_defense=True,
                attempts=(DefenseAttempt(DefenseType.DODGE, True, True, True),),
                selected_defense=DefenseType.DODGE,
                reason_code="DODGED",
            ),
            reason_code="DODGED",
        )
        block_outcome = CombatOutcome(
            action_id="action-2",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.DEFENDED,
            hit=False,
            defense_result=DefenseResolution.BLOCKED,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.BLOCKED,
                successful_defense=True,
                attempts=(DefenseAttempt(DefenseType.DODGE, True, True, False),),
                selected_defense=DefenseType.SHIELD_BLOCK,
                reason_code="BLOCKED",
            ),
            reason_code="DEFENDED",
        )
        parry_outcome = CombatOutcome(
            action_id="action-3",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.DEFENDED,
            hit=False,
            defense_result=DefenseResolution.PARRIED,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.PARRIED,
                successful_defense=True,
                attempts=(DefenseAttempt(DefenseType.DODGE, True, True, False),),
                selected_defense=DefenseType.PARRY,
                reason_code="PARRIED",
            ),
            reason_code="DEFENDED",
        )
        miss_outcome = CombatOutcome(
            action_id="action-4",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.MISS,
            hit=False,
            defense_result=DefenseResolution.NOT_ATTEMPTED,
            defense_outcome=DefenseOutcome(
                resolution=DefenseResolution.NOT_ATTEMPTED,
                successful_defense=False,
                attempts=(),
                selected_defense=None,
                reason_code="NOT_ATTEMPTED",
            ),
            reason_code="MISS",
        )

        self.assertIn("odskakuje", narrator.render_outcome(dodge_outcome, dodge_event, "attacker").lower())
        self.assertIn("tarczą", narrator.render_outcome(block_outcome, block_event, "defender").lower())
        self.assertIn("paruje", narrator.render_outcome(parry_outcome, parry_event, "observer").lower())
        self.assertIn("wymyka", narrator.render_outcome(miss_outcome, miss_event, "attacker").lower())

    def test_command_path_and_heartbeat_use_explicit_defense_pipeline(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("pipeline_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            self._clear_combat_slots(npc.character)
            hero.equipment["bron_glowna"] = Item(
                "miecz testowy",
                "Miecz testowy.",
                1.0,
                10,
                "pipeline_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_type="miecz",
                base_damage=7,
            )
            hero.skills.values["bron_jednoraczna"]["level"] = 20
            npc.character.inventory.clear()
            npc.character.equipment["tarcza"] = None
            npc.character.equipment["bron_glowna"] = None
            server.combat.rng = ScriptedRng(randint_values=[20, 1, 1, 20, 1, 1], random_values=[1.0, 1.0, 1.0, 1.0])

            result = asyncio.run(harness.execute(hero, "zabij wilk"))

            self.assertTrue(server.combat.has_fight(hero.username, npc.id))
            self.assertIn("wilk", result.output.lower())
            attack_events = [event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED]
            self.assertTrue(attack_events)
            payload = attack_events[-1].payload
            self.assertTrue(payload.get("action_id"))
            self.assertTrue(payload.get("combat_event"))
            self.assertIn("action_id", payload["combat_event"])


if __name__ == "__main__":
    unittest.main()

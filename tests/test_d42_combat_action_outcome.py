from __future__ import annotations

import asyncio
import dataclasses
import unittest
from unittest.mock import patch

from astergard.combat.actions import (
    CombatAction,
    CombatActionType,
    CombatOutcome,
    CombatOutcomeType,
    DefenseResolution,
)
from astergard.engine.events import DomainEventType
from astergard.items.models import Item
from astergard.testing import TestGameHarness


class D42CombatActionOutcomeTests(unittest.TestCase):
    def test_basic_attack_action_uses_active_weapon_and_is_immutable(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("action_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            inventory_blade = Item("zapasowy miecz", "Zapasowa broń.", 1.0, 10, "inventory_sword", item_type="weapon", slot="bron_glowna", weapon_type="miecz")
            equipped_blade = Item("miecz bojowy", "Aktywna broń.", 1.1, 10, "equipped_sword", item_type="weapon", slot="bron_glowna", weapon_type="miecz")
            hero.inventory.append(inventory_blade)
            hero.equipment["bron_glowna"] = equipped_blade

            action = server.combat.build_basic_attack_action(hero, npc.character)

            self.assertEqual(action.action_type, CombatActionType.BASIC_ATTACK)
            self.assertEqual(action.actor_id, hero.username)
            self.assertEqual(action.target_id, npc.id)
            self.assertEqual(action.weapon_id, equipped_blade.id)
            self.assertEqual(action.weapon_specialization_id, server.combat._weapon_skill_name(equipped_blade))
            self.assertIsNone(action.technique_id)
            self.assertNotEqual(action.weapon_id, inventory_blade.id)
            self.assertGreaterEqual(len(action.action_id), 8)
            with self.assertRaises(dataclasses.FrozenInstanceError):
                action.actor_id = "x"  # type: ignore[misc]

    def test_basic_attack_action_without_weapon_and_npc_action_share_canonical_ids(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("barehanded", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")

            player_action = server.combat.build_basic_attack_action(hero, npc.character)
            npc_action = server.combat.build_basic_attack_action(npc.character, hero)

            self.assertEqual(player_action.actor_id, hero.username)
            self.assertEqual(player_action.target_id, npc.id)
            self.assertIsNone(player_action.weapon_id)
            self.assertIsNone(player_action.technique_id)
            self.assertEqual(npc_action.actor_id, npc.id)
            self.assertEqual(npc_action.target_id, hero.username)

    def test_combat_outcome_model_is_immutable_and_serializable(self) -> None:
        outcome = CombatOutcome(
            action_id="action-1",
            actor_id="hero",
            target_id="wolf",
            result_type=CombatOutcomeType.HIT,
            hit=True,
            defense_result=DefenseResolution.UNKNOWN_DEFENSE,
            damage=4,
            hit_location="korpus",
            wound_ids=("w1",),
            effect_ids=(),
            target_defeated=False,
            combat_ended=False,
            reason_code="HIT",
        )

        payload = outcome.to_dict()
        restored = CombatOutcome.from_dict(payload)

        self.assertEqual(restored.action_id, "action-1")
        self.assertEqual(restored.damage, 4)
        self.assertEqual(restored.hit_location, "korpus")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            outcome.damage = 9  # type: ignore[misc]

    def test_resolve_action_reports_missing_target(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("resolver", room_id=101)
            action = CombatAction(
                actor_id=hero.username,
                target_id="missing",
                action_type=CombatActionType.BASIC_ATTACK,
            )

            outcome = server.combat.resolve_action(action, hero, None)

            self.assertEqual(outcome.result_type, CombatOutcomeType.NO_TARGET)
            self.assertEqual(outcome.reason_code, "TARGET_NOT_FOUND")
            self.assertEqual(outcome.action_id, action.action_id)

    def test_attack_and_heartbeat_emit_action_id_and_keep_legacy_result(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("integration_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")

            captured: list = []
            original_attack = server.combat.attack

            def capture_attack(*args, **kwargs):
                result = original_attack(*args, **kwargs)
                captured.append(result)
                return result

            with patch.object(server.combat, "attack", side_effect=capture_attack):
                result = asyncio.run(harness.execute(hero, "zabij wilk"))
                self.assertTrue(captured)
                attack_result = captured[0]

            self.assertTrue(server.combat.has_fight(hero.username, npc.id))
            self.assertIsNotNone(attack_result.combat_action)
            self.assertIsNotNone(attack_result.combat_outcome)
            assert attack_result.combat_action is not None
            assert attack_result.combat_outcome is not None
            self.assertEqual(attack_result.combat_action.action_id, attack_result.combat_outcome.action_id)
            self.assertEqual(attack_result.combat_event.action_id, attack_result.combat_action.action_id)

            attack_events = [event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED]
            self.assertTrue(attack_events)
            self.assertEqual(attack_events[-1].payload.get("action_id"), attack_result.combat_action.action_id)
            self.assertIn("wilk", result.output.lower())
            self.assertEqual(attack_result.hit, attack_result.combat_outcome.hit)
            self.assertEqual(attack_result.defender_dead, attack_result.combat_outcome.target_defeated)

    def test_controlled_combat_respects_previous_results_and_narration(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("contract_hero", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            hero.inventory.clear()
            npc.character.inventory.clear()
            hero.equipment["bron_glowna"] = Item(
                "miecz kontraktowy",
                "Miecz testowy.",
                1.0,
                10,
                "contract_sword",
                item_type="weapon",
                slot="bron_glowna",
                weapon_type="miecz",
                base_damage=6,
            )
            hero.skills.values["bron_jednoraczna"]["level"] = 20
            npc.character.skills.values["uniki"]["level"] = 1

            result = server.combat.attack(hero, npc.character)

            self.assertIsNotNone(result.combat_action)
            self.assertIsNotNone(result.combat_outcome)
            assert result.combat_outcome is not None
            self.assertIsNotNone(result.combat_event)
            assert result.combat_event is not None
            self.assertEqual(result.hit, result.combat_outcome.hit)
            self.assertEqual(result.effective_damage, result.combat_outcome.damage)
            self.assertEqual(result.body_part, result.combat_outcome.legacy_body_part)
            self.assertEqual(result.combat_event.hit_location, result.combat_outcome.hit_location)
            self.assertEqual(result.defender_dead, result.combat_outcome.target_defeated)
            self.assertIn(result.combat_outcome.result_type, {CombatOutcomeType.HIT, CombatOutcomeType.TARGET_DEFEATED, CombatOutcomeType.MISS, CombatOutcomeType.DEFENDED})
            self.assertTrue(result.message)
            assert result.combat_event is not None
            self.assertTrue(result.combat_event.to_dict()["action_id"])


if __name__ == "__main__":
    unittest.main()

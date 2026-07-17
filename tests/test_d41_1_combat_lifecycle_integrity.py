from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

from astergard.characters.models import Character
from astergard.combat.manager import CombatManager
from astergard.combat.wounds import is_dead
from astergard.engine.events import DomainEventType
from astergard.items.models import Item
from astergard.testing import TestGameHarness


class AlternatingRandom:
    def __init__(self) -> None:
        self._calls = 0

    def randint(self, a: int, b: int) -> int:
        self._calls += 1
        return a if self._calls % 2 == 1 else b

    def random(self) -> float:
        return 0.99


class D411CombatLifecycleIntegrityTests(unittest.TestCase):
    def test_zabij_starts_combat_and_second_zabij_does_not_attack_again(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            server.combat.rng = AlternatingRandom()
            player = harness.create_character("tester", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            player.stats.zrecznosc = 1
            for skill in player.skills.values.values():
                skill["level"] = 1
            npc.character.stats.zrecznosc = 30
            npc.character.skills.values["uniki"]["level"] = 30

            with patch.object(server.combat, "attack", wraps=server.combat.attack) as mocked_attack:
                combat_ctx = harness.context_for(player).combat_context()
                first = asyncio.run(harness.execute(player, "zabij wilk"))
                self.assertIn("wilk", first.output.lower())
                self.assertTrue(server.combat.has_fight(player.username, npc.id))
                self.assertTrue(player.in_combat)
                self.assertTrue(npc.character.in_combat)
                self.assertEqual(mocked_attack.call_count, 1)

                second_output = server.services.combat_service.attack_npc(combat_ctx, "wilk", 1)
                self.assertIn("już walczysz", second_output.lower())
                self.assertEqual(mocked_attack.call_count, 1)

                heartbeat_before = mocked_attack.call_count
                harness.tick_once()
                self.assertGreater(mocked_attack.call_count, heartbeat_before)

                combat_attacked_events = [event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED]
                self.assertEqual(len(combat_attacked_events), 1)
                self.assertTrue(server.combat.has_fight(player.username, npc.id))

    def test_equipped_weapon_and_shield_are_only_active_when_worn(self) -> None:
        character = Character("tester")
        character.inventory.clear()
        sword = Item("miecz", "opis", 1.0, 0, "sword", item_type="weapon", slot="bron_glowna", base_damage=4)
        shield = Item("tarcza", "opis", 2.0, 0, "shield", item_type="shield", slot="tarcza", shield_block=5)

        character.equipment["bron_glowna"] = sword
        character.equipment["tarcza"] = shield
        self.assertIs(character.weapon(), sword)
        self.assertIs(character.shield(), shield)

        character.equipment["bron_glowna"] = None
        character.equipment["tarcza"] = None
        self.assertIsNone(character.weapon())
        self.assertIsNone(character.shield())

    def test_inventory_only_weapon_and_shield_are_not_active_equipment(self) -> None:
        character = Character("tester")
        character.inventory.clear()
        sword = Item("miecz", "opis", 1.0, 0, "sword", item_type="weapon", slot="bron_glowna", base_damage=4)
        shield = Item("tarcza", "opis", 2.0, 0, "shield", item_type="shield", slot="tarcza", shield_block=5)
        character.inventory.extend([sword, shield])

        self.assertIsNone(character.weapon())
        self.assertIsNone(character.shield())

    def test_successful_flee_clears_only_fleeing_character_relations(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            player = harness.create_character("runner", room_id=101)
            ally = harness.create_character("ally", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            service = server.services.combat_service
            ctx = harness.context_for(player).combat_context()

            server.combat.start_fight(player, npc.character)
            server.combat.start_fight(ally, npc.character)
            self.assertTrue(player.in_combat)
            self.assertTrue(ally.in_combat)
            self.assertTrue(npc.character.in_combat)

            with patch("astergard.application.services.combat_service.random.random", return_value=0.0):
                output = service.flee(ctx)

            self.assertNotEqual(player.room_id, 101)
            self.assertFalse(server.combat.has_fight(player.username, npc.id))
            self.assertTrue(server.combat.has_fight(ally.username, npc.id))
            self.assertFalse(player.in_combat)
            self.assertTrue(ally.in_combat)
            self.assertTrue(npc.character.in_combat)
            flee_events = [
                event
                for event in server.services.event_bus.history
                if event.type == DomainEventType.COMBAT_FLED and event.payload.get("success") is True
            ]
            self.assertEqual(len(flee_events), 1)
            self.assertTrue(output)

    def test_failed_flee_keeps_combat_active(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            player = harness.create_character("runner", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            service = server.services.combat_service
            ctx = harness.context_for(player).combat_context()

            server.combat.start_fight(player, npc.character)
            before_room = player.room_id
            with patch("astergard.application.services.combat_service.random.random", return_value=1.0):
                output = service.flee(ctx)

            self.assertEqual(player.room_id, before_room)
            self.assertTrue(server.combat.has_fight(player.username, npc.id))
            self.assertTrue(player.in_combat)
            self.assertTrue(npc.character.in_combat)
            flee_events = [
                event
                for event in server.services.event_bus.history
                if event.type == DomainEventType.COMBAT_FLED and event.payload.get("success") is False
            ]
            self.assertEqual(len(flee_events), 1)
            self.assertIn("nie udaje", output.lower())

    def test_separation_and_death_cleanup_active_fights(self) -> None:
        combat = CombatManager()
        attacker = Character("a")
        defender = Character("b")
        combat.start_fight(attacker, defender)

        defender.room_id = 99
        combat.process_active_round({"a": attacker, "b": defender})
        self.assertEqual(combat.active_fights, [])
        self.assertFalse(attacker.in_combat)
        self.assertFalse(defender.in_combat)

        combat2 = CombatManager()
        attacker2 = Character("c")
        defender2 = Character("d")
        combat2.start_fight(attacker2, defender2)
        defender2.die()
        combat2.process_active_round({"c": attacker2, "d": defender2})
        self.assertEqual(combat2.active_fights, [])
        self.assertFalse(attacker2.in_combat)
        self.assertFalse(defender2.in_combat)
        self.assertTrue(is_dead(defender2.wounds) or not defender2.is_alive)

    def test_basic_attack_and_narration_still_emit_result(self) -> None:
        combat = CombatManager(AlternatingRandom())
        attacker = Character("atakujacy")
        defender = Character("obronca")
        attacker.inventory.clear()
        defender.inventory.clear()
        attacker.equipment["bron_glowna"] = Item("miecz", "opis", 1.0, 0, "sword", item_type="weapon", slot="bron_glowna", base_damage=4)
        result = combat.attack(attacker, defender)
        self.assertIsNotNone(result.message)
        self.assertIsNotNone(result.combat_event)


if __name__ == "__main__":
    unittest.main()

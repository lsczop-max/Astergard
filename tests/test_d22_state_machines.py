from __future__ import annotations

import unittest
from unittest.mock import patch

from astergard.characters.models import Character
from astergard.combat.hit_locations import BodyLocation, BodyLocationGroup, HitLocationOutcome
from astergard.combat.manager import CombatManager
from astergard.npcs.models import NPCFactory
from astergard.server.session import ClientConnection
from astergard.state import CharacterState, NPCState, SessionState, StateTransitionError


class DummyWriter:
    def close(self) -> None:
        pass

    async def wait_closed(self) -> None:
        pass


class StateMachineTests(unittest.TestCase):
    def test_session_state_machine_accepts_valid_disconnect(self) -> None:
        connection = ClientConnection(None, DummyWriter())
        connection.transition_state(SessionState.IN_GAME)
        self.assertEqual(connection.state, SessionState.IN_GAME.value)
        connection.transition_state(SessionState.DISCONNECTED)
        self.assertEqual(connection.state, SessionState.DISCONNECTED.value)

    def test_session_state_machine_rejects_reconnect_after_disconnect(self) -> None:
        connection = ClientConnection(None, DummyWriter(), state=SessionState.DISCONNECTED.value)
        with self.assertRaises(StateTransitionError):
            connection.transition_state(SessionState.IN_GAME)

    def test_character_state_machine_syncs_legacy_flags(self) -> None:
        character = Character("tester")
        character.enter_combat()
        self.assertTrue(character.in_combat)
        self.assertTrue(character.is_alive)
        self.assertEqual(character.state, CharacterState.IN_COMBAT.value)
        character.leave_combat()
        self.assertFalse(character.in_combat)
        self.assertEqual(character.state, CharacterState.ALIVE.value)
        character.die()
        self.assertFalse(character.is_alive)
        self.assertEqual(character.state, CharacterState.DEAD.value)

    def test_character_state_machine_rejects_resurrection_without_explicit_policy(self) -> None:
        character = Character("tester")
        character.die()
        with self.assertRaises(StateTransitionError):
            character.transition_state(CharacterState.ALIVE)

    def test_npc_state_machine_validates_ai_transitions(self) -> None:
        npc = NPCFactory().create("merchant", room_id=1)
        npc.transition_ai_state(NPCState.PATROL)
        self.assertEqual(npc.ai_state, NPCState.PATROL.value)
        npc.transition_ai_state(NPCState.AGGRESSIVE)
        self.assertEqual(npc.ai_state, NPCState.AGGRESSIVE.value)

    def test_npc_state_machine_rejects_dead_to_aggressive(self) -> None:
        npc = NPCFactory().create("merchant", room_id=1)
        npc.transition_ai_state(NPCState.DEAD)
        with self.assertRaises(StateTransitionError):
            npc.transition_ai_state(NPCState.AGGRESSIVE)

    def test_combat_death_uses_character_state_machine(self) -> None:
        attacker = Character("attacker")
        defender = Character("defender")
        attacker.stats.zrecznosc = 99
        attacker.skills.values["bron_cieta"]["level"] = 99
        defender.stats.zrecznosc = 1
        defender.wounds["glowa"] = 3
        manager = CombatManager()
        fixed_hit_location = HitLocationOutcome(
            location=BodyLocation.HEAD,
            location_group=BodyLocationGroup.HEAD_GROUP,
            base_weight=1.0,
            weapon_weight_modifier=1.0,
            quality_modifier=1.0,
            attack_type_modifier=1.0,
            final_weight=1.0,
            reason_code="TEST",
        )
        with patch("astergard.combat.manager.resolve_hit_location", return_value=fixed_hit_location):
            result = manager.attack(attacker, defender)
        self.assertTrue(result.defender_dead)
        self.assertEqual(defender.state, CharacterState.DEAD.value)
        self.assertFalse(defender.is_alive)


if __name__ == "__main__":
    unittest.main()

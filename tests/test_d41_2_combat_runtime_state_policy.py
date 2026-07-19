from __future__ import annotations

import json
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch

from astergard.application.bootstrap import GameBootstrapper
from astergard.engine.events import DomainEventType
from astergard.items.models import Item
from astergard.testing import TestGameHarness


class D412CombatRuntimeStatePolicyTests(unittest.TestCase):
    def test_player_reload_clears_transient_combat_state_but_keeps_durable_state(self) -> None:
        with TestGameHarness() as harness:
            character = harness.create_character("runtime_player", room_id=101)
            character.gold = 123
            character.stats.kondycja = max(1, character.stats.kondycja - 9)
            character.wounds["korpus"] = 2
            character.equipment["bron_glowna"] = Item(
                "miecz runtime",
                "Testowy miecz do odczytu.",
                1.0,
                10,
                "runtime_sword",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="miecz",
                base_damage=4,
            )
            character.equipment["tarcza"] = Item(
                "tarcza runtime",
                "Testowa tarcza do odczytu.",
                2.0,
                12,
                "runtime_shield",
                item_type="shield",
                slot="tarcza",
                wearable=True,
                weapon_type="tarcza",
                shield_block=5,
            )
            character.in_combat = True

            reloaded = harness.save_and_reload_character(character)

            self.assertFalse(reloaded.in_combat)
            self.assertEqual(reloaded.gold, 123)
            self.assertEqual(reloaded.stats.kondycja, character.stats.kondycja)
            self.assertEqual(reloaded.wounds["korpus"], 2)
            weapon = reloaded.weapon()
            shield = reloaded.shield()
            self.assertIsNotNone(weapon)
            self.assertIsNotNone(shield)
            assert weapon is not None
            assert shield is not None
            self.assertEqual(weapon.vnum, "runtime_sword")
            self.assertEqual(shield.vnum, "runtime_shield")

    def test_legacy_world_snapshot_clears_in_combat_and_keeps_durable_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "mud.db")
            bootstrap = GameBootstrapper(db_path).build()
            npc = next(iter(bootstrap.npcs.npcs.values()))
            npc.character.wounds["korpus"] = 3
            npc.character.stats.kondycja = max(1, npc.character.stats.kondycja - 5)
            bootstrap.repo.world_state.save(bootstrap.world, bootstrap.npcs.npcs)

            with bootstrap.repo.connection() as con:
                row = con.execute("SELECT world_json FROM world_snapshots WHERE id = 1").fetchone()
                assert row is not None
                payload = json.loads(str(row[0]))
                npc_payload = payload["npcs"][npc.id]["character"]
                npc_payload["in_combat"] = True
                npc_payload["state"] = "IN_COMBAT"
                npc_payload["active_opponent"] = "ghost"
                con.execute("UPDATE world_snapshots SET world_json=? WHERE id = 1", (json.dumps(payload, ensure_ascii=False),))

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with TestGameHarness(db_path=db_path) as harness:
                    server = harness.require_server()
                    loaded_npc = server.npcs.npcs[npc.id]

                    self.assertEqual(server.combat.active_fights, [])
                    self.assertFalse(loaded_npc.character.in_combat)
                    self.assertTrue(loaded_npc.character.is_alive)
                    self.assertEqual(loaded_npc.character.wounds["korpus"], 3)
                    self.assertGreaterEqual(loaded_npc.character.stats.kondycja, 1)

                    before_events = len([event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED])
                    harness.tick_once()
                    after_events = len([event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED])

                    self.assertEqual(before_events, after_events)
                    self.assertFalse(loaded_npc.character.in_combat)

    def test_new_combat_starts_normally_after_reload_and_flee_clears_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "mud.db")
            bootstrap = GameBootstrapper(db_path).build()
            npc = next(iter(bootstrap.npcs.npcs.values()))
            bootstrap.repo.world_state.save(bootstrap.world, bootstrap.npcs.npcs)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with TestGameHarness(db_path=db_path) as harness:
                    server = harness.require_server()
                    hero = harness.create_character("hero_runtime", room_id=npc.room_id)
                    reloaded_npc = server.npcs.npcs[npc.id]
                    ctx = harness.context_for(hero).combat_context()

                    self.assertEqual(server.combat.active_fights, [])
                    self.assertFalse(hero.in_combat)
                    self.assertFalse(reloaded_npc.character.in_combat)

                    started = server.combat.start_fight(hero, reloaded_npc.character)
                    self.assertTrue(started)
                    self.assertEqual(len(server.combat.active_fights), 1)
                    self.assertTrue(server.combat.has_fight(hero.username, reloaded_npc.id))

                    with patch("astergard.application.services.combat_service.random.random", return_value=0.0):
                        result = server.services.combat_service.flee(ctx)
                    self.assertTrue(result)
                    self.assertEqual(server.combat.active_fights, [])
                    self.assertFalse(hero.in_combat)
                    self.assertFalse(reloaded_npc.character.in_combat)

                    before_events = len([event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED])
                    harness.tick_once()
                    after_events = len([event for event in server.services.event_bus.history if event.type == DomainEventType.COMBAT_ATTACKED])
                    self.assertEqual(before_events, after_events)

    def test_disconnect_removes_participant_without_orphaning_combat(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            player = harness.create_character("disconnect_runtime", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            server.combat.start_fight(player, npc.character)
            self.assertTrue(server.combat.has_fight(player.username, npc.id))

            transport = harness.writers[player.username]
            server.clients.pop(transport)

            harness.tick_once()

            self.assertFalse(server.combat.has_fight(player.username, npc.id))
            self.assertEqual(server.combat.active_fights, [])
            self.assertFalse(npc.character.in_combat)


if __name__ == "__main__":
    unittest.main()

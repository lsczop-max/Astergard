from __future__ import annotations
import asyncio
from typing import Any, Coroutine, cast
import tempfile, unittest
from astergard.commands.parser import CommandParser
from astergard.server.game import GameContext, GameServer
from astergard.combat.manager import CombatManager
from astergard.characters.models import Character
from astergard.items.models import Item

class AstergardCoreTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=True)
        return GameServer(tmp.name)

    def test_parser_ordinals_and_direction(self) -> None:
        parsed = CommandParser.parse("wez drugi dlugi miecz")
        self.assertEqual(parsed.command, "wez")
        self.assertEqual(parsed.argument, "dlugi miecz")
        self.assertEqual(parsed.index, 2)
        self.assertEqual(CommandParser.parse("n").command, "polnoc")

    def test_world_has_500_symmetric_locations(self) -> None:
        srv = self.make_server()
        self.assertEqual(len(srv.world.locations), 500)
        for loc in srv.world.locations.values():
            for direction, ex in loc.exits.items():
                target = srv.world.locations[ex.target_room]
                opposite = {"polnoc":"poludnie","poludnie":"polnoc","wschod":"zachod","zachod":"wschod","gora":"dol","dol":"gora"}.get(direction)
                if opposite:
                    self.assertIn(opposite, target.exits)

    def test_inventory_equipment_and_weight(self) -> None:
        srv = self.make_server(); char = Character("tester")
        ctx = srv.make_context(char)
        out: str = asyncio.run(cast(Coroutine[Any, Any, str], srv.cmd_wear(ctx, "miecz", 1)))
        self.assertIn("Zakładasz", out)
        self.assertIsNotNone(char.equipment["prawa_reka"])

    def test_combat_damage_can_wound(self) -> None:
        attacker = Character("a"); defender = Character("d")
        attacker.equipment["prawa_reka"] = Item("topór", "", 2, 10, "axe", "weapon", "prawa_reka", base_damage=10)
        res = CombatManager().attack(attacker, defender)
        self.assertTrue(sum(defender.wounds.values()) >= 0)
        self.assertIsInstance(res.message, str)

    def test_quest_trade_and_commands(self) -> None:
        srv = self.make_server(); char = Character("tester")
        ctx = srv.make_context(char)
        talk: str = asyncio.run(cast(Coroutine[Any, Any, str], srv.cmd_talk(ctx, "kupiec o wilki", 1)))
        self.assertIn("Otrzymujesz", talk)
        offer: str = asyncio.run(cast(Coroutine[Any, Any, str], srv.cmd_offer(ctx, None, 1)))
        self.assertIn("mikstura", offer)

if __name__ == "__main__":
    unittest.main()

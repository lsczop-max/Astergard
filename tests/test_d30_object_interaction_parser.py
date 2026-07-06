from __future__ import annotations

import asyncio
import tempfile
import unittest

from astergard.characters.models import Character
from astergard.commands.parser import CommandParser
from astergard.items.models import Item
from astergard.server.game import GameServer


class D30ObjectInteractionParserTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_parser_preserves_relation_connector_for_put(self) -> None:
        parsed = CommandParser.parse("włóż miecz do plecaka")
        self.assertEqual(parsed.command, "wloz")
        self.assertEqual(parsed.argument, "miecz do plecak")

    def test_get_all_takes_all_room_items_that_fit(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("collector")
            char.inventory.clear()
            loc = server.world.get_location(char.room_id)
            assert loc is not None
            loc.items.clear()
            loc.items.append(Item("żelazny klucz", "Klucz.", 0.1, 1, "iron_key"))
            loc.items.append(Item("srebrny pierścień", "Pierścień.", 0.05, 10, "silver_ring"))
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "weź wszystko")
            self.assertIn("Podnosisz:", out)
            self.assertEqual({item.vnum for item in char.inventory}, {"iron_key", "silver_ring"})
            self.assertEqual(loc.items, [])
        asyncio.run(run())

    def test_put_item_into_container_with_polish_relation(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("packer")
            char.inventory.clear()
            pouch = Item("skórzany plecak", "Plecak.", 0.5, 5, "backpack", is_container=True, capacity=5.0)
            key = Item("żelazny klucz", "Klucz.", 0.1, 1, "iron_key")
            char.inventory.extend([pouch, key])
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "włóż klucza do plecaka")
            self.assertIn("Wkładasz", out)
            self.assertEqual([item.vnum for item in pouch.contains], ["iron_key"])
            self.assertNotIn(key, char.inventory)
            inv = await server.dispatcher.execute_line(ctx, "ekw")
            self.assertIn("w środku", inv)
        asyncio.run(run())

    def test_give_item_to_npc_with_dative_shorthand(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("giver")
            char.inventory.clear()
            pelt = Item("wilcza skóra", "Skóra.", 1.0, 8, "wolf_pelt")
            char.inventory.append(pelt)
            char.active_quests["wolf_pelt"] = {"current": 0}
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "daj skórę kupcowi")
            self.assertIn("Dajesz", out)
            self.assertNotIn(pelt, char.inventory)
            self.assertEqual(char.active_quests["wolf_pelt"]["current"], 1)
        asyncio.run(run())

    def test_drop_all_moves_inventory_to_room(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("dropper")
            ctx = server.make_context(char)
            loc = server.world.get_location(char.room_id)
            assert loc is not None
            before = len(char.inventory)
            out = await server.dispatcher.execute_line(ctx, "upuść wszystko")
            self.assertIn("Upuszczasz:", out)
            self.assertEqual(len(char.inventory), 0)
            self.assertGreaterEqual(len(loc.items), before)
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

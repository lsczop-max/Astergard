from __future__ import annotations

import asyncio
import tempfile
import unittest

from astergard.characters.models import Character
from astergard.commands.parser import CommandParser
from astergard.items.models import Item
from astergard.server.game import GameServer


class D31ContainerInteractionEngineTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def make_character_with_container(self) -> tuple[GameServer, Character, Item, Item, Item]:
        server = self.make_server()
        char = Character("container_tester")
        char.inventory.clear()
        backpack = Item("skórzany plecak", "Plecak z ciemnej skóry.", 0.5, 5, "backpack", is_container=True, capacity=10.0)
        key = Item("żelazny klucz", "Ciężki klucz z obtartym piórem.", 0.1, 1, "iron_key")
        ring = Item("srebrny pierścień", "Wąski pierścień z wyrytą kreską.", 0.05, 10, "silver_ring")
        backpack.contains.extend([key, ring])
        char.inventory.append(backpack)
        return server, char, backpack, key, ring

    def test_parser_preserves_source_connector_for_get_from_container(self) -> None:
        parsed = CommandParser.parse("weź klucza z plecaka")
        self.assertEqual(parsed.command, "wez")
        self.assertEqual(parsed.argument, "klucz z plecak")

    def test_take_specific_item_from_container_with_wez_z(self) -> None:
        async def run() -> None:
            server, char, backpack, key, ring = self.make_character_with_container()
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "weź klucza z plecaka")
            self.assertIn("Wyjmujesz żelazny klucz", out)
            self.assertIn(key, char.inventory)
            self.assertNotIn(key, backpack.contains)
            self.assertIn(ring, backpack.contains)
        asyncio.run(run())

    def test_take_specific_item_from_container_with_wyjmij(self) -> None:
        async def run() -> None:
            server, char, backpack, key, _ring = self.make_character_with_container()
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "wyjmij klucz z plecaka")
            self.assertIn("Wyjmujesz żelazny klucz", out)
            self.assertIn(key, char.inventory)
            self.assertEqual(backpack.contains[0].vnum, "silver_ring")
        asyncio.run(run())

    def test_take_all_from_container(self) -> None:
        async def run() -> None:
            server, char, backpack, key, ring = self.make_character_with_container()
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "weź wszystko z plecaka")
            self.assertIn("Wyjmujesz z skórzany plecak", out)
            self.assertEqual(backpack.contains, [])
            self.assertIn(key, char.inventory)
            self.assertIn(ring, char.inventory)
        asyncio.run(run())

    def test_look_inside_container_and_item_inside_container(self) -> None:
        async def run() -> None:
            server, char, _backpack, _key, _ring = self.make_character_with_container()
            ctx = server.make_context(char)
            listing = await server.dispatcher.execute_line(ctx, "obejrzyj w plecaku")
            self.assertIn("żelazny klucz", listing)
            self.assertIn("srebrny pierścień", listing)
            item_desc = await server.dispatcher.execute_line(ctx, "obejrzyj klucz w plecaku")
            self.assertIn("Ciężki klucz", item_desc)
        asyncio.run(run())

    def test_missing_item_inside_container_has_clear_message(self) -> None:
        async def run() -> None:
            server, char, _backpack, _key, _ring = self.make_character_with_container()
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "wyjmij miecz z plecaka")
            self.assertIn("Nie ma tego w skórzany plecak", out)
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

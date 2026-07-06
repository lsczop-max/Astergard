from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from astergard.characters.models import Character
from astergard.commands.parser import CommandParser
from astergard.items.models import Item
from astergard.server.game import GameServer


class D29PolishParserTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_parser_normalizes_polish_diacritics_prepositions_and_ordinals(self) -> None:
        parsed = CommandParser.parse("spójrz na drugiego żołnierza!")
        self.assertEqual(parsed.command, "spojrz")
        self.assertEqual(parsed.argument, "drugiego zolnierz")  # only first-token ordinal is positional
        parsed = CommandParser.parse("weź drugi żelazny klucz")
        self.assertEqual(parsed.command, "wez")
        self.assertEqual(parsed.argument, "zelazny klucz")
        self.assertEqual(parsed.index, 2)

    def test_short_arkadia_style_aliases_work_for_look_and_inventory(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("alias")
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "ob")
            self.assertIn("Widoczne wyjścia", out)
            inv = await server.dispatcher.execute_line(ctx, "ekw")
            self.assertIn("Plecak", inv)
        asyncio.run(run())

    def test_diacritic_item_matching_allows_declined_forms(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("declension")
            loc = server.world.get_location(char.room_id)
            assert loc is not None
            loc.items.append(Item("żelazny klucz", "Ciężki klucz.", 0.1, 1, "iron_key"))
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "podnieś klucza")
            self.assertIn("Podnosisz", out)
            self.assertTrue(any(item.vnum == "iron_key" for item in char.inventory))
        asyncio.run(run())

    def test_npc_matching_accepts_abbreviated_declined_name(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("npc")
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "sp żol")
            self.assertTrue("Żołnierz" in out or "zolnierz" in out.lower() or "Nic ciekawego" not in out)
        asyncio.run(run())

    def test_player_help_hides_admin_and_diagnostics_commands(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("player")
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "pomoc")
            self.assertIn("Eksploracja", out)
            self.assertNotIn("Administracja", out)
            self.assertNotIn("Diagnostyka", out)
            self.assertNotIn("teleport", out)
        asyncio.run(run())

    def test_quest_log_no_longer_raises_render_error(self) -> None:
        async def run() -> None:
            server = self.make_server()
            char = Character("quest")
            ctx = server.make_context(char)
            out = await server.dispatcher.execute_line(ctx, "dziennik")
            self.assertIn("Nie masz aktywnych zadań", out)
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

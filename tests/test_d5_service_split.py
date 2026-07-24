from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from typing import Any, Coroutine, cast
from unittest.mock import patch

from astergard.characters.models import Character
from astergard.crafting.services import CraftingService
from astergard.items.models import Item
from astergard.server.game import GameServer


class D5ServiceSplitTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_bootstrap_contains_d5_application_services(self) -> None:
        server = self.make_server()
        self.assertIsNotNone(server.services.exploration_service)
        self.assertIsNotNone(server.services.communication_service)
        self.assertIsNotNone(server.services.crafting)
        self.assertIsNotNone(server.services.system_service)
        self.assertFalse(hasattr(server.services, "magic"))
        self.assertFalse(hasattr(server.services, "magic_crafting_service"))
        self.assertNotIn("cast", server.dispatcher.commands)
        self.assertIn("craft", server.dispatcher.commands)
        self.assertFalse(hasattr(server, "cmd_cast"))
        self.assertTrue(hasattr(server, "cmd_craft"))

    def test_exploration_handler_delegates_to_service(self) -> None:
        server = self.make_server()
        char = Character("look")
        ctx = server.make_context(char)
        result: str = asyncio.run(cast(Coroutine[Any, Any, str], server.cmd_look(ctx, None, 1)))
        self.assertIn("Brama Dymnych Chorągwi", result)
        self.assertNotIn("drogi stąd", result.lower())

    def test_communication_handler_delegates_to_service(self) -> None:
        server = self.make_server()
        char = Character("speaker")
        ctx = server.make_context(char)
        result: str = asyncio.run(cast(Coroutine[Any, Any, str], server.cmd_say(ctx, "test", 1)))
        self.assertEqual(result, "Mówisz: test")

    def test_crafting_handler_delegates_to_service(self) -> None:
        server = self.make_server()
        char = Character("crafter")
        char.skills.state("pierwsza_pomoc")["level"] = 2
        char.inventory.extend(
            [
                Item("torfowe ziele", "Surowe ziele z mokradła.", 0.1, 1, "bog_tea_herb"),
                Item("woda w bukłaku", "Zwykła woda do naparu.", 0.5, 1, "water_skin"),
            ]
        )
        ctx = server.make_context(char)
        with patch.object(CraftingService, "__init__", side_effect=AssertionError("Nie twórz drugiej instancji CraftingService")), patch.object(
            server.services.crafting,
            "craft",
            wraps=server.services.crafting.craft,
        ) as craft:
            result: str = asyncio.run(cast(Coroutine[Any, Any, str], server.dispatcher.execute_line(ctx, "craft torfowy napar")))
        self.assertIn("Tworzysz torfowy napar.", result)
        self.assertIn("Praktyczny napój dla tych, którzy wracają z mokradła po zmroku.", result)
        self.assertIn("torfowy napar", [item.name for item in char.inventory])
        craft.assert_called_once_with(char, "torfowy napar")

    def test_cast_is_not_registered_or_resolved_by_dispatcher(self) -> None:
        server = self.make_server()
        char = Character("caster")
        ctx = server.make_context(char)
        result: str = asyncio.run(cast(Coroutine[Any, Any, str], server.dispatcher.execute_line(ctx, "cast wzmocnienie")))
        self.assertEqual(result, "Nie rozpoznajesz takiego polecenia.")
        self.assertNotIn("cast", server.dispatcher.commands)

    def test_system_handler_delegates_to_service(self) -> None:
        server = self.make_server()
        server.repo.register("saver", "pw")
        char = server.repo.load("saver")
        ctx = server.make_context(char)
        result: str = asyncio.run(cast(Coroutine[Any, Any, str], server.cmd_save(ctx, None, 1)))
        self.assertEqual(result, "Postać została zapisana.")

    def test_remaining_command_handlers_are_thin_after_d5(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative in [
            "astergard/commands/exploration.py",
            "astergard/commands/communication.py",
            "astergard/commands/crafting.py",
            "astergard/commands/system.py",
        ]:
            line_count = len((root / relative).read_text(encoding="utf-8").splitlines())
            self.assertLess(line_count, 35, relative)


if __name__ == "__main__":
    unittest.main()

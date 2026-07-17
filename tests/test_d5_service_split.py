from __future__ import annotations

import asyncio
from typing import Any, Coroutine, cast
import tempfile
import unittest
from pathlib import Path

from astergard.characters.models import Character
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
        self.assertIsNotNone(server.services.magic_crafting_service)
        self.assertIsNotNone(server.services.system_service)

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
            "astergard/commands/magic_crafting.py",
            "astergard/commands/system.py",
        ]:
            line_count = len((root / relative).read_text(encoding="utf-8").splitlines())
            self.assertLess(line_count, 35, relative)


if __name__ == "__main__":
    unittest.main()

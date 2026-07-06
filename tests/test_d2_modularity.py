from __future__ import annotations

import asyncio
import tempfile
import unittest

from astergard.server.game import GameContext, GameServer


class D2ModularityTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=True)
        return GameServer(tmp.name)

    def test_command_dispatcher_uses_external_handlers(self) -> None:
        server = self.make_server()
        handler = server.dispatcher.commands["oferta"]
        self.assertEqual(handler.__module__, "astergard.commands.economy")
        self.assertIn("polnoc", server.dispatcher.commands)

    def test_compatibility_command_aliases_still_work(self) -> None:
        server = self.make_server()
        char = server.repo.load("missing") if False else __import__("astergard.characters.models", fromlist=["Character"]).Character("tester")
        ctx = server.make_context(char)
        result = asyncio.run(server.cmd_inventory(ctx, None, 1))
        self.assertIn("Wyposażenie", result)

    def test_server_game_is_orchestration_layer(self) -> None:
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        line_count = len((root / "astergard" / "server" / "game.py").read_text(encoding="utf-8").splitlines())
        self.assertLess(line_count, 220)


if __name__ == "__main__":
    unittest.main()

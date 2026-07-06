from __future__ import annotations

import unittest
from pathlib import Path

from astergard.characters.models import Character
from astergard.server.game import GameServer


class ContextPortTests(unittest.TestCase):
    def test_context_has_no_server_escape_hatch(self) -> None:
        server = GameServer(":memory:")
        ctx = server.make_context(Character("tester"))
        self.assertFalse(hasattr(ctx, "server"))
        self.assertIs(ctx.world, server.world)
        self.assertIs(ctx.repo, server.repo)

    def test_application_and_command_layers_do_not_reference_ctx_server(self) -> None:
        root = Path(__file__).resolve().parents[1] / "astergard"
        scanned = []
        for rel in ("commands", "application/services"):
            for path in (root / rel).rglob("*.py"):
                scanned.append(path)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("ctx.server", text, str(path))
        self.assertGreater(len(scanned), 5)

    def test_context_room_presence_port_is_callable(self) -> None:
        server = GameServer(":memory:")
        char = Character("tester")
        char.room_id = 0
        ctx = server.make_context(char)
        server.clients[object()] = char  # type: ignore[index]
        self.assertEqual(ctx.players_in_room(0), [char])


if __name__ == "__main__":
    unittest.main()

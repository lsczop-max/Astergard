from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.application.context_assembler import GameContextAssembler
from astergard.characters.models import Character
from astergard.server.context import GameContext
from astergard.server.game import GameServer


class D9ContextAssemblyTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_game_context_does_not_store_service_container(self) -> None:
        server = self.make_server()
        ctx = server.make_context(Character("tester"))
        self.assertIsInstance(ctx, GameContext)
        self.assertFalse(hasattr(ctx, "_services"))
        self.assertFalse(hasattr(ctx, "services"))
        self.assertIs(ctx.exploration().world, server.world)
        self.assertIs(ctx.system_context().repo, server.repo)

    def test_game_context_module_has_no_game_services_import_or_field(self) -> None:
        path = Path(__file__).resolve().parents[1] / "astergard" / "server" / "context.py"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("from astergard.application.bootstrap import GameServices", text)
        self.assertNotIn("_services", text)
        self.assertNotIn("services:", text)

    def test_context_assembler_builds_all_use_case_ports(self) -> None:
        server = self.make_server()
        assembler = GameContextAssembler(server.services, server.get_players_in_room, server.move_direct)
        ctx = assembler.build(Character("tester"), current_command="look")
        self.assertEqual("look", ctx.exploration().current_command)
        self.assertIs(ctx.inventory().world, server.world)
        self.assertIs(ctx.combat_context().combat, server.combat)
        self.assertIs(ctx.economy_context().economy, server.economy)


if __name__ == "__main__":
    unittest.main()

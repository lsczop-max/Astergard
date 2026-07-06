from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.application.use_case_contexts import ExplorationContext, SystemContext
from astergard.characters.models import Character
from astergard.server.game import GameServer


class D7UseCaseContextTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_game_context_builds_narrow_contexts(self) -> None:
        server = self.make_server()
        ctx = server.make_context(Character("ctx"))
        self.assertIsInstance(ctx.exploration(), ExplorationContext)
        self.assertIsInstance(ctx.system_context(), SystemContext)
        self.assertIs(ctx.exploration().world, server.world)
        self.assertIs(ctx.system_context().repo, server.repo)

    def test_game_context_does_not_expose_public_services_container(self) -> None:
        server = self.make_server()
        ctx = server.make_context(Character("ctx"))
        self.assertFalse(hasattr(ctx, "services"))
        self.assertFalse(hasattr(ctx, "server"))

    def test_application_services_use_narrow_context_imports(self) -> None:
        root = Path(__file__).resolve().parents[1] / "astergard" / "application" / "services"
        for path in root.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("from astergard.server.context import GameContext", text, str(path))


if __name__ == "__main__":
    unittest.main()

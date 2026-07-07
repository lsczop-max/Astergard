from __future__ import annotations

import asyncio
import tempfile
import unittest

from astergard.characters.models import Character
from astergard.commands.engine import PermissionLevel
from astergard.commands.dispatcher import CommandDispatcher
from astergard.server.game import GameServer


class CommandEngineD24Tests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_dispatcher_keeps_metadata_for_registered_commands(self) -> None:
        server = self.make_server()
        spec = server.dispatcher.registry.get("wez")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.metadata.canonical_name, "get")
        self.assertEqual(spec.metadata.usage, "wez <przedmiot>")
        self.assertTrue(spec.metadata.argument.required)
        self.assertIn("weź", spec.aliases)

    def test_help_is_generated_from_command_registry(self) -> None:
        async def scenario() -> None:
            server = self.make_server()
            ctx = server.make_context(Character("tester"))
            general = await server.dispatcher.execute_line(ctx, "pomoc")
            self.assertIn("Dostępne komendy", general)
            self.assertIn("Eksploracja", general)
            detail = await server.dispatcher.execute_line(ctx, "pomoc wez")
            self.assertIn("get:", detail)
            self.assertIn("Użycie: wez <przedmiot>", detail)
        asyncio.run(scenario())

    def test_required_argument_validation_runs_before_handler(self) -> None:
        async def scenario() -> None:
            server = self.make_server()
            ctx = server.make_context(Character("tester"))
            response = await server.dispatcher.execute_line(ctx, "wez")
            self.assertIn("Brakuje argumentu", response)
            self.assertIn("wez <przedmiot>", response)
        asyncio.run(scenario())

    def test_cooldown_blocks_immediate_reuse(self) -> None:
        async def scenario() -> None:
            server = self.make_server()
            ctx = server.make_context(Character("tester"))
            first = await server.dispatcher.execute_line(ctx, "szukaj")
            second = await server.dispatcher.execute_line(ctx, "szukaj")
            self.assertNotIn("Poczekaj", first)
            self.assertIn("Poczekaj", second)
        asyncio.run(scenario())

    def test_admin_permission_is_enforced_by_dispatcher(self) -> None:
        async def admin_only(ctx, arg, index):
            return "secret"

        async def scenario() -> None:
            dispatcher = CommandDispatcher()
            from astergard.commands.engine import CommandMetadata
            dispatcher.register(
                "sekret",
                admin_only,
                CommandMetadata(
                    canonical_name="secret",
                    description="Admin only.",
                    usage="sekret",
                    permission=PermissionLevel.ADMIN,
                ),
                aliases=["sekret"],
            )
            server = self.make_server()
            ctx = server.make_context(Character("tester"))
            denied = await dispatcher.execute_line(ctx, "sekret")
            self.assertIn("Nie masz uprawnień", denied)
            admin_ctx = server.make_context(Character("admin"))
            allowed = await dispatcher.execute_line(admin_ctx, "sekret")
            self.assertEqual(allowed, "secret")
        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()

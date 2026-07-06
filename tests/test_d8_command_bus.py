from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.commands.registration import build_command_bus
from astergard.server.game import GameServer


class D8CommandBusTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        return GameServer(tmp.name)

    def test_command_bus_binds_services_before_runtime(self) -> None:
        server = self.make_server()
        bus = build_command_bus(server.services)
        self.assertIn("inventory", bus.handlers)
        self.assertIn("move", bus.handlers)
        self.assertIn("wez", bus.aliases["get"])
        self.assertIn("polnoc", bus.direction_names)

    def test_command_modules_do_not_reach_into_private_service_container(self) -> None:
        root = Path(__file__).resolve().parents[1] / "astergard" / "commands"
        for path in root.glob("*.py"):
            if path.name == "registration.py":
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("ctx._services", text, str(path))
            self.assertNotIn("ctx.services", text, str(path))
            self.assertNotIn("GameServices", text, str(path))

    def test_server_compatibility_methods_are_dispatcher_bound(self) -> None:
        server = self.make_server()
        self.assertIs(server.cmd_offer, server.dispatcher.commands["oferta"])
        self.assertEqual(server.dispatcher.commands["oferta"].__module__, "astergard.commands.economy")


if __name__ == "__main__":
    unittest.main()

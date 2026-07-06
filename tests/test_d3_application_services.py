from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.application.bootstrap import GameBootstrapper, GameServices
from astergard.application.heartbeat import HeartbeatService
from astergard.characters.models import Character
from astergard.server.game import GameServer


class D3ApplicationServiceTests(unittest.TestCase):
    def test_bootstrapper_builds_complete_service_graph(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            services = GameBootstrapper(tmp.name).build()
        self.assertIsInstance(services, GameServices)
        self.assertEqual(len(services.world.locations), 500)
        self.assertIn("oferta", services.dispatcher.commands)
        self.assertGreater(sum(len(loc.npc_ids) for loc in services.world.locations.values()), 0)

    def test_heartbeat_tick_is_testable_without_network_server(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            server = GameServer(tmp.name)
        char = Character("tick")
        char.stats.kondycja = 1
        heartbeat = HeartbeatService(server.services, lambda: [char])
        heartbeat.tick_once()
        self.assertGreater(char.stats.kondycja, 1)

    def test_server_game_delegates_bootstrap_and_flow(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "astergard" / "server" / "game.py").read_text(encoding="utf-8")
        self.assertIn("GameBootstrapper", text)
        self.assertIn("SessionFlow", text)
        self.assertIn("HeartbeatService", text)
        self.assertLess(len(text.splitlines()), 180)


if __name__ == "__main__":
    unittest.main()

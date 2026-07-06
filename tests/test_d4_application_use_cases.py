from __future__ import annotations

import asyncio
from typing import Any, Coroutine, cast
import tempfile
import unittest
from pathlib import Path

from astergard.characters.models import Character
from astergard.items.models import Item
from astergard.server.game import GameContext, GameServer


class D4ApplicationUseCaseTests(unittest.TestCase):
    def make_server(self) -> GameServer:
        tmp = tempfile.NamedTemporaryFile(delete=True)
        return GameServer(tmp.name)

    def test_inventory_handler_delegates_to_application_service(self) -> None:
        server = self.make_server()
        char = Character("inv")
        ctx = server.make_context(char)
        result: str = asyncio.run(cast(Coroutine[Any, Any, str], server.cmd_inventory(ctx, None, 1)))
        self.assertIn("Wyposażenie", result)
        self.assertIs(server.services.inventory_service, server.services.inventory_service)

    def test_inventory_service_moves_item_from_room_to_character(self) -> None:
        server = self.make_server()
        char = Character("getter")
        char.inventory.clear()
        loc = server.world.get_location(char.room_id)
        self.assertIsNotNone(loc)
        assert loc is not None
        loc.items.append(Item("testowy kamień", "", 0.1, 1, "stone"))
        message = server.services.inventory_service.get_item(char, loc, "kamień", 1)
        self.assertIn("Podnosisz", message)
        self.assertEqual(len(char.inventory), 1)
        self.assertFalse(any(item.name == "testowy kamień" for item in loc.items))

    def test_combat_service_owns_corpse_quest_and_faction_coordination(self) -> None:
        server = self.make_server()
        src = Path(__file__).resolve().parents[1] / "astergard" / "application" / "services" / "combat_service.py"
        text = src.read_text(encoding="utf-8")
        self.assertIn("register_kill", text)
        self.assertIn("progress", text)
        self.assertIn("_spawn_corpse", text)

    def test_command_handlers_are_thin_after_d4(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative in [
            "astergard/commands/inventory.py",
            "astergard/commands/combat.py",
            "astergard/commands/economy.py",
            "astergard/commands/social_systems.py",
        ]:
            line_count = len((root / relative).read_text(encoding="utf-8").splitlines())
            self.assertLess(line_count, 45, relative)

    def test_bootstrap_uses_same_manager_instances_for_use_cases(self) -> None:
        server = self.make_server()
        self.assertIs(server.services.combat_service.combat, server.combat)
        self.assertIs(server.services.combat_service.quests, server.quests)
        self.assertIs(server.services.quest_service.quests, server.quests)
        self.assertIs(server.services.economy_service.economy, server.economy)


if __name__ == "__main__":
    unittest.main()

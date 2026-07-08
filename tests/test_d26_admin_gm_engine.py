from __future__ import annotations

import asyncio
import unittest

from astergard.admin.permissions import AdminRole, has_role, role_for_actor
from astergard.testing import TestGameHarness


class D26AdminGMEngineTests(unittest.TestCase):
    def test_player_cannot_use_gm_command(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                player = harness.create_character("plain")
                transcript = await harness.execute(player, "worldstats")
                self.assertIn("Nie masz uprawnień", transcript.output)

        asyncio.run(run())

    def test_gm_can_inspect_and_teleport_player(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                gm = harness.create_character("gm")
                gm.admin_role = "gm"
                target = harness.create_character("target", room_id=0)
                inspect_result = await harness.execute(gm, "inspect target")
                self.assertIn("Gracz: target", inspect_result.output)
                teleport_result = await harness.execute(gm, "teleport target 5")
                self.assertIn("Teleportowano target", teleport_result.output)
                self.assertEqual(target.room_id, 5)

        asyncio.run(run())

    def test_admin_can_save_world_and_audit_action(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                admin = harness.create_character("adminuser")
                admin.admin_role = "admin"
                result = await harness.execute(admin, "saveworld")
                self.assertIn("Świat zapisano", result.output)
                audit = await harness.execute(admin, "auditlog 5")
                self.assertIn("saveworld", audit.output)

        asyncio.run(run())

    def test_destructive_kill_requires_confirmation(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                admin = harness.create_character("killer")
                admin.admin_role = "admin"
                target = harness.create_character("victim")
                denied = await harness.execute(admin, "adminkill victim")
                self.assertIn("confirm", denied.output)
                self.assertTrue(target.is_alive)
                killed = await harness.execute(admin, "adminkill victim confirm")
                self.assertIn("Zabito victim", killed.output)
                self.assertFalse(target.is_alive)

        asyncio.run(run())

    def test_gm_can_spawn_npc_and_list_sessions(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                gm = harness.create_character("spawner")
                gm.admin_role = "gm"
                before = len(harness.require_server().npcs.npcs)
                spawned = await harness.execute(gm, "spawnnpc wolf 0")
                self.assertIn("Zespawnowano NPC", spawned.output)
                self.assertGreater(len(harness.require_server().npcs.npcs), before)
                worldstats = await harness.execute(gm, "worldstats")
                self.assertIn("Jak wygląda świat", worldstats.output)
                sessions = await harness.execute(gm, "listsessions")
                self.assertIn("Kto jest teraz w świecie", sessions.output)
                self.assertIn("spawner", sessions.output)

        asyncio.run(run())

    def test_permission_roles_ordering(self) -> None:
        class Actor:
            username = "someone"
            admin_role = "gm"

        self.assertEqual(role_for_actor(Actor()), AdminRole.GM)
        self.assertTrue(has_role(Actor(), AdminRole.HELPER))
        self.assertFalse(has_role(Actor(), AdminRole.ADMIN))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import unittest

from astergard.testing import TestGameHarness
from astergard.world.content import make_content_pack
from astergard.world.manager import WorldManager


class D33WorldContentFrameworkTests(unittest.TestCase):
    def test_content_pack_overlays_named_rooms_without_changing_world_size(self) -> None:
        world = WorldManager()
        world.generate_world()
        self.assertEqual(len(world.locations), 483)
        self.assertEqual(world.locations[0].name, "Brama Dymnych Chorągwi")
        self.assertIn("brama", world.locations[0].inspectables)
        self.assertTrue(any(item.vnum == "iron_key" for item in world.locations[0].items))
        self.assertGreaterEqual(len(make_content_pack()), 6)

    def test_look_shows_room_story_without_menu_like_hints(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("d33_look")
                transcript = await harness.execute(char, "spojrz")
                self.assertIn("Brama Dymnych Chorągwi", transcript.output)
                self.assertNotIn("Możesz obejrzeć", transcript.output)
                self.assertIn("brama", transcript.output.lower())

        asyncio.run(run())

    def test_player_can_inspect_authored_detail_with_polish_alias(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("d33_detail")
                transcript = await harness.execute(char, "obejrzyj brame")
                self.assertIn("okuta żelazem", transcript.output)

        asyncio.run(run())

    def test_content_pack_adds_distinct_room_identity_after_movement(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("d33_move")
                transcript = await harness.execute(char, "wschod")
                self.assertIn("Kierujesz się na wschód.", transcript.output)
                self.assertIn("Plac Przed Wartownią", transcript.output)
                self.assertNotIn("Możesz obejrzeć", transcript.output)
                detail = await harness.execute(char, "spojrz na wartownie")
                self.assertIn("Okna wychodzą na plac", detail.output)

    def test_sense_commands_expose_senses_and_respect_context(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("d33_sense")
                char.room_id = 21
                smell = await harness.execute(char, "powachaj")
                self.assertTrue("Pachnie" in smell.output or "Czujesz" in smell.output)
                touch = await harness.execute(char, "dotknij kamienia")
                self.assertIn("Kamień", touch.output)

        asyncio.run(run())

    def test_ambient_world_message_is_rendered_once(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                char = harness.create_character("d33_ambient")
                zone = server.world.locations[char.room_id].zone
                server.world.set_ambient_message(zone, "Przeleci kruk nad bramą.")
                first = await harness.execute(char, "spojrz")
                self.assertIn("Przeleci kruk", first.output)
                second = await harness.execute(char, "spojrz")
                self.assertNotIn("Przeleci kruk", second.output)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

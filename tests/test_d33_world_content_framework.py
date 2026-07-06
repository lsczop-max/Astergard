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
        self.assertEqual(len(world.locations), 500)
        self.assertEqual(world.locations[0].name, "Brama Dymnych Chorągwi")
        self.assertIn("brama", world.locations[0].inspectables)
        self.assertTrue(any(item.vnum == "iron_key" for item in world.locations[0].items))
        self.assertGreaterEqual(len(make_content_pack()), 6)

    def test_look_lists_inspectable_details_in_start_room(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("d33_look")
                transcript = await harness.execute(char, "spojrz")
                self.assertIn("Brama Dymnych Chorągwi", transcript.output)
                self.assertIn("Możesz obejrzeć", transcript.output)
                self.assertIn("brama", transcript.output)

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
                await harness.execute(char, "poludnie")
                transcript = await harness.execute(char, "spojrz")
                self.assertIn("Trakt Przy Murze", transcript.output)
                self.assertIn("Możesz obejrzeć", transcript.output)
                detail = await harness.execute(char, "spojrz na mur")
                self.assertIn("szczeliny obserwacyjne", detail.output)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

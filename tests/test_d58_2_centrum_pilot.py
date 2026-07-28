from __future__ import annotations

import asyncio
import unittest

from astergard.testing import TestGameHarness
from astergard.world.region_i_content import load_region_i_pilot_content
from astergard.world.manager import WorldManager


class D582CentrumPilotTests(unittest.TestCase):
    def test_runtime_pilot_asset_has_exactly_fifteen_unique_rooms(self) -> None:
        pilots = load_region_i_pilot_content()
        room_ids = [pilot.id for pilot in pilots]
        self.assertEqual(len(pilots), 15)
        self.assertEqual(len(set(room_ids)), 15)
        self.assertEqual(sorted(room_ids), sorted({81, 14, 77, 78, 79, 80, 1, 0, 22, 24, 21, 23, 20, 58, 64}))

    def test_pilot_rooms_are_active_and_match_authoring(self) -> None:
        world = WorldManager()
        world.generate_world()
        pilots = load_region_i_pilot_content()

        for pilot in pilots:
            location = world.locations[pilot.id]
            self.assertEqual(location.name, pilot.name, pilot.id)
            self.assertEqual(location.description, pilot.description, pilot.id)
            self.assertTrue(set(pilot.inspectables).issubset(location.inspectables), pilot.id)
            self.assertEqual(location.dynamic_hooks, pilot.dynamic_hooks, pilot.id)

    def test_pilot_look_command_uses_active_description(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("pilot", room_id=14)
                transcript = await harness.execute(char, "spojrz")
                self.assertIn("Karczma pod Żurawiem", transcript.output)
                self.assertIn("Dym z paleniska", transcript.output)
                self.assertIn("szynkwasem", transcript.output)

        asyncio.run(run())

    def test_runtime_pilot_rooms_keep_technical_inspectables(self) -> None:
        world = WorldManager()
        world.generate_world()
        location = world.locations[14]
        self.assertGreaterEqual(len(location.inspectables), 3)
        self.assertIn("palenisko", location.inspectables)
        self.assertIn("szyld", location.inspectables)
        self.assertIn("szynkwas", location.inspectables)


if __name__ == "__main__":
    unittest.main()

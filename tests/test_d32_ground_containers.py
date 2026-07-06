from __future__ import annotations

import asyncio
import unittest

from astergard.items.models import Item
from astergard.testing import TestGameHarness


class D32GroundContainerTests(unittest.TestCase):
    def test_take_specific_index_from_ground_container(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                char = harness.create_character("d32_index")
                loc = server.world.get_location(char.room_id)
                assert loc is not None
                chest = Item("drewniana skrzynia", "Stara skrzynia.", 3.0, 5, "wooden_chest", is_container=True, capacity=20)
                chest.contains.append(Item("krótki miecz", "Pierwszy miecz.", 1.0, 3, "short_sword"))
                chest.contains.append(Item("krótki miecz", "Drugi miecz.", 1.0, 3, "short_sword"))
                loc.items.append(chest)
                result = await harness.execute(char, "wez drugi miecz z skrzyni")
                self.assertIn("Wyjmujesz krótki miecz", result.output)
                self.assertEqual(len(chest.contains), 1)
                self.assertEqual(len([item for item in char.inventory if item.name == "krótki miecz"]), 1)
        asyncio.run(run())

    def test_search_ground_container_renders_contents(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                char = harness.create_character("d32_search")
                loc = server.world.get_location(char.room_id)
                assert loc is not None
                chest = Item("żelazna skrzynia", "Ciężka skrzynia.", 4.0, 10, "iron_chest", is_container=True, capacity=20)
                chest.contains.append(Item("zardzewiały klucz", "Klucz z plamami rdzy.", 0.1, 1, "rusty_key"))
                loc.items.append(chest)
                result = await harness.execute(char, "przeszukaj skrzynie")
                self.assertIn("W żelazna skrzynia widzisz", result.output)
                self.assertIn("zardzewiały klucz", result.output)
        asyncio.run(run())

    def test_transfer_between_ground_and_inventory_containers(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                char = harness.create_character("d32_transfer")
                loc = server.world.get_location(char.room_id)
                assert loc is not None
                backpack = Item("skórzany plecak", "Pojemny plecak.", 0.8, 8, "leather_backpack", is_container=True, capacity=20)
                chest = Item("skrzynia", "Skrzynia przy ścianie.", 2.0, 3, "chest", is_container=True, capacity=20)
                key = Item("mosiężny klucz", "Żółtawy klucz.", 0.1, 1, "brass_key")
                chest.contains.append(key)
                char.inventory.append(backpack)
                loc.items.append(chest)
                result = await harness.execute(char, "przeloz klucz z skrzyni do plecaka")
                self.assertIn("Przekładasz mosiężny klucz", result.output)
                self.assertEqual(chest.contains, [])
                self.assertEqual(backpack.contains[0].vnum, "brass_key")
        asyncio.run(run())

    def test_put_item_into_ground_container(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                char = harness.create_character("d32_put_ground")
                loc = server.world.get_location(char.room_id)
                assert loc is not None
                chest = Item("skrzynia", "Skrzynia.", 2.0, 3, "chest", is_container=True, capacity=20)
                ring = Item("srebrny pierścień", "Prosty pierścień.", 0.1, 4, "silver_ring")
                loc.items.append(chest)
                char.inventory.append(ring)
                result = await harness.execute(char, "wloz pierscien do skrzyni")
                self.assertIn("Wkładasz srebrny pierścień", result.output)
                self.assertEqual(chest.contains[0].vnum, "silver_ring")
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

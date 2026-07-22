from __future__ import annotations

import asyncio
import unittest

from astergard.items.models import Item
from astergard.testing import TestGameHarness


class EquipmentSlotTests(unittest.TestCase):
    def test_wear_equips_canonical_slot_and_blocks_second_item(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("slot_user", room_id=60)
            amulet_a = Item(
                "amulet odwagi",
                "Prosty amulet.",
                0.1,
                10,
                "amulet_a",
                slot="amulet",
                wearable=True,
            )
            amulet_b = Item(
                "amulet mocy",
                "Drugi amulet.",
                0.1,
                10,
                "amulet_b",
                slot="amulet",
                wearable=True,
            )
            character.inventory.extend([amulet_a, amulet_b])

            first = server.services.inventory_service.wear_item(character, "amulet odwagi", 1)
            second = server.services.inventory_service.wear_item(character, "amulet mocy", 1)

            self.assertIn("Zakładasz amulet odwagi.", first)
            self.assertIn("Na miejscu amuletu już coś nosisz.", second)
            self.assertIs(character.equipment["amulet"], amulet_a)
            self.assertIn(amulet_b, character.inventory)

    def test_wear_rejects_shield_when_two_handed_weapon_is_equipped(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("slot_user", room_id=60)
            halberd = Item(
                "halabarda strażnicza",
                "Długa broń.",
                3.4,
                20,
                "watch_halberd",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="halabarda",
                weapon_profile_id="watch_halberd",
            )
            shield = Item(
                "okrągła tarcza",
                "Osłona.",
                2.0,
                12,
                "round_shield",
                item_type="shield",
                slot="tarcza",
                wearable=True,
                weapon_type="tarcza",
            )
            character.inventory.extend([halberd, shield])

            first = server.services.inventory_service.wear_item(character, "halabarda strażnicza", 1)
            second = server.services.inventory_service.wear_item(character, "okrągła tarcza", 1)

            self.assertIn("Zakładasz halabarda strażnicza.", first)
            self.assertIn("Najpierw odłóż broń dwuręczną", second)
            self.assertIs(character.equipment["bron_glowna"], halberd)
            self.assertIsNone(character.equipment["tarcza"])
            self.assertIn(shield, character.inventory)

    def test_wear_rejects_two_handed_weapon_when_shield_is_equipped(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("slot_user", room_id=60)
            sword = Item(
                "prosty miecz",
                "Krótka broń.",
                1.2,
                20,
                "garrison_short_sword",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="miecz",
                weapon_profile_id="garrison_short_sword",
            )
            halberd = Item(
                "halabarda strażnicza",
                "Długa broń.",
                3.4,
                20,
                "watch_halberd",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="halabarda",
                weapon_profile_id="watch_halberd",
            )
            shield = Item(
                "okrągła tarcza",
                "Osłona.",
                2.0,
                12,
                "round_shield",
                item_type="shield",
                slot="tarcza",
                wearable=True,
                weapon_type="tarcza",
            )
            character.inventory.extend([sword, halberd, shield])

            first = server.services.inventory_service.wear_item(character, "okrągła tarcza", 1)
            second = server.services.inventory_service.wear_item(character, "halabarda strażnicza", 1)

            self.assertIn("Zakładasz okrągła tarcza.", first)
            self.assertIn("Najpierw zdejmij tarczę", second)
            self.assertIs(character.equipment["tarcza"], shield)
            self.assertIsNone(character.equipment["bron_glowna"])
            self.assertIn(halberd, character.inventory)

    def test_remove_frees_slot_and_returns_item_to_inventory(self) -> None:
        with TestGameHarness() as harness:
            character = harness.create_character("slot_user", room_id=60)
            ring = Item(
                "pierścień strażnika",
                "Prosty pierścień.",
                0.1,
                12,
                "ring_1",
                slot="pierscien_1",
                wearable=True,
            )
            character.inventory.append(ring)

            wear = asyncio.run(harness.execute(character, "zaloz pierścień strażnika"))
            remove = asyncio.run(harness.execute(character, "zdejmij pierścień strażnika"))

            self.assertIn("Zakładasz pierścień strażnika.", wear.output)
            self.assertIn("Zdejmujesz pierścień strażnika.", remove.output)
            self.assertIsNone(character.equipment["pierscien_1"])
            self.assertIn(ring, character.inventory)

    def test_old_alias_slots_map_to_new_canonical_slots(self) -> None:
        with TestGameHarness() as harness:
            character = harness.create_character("alias_user", room_id=60)
            sword = Item(
                "stary miecz",
                "Stara broń.",
                1.0,
                10,
                "old_sword",
                item_type="weapon",
                slot="prawa_reka",
                wearable=True,
                weapon_type="miecz",
            )
            shield = Item(
                "stara tarcza",
                "Stara tarcza.",
                2.0,
                10,
                "old_shield",
                item_type="shield",
                slot="lewa_reka",
                wearable=True,
                weapon_type="tarcza",
            )
            character.equipment["prawa_reka"] = sword
            character.equipment["lewa_reka"] = shield

            self.assertIs(character.equipment["bron_glowna"], sword)
            self.assertIs(character.equipment["bron_pomocnicza"], shield)

    def test_save_load_preserves_new_slots(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("persist", "secret"))
            character = server.repo.load("persist")
            character.equipment["amulet"] = Item(
                "amulet testowy",
                "Testowy amulet.",
                0.1,
                5,
                "test_amulet",
                slot="amulet",
                wearable=True,
            )
            character.equipment["bron_glowna"] = Item(
                "testowy miecz",
                "Testowy miecz.",
                1.2,
                20,
                "test_sword",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="miecz",
            )
            server.repo.save(character)
            loaded = server.repo.load("persist")
            self.assertIsNotNone(loaded.equipment["amulet"])
            self.assertIsNotNone(loaded.equipment["bron_glowna"])
            assert loaded.equipment["amulet"] is not None
            assert loaded.equipment["bron_glowna"] is not None
            self.assertEqual(loaded.equipment["amulet"].slot, "amulet")
            self.assertEqual(loaded.equipment["bron_glowna"].slot, "bron_glowna")

    def test_inventory_renders_full_slot_list_and_look_shows_equipment(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("hero", room_id=60)
            observer = harness.create_character("observer", room_id=60)
            hero.equipment["bron_glowna"] = Item(
                "testowy miecz",
                "Testowy miecz.",
                1.2,
                20,
                "hero_sword",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="miecz",
            )
            observer.equipment["tarcza"] = Item(
                "tarcza testowa",
                "Testowa tarcza.",
                2.0,
                10,
                "observer_shield",
                item_type="shield",
                slot="tarcza",
                wearable=True,
                weapon_type="tarcza",
            )

            inventory_text = server.services.inventory_service.render_inventory(hero)

            async def run_look() -> str:
                return await server.services.dispatcher.commands["look"](
                    server.make_context(hero),
                    None,
                    1,
                )

            look_text = asyncio.run(run_look())
            ob_text = asyncio.run(harness.execute(hero, "ob siebie"))
            self.assertIn("Wyposażenie przy tobie: testowy miecz", inventory_text)
            self.assertIn("Obciążenie: niewielkie", inventory_text)
            self.assertIn("Jesteś", ob_text.output)
            self.assertIn("Twoją prawą rękę zajmuje: testowy miecz.", ob_text.output)
            self.assertNotIn("tarcza testowa", ob_text.output)
            self.assertIn("tarcza", look_text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from astergard.characters.models import Character
from astergard.commands.parser import CommandParser
from astergard.crafting.services import CraftingService
from astergard.items.models import Item


class D45QualityPassTests(unittest.TestCase):
    def test_parser_understands_multiword_direction_phrases(self) -> None:
        self.assertEqual(CommandParser.parse("na północ").command, "polnoc")
        self.assertEqual(CommandParser.parse("w górę").command, "gora")
        self.assertEqual(CommandParser.parse("do środka").command, "do srodka")

    def test_equipment_summary_reads_naturally(self) -> None:
        character = Character("tester")
        character.equipment["glowa"] = Item("hełm", "Prosty hełm.", 1.0, 10, "helm", "armor", "glowa", protection=1)
        character.equipment["bron_glowna"] = Item("miecz", "Broń do walki.", 1.5, 15, "sword", "weapon", "bron_glowna", wearable=True, weapon_type="miecz")
        character.equipment["tarcza"] = Item("tarcza", "Drewniana tarcza.", 2.0, 12, "shield", "shield", "tarcza", wearable=True, weapon_type="tarcza", protection=1, shield_block=2)

        summary = character.equipment_summary()
        self.assertIn("hełm na głowie", summary)
        self.assertIn("miecz w prawej dłoni", summary)
        self.assertIn("tarcza", summary)
        self.assertNotIn("broń główna", summary)

    def test_crafting_matches_normalized_local_ingredients(self) -> None:
        character = Character("craft")
        character.skills.state("pierwsza_pomoc")["level"] = 2
        character.inventory.extend(
            [
                Item("Torfowe ziele", "Świeżo zebrane.", 0.1, 4, "bagna_bog_herb"),
                Item("woda w bukłaku", "Woda.", 1.0, 1, "waterskin"),
            ]
        )

        output = CraftingService().craft(character, "napar torfowy")
        self.assertIn("Tworzysz torfowy napar", output)
        self.assertTrue(any(item.vnum == "bog_tea" for item in character.inventory))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import tempfile
import unittest
from typing import Any, cast

from astergard.characters.creation import CharacterCreationError, CharacterCreationProfile
from astergard.characters.professions import ProfessionError, ProfessionSelection
from astergard.database.repository import PlayerRepository
from astergard.testing import FakeReader, FakeWriter, TestGameHarness as GameHarness


class CharacterCreatorTests(unittest.TestCase):
    def test_new_character_flow_creates_profile_origin_items_and_professions(self) -> None:
        async def run() -> None:
            with GameHarness() as harness:
                reader = FakeReader.from_text_lines(
                    [
                        "nowy_gracz",
                        "sekret",
                        "Ala",
                        "kobiecy opis",
                        "24",
                        "2",
                        "Podgrodzie",
                        "tradycyjna",
                        "wyznanie społeczne",
                        "6",
                        "bard",
                        "Wysoka, ciemnowłosa kobieta z blizną na dłoni.",
                        "Wychowała się przy targu i zna ceny lepiej niż mapy.",
                    ]
                )
                writer = FakeWriter()
                result = await harness.require_server().session_flow.login(cast(Any, reader), cast(Any, writer))
                assert result.character is not None
                char = result.character
                self.assertEqual(char.name, "Ala")
                self.assertEqual(char.origin, "chlop_z_podgrodzia")
                self.assertEqual(char.starting_reputation, 5)
                self.assertEqual(char.global_reputation, 5)
                self.assertEqual(char.main_profession, "lucznik")
                self.assertEqual(char.secondary_profession, "bard")
                self.assertEqual(char.combat_style, "ofensywny")
                self.assertIn("hunting_bow", [item.vnum for item in char.equipment.values() if item is not None])
                self.assertIn("lute", [item.vnum for item in char.inventory])
                self.assertIn("luki", char.skills.values)
                self.assertGreaterEqual(char.skills.values["luki"]["level"], 3)
                self.assertIn("muzyka", char.skills.values)
                self.assertGreaterEqual(char.skills.values["muzyka"]["level"], 3)
                self.assertIn("Wybierz profesję główną", writer.text())

        asyncio.run(run())

    def test_profile_roundtrip_persists_creator_data_and_professions(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            profile = CharacterCreationProfile.build(
                name="Marek",
                gender_description="mężczyzna",
                age="31",
                origin="mieszczanin Astergardu",
                birth_region="Astergard",
                culture="miejską",
                religion="wyznanie społeczne",
                main_profession="szermierz",
                secondary_profession="kowal",
                appearance="Krótko ostrzyżony kupiecki syn w czystym płaszczu.",
                history="Syn cechowego pisarza, który zna miejskie zwyczaje i handlowe skróty.",
            )
            self.assertTrue(repo.register("creator", "pw", profile))
            char = repo.load("creator")
            self.assertEqual(char.name, "Marek")
            self.assertEqual(char.origin, "mieszczanin_astergardu")
            self.assertEqual(char.main_profession, "szermierz")
            self.assertEqual(char.secondary_profession, "kowal")
            self.assertEqual(char.combat_style, "ofensywny")
            self.assertIn("dueling_blade", [item.vnum for item in char.inventory] + [item.vnum for item in char.equipment.values() if item is not None])
            self.assertIn("smith_tools", [item.vnum for item in char.inventory])

            char.history = "Zmieniona historia po pierwszym zapisie."
            repo.save(char)
            loaded = repo.load("creator")
            self.assertEqual(loaded.name, "Marek")
            self.assertEqual(loaded.history, "Zmieniona historia po pierwszym zapisie.")
            self.assertEqual(loaded.main_profession, "szermierz")
            self.assertEqual(loaded.secondary_profession, "kowal")
            self.assertIn("dueling_blade", [item.vnum for item in loaded.inventory] + [item.vnum for item in loaded.equipment.values() if item is not None])

    def test_legacy_character_defaults_survive_missing_creator_json(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("legacy", "secret"))
            with repo.connection() as con:
                row = con.execute(
                    """
                    SELECT room_id,gold,stats_json,skills_json,wounds_json,reputation_json,global_reputation,local_reputation_json,
                           renown,title,crimes_json,wanted_level,wanted_posts_json,quests_json,completed_json,inventory_json,equipment_json,effects_json,combat_style
                    FROM players WHERE username=?
                    """,
                    ("legacy",),
                ).fetchone()
            assert row is not None
            char = repo.characters.serializer.hydrate("legacy", row)
            self.assertEqual(char.main_profession, "")
            self.assertEqual(char.secondary_profession, "")
            self.assertEqual(char.starting_reputation, 0)
            self.assertEqual(char.origin, "")

    def test_invalid_creation_data_is_rejected(self) -> None:
        with self.assertRaises(CharacterCreationError):
            CharacterCreationProfile.build(
                name="A",
                gender_description="mężczyzna",
                age="24",
                origin="mieszczanin Astergardu",
                birth_region="Astergard",
                culture="miejską",
                religion="wyznanie społeczne",
                main_profession="wojownik",
                secondary_profession=None,
                appearance="Wygląd",
                history="Poprawna historia o właściwej długości.",
            )

        with self.assertRaises(ProfessionError):
            CharacterCreationProfile.build(
                name="Ala",
                gender_description="mężczyzna",
                age="24",
                origin="mieszczanin Astergardu",
                birth_region="Astergard",
                culture="miejską",
                religion="wyznanie społeczne",
                main_profession="nieznana",
                secondary_profession=None,
                appearance="Wygląd",
                history="Poprawna historia o właściwej długości.",
            )

        with self.assertRaises(ProfessionError):
            CharacterCreationProfile.build(
                name="Ala",
                gender_description="mężczyzna",
                age="24",
                origin="mieszczanin Astergardu",
                birth_region="Astergard",
                culture="miejską",
                religion="wyznanie społeczne",
                main_profession="wojownik",
                secondary_profession="wojownik",
                appearance="Wygląd",
                history="Poprawna historia o właściwej długości.",
            )

    def test_duplicate_secondary_profession_is_blocked(self) -> None:
        selection = ProfessionSelection("wojownik")
        upgraded = selection.add_secondary("bard")
        self.assertEqual(upgraded.secondary_profession, "bard")
        with self.assertRaises(ProfessionError):
            upgraded.add_secondary("kowal")

    def test_profile_command_renders_full_character_profile(self) -> None:
        async def run() -> None:
            with GameHarness() as harness:
                reader = FakeReader.from_text_lines(
                    [
                        "profil_user",
                        "sekret",
                        "Marek",
                        "męski opis",
                        "31",
                        "1",
                        "Astergard",
                        "mieszczańska",
                        "wyznanie społeczne",
                        "1",
                        "0",
                        "Wysoki mężczyzna w prostym, czystym płaszczu.",
                        "Syn cechowego pisarza, który umie czytać rachunki i mapy.",
                    ]
                )
                writer = FakeWriter()
                result = await harness.require_server().session_flow.login(cast(Any, reader), cast(Any, writer))
                assert result.character is not None
                transcript = await harness.execute(result.character, "profil")
                self.assertIn("Imię: Marek", transcript.output)
                self.assertIn("Pochodzenie: mieszczanin Astergardu", transcript.output)
                self.assertIn("Profesja główna: wojownik", transcript.output)
                self.assertIn("Reputacja startowa: 25", transcript.output)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

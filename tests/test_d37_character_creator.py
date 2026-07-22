from __future__ import annotations

import asyncio
import tempfile
import unittest
import warnings
from typing import Any, cast

from astergard.characters.creation import CharacterCreationError, CharacterCreationProfile
from astergard.characters.professions import ProfessionError, ProfessionSelection
from astergard.database.repository import PlayerRepository
from astergard.application.session_transport import TcpSessionTransport
from astergard.testing import FakeReader, FakeWriter, TestGameHarness as GameHarness
from astergard.characters.appearance import appearance_profile_from_choices


class CharacterCreatorTests(unittest.TestCase):
    def test_new_character_flow_creates_profile_origin_items_and_professions(self) -> None:
        async def run() -> None:
            with GameHarness() as harness:
                reader = FakeReader.from_text_lines(
                    [
                        "nowy_gracz",
                        "sekret",
                        "Ala",
                        "kobieta",
                        "24",
                        "chłop z Podgrodzia",
                        "wieś",
                        "Podgrodzie",
                        "tradycyjna",
                        "wyznanie społeczne",
                        "szermierz",
                        "bard",
                        "szczupła",
                        "wysoka",
                        "szare",
                        "ciemne",
                        "spięte",
                        "blizna na dłoni",
                    ]
                )
                writer = FakeWriter()
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                result = await harness.require_server().session_flow.login(transport)
                assert result.character is not None
                char = result.character
                self.assertEqual(char.name, "Ala")
                self.assertEqual(char.origin, "chlop_z_podgrodzia")
                self.assertEqual(char.starting_reputation, 5)
                self.assertEqual(char.global_reputation, 5)
                self.assertEqual(char.main_profession, "szermierz")
                self.assertEqual(char.secondary_profession, "bard")
                self.assertEqual(char.childhood, "wies")
                self.assertEqual(char.combat_style, "ofensywny")
                self.assertEqual(char.room_id, 14)
                self.assertIn("dueling_blade", [item.vnum for item in char.equipment.values() if item is not None])
                self.assertIn("lute", [item.vnum for item in char.inventory])
                self.assertIn("muzyka", char.skills.values)
                self.assertGreaterEqual(char.skills.values["muzyka"]["level"], 3)
                self.assertIsNotNone(char.appearance_profile)
                assert char.appearance_profile is not None
                self.assertEqual(char.appearance_profile.build, "szczuply")
                self.assertEqual(char.appearance_profile.height, "wysoki")
                self.assertEqual(char.appearance_profile.eyes, "szare")
                self.assertEqual(char.appearance_profile.hair_color, "ciemne")
                self.assertEqual(char.appearance_profile.hair_style, "spiete")
                self.assertEqual(char.appearance_profile.beard, "brak")
                self.assertEqual(char.appearance_profile.special_feature, "blizna_dlon")
                self.assertIn("Jesteś wysoką, szczupłą kobietą o szarych oczach.", char.appearance)
                self.assertIn("Powoli odzyskujesz świadomość", writer.text())
                self.assertIn("Karczmarz opiera łokcie", writer.text())
                self.assertNotIn("Wybierz pochodzenie", writer.text())
                self.assertNotIn("Wybierz profesję główną", writer.text())

        asyncio.run(run())

    def test_new_character_flow_supports_numbered_choice_menus(self) -> None:
        async def run() -> None:
            with GameHarness() as harness:
                reader = FakeReader.from_text_lines(
                    [
                        "numeryczny_gracz",
                        "sekret",
                        "Ala",
                        "kobieta",
                        "24",
                        "2",
                        "1",
                        "2",
                        "szermierz",
                        "bard",
                        "4",
                        "2",
                        "1",
                        "1",
                        "1",
                        "1",
                    ]
                )
                writer = FakeWriter()
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                result = await harness.require_server().session_flow.login(transport)
                assert result.character is not None
                char = result.character
                self.assertEqual(char.origin, "chlop_z_podgrodzia")
                self.assertEqual(char.childhood, "wies")
                self.assertEqual(char.birth_region, "Podgrodzie")
                self.assertEqual(char.main_profession, "szermierz")
                self.assertEqual(char.secondary_profession, "bard")
                self.assertIsNotNone(char.appearance_profile)
                assert char.appearance_profile is not None
                self.assertEqual(char.appearance_profile.build, "krepy")
                self.assertEqual(char.appearance_profile.height, "niski")
                self.assertEqual(char.appearance_profile.eyes, "szare")
                self.assertEqual(char.appearance_profile.hair_color, "ciemne")
                self.assertEqual(char.appearance_profile.hair_style, "krotkie")
                self.assertEqual(char.appearance_profile.beard, "brak")
                self.assertEqual(char.appearance_profile.special_feature, "brak")
                self.assertIn("Jesteś niską, krępą kobietą o szarych oczach.", char.appearance)
                transcript = writer.text()
                self.assertIn("Pochodzenie:", transcript)
                self.assertIn("1. mieszczanin Astergardu", transcript)
                self.assertIn("Dzieciństwo:", transcript)
                self.assertIn("Region urodzenia:", transcript)
                self.assertIn("— Jakiej jesteś budowy?", transcript)
                self.assertIn("— Jakiego jesteś wzrostu?", transcript)
                self.assertIn("— Jakiego koloru są twoje oczy?", transcript)
                self.assertIn("— Jaki mają kolor twoje włosy?", transcript)
                self.assertIn("— Jak nosisz włosy?", transcript)
                self.assertIn("— Masz jakąś cechę szczególną? Jeśli nie, wybierz brak.", transcript)
                self.assertIn("Profesje główne:", transcript)
                self.assertIn("Wpisz numer albo nazwę.", transcript)

        asyncio.run(run())

    def test_profile_roundtrip_persists_creator_data_and_professions(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            appearance_profile = appearance_profile_from_choices(
                gender_id="m",
                build="krępy",
                height="wysoki",
                eyes="piwne",
                hair_color="ciemne",
                hair_style="krótkie",
                beard="brak",
                special_feature="brak",
            )
            profile = CharacterCreationProfile.build(
                name="Marek",
                gender_id="m",
                age="31",
                origin="mieszczanin Astergardu",
                childhood="miasto",
                birth_region="Astergard",
                main_profession="szermierz",
                secondary_profession="kowal",
                appearance_profile=appearance_profile,
            )
            self.assertTrue(repo.register("creator", "pw", profile))
            char = repo.load("creator")
            self.assertEqual(char.name, "Marek")
            self.assertEqual(char.origin, "mieszczanin_astergardu")
            self.assertEqual(char.childhood, "miasto")
            self.assertEqual(char.main_profession, "szermierz")
            self.assertEqual(char.secondary_profession, "kowal")
            self.assertEqual(char.combat_style, "ofensywny")
            self.assertIsNotNone(char.appearance_profile)
            assert char.appearance_profile is not None
            self.assertEqual(char.appearance_profile, appearance_profile)
            self.assertIn("Jesteś wysokim, krępym mężczyzną o piwnych oczach.", char.appearance)
            self.assertIn("dueling_blade", [item.vnum for item in char.inventory] + [item.vnum for item in char.equipment.values() if item is not None])
            self.assertIn("smith_tools", [item.vnum for item in char.inventory])

            char.history = "Zmieniona historia po pierwszym zapisie."
            repo.save(char)
            loaded = repo.load("creator")
            self.assertEqual(loaded.name, "Marek")
            self.assertEqual(loaded.history, "Zmieniona historia po pierwszym zapisie.")
            self.assertEqual(loaded.main_profession, "szermierz")
            self.assertEqual(loaded.secondary_profession, "kowal")
            self.assertIsNotNone(loaded.appearance_profile)
            assert loaded.appearance_profile is not None
            self.assertEqual(loaded.appearance_profile, appearance_profile)
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
            self.assertEqual(char.room_id, 14)

    def test_legacy_creator_profile_is_migrated_idempotently(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("migrated", "secret"))
            with repo.connection() as con:
                con.execute(
                    """
                    UPDATE players
                    SET creator_json=?, inventory_json=?, equipment_json=?
                    WHERE username=?
                    """,
                    (
                        '{"name":"Stary","gender_description":"kobieta","age":30,"origin":"mieszczanin_astergardu","childhood":"miasto","birth_region":"Astergard","main_profession":"lucznik","secondary_profession":"luczarz","appearance":"Stara postać","history":"","starting_reputation":0,"career_path":{"career_id":null,"organization_id":null,"school_id":null,"organization_rank":null},"active_defense_style":null,"combat_learning":{"known_weapon_specializations":[],"known_defense_specializations":[],"known_additional_skills":[],"known_techniques":[]}}',
                        '[{"name":"stary łuk","description":"legacy","weight":1.0,"value":1,"vnum":"hunting_bow","item_type":"weapon","slot":"bron_glowna","is_container":false,"capacity":0.0,"contains":[],"wearable":true,"armor_value":0,"weapon_type":"łuk","damage_type":"pociskowa","base_damage":4,"protection":0,"durability":10.0,"max_durability":10.0,"is_consumable":false,"effects_on_consume":{},"can_be_sold_to_merchants":true,"reach":2,"initiative_modifier":0,"parry_bonus":0,"shield_block":0,"id":"legacy-bow","presentation_category":null,"scene_position":null,"forms":{},"weapon_profile_id":"hunting_bow","armor_profile_id":null,"shield_profile_id":null}]',
                        '{"bron_glowna":{"name":"stara kusza","description":"legacy","weight":2.0,"value":1,"vnum":"light_crossbow","item_type":"weapon","slot":"bron_glowna","is_container":false,"capacity":0.0,"contains":[],"wearable":true,"armor_value":0,"weapon_type":"kusza","damage_type":"pociskowa","base_damage":5,"protection":0,"durability":10.0,"max_durability":10.0,"is_consumable":false,"effects_on_consume":{},"can_be_sold_to_merchants":true,"reach":2,"initiative_modifier":0,"parry_bonus":0,"shield_block":0,"id":"legacy-crossbow","presentation_category":null,"scene_position":null,"forms":{},"weapon_profile_id":"light_crossbow","armor_profile_id":null,"shield_profile_id":null}}',
                        "migrated",
                    ),
                )
                row = con.execute(
                    """
                    SELECT room_id,gold,stats_json,skills_json,wounds_json,reputation_json,global_reputation,local_reputation_json,
                           renown,title,crimes_json,wanted_level,wanted_posts_json,quests_json,completed_json,inventory_json,equipment_json,effects_json,combat_style,creator_json,visited_room_ids_json
                    FROM players WHERE username=?
                    """,
                    ("migrated",),
                ).fetchone()
            assert row is not None
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                first = repo.characters.serializer.hydrate("migrated", row)
            self.assertGreaterEqual(len(captured), 1)
            self.assertEqual(first.main_profession, "wojownik")
            self.assertEqual(first.secondary_profession, "")
            self.assertTrue(all(item.vnum not in {"hunting_bow", "light_crossbow"} for item in first.inventory))
            self.assertTrue(all(item.vnum not in {"hunting_bow", "light_crossbow"} for item in first.equipment.values() if item is not None))
            repo.save(first)
            second = repo.load("migrated")
            self.assertEqual(
                (
                    first.main_profession,
                    first.secondary_profession,
                    [item.vnum for item in first.inventory],
                    [item.vnum for item in first.equipment.values() if item is not None],
                    first.skills.to_dict(),
                ),
                (
                    second.main_profession,
                    second.secondary_profession,
                    [item.vnum for item in second.inventory],
                    [item.vnum for item in second.equipment.values() if item is not None],
                    second.skills.to_dict(),
                ),
            )

    def test_new_characters_start_in_the_inn(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("innborn", "secret"))
            char = repo.load("innborn")
            self.assertEqual(char.room_id, 14)

    def test_invalid_creation_data_is_rejected(self) -> None:
        with self.assertRaises(CharacterCreationError):
            CharacterCreationProfile.build(
                name="A",
                gender_id="m",
                age="24",
                origin="mieszczanin Astergardu",
                childhood="miasto",
                birth_region="Astergard",
                main_profession="wojownik",
                secondary_profession=None,
                appearance="Wygląd",
            )

        with self.assertRaises(ProfessionError):
            CharacterCreationProfile.build(
                name="Ala",
                gender_id="m",
                age="24",
                origin="mieszczanin Astergardu",
                childhood="miasto",
                birth_region="Astergard",
                main_profession="nieznana",
                secondary_profession=None,
                appearance="Wygląd",
            )

        with self.assertRaises(ProfessionError):
            CharacterCreationProfile.build(
                name="Ala",
                gender_id="m",
                age="24",
                origin="mieszczanin Astergardu",
                childhood="miasto",
                birth_region="Astergard",
                main_profession="wojownik",
                secondary_profession="wojownik",
                appearance="Wygląd",
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
                        "mężczyzna",
                        "31",
                        "mieszczanin Astergardu",
                        "miasto",
                        "Astergard",
                        "wojownik",
                        "0",
                        "krępy",
                        "wysoki",
                        "piwne",
                        "ciemne",
                        "krótkie",
                        "krótki zarost",
                        "wąska blizna na policzku",
                    ]
                )
                writer = FakeWriter()
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                result = await harness.require_server().session_flow.login(transport)
                assert result.character is not None
                transcript = await harness.execute(result.character, "profil")
                self.assertIn("O tobie:", transcript.output)
                self.assertIn("Nazywasz się Marek.", transcript.output)
                self.assertIn("Twoje pochodzenie to mieszczanin Astergardu.", transcript.output)
                self.assertIn("Ścieżka główna: wojownik.", transcript.output)
                self.assertIn("Na początku niesiesz:", transcript.output)
                self.assertNotIn("Obciążenie:", transcript.output)
                self.assertNotIn("100/100", transcript.output)
                self.assertIn("Płeć: mężczyzna.", transcript.output)
                self.assertNotIn("Wygląd:", transcript.output)
                ob = await harness.execute(result.character, "ob siebie")
                self.assertIn("Jesteś wysokim, krępym mężczyzną o piwnych oczach.", ob.output)
                self.assertIn("Masz krótkie, ciemne włosy.", ob.output)
                self.assertIn("Na twarzy nosisz kilkudniowy zarost.", ob.output)
                self.assertIn("Wąska blizna przecina policzek.", ob.output)
                self.assertIn("Marek, mężczyzna.", ob.output)
                rep = await harness.execute(result.character, "reputacja")
                self.assertIn("Twoje imię w świecie:", rep.output)
                self.assertIn("Jak mówią o tobie ludzie:", rep.output)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

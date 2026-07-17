from __future__ import annotations

import json
import tempfile
import unittest
import warnings

from astergard.characters.creation import CharacterCreationProfile
from astergard.characters.professions import (
    ADDITIONAL_PROFESSIONS,
    MAIN_PROFESSIONS,
    ProfessionError,
    profession_menu_text,
    resolve_profession,
)
from astergard.combat.balance import profession_balance_scenarios
from astergard.combat.weapons import load_default_weapon_profile_catalog
from astergard.database.repository import PlayerRepository
from astergard.items.models import Item


class RangedWeaponsRemovedRegressionTests(unittest.TestCase):
    def test_removed_professions_are_absent_from_catalog_and_menu(self) -> None:
        removed = ("lucznik", "kusznik", "luczarz")
        self.assertNotIn("lucznik", MAIN_PROFESSIONS)
        self.assertNotIn("kusznik", MAIN_PROFESSIONS)
        self.assertNotIn("luczarz", ADDITIONAL_PROFESSIONS)
        self.assertEqual(len(MAIN_PROFESSIONS), 5)
        self.assertEqual(len(ADDITIONAL_PROFESSIONS), 5)

        menu = profession_menu_text()
        for key in removed:
            self.assertNotIn(key, menu)

        for key in removed:
            with self.assertRaises(ProfessionError):
                resolve_profession(key)
            with self.assertRaises(ProfessionError):
                resolve_profession(key, kind="main" if key != "luczarz" else "secondary")

    def test_weapon_profile_catalog_has_no_bow_or_crossbow_profiles(self) -> None:
        catalog = load_default_weapon_profile_catalog()
        forbidden = ("bow", "crossbow", "łuk", "luk", "kusz", "arrow", "bolt", "bełt", "strzał")
        for profile in catalog.profiles:
            blob = f"{profile.id} {profile.name} {' '.join(profile.tags)}".casefold()
            self.assertFalse(any(term in blob for term in forbidden), profile.id)

    def test_new_characters_do_not_receive_ranged_items(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            profile = CharacterCreationProfile.build(
                name="Mira",
                gender_description="kobieta",
                age="27",
                origin="uczeń rzemieślnika",
                childhood="miasto",
                birth_region="Astergard",
                main_profession="szermierz",
                secondary_profession="bard",
                appearance="Szczupła postać z prostym mieczem przy pasie.",
            )
            self.assertTrue(repo.register("mira", "secret", profile))
            char = repo.load("mira")
            forbidden = {"hunting_bow", "light_crossbow", "bowyer_tools", "bowyer_blank_npc"}
            for item in [*char.inventory, *[equipped for equipped in char.equipment.values() if equipped is not None]]:
                blob = f"{item.name} {item.vnum or ''} {item.weapon_type or ''} {item.damage_type or ''}".casefold()
                self.assertFalse(any(term in blob for term in ("bow", "crossbow", "łuk", "luk", "kusz", "arrow", "bolt", "strzał", "bełt")), blob)
                self.assertNotIn(item.vnum, forbidden)

    def test_profession_balance_scenarios_cover_only_current_main_professions(self) -> None:
        scenarios = profession_balance_scenarios(iterations=1)
        self.assertEqual(len(scenarios), len(MAIN_PROFESSIONS))
        names = {scenario.name for scenario in scenarios}
        self.assertTrue(all("lucznik" not in name for name in names))
        self.assertTrue(all("kusznik" not in name for name in names))

    def test_legacy_save_migrates_and_is_idempotent(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("legacy", "secret"))
            creator_json = {
                "name": "Stary",
                "gender_description": "kobieta",
                "age": 30,
                "origin": "mieszczanin_astergardu",
                "childhood": "miasto",
                "birth_region": "Astergard",
                "main_profession": "lucznik",
                "secondary_profession": "luczarz",
                "appearance": "Stara postać",
                "history": "",
                "starting_reputation": 0,
                "career_path": {
                    "career_id": None,
                    "organization_id": None,
                    "school_id": None,
                    "organization_rank": None,
                },
                "active_defense_style": None,
                "combat_learning": {
                    "known_weapon_specializations": [],
                    "known_defense_specializations": [],
                    "known_additional_skills": [],
                    "known_techniques": [],
                },
            }
            bow = Item(
                "stary łuk",
                "legacy",
                1.0,
                1,
                "hunting_bow",
                "weapon",
                "bron_glowna",
                weapon_type="łuk",
                damage_type="pociskowa",
                base_damage=4,
                reach=2,
            )
            bolt = Item("bełty", "legacy", 0.4, 1, "bolt_bundle", "tool")
            crossbow = Item(
                "stara kusza",
                "legacy",
                2.0,
                1,
                "light_crossbow",
                "weapon",
                "bron_glowna",
                weapon_type="kusza",
                damage_type="pociskowa",
                base_damage=5,
                reach=2,
            )
            skills_json = {
                "luki": {"level": 7, "progress": 2},
                "kusze": {"level": 4, "progress": 1},
                "luczarstwo": {"level": 5, "progress": 3},
                "bron_jednoraczna": {"level": 2, "progress": 0},
            }
            with repo.connection() as con:
                con.execute(
                    """
                    UPDATE players
                    SET creator_json=?, inventory_json=?, equipment_json=?, skills_json=?
                    WHERE username=?
                    """,
                    (
                        json.dumps(creator_json, ensure_ascii=False),
                        json.dumps([bow.to_dict(), bolt.to_dict()], ensure_ascii=False),
                        json.dumps({"bron_glowna": crossbow.to_dict()}, ensure_ascii=False),
                        json.dumps(skills_json, ensure_ascii=False),
                        "legacy",
                    ),
                )

            with warnings.catch_warnings(record=True) as first_warnings:
                warnings.simplefilter("always")
                first = repo.load("legacy")
            self.assertGreaterEqual(len(first_warnings), 1)
            self.assertEqual(first.main_profession, "wojownik")
            self.assertEqual(first.secondary_profession, "")
            self.assertNotIn("luki", first.skills.values)
            self.assertNotIn("kusze", first.skills.values)
            self.assertNotIn("luczarstwo", first.skills.values)
            self.assertTrue(all(item.vnum not in {"hunting_bow", "light_crossbow", "bolt_bundle"} for item in first.inventory))
            self.assertTrue(all(item.vnum not in {"hunting_bow", "light_crossbow"} for item in first.equipment.values() if item is not None))

            repo.save(first)
            with warnings.catch_warnings(record=True) as second_warnings:
                warnings.simplefilter("always")
                second = repo.load("legacy")
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
            self.assertEqual(len(second_warnings), 0)


if __name__ == "__main__":
    unittest.main()

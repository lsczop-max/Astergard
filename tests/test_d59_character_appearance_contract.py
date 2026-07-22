from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
import warnings

from astergard.characters.appearance import (
    BUILD_DEFINITIONS,
    EYE_COLOR_DEFINITIONS,
    HAIR_STYLE_DEFINITIONS,
    HEIGHT_DEFINITIONS,
    CharacterAppearanceProfile,
    appearance_profile_from_choices,
    gender_label,
    gender_instrumental,
    render_appearance_lines,
    render_self_observation,
)
from astergard.database.repository import PlayerRepository
from astergard.items.models import Item
from astergard.testing import TestGameHarness


def _appearance_profile_json(*, build: str, height: str, eyes: str, hair_color: str, hair_style: str, beard: str, special_feature: str, gender: str = "f") -> dict[str, str]:
    payload = {
        "gender": gender,
        "build": build,
        "height": height,
        "eyes": eyes,
        "hair_color": hair_color,
        "hair_style": hair_style,
        "beard": beard,
        "special_feature": special_feature,
    }
    return payload


class CharacterAppearanceContractTests(unittest.TestCase):
    legacy_build_a = "".join(["wys", "portowany"])
    legacy_build_b = "".join(["atle", "tyczny"])

    def test_legacy_gender_conflict_prefers_top_level_gender(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("legacy", "secret"))
            creator_json = {
                "name": "Stara",
                "gender_description": "kobieta",
                "age": 30,
                "origin": "mieszczanin_astergardu",
                "childhood": "miasto",
                "birth_region": "Astergard",
                "main_profession": "wojownik",
                "secondary_profession": "",
                "appearance": "legacy",
                "appearance_profile": _appearance_profile_json(
                    build="szczuply",
                    height="wysoki",
                    eyes="szare",
                    hair_color="ciemne",
                    hair_style="krotkie",
                    beard="brak",
                    special_feature="brak",
                    gender="m",
                ),
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
            with repo.connection() as con:
                con.execute(
                    "UPDATE players SET creator_json=? WHERE username=?",
                    (json.dumps(creator_json, ensure_ascii=False), "legacy"),
                )
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                char = repo.load("legacy")
            self.assertEqual(len(captured), 1)
            self.assertIs(captured[0].category, UserWarning)
            self.assertIn("Konflikt legacy płci", str(captured[0].message))
            self.assertEqual(char.gender_id, "f")
            self.assertEqual(char.gender_description, "kobieta")
            self.assertIsNotNone(char.appearance_profile)
            assert char.appearance_profile is not None
            self.assertEqual(char.appearance_profile.beard, "brak")

    def test_partial_profile_falls_back_to_none(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                repo = harness.require_server().repo
                self.assertTrue(repo.register("partial", "secret"))
                creator_json = {
                    "name": "Stara",
                    "gender_description": "kobieta",
                    "age": 30,
                    "origin": "mieszczanin_astergardu",
                    "childhood": "miasto",
                    "birth_region": "Astergard",
                    "main_profession": "wojownik",
                    "secondary_profession": "",
                    "appearance": "legacy",
                    "appearance_profile": {"build": "szczuply", "height": "wysoki"},
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
                with repo.connection() as con:
                    con.execute(
                        "UPDATE players SET creator_json=? WHERE username=?",
                        (json.dumps(creator_json, ensure_ascii=False), "partial"),
                    )
                with warnings.catch_warnings(record=True) as captured:
                    warnings.simplefilter("always")
                    char = repo.load("partial")
                self.assertGreaterEqual(len(captured), 1)
                self.assertTrue(any("Nieprawidłowy profil wyglądu" in str(w.message) for w in captured))
                self.assertEqual(char.gender_id, "f")
                self.assertIsNone(char.appearance_profile)
                ob = await harness.execute(char, "ob siebie")
                self.assertNotIn("Jesteś wysok", ob.output)
                self.assertNotIn("Włosy", ob.output)
                self.assertIn("Stara, kobieta.", ob.output)

        asyncio.run(run())

    def test_profile_validator_rejects_partial_and_invalid_values(self) -> None:
        required = {
            "build": "szczuply",
            "height": "wysoki",
            "eyes": "szare",
            "hair_color": "ciemne",
            "hair_style": "krotkie",
            "beard": "brak",
            "special_feature": "brak",
        }
        invalid_payloads: list[dict[str, object]] = [
            {**required, "build": None},
            {**required, "height": 10},
            {**required, "eyes": ["szare"]},
            {**required, "hair_color": True},
            {**required, "hair_style": "nieznane"},
            {**required, "beard": "broda", "gender": "f"},
            {**required, "special_feature": None},
            {**required, "unexpected": "pole"},
            {"build": "szczuply", "height": "wysoki"},
        ]
        for payload in invalid_payloads:
            with self.assertRaises(ValueError):
                CharacterAppearanceProfile.from_dict(payload)

    def test_legacy_build_aliases_map_to_new_canonical_builds(self) -> None:
        base = {
            "height": "wysoki",
            "eyes": "szare",
            "hair_color": "ciemne",
            "hair_style": "krotkie",
            "beard": "brak",
            "special_feature": "brak",
        }
        with self.subTest("legacy alias A -> zylasty"):
            profile = CharacterAppearanceProfile.from_dict({**base, "build": self.legacy_build_a})
            self.assertEqual(profile.build, "zylasty")
        with self.subTest("legacy alias B -> barczysty"):
            profile = CharacterAppearanceProfile.from_dict({**base, "build": self.legacy_build_b})
            self.assertEqual(profile.build, "barczysty")
        self.assertEqual(set(BUILD_DEFINITIONS), {"drobny", "szczuply", "zylasty", "krepy", "barczysty", "postawny"})
        self.assertNotIn(self.legacy_build_a, BUILD_DEFINITIONS)
        self.assertNotIn(self.legacy_build_b, BUILD_DEFINITIONS)
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("legacy_builds", "secret"))
            creator_json = {
                "name": "Stary",
                "gender_description": "mężczyzna",
                "age": 30,
                "origin": "mieszczanin_astergardu",
                "childhood": "miasto",
                "birth_region": "Astergard",
                "main_profession": "wojownik",
                "secondary_profession": "",
                "appearance": "legacy",
                "appearance_profile": {
                    **base,
                    "build": self.legacy_build_a,
                },
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
            with repo.connection() as con:
                con.execute(
                    "UPDATE players SET creator_json=? WHERE username=?",
                    (json.dumps(creator_json, ensure_ascii=False), "legacy_builds"),
                )
            with repo.connection() as con:
                before_load = con.execute("SELECT creator_json FROM players WHERE username=?", ("legacy_builds",)).fetchone()[0]
            loaded = repo.load("legacy_builds")
            self.assertIsNotNone(loaded.appearance_profile)
            assert loaded.appearance_profile is not None
            self.assertEqual(loaded.appearance_profile.build, "zylasty")
            with repo.connection() as con:
                after_load = con.execute("SELECT creator_json FROM players WHERE username=?", ("legacy_builds",)).fetchone()[0]
            self.assertEqual(before_load, after_load)
            repo.save(loaded)
            reloaded = repo.load("legacy_builds")
            self.assertIsNotNone(reloaded.appearance_profile)
            assert reloaded.appearance_profile is not None
            self.assertEqual(reloaded.appearance_profile.build, "zylasty")
            with repo.connection() as con:
                raw_creator_json = con.execute("SELECT creator_json FROM players WHERE username=?", ("legacy_builds",)).fetchone()[0]
            stored_creator_json = json.loads(raw_creator_json)
            self.assertEqual(stored_creator_json["appearance_profile"]["build"], "zylasty")

    def test_render_matrix_uses_explicit_forms_and_hides_absences(self) -> None:
        expected_builds = {
            "drobny": {"m": "drobnym", "f": "drobną"},
            "szczuply": {"m": "szczupłym", "f": "szczupłą"},
            "zylasty": {"m": "żylastym", "f": "żylastą"},
            "krepy": {"m": "krępym", "f": "krępą"},
            "barczysty": {"m": "barczystym", "f": "barczystą"},
            "postawny": {"m": "postawnym", "f": "postawną"},
        }
        expected_height = {
            "bardzo_niski": {"m": "bardzo niskim", "f": "bardzo niską", "phrase": "bardzo niskiego wzrostu"},
            "niski": {"m": "niskim", "f": "niską", "phrase": "niskiego wzrostu"},
            "sredni": {"m": "średnim", "f": "średnią", "phrase": "średniego wzrostu"},
            "wysoki": {"m": "wysokim", "f": "wysoką", "phrase": "wysokiego wzrostu"},
            "bardzo_wysoki": {"m": "bardzo wysokim", "f": "bardzo wysoką", "phrase": "bardzo wysokiego wzrostu"},
        }
        for gender_id in ("m", "f"):
            for build_key in BUILD_DEFINITIONS:
                for height_key in HEIGHT_DEFINITIONS:
                    profile = appearance_profile_from_choices(
                        gender_id=gender_id,
                        build=build_key,
                        height=height_key,
                        eyes="szare",
                        hair_color="ciemne",
                        hair_style="krotkie",
                        beard="brak",
                        special_feature="brak",
                    )
                    text = "\n".join(render_appearance_lines(profile, gender_id=gender_id))
                    build_form = expected_builds[build_key][gender_id]
                    if height_key == "sredni":
                        expected_intro = (
                            f"Jesteś {build_form} {gender_instrumental(gender_id)} {expected_height[height_key]['phrase']} "
                            f"o {EYE_COLOR_DEFINITIONS['szare'].forms['locative_plural']}."
                        )
                    else:
                        height_form = expected_height[height_key][gender_id]
                        expected_intro = (
                            f"Jesteś {height_form}, {build_form} {gender_instrumental(gender_id)} "
                            f"o {EYE_COLOR_DEFINITIONS['szare'].forms['locative_plural']}."
                        )
                    self.assertIn(expected_intro, text)
                    self.assertIn("Masz krótkie, ciemne włosy.", text)
                    self.assertNotIn("Nie masz wyraźnych znaków szczególnych", text)
                    self.assertNotIn("Na twarzy nosisz", text)
                    self.assertNotIn("o szare oczach", text)
                    self.assertNotIn("średnim mężczyzną", text)
                    self.assertNotIn("średnią kobietą", text)
                    self.assertNotIn(self.legacy_build_a, text)
                    self.assertNotIn(self.legacy_build_b, text)
                    self.assertNotIn("_", text)
                    if "_" in height_key:
                        self.assertNotIn(height_key, text)

    def test_hair_styles_and_beard_rules_are_domain_validated(self) -> None:
        with self.assertRaises(ValueError):
            appearance_profile_from_choices(
                gender_id="f",
                build="szczuply",
                height="wysoki",
                eyes="szare",
                hair_color="ciemne",
                hair_style="krotkie",
                beard="broda",
                special_feature="brak",
            )

        for hair_style_key, hair_style_option in HAIR_STYLE_DEFINITIONS.items():
            profile = appearance_profile_from_choices(
                gender_id="m",
                build="szczuply",
                height="wysoki",
                eyes="szare",
                hair_color="ciemne",
                hair_style=hair_style_key,
                beard="brak",
                special_feature="brak",
            )
            text = "\n".join(render_appearance_lines(profile, gender_id="m"))
            if hair_style_key == "ogolone":
                self.assertIn("Masz gładko ogoloną głowę.", text)
                self.assertNotIn("ciemne", text)
            elif hair_style_key == "warkocze":
                self.assertIn("Masz ciemne włosy zaplecione w warkocze.", text)
                self.assertNotIn("w warkoczach", text)
            elif hair_style_key == "spiete":
                self.assertIn("Masz ciemne włosy spięte z tyłu.", text)
            elif hair_style_key == "rozpuszczone":
                self.assertIn("Masz ciemne włosy noszone swobodnie.", text)
            elif hair_style_key == "krotkie":
                self.assertIn("Masz krótkie, ciemne włosy.", text)
            elif hair_style_key == "dlugie":
                self.assertIn("Masz długie, ciemne włosy.", text)
            else:
                self.assertIn(hair_style_option.label, text)

    def test_equipment_rendering_uses_real_slots_and_neutral_handedness(self) -> None:
        self.assertEqual(gender_label("m"), "mężczyzna")
        self.assertEqual(gender_label("f"), "kobieta")
        with TestGameHarness() as harness:
            character = harness.create_character("slot_user", room_id=60)
            backpack = Item("skórzany plecak", "Plecak.", 1.0, 5, "backpack", slot="plecy", wearable=True, display_accusative="skórzany plecak")
            belt_pouch = Item("sakiewka monet", "Sakiewka.", 0.1, 1, "coin_pouch", slot="pas", wearable=True)
            weapon = Item(
                "prosty miecz",
                "Miecz.",
                1.2,
                10,
                "simple_sword",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="miecz",
                weapon_profile_id="garrison_short_sword",
            )
            character.equipment["plecy"] = backpack
            character.equipment["pas"] = belt_pouch
            character.equipment["bron_glowna"] = weapon
            text = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("Na plecach niesiesz skórzany plecak.", text)
            self.assertIn("U pasa wisi sakiewka monet.", text)
            self.assertIn("W prawej ręce trzymasz prosty miecz.", text)
            self.assertNotIn("inventory", text)
            self.assertNotIn("przedramię", text)

            shield = Item(
                "migdałowa tarcza",
                "Tarcza.",
                2.0,
                10,
                "round_shield",
                item_type="shield",
                slot="tarcza",
                wearable=True,
                weapon_type="tarcza",
                display_nominative="migdałowa tarcza",
                display_accusative="migdałową tarczę",
            )
            character.equipment["tarcza"] = shield
            text_with_shield = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("W lewej ręce trzymasz migdałową tarczę.", text_with_shield)
            self.assertIn("W prawej ręce trzymasz prosty miecz.", text_with_shield)
            self.assertNotIn("przedramię", text_with_shield)
            self.assertNotIn("W obu dłoniach", text_with_shield)
            character.equipment["tarcza"] = None

            offhand = Item(
                "sztylet pojedynkowy",
                "Sztylet.",
                0.7,
                8,
                "duelist_dagger",
                item_type="weapon",
                slot="bron_pomocnicza",
                wearable=True,
                weapon_type="sztylet",
                weapon_profile_id="duelist_dagger",
            )
            character.equipment["bron_pomocnicza"] = offhand
            text_two = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("W prawej ręce trzymasz prosty miecz.", text_two)
            self.assertIn("W lewej ręce trzymasz sztylet pojedynkowy.", text_two)
            self.assertNotIn("przedramię", text_two)
            self.assertNotIn("drugiej dłoni", text_two)

            halberd = Item(
                "halabarda",
                "Halabarda.",
                3.4,
                20,
                "test_halberd",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="halabarda",
                weapon_profile_id="watch_halberd",
                display_nominative="halabarda strażnicza",
                display_accusative="halabardę strażniczą",
            )
            character.equipment["bron_pomocnicza"] = None
            character.equipment["bron_glowna"] = halberd
            text_two_handed = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("Oburącz dzierżysz halabardę strażniczą.", text_two_handed)
            self.assertNotIn("przedramię", text_two_handed)

    def test_blizna_dlon_is_rendered_naturally(self) -> None:
        profile = appearance_profile_from_choices(
            gender_id="f",
            build="drobny",
            height="sredni",
            eyes="zielone",
            hair_color="jasne",
            hair_style="dlugie",
            beard="brak",
            special_feature="blizna_dlon",
        )
        text = "\n".join(render_appearance_lines(profile, gender_id="f"))
        self.assertIn("dłoni", text)
        self.assertNotIn("Blizna znaczy dłoń", text)
        self.assertNotIn("policzku", text)

    def test_legacy_two_handed_weapon_and_shield_conflict_is_neutralized_on_load(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("conflict", "secret"))
            char = repo.load("conflict")
            char.gender_id = "m"
            char.name = "Konflikt"
            char.appearance_profile = None
            char.equipment["bron_glowna"] = Item(
                "halabarda",
                "Halabarda.",
                3.4,
                20,
                "test_halberd",
                item_type="weapon",
                slot="bron_glowna",
                wearable=True,
                weapon_type="halabarda",
                weapon_profile_id="watch_halberd",
                display_nominative="halabarda strażnicza",
                display_accusative="halabardę strażniczą",
            )
            char.equipment["tarcza"] = Item(
                "okrągła tarcza",
                "Tarcza.",
                2.0,
                10,
                "round_shield",
                item_type="shield",
                slot="tarcza",
                wearable=True,
                weapon_type="tarcza",
            )
            assert char.equipment["tarcza"] is not None
            shield_id = char.equipment["tarcza"].id
            repo.save(char)
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                loaded = repo.load("conflict")
            self.assertEqual(len(captured), 0)
            self.assertIsNone(loaded.equipment["tarcza"])
            self.assertIsNotNone(loaded.equipment["bron_glowna"])
            shield_items = [item for item in loaded.inventory if item.id == shield_id]
            self.assertEqual(len(shield_items), 1)
            self.assertEqual(shield_items[0].id, shield_id)
            repo.save(loaded)
            reloaded = repo.load("conflict")
            self.assertIsNone(reloaded.equipment["tarcza"])
            self.assertIsNotNone(reloaded.equipment["bron_glowna"])
            self.assertEqual(len([item for item in reloaded.inventory if item.id == shield_id]), 1)
            text = render_self_observation(
                name="Konflikt",
                gender_id="m",
                wounds=loaded.wounds,
                equipment=loaded.equipment,
                appearance_profile=None,
            )
            self.assertIn("Oburącz dzierżysz halabardę strażniczą.", text)
            self.assertNotIn("przedramię", text)
            self.assertNotIn("okrągła tarcza", text)
            loaded.resolve_equipment_conflicts()
            self.assertEqual(len([item for item in loaded.inventory if item.id == shield_id]), 1)



if __name__ == "__main__":
    unittest.main()

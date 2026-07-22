from __future__ import annotations

import tempfile
import unittest

from astergard.characters.appearance import render_self_observation, visible_equipped_items
from astergard.database.repository import PlayerRepository
from astergard.items.models import Item
from astergard.testing import TestGameHarness


def _weapon(
    name: str,
    *,
    vnum: str,
    weapon_profile_id: str,
    slot: str = "bron_glowna",
    display_nominative: str | None = None,
    display_accusative: str | None = None,
) -> Item:
    return Item(
        name,
        name,
        1.0,
        10,
        vnum,
        item_type="weapon",
        slot=slot,
        wearable=True,
        weapon_type="weapon",
        weapon_profile_id=weapon_profile_id,
        display_nominative=display_nominative or name,
        display_accusative=display_accusative or display_nominative or name,
    )


def _wearable(
    name: str,
    *,
    vnum: str,
    slot: str,
    item_type: str = "clothing",
    layer: str | None = None,
    coverage_areas: tuple[str, ...] = (),
    display_nominative: str | None = None,
    display_accusative: str | None = None,
) -> Item:
    return Item(
        name,
        name,
        1.0,
        10,
        vnum,
        item_type=item_type,
        slot=slot,
        wearable=True,
        display_nominative=display_nominative or name,
        display_accusative=display_accusative or display_nominative or name,
        presentation_layer=layer,
        coverage_areas=coverage_areas,
    )


def _visibility_fixture() -> dict[str, Item]:
    shirt = _wearable(
        "koszula",
        vnum="shirt_visibility",
        slot="korpus",
        item_type="clothing",
        layer="clothing",
        coverage_areas=("torso", "back", "shoulders", "arms"),
        display_nominative="koszula",
        display_accusative="koszulę",
    )
    chainmail = _wearable(
        "kolczuga",
        vnum="chainmail_visibility",
        slot="korpus",
        item_type="armor",
        layer="armor",
        coverage_areas=("torso", "back", "shoulders", "arms", "hands"),
        display_nominative="ciemna kolczuga",
        display_accusative="ciemną kolczugę",
    )
    coat = _wearable(
        "wełniany płaszcz",
        vnum="cloak_visibility",
        slot="korpus",
        item_type="outerwear",
        layer="outerwear",
        coverage_areas=("torso", "back", "shoulders"),
        display_nominative="wełniany płaszcz",
        display_accusative="wełniany płaszcz",
    )
    coat.coverage_mode = "partial"
    belt = _wearable(
        "skórzany pas",
        vnum="belt_visibility",
        slot="pas",
        item_type="clothing",
        layer="clothing",
        coverage_areas=("waist",),
        display_nominative="skórzany pas",
        display_accusative="skórzany pas",
    )
    pouch = _wearable(
        "sakiewka monet",
        vnum="pouch_visibility",
        slot="pas",
        item_type="accessory",
        layer="accessory",
        coverage_areas=(),
        display_nominative="sakiewka monet",
        display_accusative="sakiewkę monet",
    )
    sword = _weapon(
        "długi miecz",
        vnum="long_sword_visibility",
        weapon_profile_id="garrison_short_sword",
        display_accusative="długi miecz",
    )
    shield = _wearable(
        "migdałowa tarcza",
        vnum="shield_visibility",
        slot="tarcza",
        item_type="shield",
        display_nominative="migdałowa tarcza",
        display_accusative="migdałową tarczę",
    )
    return {
        "koszula": shirt,
        "kolczuga": chainmail,
        "wełniany płaszcz": coat,
        "skórzany pas": belt,
        "sakiewka monet": pouch,
        "długi miecz": sword,
        "migdałowa tarcza": shield,
    }


def _equip_in_order(server, character, items: dict[str, Item], order: list[str]) -> None:
    character.inventory.extend(items[name] for name in order)
    for name in order:
        server.services.inventory_service.wear_item(character, name, 1)


class EquipmentVisibilityContractTests(unittest.TestCase):
    def test_visibility_is_deterministic_across_insertion_orders(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()

            first = harness.create_character("order_a", room_id=60)
            first.name = "Wędrowiec"
            first.gender_id = "m"
            first_items = _visibility_fixture()
            _equip_in_order(server, first, first_items, ["koszula", "kolczuga", "wełniany płaszcz", "skórzany pas", "sakiewka monet"])
            text_first = render_self_observation(
                name="Wędrowiec",
                gender_id="m",
                wounds=first.wounds,
                equipment=first.equipment,
                appearance_profile=None,
            )

            second = harness.create_character("order_b", room_id=60)
            second.name = "Wędrowiec"
            second.gender_id = "m"
            second_items = _visibility_fixture()
            _equip_in_order(server, second, second_items, ["sakiewka monet", "skórzany pas", "wełniany płaszcz", "kolczuga", "koszula"])
            text_second = render_self_observation(
                name="Wędrowiec",
                gender_id="m",
                wounds=second.wounds,
                equipment=second.equipment,
                appearance_profile=None,
            )

            self.assertEqual(text_first, text_second)
            expected_lines = [
                "Biodra opasuje skórzany pas.",
                "Spod rozpiętego płaszcza widać ciemną kolczugę.",
                "Ramiona okrywa wełniany płaszcz.",
                "U pasa wisi sakiewka monet.",
            ]
            for line in expected_lines:
                self.assertIn(line, text_first)
            self.assertLess(text_first.index(expected_lines[0]), text_first.index(expected_lines[1]))
            self.assertLess(text_first.index(expected_lines[1]), text_first.index(expected_lines[2]))
            self.assertLess(text_first.index(expected_lines[2]), text_first.index(expected_lines[3]))

    def test_visible_equipped_items_is_pure_and_idempotent(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            character = harness.create_character("purity", room_id=60)
            character.name = "Strażnik"
            character.gender_id = "m"
            items = _visibility_fixture()
            character.inventory.extend(items[name] for name in ["koszula", "kolczuga", "wełniany płaszcz", "skórzany pas", "sakiewka monet", "długi miecz", "migdałowa tarcza"])
            for name in ["koszula", "kolczuga", "wełniany płaszcz", "skórzany pas", "sakiewka monet", "długi miecz", "migdałowa tarcza"]:
                server.services.inventory_service.wear_item(character, name, 1)

            equipment_snapshot = character.equipment.to_dict()
            inventory_snapshot = [item.to_dict() for item in character.inventory]
            item_snapshots = {item.id: item.to_dict() for item in character.equipment.all_items()}
            identity_snapshot = tuple((item.id, id(item)) for item in character.equipment.all_items())

            first = visible_equipped_items(character.equipment)
            second = visible_equipped_items(character.equipment)

            self.assertEqual(character.equipment.to_dict(), equipment_snapshot)
            self.assertEqual([item.to_dict() for item in character.inventory], inventory_snapshot)
            self.assertEqual({item.id: item.to_dict() for item in character.equipment.all_items()}, item_snapshots)
            self.assertEqual(tuple((item.id, id(item)) for item in character.equipment.all_items()), identity_snapshot)

            self.assertEqual(
                [(entry.slot, getattr(entry.item, "id", ""), tuple(sorted(entry.visible_areas))) for entry in first],
                [(entry.slot, getattr(entry.item, "id", ""), tuple(sorted(entry.visible_areas))) for entry in second],
            )
            self.assertTrue(all(first_entry.item is second_entry.item for first_entry, second_entry in zip(first, second)))

    def test_weapon_rendering_uses_exact_holding_phrases(self) -> None:
        with TestGameHarness() as harness:
            character = harness.create_character("fighter", room_id=60)
            sword = _weapon(
                "długi miecz",
                vnum="long_sword",
                weapon_profile_id="garrison_short_sword",
                display_accusative="długi miecz",
            )
            axe = _weapon(
                "topór bojowy",
                vnum="battle_axe",
                weapon_profile_id="battle_axe",
                slot="bron_pomocnicza",
                display_accusative="topór bojowy",
            )
            shield = _wearable(
                "migdałowa tarcza",
                vnum="almond_shield",
                slot="tarcza",
                item_type="shield",
                display_nominative="migdałowa tarcza",
                display_accusative="migdałową tarczę",
            )
            halberd = _weapon(
                "halabarda strażnicza",
                vnum="watch_halberd",
                weapon_profile_id="watch_halberd",
                display_accusative="halabardę strażniczą",
            )
            dagger = _weapon(
                "sztylet pojedynkowy",
                vnum="duelist_dagger",
                weapon_profile_id="duelist_dagger",
                slot="bron_pomocnicza",
                display_accusative="sztylet pojedynkowy",
            )
            character.inventory.extend([sword, axe, shield, halberd, dagger])

            character.equipment["bron_glowna"] = sword
            text_one = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("W prawej ręce trzymasz długi miecz.", text_one)
            self.assertNotIn("przedramię", text_one)
            self.assertNotIn("weapon_profile_id", text_one)

            character.equipment["bron_glowna"] = None
            character.equipment["bron_pomocnicza"] = axe
            text_left = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("W lewej ręce trzymasz topór bojowy.", text_left)

            character.equipment["bron_glowna"] = sword
            character.equipment["bron_pomocnicza"] = dagger
            text_two = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("W prawej ręce trzymasz długi miecz.", text_two)
            self.assertIn("W lewej ręce trzymasz sztylet pojedynkowy.", text_two)
            self.assertNotIn("przedramię", text_two)

            character.equipment["bron_pomocnicza"] = None
            character.equipment["tarcza"] = shield
            text_shield = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("W prawej ręce trzymasz długi miecz.", text_shield)
            self.assertIn("W lewej ręce trzymasz migdałową tarczę.", text_shield)
            self.assertNotIn("przedramię", text_shield)

            character.equipment["bron_glowna"] = halberd
            character.equipment["tarcza"] = None
            text_two_handed = render_self_observation(
                name="Agran",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("Oburącz dzierżysz halabardę strażniczą.", text_two_handed)
            self.assertNotIn("W lewej ręce trzymasz", text_two_handed)
            self.assertNotIn("przedramię", text_two_handed)

    def test_layer_visibility_hides_lower_layers_but_keeps_partial_overlays(self) -> None:
        with TestGameHarness() as harness:
            character = harness.create_character("layered", room_id=60)
            shirt = _wearable(
                "koszula",
                vnum="shirt_1",
                slot="korpus",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("torso", "back", "shoulders", "arms"),
                display_nominative="koszula",
                display_accusative="koszulę",
            )
            chainmail = _wearable(
                "kolczuga",
                vnum="chainmail_1",
                slot="korpus",
                item_type="armor",
                layer="armor",
                coverage_areas=("torso", "back", "shoulders", "arms", "hands"),
                display_nominative="ciemna kolczuga",
                display_accusative="ciemną kolczugę",
            )
            coat = _wearable(
                "wełniany płaszcz",
                vnum="cloak_1",
                slot="korpus",
                item_type="outerwear",
                layer="outerwear",
                coverage_areas=("torso", "back", "shoulders", "arms", "hands"),
                display_nominative="wełniany płaszcz",
                display_accusative="wełniany płaszcz",
            )
            boots = _wearable(
                "skórzane buty",
                vnum="boots_1",
                slot="stopy",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("feet",),
                display_nominative="skórzane buty",
                display_accusative="skórzane buty",
            )
            trousers = _wearable(
                "skórzane spodnie",
                vnum="trousers_1",
                slot="nogi",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("legs",),
                display_nominative="skórzane spodnie",
                display_accusative="skórzane spodnie",
            )
            gloves = _wearable(
                "skórzane rękawice",
                vnum="gloves_1",
                slot="dlonie",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("hands",),
                display_nominative="skórzane rękawice",
                display_accusative="skórzane rękawice",
            )
            backpack = _wearable(
                "podróżny plecak",
                vnum="backpack_1",
                slot="plecy",
                item_type="accessory",
                layer="accessory",
                coverage_areas=("back", "shoulders"),
                display_nominative="podróżny plecak",
                display_accusative="podróżny plecak",
            )
            belt = _wearable(
                "skórzany pas",
                vnum="belt_1",
                slot="pas",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("waist",),
                display_nominative="skórzany pas",
                display_accusative="skórzany pas",
            )
            pouch = _wearable(
                "sakiewka monet",
                vnum="pouch_1",
                slot="pas",
                item_type="accessory",
                layer="accessory",
                coverage_areas=(),
                display_nominative="sakiewka monet",
                display_accusative="sakiewkę monet",
            )
            character.inventory.extend([shirt, chainmail, coat, boots, trousers, gloves, backpack, belt, pouch])

            for name in ("koszula", "kolczuga", "wełniany płaszcz", "skórzane buty", "skórzane spodnie", "skórzane rękawice", "podróżny plecak", "skórzany pas", "sakiewka monet"):
                self.assertIn(name, [item.name for item in character.inventory])

            harness.require_server().services.inventory_service.wear_item(character, "koszula", 1)
            harness.require_server().services.inventory_service.wear_item(character, "kolczuga", 1)
            harness.require_server().services.inventory_service.wear_item(character, "wełniany płaszcz", 1)
            harness.require_server().services.inventory_service.wear_item(character, "skórzane buty", 1)
            harness.require_server().services.inventory_service.wear_item(character, "skórzane spodnie", 1)
            harness.require_server().services.inventory_service.wear_item(character, "skórzane rękawice", 1)
            harness.require_server().services.inventory_service.wear_item(character, "podróżny plecak", 1)
            harness.require_server().services.inventory_service.wear_item(character, "skórzany pas", 1)
            harness.require_server().services.inventory_service.wear_item(character, "sakiewka monet", 1)

            text = render_self_observation(
                name="Wędrowiec",
                gender_id="m",
                wounds=character.wounds,
                equipment=character.equipment,
                appearance_profile=None,
            )
            self.assertIn("Masz na sobie wełniany płaszcz.", text)
            self.assertNotIn("Masz na sobie ciemną kolczugę.", text)
            self.assertNotIn("koszula", text)
            self.assertIn("Na nogach nosisz skórzane spodnie.", text)
            self.assertIn("Stopy chronią skórzane buty.", text)
            self.assertNotIn("Na dłoniach nosisz skórzane rękawice.", text)
            self.assertIn("Na plecach niesiesz podróżny plecak.", text)
            self.assertIn("Biodra opasuje skórzany pas.", text)
            self.assertIn("U pasa wisi sakiewka monet.", text)
            self.assertNotIn("U pasa wisi sakiewkę monet.", text)
            self.assertNotIn("U pasa wisi skórzany pas.", text)
            self.assertNotIn("Spod rozpiętego płaszcza", text)
            self.assertEqual(text.count("podróżny plecak"), 1)
            self.assertNotIn("inventory", text)
            self.assertNotIn("pusty", text)
            self.assertNotIn("tech_id", text)
            self.assertNotIn("weapon_profile_id", text)

            open_character = harness.create_character("layered_open", room_id=60)
            open_coat = _wearable(
                "wełniany płaszcz",
                vnum="cloak_open_1",
                slot="korpus",
                item_type="outerwear",
                layer="outerwear",
                coverage_areas=("torso", "back", "shoulders"),
                display_nominative="wełniany płaszcz",
                display_accusative="wełniany płaszcz",
            )
            open_coat.coverage_mode = "partial"
            open_chainmail = _wearable(
                "kolczuga",
                vnum="chainmail_open_1",
                slot="korpus",
                item_type="armor",
                layer="armor",
                coverage_areas=("torso", "back", "shoulders", "arms", "hands"),
                display_nominative="ciemna kolczuga",
                display_accusative="ciemną kolczugę",
            )
            open_character.inventory.extend([open_coat, open_chainmail])
            harness.require_server().services.inventory_service.wear_item(open_character, "kolczuga", 1)
            harness.require_server().services.inventory_service.wear_item(open_character, "wełniany płaszcz", 1)
            open_text = render_self_observation(
                name="Wędrowiec",
                gender_id="m",
                wounds=open_character.wounds,
                equipment=open_character.equipment,
                appearance_profile=None,
            )
            self.assertIn("Spod rozpiętego płaszcza widać ciemną kolczugę.", open_text)
            self.assertIn("Ramiona okrywa wełniany płaszcz.", open_text)
            self.assertNotIn("Masz na sobie ciemną kolczugę.", open_text)
            self.assertNotIn("Masz na sobie wełniany płaszcz.", open_text)
            self.assertNotIn("U pasa wisi skórzany pas.", open_text)
            self.assertEqual(open_text.count("ciemną kolczugę"), 1)

    def test_legacy_item_without_visibility_metadata_uses_neutral_fallback_and_survives_reload(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("legacy_visibility", "secret"))
            character = repo.load("legacy_visibility")
            legacy_cloak = Item(
                "stara zbroja",
                "Stara zbroja.",
                3.0,
                10,
                "legacy_armor",
                item_type="armor",
                slot="korpus",
                wearable=True,
            )
            character.inventory.append(legacy_cloak)
            repo.save(character)
            loaded = repo.load("legacy_visibility")
            loaded_item = next(item for item in loaded.inventory if item.id == legacy_cloak.id)
            self.assertEqual(len([item for item in loaded.inventory if item.id == legacy_cloak.id]), 1)
            loaded.inventory.remove(loaded_item)
            loaded.equipment["korpus"] = loaded_item
            text = render_self_observation(
                name="Stara",
                gender_id="f",
                wounds=loaded.wounds,
                equipment=loaded.equipment,
                appearance_profile=None,
            )
            self.assertIn("Widoczne wyposażenie: stara zbroja.", text)
            self.assertNotIn("Masz na sobie stara zbroja.", text)
            self.assertNotIn("tech_id", text)
            repo.save(loaded)
            reloaded = repo.load("legacy_visibility")
            self.assertEqual(len([item for item in reloaded.inventory if item.id == legacy_cloak.id]), 0)
            self.assertIsNotNone(reloaded.equipment["korpus"])

    def test_stack_save_reload_preserves_layers_and_display_forms(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("stacked", "secret"))
            character = repo.load("stacked")
            shirt = _wearable(
                "koszula",
                vnum="shirt_2",
                slot="korpus",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("torso", "back", "shoulders", "arms"),
                display_nominative="koszula",
                display_accusative="koszulę",
            )
            chainmail = _wearable(
                "kolczuga",
                vnum="chainmail_2",
                slot="korpus",
                item_type="armor",
                layer="armor",
                coverage_areas=("torso", "back", "shoulders", "arms", "hands"),
                display_nominative="ciemna kolczuga",
                display_accusative="ciemną kolczugę",
            )
            character.inventory.extend([shirt, chainmail])
            repo.save(character)
            loaded = repo.load("stacked")
            harness = TestGameHarness(db_path=tmp.name).start()
            try:
                server = harness.require_server()
                server.services.inventory_service.wear_item(loaded, "koszula", 1)
                server.services.inventory_service.wear_item(loaded, "kolczuga", 1)
                repo.save(loaded)
                reloaded = repo.load("stacked")
                top_item = reloaded.equipment["korpus"]
                self.assertIsNotNone(top_item)
                self.assertEqual([item.display_name() for item in reloaded.equipment.layers("korpus")], ["koszula", "ciemna kolczuga"])
                assert top_item is not None
                self.assertEqual(top_item.display_name(), "ciemna kolczuga")
                text = render_self_observation(
                    name="Stary",
                    gender_id="m",
                    wounds=reloaded.wounds,
                    equipment=reloaded.equipment,
                    appearance_profile=None,
                )
                self.assertIn("Masz na sobie ciemną kolczugę.", text)
                self.assertNotIn("koszula", text)
            finally:
                harness.close()

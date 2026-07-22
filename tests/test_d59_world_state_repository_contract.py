from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.characters.appearance import render_self_observation
from astergard.database.connections import SQLiteConnectionFactory
from astergard.database.world_state_repository import WorldStateRepository
from astergard.items.models import EquipmentSet, Item
from astergard.npcs.models import NPC, NPCFactory
from astergard.world.manager import WorldManager


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
    coverage_mode: str | None = None,
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
        coverage_mode=coverage_mode,
    )


class WorldStateRepositoryContractTests(unittest.TestCase):
    def test_world_state_repository_roundtrip_preserves_equipment_layers_and_visibility_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "world.db"
            cf = SQLiteConnectionFactory(str(db_path))
            cf.migrate()
            repo = WorldStateRepository(cf)

            world = WorldManager()
            world.generate_world()
            npc_factory = NPCFactory()
            npc = npc_factory.create("watch_sergeant", 0)
            npc.id = "world_repo_guard"
            npc.name = "Strażnik"
            npc.short_desc = "Strażnik"
            npc.long_desc = "Strażnik pilnuje drogi."
            npc.room_id = 0
            npc.character.name = "Strażnik"
            npc.character.gender_id = "m"
            npc.character.inventory = []
            npc.character.equipment = EquipmentSet.default()
            npc.character.appearance_profile = None

            shirt = _wearable(
                "koszula",
                vnum="repo_shirt",
                slot="korpus",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("torso", "back", "shoulders", "arms"),
                display_nominative="koszula",
                display_accusative="koszulę",
            )
            chainmail = _wearable(
                "kolczuga",
                vnum="repo_chainmail",
                slot="korpus",
                item_type="armor",
                layer="armor",
                coverage_areas=("torso", "back", "shoulders", "arms", "hands"),
                display_nominative="ciemna kolczuga",
                display_accusative="ciemną kolczugę",
            )
            coat = _wearable(
                "wełniany płaszcz",
                vnum="repo_coat",
                slot="korpus",
                item_type="outerwear",
                layer="outerwear",
                coverage_areas=("torso", "back", "shoulders"),
                coverage_mode="partial",
                display_nominative="wełniany płaszcz",
                display_accusative="wełniany płaszcz",
            )
            legacy = Item("stara zbroja", "Stara zbroja.", 3.0, 10, "repo_legacy_armor", item_type="armor", slot="korpus", wearable=True)
            belt = _wearable(
                "skórzany pas",
                vnum="repo_belt",
                slot="pas",
                item_type="clothing",
                layer="clothing",
                coverage_areas=("waist",),
                display_nominative="skórzany pas",
                display_accusative="skórzany pas",
            )
            pouch = _wearable(
                "sakiewka monet",
                vnum="repo_pouch",
                slot="pas",
                item_type="accessory",
                layer="accessory",
                coverage_areas=(),
                display_nominative="sakiewka monet",
                display_accusative="sakiewkę monet",
            )
            sword = _weapon(
                "długi miecz",
                vnum="repo_sword",
                weapon_profile_id="garrison_short_sword",
                display_accusative="długi miecz",
            )
            shield = _wearable(
                "migdałowa tarcza",
                vnum="repo_shield",
                slot="tarcza",
                item_type="shield",
                display_nominative="migdałowa tarcza",
                display_accusative="migdałową tarczę",
            )

            npc.character.inventory.extend([shirt, chainmail, coat, legacy, belt, pouch, sword, shield])
            npc.character.equipment.push("korpus", shirt)
            npc.character.inventory.remove(shirt)
            npc.character.equipment.push("korpus", chainmail)
            npc.character.inventory.remove(chainmail)
            npc.character.equipment.push("korpus", coat)
            npc.character.inventory.remove(coat)
            npc.character.equipment.push("korpus", legacy)
            npc.character.inventory.remove(legacy)
            npc.character.equipment.push("pas", belt)
            npc.character.inventory.remove(belt)
            npc.character.equipment.push("pas", pouch)
            npc.character.inventory.remove(pouch)
            npc.character.equipment["bron_glowna"] = sword
            npc.character.inventory.remove(sword)
            npc.character.equipment["tarcza"] = shield
            npc.character.inventory.remove(shield)

            world.locations[0].npc_ids = [npc.id]
            npcs = {npc.id: npc}
            repo.save(world, npcs)

            loaded_world = WorldManager()
            loaded_world.generate_world()
            loaded_npcs: dict[str, NPC] = {}
            self.assertTrue(repo.load_into(loaded_world, loaded_npcs, npc_factory))
            loaded_npc = loaded_npcs[npc.id]

            equipment = loaded_npc.character.equipment
            self.assertEqual([item.display_name() for item in equipment.layers("korpus")], ["koszula", "ciemna kolczuga", "wełniany płaszcz", "stara zbroja"])
            self.assertEqual([item.display_name() for item in equipment.layers("pas")], ["skórzany pas", "sakiewka monet"])
            main_weapon = equipment["bron_glowna"]
            loaded_shield = equipment["tarcza"]
            assert main_weapon is not None
            assert loaded_shield is not None
            self.assertEqual(main_weapon.display_name(), "długi miecz")
            self.assertEqual(loaded_shield.display_name(), "migdałowa tarcza")

            visible_text = render_self_observation(
                name="Strażnik",
                gender_id=loaded_npc.character.gender_id,
                wounds=loaded_npc.character.wounds,
                equipment=equipment,
                appearance_profile=None,
            )
            self.assertIn("Spod rozpiętego płaszcza widać ciemną kolczugę.", visible_text)
            self.assertIn("Ramiona okrywa wełniany płaszcz.", visible_text)
            self.assertIn("Widoczne wyposażenie: stara zbroja.", visible_text)
            self.assertIn("Biodra opasuje skórzany pas.", visible_text)
            self.assertIn("U pasa wisi sakiewka monet.", visible_text)
            self.assertIn("W prawej ręce trzymasz długi miecz.", visible_text)
            self.assertIn("W lewej ręce trzymasz migdałową tarczę.", visible_text)
            self.assertNotIn("weapon_profile_id", visible_text)
            self.assertNotIn("display_nominative", visible_text)

            self.assertEqual(len({item.id for item in equipment.all_items()}), len(equipment.all_items()))
            self.assertEqual(equipment.layers("korpus")[2].coverage_mode, "partial")
            self.assertEqual(equipment.layers("korpus")[1].coverage_areas, ("torso", "back", "shoulders", "arms", "hands"))
            self.assertEqual(equipment.layers("pas")[1].display_accusative_name(), "sakiewkę monet")


if __name__ == "__main__":
    unittest.main()

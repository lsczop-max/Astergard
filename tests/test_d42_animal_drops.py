from __future__ import annotations

import unittest
from unittest.mock import patch

from astergard.application.services.animal_loot_service import AnimalLootService
from astergard.application.services.combat_service import CombatApplicationService
from astergard.application.use_case_contexts import CombatContext
from astergard.characters.models import Character
from astergard.combat.manager import CombatManager, CombatResult
from astergard.economy.services import EconomyService
from astergard.engine.events import EventBus
from astergard.factions.reputation import FactionManager
from astergard.npcs.manager import NPCManager
from astergard.npcs.models import NPCFactory
from astergard.quests.manager import QuestManager
from astergard.world.manager import WorldManager


class AnimalDropTests(unittest.TestCase):
    def test_animal_loot_service_builds_tradeable_wolf_drops(self) -> None:
        factory = NPCFactory()
        wolf = factory.create("wolf", 455)
        loot_service = AnimalLootService()

        with patch("astergard.application.services.animal_loot_service.random.random", return_value=0.0):
            loot = loot_service.build_loot(wolf)

        loot_names = {item.name for item in loot}
        self.assertTrue({"wilcza skóra", "wilcze mięso", "wilcze kły", "wilcze pazury", "wilcze futro"}.issubset(loot_names))
        self.assertTrue(all(item.weight > 0 for item in loot))
        self.assertTrue(all(item.value > 0 for item in loot))
        self.assertTrue(all(item.can_be_sold_to_merchants for item in loot))

    def test_animal_loot_service_can_drop_feathers(self) -> None:
        factory = NPCFactory()
        goose = factory.create("podgrodzie_ges", 72)
        loot_service = AnimalLootService()

        with patch("astergard.application.services.animal_loot_service.random.random", return_value=0.0):
            loot = loot_service.build_loot(goose)

        self.assertIn("pióra gęsi", {item.name for item in loot})

    def test_corpse_contains_generated_animal_loot_after_death(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()
        combat = CombatManager()
        factions = FactionManager()
        quests = QuestManager()
        service = CombatApplicationService(world, npcs, combat, factions, quests)
        character = Character("tester")
        character.room_id = 455
        ctx = CombatContext(
            character=character,
            event_bus=EventBus(),
            world=world,
            npcs=npcs,
            combat=combat,
            factions=factions,
            quests=quests,
            move_direct=lambda _character, _direction: "",
        )

        with patch.object(combat, "attack", return_value=CombatResult(True, "Wrog pada martwy.", defender_dead=True)):
            with patch("astergard.application.services.animal_loot_service.random.random", return_value=0.0):
                service.attack_npc(ctx, "wilk", 1)

        location = world.get_location(455)
        assert location is not None
        corpse = next(item for item in location.items if item.vnum == "corpse_wolf")
        corpse_names = {item.name for item in corpse.contains}
        self.assertIn("wilcza skóra", corpse_names)
        self.assertIn("wilcze mięso", corpse_names)
        self.assertIn("wilcze futro", corpse_names)

    def test_new_merchants_spawn_with_stock_and_buyer_can_sell_drops(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()
        merchants = {
            vnum: next(npc for npc in npcs.npcs.values() if npc.vnum == vnum)
            for vnum in ("tanner", "butcher", "skin_trader")
        }
        for merchant in merchants.values():
            self.assertTrue(merchant.is_merchant)
            self.assertGreaterEqual(len(merchant.shop_inventory), 5)
            self.assertGreater(merchant.merchant_gold, 0)

        economy = EconomyService()
        buyer = Character("buyer")
        buyer.inventory.clear()
        with patch("astergard.application.services.animal_loot_service.random.random", return_value=0.0):
            pelt = AnimalLootService().build_loot(NPCFactory().create("wolf", 455))[0]
        buyer.inventory.append(pelt)
        gold_before = buyer.gold
        price_before = merchants["skin_trader"].merchant_gold
        result = economy.sell(buyer, merchants["skin_trader"], pelt.name)
        self.assertIn("Sprzedajesz", result)
        self.assertGreater(buyer.gold, gold_before)
        self.assertLess(merchants["skin_trader"].merchant_gold, price_before)


if __name__ == "__main__":
    unittest.main()

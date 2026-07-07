from __future__ import annotations

import asyncio
import unittest

from astergard.economy.services import EconomyService
from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import WorldManager


class D351ILocalEconomyTests(unittest.TestCase):
    def test_populate_registers_local_shops_with_positive_prices(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        economy = EconomyService()
        for vnum in ["merchant", "innkeeper", "podgrodzie_piekarz", "podgrodzie_kowal", "podgrodzie_rybak", "podgrodzie_przekupka"]:
            merchant = next(npc for npc in npcs.npcs.values() if npc.vnum == vnum)
            self.assertTrue(merchant.is_merchant, vnum)
            self.assertGreater(merchant.merchant_gold, 0, vnum)
            self.assertGreater(len(merchant.shop_inventory), 0, vnum)
            for item in merchant.shop_inventory:
                self.assertGreater(economy.buy_price(item), 0, item.name)

    def test_buy_sell_and_unknown_item_flow_changes_gold(self) -> None:
        async def scenario() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("local_economy", room_id=0)
                char.gold = 20
                server = harness.require_server()
                merchant = next(npc for npc in server.npcs.by_room(0) if npc.is_merchant)

                offer = await harness.execute(char, "oferta")
                self.assertIn("krzesiwo", offer.output)

                gold_before_buy = char.gold
                merchant_gold_before_buy = merchant.merchant_gold
                bought = await harness.execute(char, "kup krzesiwo")
                self.assertIn("Kupujesz krzesiwo", bought.output)
                self.assertLess(char.gold, gold_before_buy)
                self.assertGreater(merchant.merchant_gold, merchant_gold_before_buy)
                self.assertTrue(any(item.name == "krzesiwo" for item in char.inventory))

                gold_before_sell = char.gold
                merchant_gold_before_sell = merchant.merchant_gold
                sold = await harness.execute(char, "sprzedaj chleb")
                self.assertIn("Sprzedajesz chleb", sold.output)
                self.assertGreater(char.gold, gold_before_sell)
                self.assertLess(merchant.merchant_gold, merchant_gold_before_sell)

                await asyncio.sleep(0.6)
                bad = await harness.execute(char, "kup smok")
                self.assertIn("Kupiec nie ma takiego towaru.", bad.output)
                self.assertEqual(char.gold, gold_before_sell + 1)

        asyncio.run(scenario())

    def test_populate_keeps_merchant_data_stable(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        merchant = next(npc for npc in npcs.npcs.values() if npc.vnum == "podgrodzie_przekupka")
        self.assertTrue(merchant.is_merchant)
        self.assertGreater(merchant.merchant_gold, 0)
        self.assertGreater(len(merchant.shop_inventory), 0)


if __name__ == "__main__":
    unittest.main()

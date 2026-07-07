from __future__ import annotations

import asyncio
import unittest

from astergard.economy.services import EconomyService
from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import WorldManager


LOCAL_MERCHANT_VNUMS: tuple[str, ...] = (
    "merchant",
    "innkeeper",
    "podgrodzie_karczmarz",
    "podgrodzie_karczmarka",
    "podgrodzie_piekarz",
    "podgrodzie_kowal",
    "tanner",
    "butcher",
    "skin_trader",
    "podgrodzie_handlarz",
    "podgrodzie_rybak",
    "podgrodzie_przekupka",
)


class D351ILocalEconomyTests(unittest.TestCase):
    def test_populate_registers_local_shops_with_positive_prices(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        economy = EconomyService()
        for vnum in LOCAL_MERCHANT_VNUMS:
            merchant = next(npc for npc in npcs.npcs.values() if npc.vnum == vnum)
            self.assertTrue(merchant.is_merchant, vnum)
            self.assertGreater(merchant.merchant_gold, 0, vnum)
            self.assertGreaterEqual(len(merchant.shop_inventory), 5, vnum)
            self.assertLessEqual(len(merchant.shop_inventory), 10, vnum)
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
                sold = await harness.execute(char, "sprzedaj krzesiwo")
                self.assertIn("Sprzedajesz krzesiwo", sold.output)
                self.assertGreater(char.gold, gold_before_sell)
                self.assertLess(merchant.merchant_gold, merchant_gold_before_sell)
                self.assertFalse(any(item.name == "krzesiwo" for item in char.inventory))
                gold_after_sell = char.gold

                await asyncio.sleep(0.6)
                bad = await harness.execute(char, "kup smok")
                self.assertIn("Kupiec nie ma takiego towaru.", bad.output)
                self.assertEqual(char.gold, gold_after_sell)

        asyncio.run(scenario())

    def test_populate_keeps_merchant_data_stable(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        merchant = next(npc for npc in npcs.npcs.values() if npc.vnum == "podgrodzie_przekupka")
        stock_names = [item.name for item in merchant.shop_inventory]
        stock_gold = merchant.merchant_gold

        npcs.populate()

        self.assertTrue(merchant.is_merchant)
        self.assertEqual([item.name for item in merchant.shop_inventory], stock_names)
        self.assertEqual(merchant.merchant_gold, stock_gold)

    def test_local_merchant_data_survives_populate(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        merchants = {vnum: next(npc for npc in npcs.npcs.values() if npc.vnum == vnum) for vnum in LOCAL_MERCHANT_VNUMS}
        snapshots = {vnum: ([item.name for item in npc.shop_inventory], npc.merchant_gold) for vnum, npc in merchants.items()}

        npcs.populate()

        for vnum, merchant in merchants.items():
            stock_names, stock_gold = snapshots[vnum]
            self.assertTrue(merchant.is_merchant, vnum)
            self.assertEqual([item.name for item in merchant.shop_inventory], stock_names, vnum)
            self.assertEqual(merchant.merchant_gold, stock_gold, vnum)


if __name__ == "__main__":
    unittest.main()

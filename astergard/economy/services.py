from __future__ import annotations

from astergard.characters.models import Character
from astergard.items.models import Item
from astergard.npcs.models import NPC
from astergard.rules.economy import EconomyRules, default_economy_rules

class EconomyService:
    def __init__(self, rules: EconomyRules | None = None) -> None:
        self.rules = rules or default_economy_rules()

    def add_gold(self, char: Character, amount: int) -> None:
        char.gold += max(0, amount)

    def remove_gold(self, char: Character, amount: int) -> bool:
        if char.gold < amount:
            return False
        char.gold -= amount
        return True

    def buy_price(self, item: Item, reputation: int = 0) -> int:
        return self.rules.buy_price(item.value, reputation)

    def sell_price(self, item: Item) -> int:
        return self.rules.sell_price(item.value)

    def buy(self, char: Character, merchant: NPC, item_name: str) -> str:
        item = next((i for i in merchant.shop_inventory if item_name in i.name), None)
        if not item:
            return "Kupiec nie ma takiego towaru."
        price = self.buy_price(item, char.reputation.get(merchant.faction, 0))
        if char.gold < price:
            return "Nie masz dość monet."
        if char.total_weight() + item.weight > char.stats.get_weight_limit():
            return "Nie uniesiesz tego."
        char.gold -= price
        merchant.merchant_gold += price
        merchant.shop_inventory.remove(item)
        char.inventory.append(item)
        return f"Kupujesz {item.name} za {price} monet."

    def sell(self, char: Character, merchant: NPC, item_name: str) -> str:
        item = next((i for i in char.inventory if item_name in i.name), None)
        if not item:
            return "Nie masz takiego przedmiotu."
        price = self.sell_price(item)
        if merchant.merchant_gold < price:
            return "Kupiec nie ma dość monet."
        merchant.merchant_gold -= price
        char.gold += price
        char.inventory.remove(item)
        merchant.shop_inventory.append(item)
        return f"Sprzedajesz {item.name} za {price} monet."

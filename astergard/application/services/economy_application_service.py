from __future__ import annotations

from astergard.application.use_case_contexts import EconomyContext
from astergard.engine.events import DomainEventType
from astergard.economy.services import EconomyService
from astergard.items.models import Item, innkeeper_favor_item
from astergard.factions.reputation import FactionManager
from astergard.npcs.models import NPC


class EconomyApplicationService:
    def __init__(self, economy: EconomyService, factions: FactionManager) -> None:
        self.economy = economy
        self.factions = factions

    def offer(self, ctx: EconomyContext) -> str:
        merchant = self._merchant(ctx)
        if merchant is None:
            return "Nie ma tu kupca."
        if self.factions.merchants_are_hostile(ctx.character, merchant.faction):
            return f"{merchant.name.capitalize()}: Nie handluję z taką reputacją."
        items = self._offer_items(ctx, merchant)
        lines = [
            f"{item.name} - {self.economy.buy_price(item, ctx.character.reputation.get(merchant.faction, 0))} monet"
            for item in items
        ]
        if not lines:
            return "Kupiec nie ma towaru."
        if self.factions.merchants_are_friendly(ctx.character, merchant.faction):
            lines.insert(0, f"{merchant.name.capitalize()}: Dla ciebie cena będzie uczciwsza.")
        elif ctx.character.global_reputation <= self.factions.rules.merchant_hostile_threshold:
            lines.insert(0, f"{merchant.name.capitalize()}: Patrzę na ciebie bardzo nieufnie.")
        return "\n".join(lines)

    def buy(self, ctx: EconomyContext, item_name: str | None) -> str:
        if not item_name:
            return "Co chcesz kupić?"
        merchant = self._merchant(ctx)
        if merchant is None:
            return "Nie ma tu kupca."
        if self.factions.merchants_are_hostile(ctx.character, merchant.faction):
            return "Kupiec odsuwa towar i nie chce handlować z kimś tak poszukiwanym."
        item = self._offered_item(ctx, merchant, item_name)
        if item is None:
            return "Kupiec nie ma takiego towaru."
        if item not in merchant.shop_inventory:
            merchant.shop_inventory.append(item)
        before_gold = ctx.character.gold
        result = self.economy.buy(ctx.character, merchant, item_name)
        if ctx.character.gold < before_gold:
            ctx.event_bus.emit(DomainEventType.ECONOMY_ITEM_BOUGHT, username=ctx.character.username, merchant=merchant.vnum, item=item_name, price=before_gold - ctx.character.gold)
        return result

    def sell(self, ctx: EconomyContext, item_name: str | None) -> str:
        if not item_name:
            return "Co chcesz sprzedać?"
        merchant = self._merchant(ctx)
        if merchant is None:
            return "Nie ma tu kupca."
        if self.factions.merchants_are_hostile(ctx.character, merchant.faction):
            return "Kupiec nie chce kupować od kogoś tak podejrzanego."
        before_gold = ctx.character.gold
        result = self.economy.sell(ctx.character, merchant, item_name)
        if ctx.character.gold > before_gold:
            ctx.event_bus.emit(DomainEventType.ECONOMY_ITEM_SOLD, username=ctx.character.username, merchant=merchant.vnum, item=item_name, price=ctx.character.gold - before_gold)
        return result

    def _merchant(self, ctx: EconomyContext) -> NPC | None:
        return next((npc for npc in ctx.npcs.by_room(ctx.character.room_id) if npc.is_merchant), None)

    def _offer_items(self, ctx: EconomyContext, merchant: NPC) -> list[Item]:
        items = list(merchant.shop_inventory)
        if merchant.vnum == "innkeeper" and "market_delivery" in ctx.character.completed_quests:
            items.append(innkeeper_favor_item())
        return items

    def _offered_item(self, ctx: EconomyContext, merchant: NPC, item_name: str) -> Item | None:
        return next((item for item in self._offer_items(ctx, merchant) if item_name in item.name), None)

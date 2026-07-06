from __future__ import annotations

from astergard.application.use_case_contexts import EconomyContext
from astergard.economy.services import EconomyService
from astergard.npcs.models import NPC
from astergard.engine.events import DomainEventType


class EconomyApplicationService:
    def __init__(self, economy: EconomyService) -> None:
        self.economy = economy

    def offer(self, ctx: EconomyContext) -> str:
        merchant = self._merchant(ctx)
        if merchant is None:
            return "Nie ma tu kupca."
        return "\n".join(f"{item.name} - {self.economy.buy_price(item, ctx.character.reputation.get(merchant.faction, 0))} monet" for item in merchant.shop_inventory) or "Kupiec nie ma towaru."

    def buy(self, ctx: EconomyContext, item_name: str | None) -> str:
        if not item_name:
            return "Co chcesz kupić?"
        merchant = self._merchant(ctx)
        if merchant is None:
            return "Nie ma tu kupca."
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
        before_gold = ctx.character.gold
        result = self.economy.sell(ctx.character, merchant, item_name)
        if ctx.character.gold > before_gold:
            ctx.event_bus.emit(DomainEventType.ECONOMY_ITEM_SOLD, username=ctx.character.username, merchant=merchant.vnum, item=item_name, price=ctx.character.gold - before_gold)
        return result

    def _merchant(self, ctx: EconomyContext) -> NPC | None:
        return next((npc for npc in ctx.npcs.by_room(ctx.character.room_id) if npc.is_merchant), None)

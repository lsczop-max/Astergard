from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from astergard.commands.helpers import give_item_with_quests
from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.inventory_service import InventoryService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]
def build_inventory_handlers(service: InventoryService) -> dict[str, CommandHandler]:
    def loc(ctx: GameContext):
        inv = ctx.inventory()
        return inv, inv.world.get_location(inv.character.room_id)

    def with_location(fn: Callable[[Any, Any, GameContext, str | None, int], str]) -> CommandHandler:
        async def handler(ctx: GameContext, arg: str | None, index: int) -> str:
            inv, room = loc(ctx)
            return fn(inv, room, ctx, arg, index)

        return handler

    def with_inventory(fn: Callable[[Any, GameContext, str | None, int], str]) -> CommandHandler:
        async def handler(ctx: GameContext, arg: str | None, index: int) -> str:
            inv = ctx.inventory()
            return fn(inv, ctx, arg, index)

        return handler

    return {
        "inventory": with_inventory(lambda inv, ctx, arg, index: service.render_inventory(ctx.character)),
        "get": with_location(lambda inv, room, ctx, arg, index: service.get_item(inv.character, room, arg, index, inv.event_bus)),
        "take_from": with_location(lambda inv, room, ctx, arg, index: service.take_from_container(inv.character, arg, index, inv.event_bus, room)),
        "drop": with_location(lambda inv, room, ctx, arg, index: service.drop_item(inv.character, room, arg, index, inv.event_bus)),
        "wear": with_inventory(lambda inv, ctx, arg, index: service.wear_item(inv.character, arg, index, inv.event_bus)),
        "remove": with_inventory(lambda inv, ctx, arg, index: service.remove_item(inv.character, arg, inv.event_bus)),
        "consume": with_inventory(lambda inv, ctx, arg, index: service.consume_item(inv.character, arg, index, inv.event_bus)),
        "put": with_location(lambda inv, room, ctx, arg, index: service.put_item(inv.character, arg, index, inv.event_bus, room)),
        "transfer": with_location(lambda inv, room, ctx, arg, index: service.transfer_item(inv.character, arg, index, inv.event_bus, room)),
        "give_item": with_inventory(lambda inv, ctx, arg, index: give_item_with_quests(service, inv, ctx, arg, index)),
    }

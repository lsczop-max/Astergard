from __future__ import annotations
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING
from astergard.server.context import GameContext
if TYPE_CHECKING:
    from astergard.application.services.inventory_service import InventoryService
CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_inventory_handlers(service: InventoryService) -> dict[str, CommandHandler]:
    def loc(ctx: GameContext):
        inv = ctx.inventory()
        return inv, inv.world.get_location(inv.character.room_id)
    async def cmd_inventory(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.render_inventory(ctx.character)
    async def cmd_get(ctx: GameContext, arg: str | None, index: int) -> str:
        inv, room = loc(ctx); return service.get_item(inv.character, room, arg, index, inv.event_bus)
    async def cmd_drop(ctx: GameContext, arg: str | None, index: int) -> str:
        inv, room = loc(ctx); return service.drop_item(inv.character, room, arg, index, inv.event_bus)
    async def cmd_take_from(ctx: GameContext, arg: str | None, index: int) -> str:
        inv, room = loc(ctx); return service.take_from_container(inv.character, arg, index, inv.event_bus, room)
    async def cmd_wear(ctx: GameContext, arg: str | None, index: int) -> str:
        inv = ctx.inventory(); return service.wear_item(inv.character, arg, index, inv.event_bus)
    async def cmd_remove(ctx: GameContext, arg: str | None, index: int) -> str:
        inv = ctx.inventory(); return service.remove_item(inv.character, arg, inv.event_bus)
    async def cmd_consume(ctx: GameContext, arg: str | None, index: int) -> str:
        inv = ctx.inventory(); return service.consume_item(inv.character, arg, index, inv.event_bus)
    async def cmd_put(ctx: GameContext, arg: str | None, index: int) -> str:
        inv, room = loc(ctx); return service.put_item(inv.character, arg, index, inv.event_bus, room)
    async def cmd_transfer(ctx: GameContext, arg: str | None, index: int) -> str:
        inv, room = loc(ctx); return service.transfer_item(inv.character, arg, index, inv.event_bus, room)
    async def cmd_give(ctx: GameContext, arg: str | None, index: int) -> str:
        inv = ctx.inventory(); return service.give_item(inv.character, ctx.quest_context().npcs, arg, index, inv.event_bus)
    return {"inventory": cmd_inventory, "get": cmd_get, "take_from": cmd_take_from, "drop": cmd_drop,
            "wear": cmd_wear, "remove": cmd_remove, "consume": cmd_consume, "put": cmd_put,
            "transfer": cmd_transfer, "give_item": cmd_give}

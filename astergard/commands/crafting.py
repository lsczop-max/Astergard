from __future__ import annotations

from collections.abc import Awaitable, Callable

from astergard.crafting.services import CraftingService
from astergard.server.context import GameContext

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_crafting_handlers(service: CraftingService) -> dict[str, CommandHandler]:
    async def cmd_craft(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.craft(ctx.character, arg or "")

    return {"craft": cmd_craft}

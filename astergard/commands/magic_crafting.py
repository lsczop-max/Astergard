from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.magic_crafting_service import MagicCraftingApplicationService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_magic_crafting_handlers(service: MagicCraftingApplicationService) -> dict[str, CommandHandler]:
    async def cmd_cast(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.cast(ctx.magic_crafting_context(), arg)

    async def cmd_craft(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.craft(ctx.magic_crafting_context(), arg)

    return {"cast": cmd_cast, "craft": cmd_craft}

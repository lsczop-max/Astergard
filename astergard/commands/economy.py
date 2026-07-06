from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.economy_application_service import EconomyApplicationService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_economy_handlers(service: EconomyApplicationService) -> dict[str, CommandHandler]:
    async def cmd_offer(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.offer(ctx.economy_context())

    async def cmd_buy(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.buy(ctx.economy_context(), arg)

    async def cmd_sell(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.sell(ctx.economy_context(), arg)

    return {"offer": cmd_offer, "buy": cmd_buy, "sell": cmd_sell}

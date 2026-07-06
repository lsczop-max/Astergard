from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.quest_service import QuestApplicationService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_social_handlers(service: QuestApplicationService) -> dict[str, CommandHandler]:
    async def cmd_talk(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.talk(ctx.quest_context(), arg)

    async def cmd_quests(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.render_quest_log(ctx.quest_context().character)

    return {"talk": cmd_talk, "quests": cmd_quests}

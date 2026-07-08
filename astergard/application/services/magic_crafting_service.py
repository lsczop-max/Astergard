from __future__ import annotations

from astergard.application.use_case_contexts import MagicCraftingContext
from astergard.commands.helpers import find_npc_in_manager
from astergard.engine.events import DomainEventType


class MagicCraftingApplicationService:
    def cast(self, ctx: MagicCraftingContext, arg: str | None) -> str:
        if not arg:
            return "Jaki czar chcesz rzucić?"
        if arg.startswith("wzmocnienie"):
            result = ctx.magic.cast_strength(ctx.character)
            ctx.event_bus.emit(DomainEventType.MAGIC_CAST, username=ctx.character.username, spell="wzmocnienie", result=result)
            return result
        if arg.startswith("grot"):
            target_name = arg.replace("grot", "", 1).strip()
            npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, target_name)
            if npc is None:
                return "Nie ma tu celu dla Grotu Źródła."
            result = ctx.magic.magic_bolt(ctx.character, npc.character)
            ctx.event_bus.emit(DomainEventType.MAGIC_CAST, username=ctx.character.username, spell="grot", target=npc.vnum, result=result)
            return result
        return "Nie znasz takiego czaru."

    def craft(self, ctx: MagicCraftingContext, arg: str | None) -> str:
        if not arg:
            return "Co chcesz stworzyć?"
        result = ctx.crafting.craft(ctx.character, arg)
        ctx.event_bus.emit(DomainEventType.CRAFTING_ATTEMPTED, username=ctx.character.username, recipe=arg, result=result)
        return result

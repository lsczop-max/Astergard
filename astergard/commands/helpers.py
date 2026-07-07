from __future__ import annotations

from astergard.items.models import Item
from astergard.npcs.models import NPC
from astergard.commands.polish import any_token_matches, tokens_match


def matching_items(items: list[Item], name: str) -> list[Item]:
    exact = [item for item in items if tokens_match(name, f"{item.name} {item.vnum}")]
    return exact


def find_item(items: list[Item], name: str, index: int = 1) -> Item | None:
    matches = matching_items(items, name)
    return matches[index - 1] if len(matches) >= index else None


def find_npc(ctx: object, room_id: int, name: str) -> NPC | None:
    npc_manager = getattr(ctx, "npcs")
    return next((npc for npc in npc_manager.by_room(room_id) if any_token_matches(name, f"{npc.name} {npc.vnum}")), None)


def find_npc_in_manager(npcs, room_id: int, name: str):
    for npc in npcs.by_room(room_id):
        if any_token_matches(name, f"{npc.name} {npc.vnum}"):
            return npc
    return None


def give_item_with_quests(service, inv, ctx, arg: str | None, index: int) -> str:
    quest_ctx = ctx.quest_context()
    return service.give_item(inv.character, quest_ctx.npcs, quest_ctx.quests, arg, index, inv.event_bus)

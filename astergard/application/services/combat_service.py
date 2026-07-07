from __future__ import annotations

import random

from astergard.application.use_case_contexts import CombatContext
from astergard.characters.models import Character
from astergard.commands.helpers import find_npc_in_manager
from astergard.items.models import Item
from astergard.engine.events import DomainEventType
from astergard.rules.movement import MovementRules, default_movement_rules


class CombatApplicationService:
    """Combat use cases that coordinate combat, corpses, quests and factions."""

    def __init__(self, world=None, npcs=None, combat=None, factions=None, quests=None, movement_rules: MovementRules | None = None) -> None:
        self.world = world
        self.npcs = npcs
        self.combat = combat
        self.factions = factions
        self.quests = quests
        self.movement_rules = movement_rules or default_movement_rules()

    def attack_npc(self, ctx: CombatContext, target_name: str | None, index: int) -> str:
        if not target_name:
            return "Kogo chcesz zaatakować?"
        npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, target_name)
        if npc is None:
            return "Nie widzisz takiego celu."
        result = ctx.combat.attack(ctx.character, npc.character)
        ctx.event_bus.emit(DomainEventType.COMBAT_ATTACKED, username=ctx.character.username, character=ctx.character, target=npc.vnum, room_id=ctx.character.room_id, defender_dead=result.defender_dead, message=result.message)
        message = result.message
        if result.defender_dead:
            self._spawn_corpse(ctx, ctx.character.room_id, npc.name, npc.vnum, npc.character.inventory)
            ctx.factions.register_kill(ctx.character, npc.faction)
            location = ctx.world.get_location(ctx.character.room_id)
            if npc.faction == ctx.factions.MEEKHAN:
                ctx.factions.record_crime(ctx.character, "zabójstwo", zone=location.zone if location is not None else None, detail=npc.vnum)
            ctx.event_bus.emit(DomainEventType.COMBATANT_DIED, username=ctx.character.username, target=npc.vnum, room_id=ctx.character.room_id)
            ctx.event_bus.emit(DomainEventType.NPC_DIED, npc_id=npc.id, vnum=npc.vnum, room_id=ctx.character.room_id)
            ctx.event_bus.emit(DomainEventType.REPUTATION_CHANGED, username=ctx.character.username, faction=npc.faction, reason="kill")
            for progress_message in ctx.quests.progress(ctx.character, "kill", npc.vnum):
                ctx.event_bus.emit(DomainEventType.QUEST_PROGRESS_UPDATED, username=ctx.character.username, objective_type="kill", target=npc.vnum, message=progress_message)
                message += "\n" + progress_message
            ctx.npcs.remove_dead(npc)
        return message

    def flee(self, ctx: CombatContext) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if loc is None or not loc.exits:
            return "Nie masz dokąd uciec."
        if self._legs_block_movement(ctx.character):
            return "<red>Twoje zgruchotane nogi odmówiły posłuszeństwa! Nie możesz się ruszyć!</red>"
        chance = self._flee_chance(ctx.character)
        if random.random() > chance:
            ctx.event_bus.emit(DomainEventType.COMBAT_FLED, username=ctx.character.username, room_id=ctx.character.room_id, success=False)
            return "Nie udało ci się uciec."
        direction = next(iter(loc.exits))
        old_room_id = ctx.character.room_id
        message = ctx.move_direct(ctx.character, direction)
        ctx.event_bus.emit(DomainEventType.COMBAT_FLED, username=ctx.character.username, from_room_id=old_room_id, to_room_id=ctx.character.room_id, direction=direction, success=True)
        return message

    def _spawn_corpse(self, ctx: CombatContext, room_id: int, name: str, vnum: str, inventory: list[Item]) -> None:
        loc = ctx.world.get_location(room_id)
        if loc is None:
            return
        loc.items.append(
            Item(
                f"zwłoki {name}",
                "Ciało pokonanego przeciwnika.",
                5.0,
                0,
                f"corpse_{vnum}",
                is_container=True,
                capacity=999,
                contains=list(inventory),
            )
        )

    def _flee_chance(self, character: Character) -> float:
        chance = 0.6
        if max(character.wounds.get("prawa_noga", 0), character.wounds.get("lewa_noga", 0)) >= self.movement_rules.severe_leg_wound_level:
            chance /= 2
        return chance

    def _legs_block_movement(self, character: Character) -> bool:
        return self.movement_rules.movement_blocked(character.wounds.get("prawa_noga", 0), character.wounds.get("lewa_noga", 0))

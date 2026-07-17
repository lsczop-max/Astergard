from __future__ import annotations

import random
from uuid import uuid4

from astergard.application.use_case_contexts import CombatContext
from astergard.application.services.animal_loot_service import AnimalLootService
from astergard.characters.models import Character
from astergard.commands.helpers import find_npc_in_manager
from astergard.commands.polish import normalize_phrase
from astergard.items.models import Item
from astergard.engine.events import DomainEventType
from astergard.npcs.models import NPC
from astergard.combat.defense import can_select_defense_style, select_defense_style
from astergard.rules.combat_specialization import ActiveDefenseStyle, defense_style_label
from astergard.rules.movement import MovementRules, default_movement_rules


class CombatApplicationService:
    """Combat use cases that coordinate combat, corpses, quests and factions."""

    def __init__(self, world=None, npcs=None, combat=None, factions=None, quests=None, movement_rules: MovementRules | None = None, loot_service: AnimalLootService | None = None) -> None:
        self.world = world
        self.npcs = npcs
        self.combat = combat
        self.factions = factions
        self.quests = quests
        self.movement_rules = movement_rules or default_movement_rules()
        self.loot_service = loot_service or AnimalLootService()

    def attack_npc(self, ctx: CombatContext, target_name: str | None, index: int) -> str:
        if not target_name:
            return "Kogo chcesz zaatakować?"
        npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, target_name)
        if npc is None:
            return "Nie ma tu takiego celu."
        started = ctx.combat.start_fight(ctx.character, npc.character)
        if not started:
            return f"Już walczysz z {npc.name}."
        npc_identity = npc.character.combat_identity or npc.character.username
        result = ctx.combat.attack(ctx.character, npc.character)
        self._emit_combat_attack(ctx, result, target=npc.vnum)
        message = result.message
        if result.defender_dead:
            ctx.combat.end_fight(
                ctx.character.username,
                npc_identity,
                reason="DEATH",
                entities={ctx.character.username: ctx.character, npc_identity: npc.character},
            )
            self._spawn_corpse(ctx, ctx.character.room_id, npc)
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
        reaction_execution = result.reaction_execution
        reaction_result = reaction_execution.reaction_result if reaction_execution is not None else None
        if reaction_execution is not None and reaction_execution.executed and reaction_result is not None:
            self._emit_combat_attack(
                ctx,
                reaction_result,
                target=ctx.character.username,
                actor=reaction_result.combat_action.actor_id if reaction_result.combat_action is not None else ctx.character.username,
            )
            if bool(getattr(reaction_result, "defender_dead", False)):
                killer = reaction_result.combat_action.actor_id if reaction_result.combat_action is not None else npc_identity
                ctx.combat.end_fight(
                    ctx.character.username,
                    npc_identity,
                    reason="DEATH",
                    entities={ctx.character.username: ctx.character, npc_identity: npc.character},
                )
                ctx.event_bus.emit(
                    DomainEventType.COMBATANT_DIED,
                    username=killer,
                    target=ctx.character.username,
                    room_id=ctx.character.room_id,
                )
            elif not ctx.character.is_alive or not npc.character.is_alive:
                killer = reaction_result.combat_action.actor_id if reaction_result.combat_action is not None else npc_identity
                ctx.combat.end_fight(
                    ctx.character.username,
                    npc_identity,
                    reason="DEATH",
                    entities={ctx.character.username: ctx.character, npc_identity: npc.character},
                )
                if not ctx.character.is_alive:
                    ctx.event_bus.emit(
                        DomainEventType.COMBATANT_DIED,
                        username=killer,
                        target=ctx.character.username,
                        room_id=ctx.character.room_id,
                    )
        elif (
            result.reaction_discovery is not None
            and result.combat_outcome is not None
            and result.combat_outcome.defense_outcome is not None
            and result.combat_outcome.defense_outcome.resolution.value == "PARRIED"
            and result.reaction_discovery.available_reactions
        ):
            reaction = result.reaction_discovery.available_reactions[0]
            reaction_outcome = reaction_execution.reaction_result if reaction_execution is not None else None
            if reaction_outcome is not None:
                self._emit_combat_attack(
                    ctx,
                    reaction_outcome,
                    target=ctx.character.username,
                    actor=reaction_outcome.combat_action.actor_id if reaction_outcome.combat_action is not None else npc_identity,
                )
            else:
                ctx.event_bus.emit(
                    DomainEventType.COMBAT_ATTACKED,
                    username=npc_identity,
                    target=ctx.character.username,
                    room_id=ctx.character.room_id,
                    action_id=uuid4().hex,
                    defender_dead=bool(not ctx.character.is_alive),
                    message=result.message,
                    observer_message=result.observer_message,
                    defender_message=result.defender_message,
                    action_type="REACTION",
                    parent_action_id=result.combat_action.action_id if result.combat_action is not None else None,
                    reaction_id=reaction.reaction_id,
                    reaction_depth=1,
                    technique_id=reaction.technique_id,
                )
        if ctx.combat.has_fight(ctx.character.username, npc_identity) and (
            not ctx.character.is_alive
            or not npc.character.is_alive
            or ctx.character.room_id != npc.character.room_id
        ):
            ctx.combat.end_fight(
                ctx.character.username,
                npc_identity,
                reason="DEATH" if not ctx.character.is_alive or not npc.character.is_alive else "SEPARATED",
                entities={ctx.character.username: ctx.character, npc_identity: npc.character},
            )
        return message

    def flee(self, ctx: CombatContext) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if loc is None or not loc.exits:
            return "Nie masz dokąd się cofnąć."
        if self._legs_block_movement(ctx.character):
            return "<red>Twoje nogi nie chcą już nieść cię dalej.</red>"
        chance = self._flee_chance(ctx.character)
        if random.random() > chance:
            ctx.event_bus.emit(DomainEventType.COMBAT_FLED, username=ctx.character.username, room_id=ctx.character.room_id, success=False)
            return "Nie udaje ci się wyrwać z walki."
        old_room_id = ctx.character.room_id
        participants: dict[str, Character] = {ctx.character.username: ctx.character}
        if ctx.players_in_room is not None:
            for player in ctx.players_in_room(old_room_id):
                if player.username != ctx.character.username:
                    participants[player.username] = player
        for npc in ctx.npcs.by_room(old_room_id):
            npc_identity = getattr(npc.character, "combat_identity", npc.id)
            participants.setdefault(str(npc_identity), npc.character)
        direction = next(iter(loc.exits))
        message = ctx.move_direct(ctx.character, direction)
        if ctx.character.room_id == old_room_id:
            return message
        ctx.combat.end_fight(ctx.character.username, reason="FLED", entities=participants)
        ctx.event_bus.emit(DomainEventType.COMBAT_FLED, username=ctx.character.username, from_room_id=old_room_id, to_room_id=ctx.character.room_id, direction=direction, success=True)
        return message

    def set_defense_style(self, ctx: CombatContext, defense_style: str | None) -> str:
        if not defense_style:
            return f"Sposób obrony: {defense_style_label(ctx.character.active_defense_style)}."
        resolved = self._resolve_defense_style(defense_style)
        if resolved is None:
            return "Nie rozpoznajesz takiego sposobu obrony. Znasz: uniki, parowanie albo tarczę."
        result = can_select_defense_style(ctx.character, resolved)
        if not result.allowed:
            return result.message
        select_defense_style(ctx.character, resolved)
        return result.message

    def _spawn_corpse(self, ctx: CombatContext, room_id: int, npc: NPC) -> None:
        loc = ctx.world.get_location(room_id)
        if loc is None:
            return
        loot = self.loot_service.build_loot(npc)
        loc.items.append(
            Item(
                f"zwłoki {npc.name}",
                "Ciało pokonanego przeciwnika.",
                5.0,
                0,
                f"corpse_{npc.vnum}",
                is_container=True,
                capacity=999,
                contains=[*npc.character.inventory, *loot],
            )
        )

    def _flee_chance(self, character: Character) -> float:
        chance = 0.6
        if max(character.wounds.get("prawa_noga", 0), character.wounds.get("lewa_noga", 0)) >= self.movement_rules.severe_leg_wound_level:
            chance /= 2
        return chance

    def _legs_block_movement(self, character: Character) -> bool:
        return self.movement_rules.movement_blocked(character.wounds.get("prawa_noga", 0), character.wounds.get("lewa_noga", 0))

    def _resolve_defense_style(self, defense_style: str) -> ActiveDefenseStyle | None:
        folded = normalize_phrase(defense_style).casefold()
        if folded in {"uniki", "unikami", "unik", "dodge"}:
            return ActiveDefenseStyle.DODGE
        if folded in {"parowanie", "parowaniem", "parry"}:
            return ActiveDefenseStyle.PARRY
        if folded in {"tarcza", "tarcze", "tarczą", "tarczami", "shield"}:
            return ActiveDefenseStyle.SHIELD
        return None

    def _emit_combat_attack(self, ctx: CombatContext, result: object, *, target: str, actor: str | None = None) -> None:
        combat_action = getattr(result, "combat_action", None)
        combat_event = getattr(result, "combat_event", None)
        if combat_action is None and combat_event is None:
            return
        self._emit_combat_payload(
            ctx,
            username=actor or ctx.character.username,
            target=target,
            room_id=ctx.character.room_id,
            action_id=combat_action.action_id if combat_action is not None else None,
            defender_dead=bool(getattr(result, "defender_dead", False)),
            message=getattr(result, "message", ""),
            combat_event=combat_event.to_dict() if combat_event is not None else None,
            observer_message=getattr(result, "observer_message", None),
            defender_message=getattr(result, "defender_message", None),
            action_type=combat_action.action_type.value if combat_action is not None else None,
            parent_action_id=combat_action.parent_action_id if combat_action is not None else None,
            reaction_id=combat_action.reaction_id if combat_action is not None else None,
            reaction_depth=combat_action.reaction_depth if combat_action is not None else None,
            technique_id=combat_action.technique_id if combat_action is not None else None,
        )

    def _emit_combat_payload(self, ctx: CombatContext, **payload: object) -> None:
        ctx.event_bus.emit(DomainEventType.COMBAT_ATTACKED, **payload)

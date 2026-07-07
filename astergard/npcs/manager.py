from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Protocol, cast

from astergard.characters.models import Character
from astergard.combat.manager import CombatManager
from astergard.factions.reputation import FactionManager
from astergard.npcs.models import NPC, NPCFactory
from astergard.world.manager import WorldManager
from astergard.rules.respawn import RespawnRules, default_respawn_rules


class RandomSource(Protocol):
    def random(self) -> float: ...
    def choice(self, seq): ...


@dataclass(slots=True)
class NPCActionEvent:
    kind: str
    npc_id: str
    room_id: int
    message: str
    target_username: str | None = None


class NPCManager:
    MAX_NPCS_PER_ROOM = 3

    def __init__(self, world: WorldManager, rules: RespawnRules | None = None) -> None:
        self.world = world
        self.rules = rules or default_respawn_rules()
        self.factory = NPCFactory()
        self.npcs: dict[str, NPC] = {}
        self.events: list[NPCActionEvent] = []

    def populate(self) -> None:
        for rid in [0, 5, 20]:
            self.spawn("meekhan_soldier", rid)
        self.spawn("merchant", 0)
        self.spawn("astergard_guard", 2)
        self.spawn("blacksmith", 12)
        self.spawn("innkeeper", 14)
        self.spawn("astergard_guard", 25)
        self.spawn("astergard_guard", 26)
        self.spawn("fisherman", 38)
        self.spawn("beggar", 40)
        self.spawn("traveler", 59)
        self.spawn("child", 60)
        self.spawn("farmer", 80)
        self.spawn("farmer", 84)
        self.spawn("traveler", 100)
        self.spawn("astergard_guard", 110)
        self.spawn("farmer", 113)
        for rid in [101, 125, 233, 399]:
            self.spawn("wolf", rid)

    def can_spawn_at(self, room_id: int) -> bool:
        loc = self.world.get_location(room_id)
        return loc is not None and self.rules.can_spawn(len(loc.npc_ids))

    def spawn(self, vnum: str, room_id: int) -> NPC | None:
        loc = self.world.get_location(room_id)
        if loc is None or not self.rules.can_spawn(len(loc.npc_ids)):
            return None
        npc = self.factory.create(vnum, room_id)
        npc.home_room_id = room_id
        self.npcs[npc.id] = npc
        loc.npc_ids.append(npc.id)
        return npc

    def by_room(self, room_id: int) -> list[NPC]:
        loc = self.world.get_location(room_id)
        return [self.npcs[nid] for nid in (loc.npc_ids if loc else []) if nid in self.npcs]

    def remove_dead(self, npc: NPC) -> None:
        loc = self.world.get_location(npc.room_id)
        if loc and npc.id in loc.npc_ids:
            loc.npc_ids.remove(npc.id)
        self.npcs.pop(npc.id, None)
        self.world.respawn_queue.append(
            {
                "vnum": npc.vnum,
                "room_id": npc.home_room_id,
                "death_room_id": npc.room_id,
                "time": time.time(),
                "delay": npc.respawn_delay_seconds,
            }
        )

    def respawn_tick(self, now: float | None = None) -> list[NPCActionEvent]:
        current_time = time.time() if now is None else now
        events: list[NPCActionEvent] = []
        pending = list(self.world.respawn_queue)
        self.world.respawn_queue.clear()
        for item in pending:
            delay_value = cast(float | int | None, item.get("delay", self.rules.default_delay_seconds))
            room_id_value = cast(float | int | str, item.get("room_id", item.get("death_room_id", 0)))
            time_value = cast(float | int | str, item["time"])

            delay = self.rules.normalized_delay(delay_value)
            room_id = int(room_id_value)
            if current_time - float(time_value) < delay:
                self.world.respawn_queue.append(item)
                continue
            if not self.can_spawn_at(room_id):
                item["time"] = current_time
                self.world.respawn_queue.append(item)
                continue
            npc = self.spawn(str(cast(Any, item["vnum"])), room_id)
            if npc is not None:
                event = NPCActionEvent("respawn", npc.id, room_id, f"{npc.name} wraca do świata.")
                events.append(event)
                self.events.append(event)
        return events

    def ai_tick(
        self,
        players: list[Character] | None = None,
        combat: CombatManager | None = None,
        factions: FactionManager | None = None,
        rng: RandomSource | None = None,
    ) -> list[NPCActionEvent]:
        random_source: RandomSource = rng or random
        events: list[NPCActionEvent] = []
        players = players or []
        for npc in list(self.npcs.values()):
            if not npc.character.is_alive:
                continue
            if npc.ai_state == "PATROL":
                event = self._patrol_tick(npc, random_source)
                if event is not None:
                    events.append(event)
            elif npc.ai_state == "AGGRESSIVE":
                event = self._aggression_tick(npc, players, combat)
                if event is not None:
                    events.append(event)
            elif npc.ai_state == "GUARD" and factions is not None:
                event = self._guard_tick(npc, players, combat, factions)
                if event is not None:
                    events.append(event)
        self.events.extend(events)
        return events

    def _patrol_tick(self, npc: NPC, rng: RandomSource) -> NPCActionEvent | None:
        if rng.random() > self.rules.patrol_move_chance:
            return None
        loc = self.world.get_location(npc.room_id)
        if not loc or not loc.exits:
            return None
        candidates = []
        for direction, exit_ in loc.exits.items():
            if exit_.is_locked:
                continue
            target = self.world.get_location(exit_.target_room)
            if target is None or target.zone != npc.zone or not self.rules.can_spawn(len(target.npc_ids)):
                continue
            candidates.append((direction, target.id))
        if not candidates:
            return None
        direction, target_room = rng.choice(candidates)
        if npc.id in loc.npc_ids:
            loc.npc_ids.remove(npc.id)
        target = self.world.get_location(target_room)
        if target and npc.id not in target.npc_ids:
            target.npc_ids.append(npc.id)
        npc.room_id = target_room
        return NPCActionEvent("patrol", npc.id, target_room, f"{npc.name} odchodzi na {direction}.")

    def _aggression_tick(
        self,
        npc: NPC,
        players: list[Character],
        combat: CombatManager | None,
    ) -> NPCActionEvent | None:
        target = next((player for player in players if player.is_alive and player.room_id == npc.room_id), None)
        if target is None:
            return None
        if combat is not None:
            combat.start(npc.id, target.username)
        npc.character.enter_combat()
        target.enter_combat()
        return NPCActionEvent(
            "aggression",
            npc.id,
            npc.room_id,
            f"<red>{npc.name} rzuca się na {target.username}!</red>",
            target.username,
        )

    def _guard_tick(
        self,
        npc: NPC,
        players: list[Character],
        combat: CombatManager | None,
        factions: FactionManager,
    ) -> NPCActionEvent | None:
        target = next(
            (
                player
                for player in players
                if player.is_alive and player.room_id == npc.room_id and factions.hostile_to_guards(player)
            ),
            None,
        )
        if target is None:
            return None
        if combat is not None:
            combat.start(npc.id, target.username)
        npc.character.enter_combat()
        target.enter_combat()
        return NPCActionEvent(
            "guard_aggression",
            npc.id,
            npc.room_id,
            f"<red>{npc.name} rozpoznaje wroga Imperium i atakuje {target.username}!</red>",
            target.username,
        )

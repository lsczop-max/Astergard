from __future__ import annotations

import random
import time
from dataclasses import dataclass
from collections import deque
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


@dataclass(frozen=True, slots=True)
class DailyRoutine:
    activity_by_phase: dict[str, str]
    route_depth: int = 2


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
        self.spawn("woodcutter", 6)
        self.spawn("podgrodzie_woznica", 60)
        self.spawn("podgrodzie_karczmarz", 62)
        self.spawn("podgrodzie_karczmarka", 62)
        self.spawn("podgrodzie_pielgrzym", 62)
        self.spawn("podgrodzie_piekarz", 63)
        self.spawn("podgrodzie_handlarz", 63)
        self.spawn("podgrodzie_przekupka", 76)
        self.spawn("podgrodzie_kowal", 66)
        self.spawn("podgrodzie_pomocnik_kowala", 66)
        self.spawn("podgrodzie_straznik_miejski", 66)
        self.spawn("podgrodzie_rybak", 69)
        self.spawn("podgrodzie_dziecko", 72)
        self.spawn("podgrodzie_zebrak", 75)
        self.spawn("podgrodzie_chlop", 77)
        self.spawn("podgrodzie_chlopka", 78)
        self.spawn("astergard_guard", 25)
        self.spawn("watch_sergeant", 25)
        self.spawn("astergard_guard", 26)
        self.spawn("customs_clerk", 43)
        self.spawn("dockhand", 41)
        self.spawn("fishmonger", 42)
        self.spawn("fisherman", 42)
        self.spawn("beggar", 40)
        self.spawn("traveler", 59)
        self.spawn("child", 24)
        self.spawn("urchin", 24)
        self.spawn("farmer", 80)
        self.spawn("farmer", 84)
        self.spawn("miller", 87)
        self.spawn("traveler", 100)
        self.spawn("astergard_guard", 110)
        self.spawn("farmer", 113)
        self.spawn("priest_aide", 35)
        self.spawn("vagrant", 56)
        self.spawn("carpenter", 48)
        self.spawn("tanner", 49)
        self.spawn("bowyer", 50)
        self.spawn("armorer", 51)
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

    def _day_phase(self, hour: int) -> str:
        if 5 <= hour < 8:
            return "świt"
        if 8 <= hour < 18:
            return "dzień"
        if 18 <= hour < 22:
            return "wieczór"
        return "noc"

    def _routine_for(self, npc: NPC) -> DailyRoutine:
        if npc.vnum in {"astergard_guard", "watch_sergeant", "podgrodzie_straznik_miejski"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Zmienia wartę i rozgląda się po ulicy.",
                    "dzień": "Patroluje ulicę.",
                    "wieczór": "Obchodzi posterunek przed nocą.",
                    "noc": "Zmienia wartę i pilnuje bramy.",
                },
                route_depth=3,
            )
        if npc.vnum in {"innkeeper", "podgrodzie_karczmarz", "podgrodzie_karczmarka"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Sprząta salę i otrzepuje stoły.",
                    "dzień": "Obsługuje gości przy ladzie.",
                    "wieczór": "Wyciera drewniane stoły i liczy kufle.",
                    "noc": "Zostaje w karczmie po zamknięciu drzwi.",
                },
                route_depth=2,
            )
        if npc.vnum in {"merchant", "customs_clerk", "fishmonger", "podgrodzie_handlarz", "podgrodzie_przekupka"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Rozstawia towar i sprawdza wagę.",
                    "dzień": "Handluje na targu i pilnuje cen.",
                    "wieczór": "Pakuje skrzynki i zwija płótno.",
                    "noc": "Zamyka stoisko i odkłada klucze.",
                },
                route_depth=2,
            )
        if npc.vnum in {"blacksmith", "carpenter", "tanner", "bowyer", "armorer", "podgrodzie_kowal", "podgrodzie_pomocnik_kowala"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Otwiera warsztat i przygotowuje narzędzia.",
                    "dzień": "Uderza młotem w rozgrzane żelazo.",
                    "wieczór": "Czyści stanowisko i wygasza ogień.",
                    "noc": "Wraca do domu z zapachem dymu i metalu.",
                },
                route_depth=2,
            )
        if npc.vnum in {"fisherman", "podgrodzie_rybak", "dockhand"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Idzie nad wodę z sieciami i liną.",
                    "dzień": "Niesie świeżo złowione ryby.",
                    "wieczór": "Wraca z połowu ciężkim krokiem.",
                    "noc": "Odpoczywa od soli i wilgoci.",
                },
                route_depth=2,
            )
        if npc.vnum == "podgrodzie_woznica":
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Sprawdza uprząż i koła wozu.",
                    "dzień": "Prowadzi wóz po błotnej drodze.",
                    "wieczór": "Odprowadza zaprzęg do stajni.",
                    "noc": "Pilnuje wozu pod płachtą.",
                },
                route_depth=3,
            )
        if npc.vnum == "podgrodzie_piekarz":
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Rozpala piec i wyrabia ciasto.",
                    "dzień": "Wyciąga bochenki z pieca.",
                    "wieczór": "Czyści blaty i liczy bochenki.",
                    "noc": "Odpoczywa po nocnym wypieku.",
                },
                route_depth=2,
            )
        if npc.vnum in {"child", "urchin", "podgrodzie_dziecko"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Wysuwa się na podwórko, zanim dorośli skończą poranki.",
                    "dzień": "Biega między zaułkami i zagląda do cudzych spraw.",
                    "wieczór": "Wraca do domu przed zmrokiem.",
                    "noc": "Śpi w bezpiecznym kącie.",
                },
                route_depth=2,
            )
        if npc.vnum in {"beggar", "vagrant", "podgrodzie_zebrak"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Szuka suchego miejsca przy ścianie.",
                    "dzień": "Prosi o jałmużnę i wypatruje dobrych twarzy.",
                    "wieczór": "Szuka schronienia przed nocą.",
                    "noc": "Drzemie pod murem.",
                },
                route_depth=2,
            )
        if npc.vnum in {"traveler", "podgrodzie_pielgrzym"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Zbiera sakwy i rusza w drogę.",
                    "dzień": "Przemierza ulice i szuka traktu.",
                    "wieczór": "Szuka noclegu przed zmrokiem.",
                    "noc": "Odpoczywa po długiej drodze.",
                },
                route_depth=2,
            )
        if npc.vnum in {"farmer", "woodcutter", "miller", "priest_aide", "podgrodzie_chlop", "podgrodzie_chlopka"}:
            return DailyRoutine(
                activity_by_phase={
                    "świt": "Przygotowuje narzędzia i zaczyna dzień pracy.",
                    "dzień": "Zajmuje się codziennym obowiązkiem.",
                    "wieczór": "Zamyka robotę i wraca do domu.",
                    "noc": "Odpoczywa po pracy.",
                },
                route_depth=3,
            )
        return DailyRoutine(
            activity_by_phase={
                "świt": "Rozpoczyna zwykły dzień.",
                "dzień": "Zajmuje się swoimi sprawami.",
                "wieczór": "Powoli kończy dzień.",
                "noc": "Odpoczywa w ciszy.",
            },
            route_depth=1,
        )

    def _local_route(self, npc: NPC, depth: int) -> list[int]:
        start_room = npc.home_room_id or npc.room_id
        start = self.world.get_location(start_room)
        if start is None:
            return [npc.room_id]
        route = [start.id]
        seen = {start.id}
        queue: deque[int] = deque([start.id])
        while queue and len(route) < depth + 1:
            room_id = queue.popleft()
            loc = self.world.get_location(room_id)
            if loc is None:
                continue
            for exit_ in loc.exits.values():
                target = self.world.get_location(exit_.target_room)
                if target is None or target.zone != npc.zone or target.id in seen:
                    continue
                seen.add(target.id)
                route.append(target.id)
                queue.append(target.id)
                if len(route) >= depth + 1:
                    break
        return route

    def _target_room_for_phase(self, npc: NPC, phase: str) -> int:
        routine = self._routine_for(npc)
        route = self._local_route(npc, routine.route_depth)
        if len(route) == 1:
            return route[0]
        if phase == "świt":
            return route[0]
        if phase == "dzień":
            return route[min(1, len(route) - 1)]
        if phase == "wieczór":
            return route[min(2, len(route) - 1)]
        return route[0]

    def _move_npc_towards(self, npc: NPC, target_room_id: int) -> NPCActionEvent | None:
        if npc.room_id == target_room_id:
            return None
        start = self.world.get_location(npc.room_id)
        target = self.world.get_location(target_room_id)
        if start is None or target is None or start.zone != npc.zone or target.zone != npc.zone:
            return None
        queue: deque[tuple[int, list[int]]] = deque([(start.id, [start.id])])
        seen = {start.id}
        while queue:
            room_id, path = queue.popleft()
            if room_id == target.id:
                if len(path) < 2:
                    return None
                next_room = path[1]
                direction = next(
                    (direction for direction, exit_ in start.exits.items() if exit_.target_room == next_room),
                    None,
                )
                if direction is None:
                    return None
                destination = self.world.get_location(next_room)
                if not self.rules.can_spawn(len(destination.npc_ids) if destination is not None else 0):
                    return None
                if npc.id in start.npc_ids:
                    start.npc_ids.remove(npc.id)
                if destination is not None and npc.id not in destination.npc_ids:
                    destination.npc_ids.append(npc.id)
                npc.room_id = next_room
                return NPCActionEvent("move", npc.id, next_room, f"{npc.name} przechodzi na {direction}.")
            current = self.world.get_location(room_id)
            if current is None:
                continue
            for exit_ in current.exits.values():
                neighbor = self.world.get_location(exit_.target_room)
                if neighbor is None or neighbor.zone != npc.zone or neighbor.id in seen:
                    continue
                seen.add(neighbor.id)
                queue.append((neighbor.id, path + [neighbor.id]))
        return None

    def _apply_daily_routine(self, npc: NPC, phase: str) -> NPCActionEvent | None:
        routine = self._routine_for(npc)
        npc.daily_phase = phase
        npc.daily_activity = routine.activity_by_phase.get(phase, routine.activity_by_phase["dzień"])
        target_room_id = self._target_room_for_phase(npc, phase)
        npc.daily_target_room_id = target_room_id
        return self._move_npc_towards(npc, target_room_id)

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
        hour: int | None = None,
    ) -> list[NPCActionEvent]:
        random_source: RandomSource = rng or random
        events: list[NPCActionEvent] = []
        players = players or []
        phase = self._day_phase(hour) if hour is not None else None
        for npc in list(self.npcs.values()):
            if not npc.character.is_alive:
                continue
            if phase is not None:
                daily_event = self._apply_daily_routine(npc, phase)
                if daily_event is not None:
                    events.append(daily_event)
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

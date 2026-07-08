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
        self.spawn("podgrodzie_ges", 72)
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
        self.spawn("haldun_farmer", 80)
        self.spawn("haldun_farmer", 82)
        self.spawn("haldun_wellkeeper", 83)
        self.spawn("haldun_farmerka", 84)
        self.spawn("haldun_solt", 85)
        self.spawn("haldun_miller", 87)
        self.spawn("haldun_blacksmith", 88)
        self.spawn("haldun_merchant", 89)
        self.spawn("haldun_pasterz", 92)
        self.spawn("haldun_wartownik", 94)
        self.spawn("dungrim_guard", 110)
        self.spawn("dungrim_patrol_guard", 112)
        self.spawn("dungrim_stablemaster", 114)
        self.spawn("dungrim_cook", 115)
        self.spawn("dungrim_sergeant", 116)
        self.spawn("dungrim_military_blacksmith", 117)
        self.spawn("dungrim_lieutenant", 118)
        self.spawn("dungrim_patrol_guard", 119)
        self.spawn("dungrim_commander", 120)
        self.spawn("dungrim_armorer", 121)
        self.spawn("dungrim_quartermaster", 122)
        self.spawn("dungrim_storekeeper", 123)
        self.spawn("dungrim_guard", 124)
        self.spawn("traveler", 100)
        self.spawn("priest_aide", 35)
        self.spawn("vagrant", 56)
        self.spawn("carpenter", 48)
        self.spawn("tanner", 49)
        self.spawn("bowyer", 50)
        self.spawn("armorer", 51)
        self.spawn("butcher", 53)
        self.spawn("skin_trader", 54)
        for rid in [101, 233, 399]:
            self.spawn("wolf", rid)
        self.spawn("straznica_dowodca", 125)
        self.spawn("straznica_wartownik", 126)
        self.spawn("straznica_zwiadowca", 127)
        self.spawn("straznica_przewodnik", 128)
        self.spawn("straznica_karawanowy", 129)
        self.spawn("straznica_woznica", 130)
        self.spawn("straznica_podrozny", 131)
        self.spawn("straznica_pielgrzym", 132)
        self.spawn("straznica_mysliwy", 133)
        self.spawn("straznica_wartownik", 134)
        self.spawn("puszcza_mysliwy", 216)
        self.spawn("puszcza_szczur", 216)
        self.spawn("puszcza_pajak", 216)
        self.spawn("puszcza_zielarz", 223)
        self.spawn("puszcza_kruk", 223)
        self.spawn("puszcza_lis", 223)
        self.spawn("puszcza_wilk_mlody", 229)
        self.spawn("puszcza_pajak_lesny", 229)
        self.spawn("puszcza_jelen", 241)
        self.spawn("puszcza_niedzwiedz", 241)
        self.spawn("puszcza_niedzwiedzica", 241)
        self.spawn("puszcza_drwal", 246)
        self.spawn("puszcza_bandyta", 246)
        self.spawn("puszcza_bandyta_lucznik", 246)
        self.spawn("puszcza_pustelnik", 252)
        self.spawn("puszcza_bandyta_zwiadowca", 252)
        self.spawn("puszcza_lowca", 252)
        self.spawn("puszcza_lowczy", 258)
        self.spawn("puszcza_pajak_duzy", 258)
        self.spawn("puszcza_wilk", 234)
        self.spawn("puszcza_wilk_stary", 234)
        self.spawn("puszcza_wataha_wilkow", 234)
        self.spawn("puszcza_dzik", 267)
        self.spawn("puszcza_bandycki_naczelnik", 267)
        self.spawn("puszcza_niedzwiedzi_olbrzym", 267)
        self.spawn("puszcza_troll", 274)
        self.spawn("puszcza_mysliwy", 185, "Boczne_Drogi")
        self.spawn("puszcza_zielarz", 190, "Boczne_Drogi")
        self.spawn("puszcza_szczur", 183, "Boczne_Drogi")
        self.spawn("puszcza_kruk", 196, "Boczne_Drogi")
        self.spawn("puszcza_lis", 201, "Boczne_Drogi")
        self.spawn("puszcza_pies_dziki", 200, "Boczne_Drogi")
        self.spawn("puszcza_wilk_mlody", 203, "Boczne_Drogi")
        self.spawn("puszcza_wilk", 206, "Boczne_Drogi")
        self.spawn("bagna_zielarz", 478)
        self.spawn("bagna_zaba", 481)
        self.spawn("bagna_mysliwy", 488)
        self.spawn("bagna_pustelnik", 493)
        self.spawn("traveler", 180, "Boczne_Drogi")
        self.spawn("puszcza_mysliwy", 280, "Knieja_Cichych_Sciezek")
        self.spawn("mountain_troll", 335, "Gory_Mekhara")
        self.spawn("warband_captain", 425, "Ruiny_Karshold")
        self.spawn("wolf", 455, "Jaskinie_Wilkow")
        self.spawn("trakty_przewodnik", 135)
        self.spawn("trakty_pielgrzym", 136)
        self.spawn("trakty_karawaniarz", 138)
        self.spawn("trakty_kurier", 140)
        self.spawn("trakty_woznica", 141)
        self.spawn("trakty_podrozny", 145)
        self.spawn("trakty_zebrak", 156)
        self.spawn("trakty_mysliwy", 165)
        self.spawn("trakty_drwal", 166)
        self.spawn("trakty_straznik", 172)
        self.spawn("trakty_handlarz", 176)

    def can_spawn_at(self, room_id: int) -> bool:
        loc = self.world.get_location(room_id)
        return loc is not None and self.rules.can_spawn(len(loc.npc_ids))

    def spawn(self, vnum: str, room_id: int, zone: str | None = None) -> NPC | None:
        loc = self.world.get_location(room_id)
        if loc is None or not self.rules.can_spawn(len(loc.npc_ids)):
            return None
        npc = self.factory.create(vnum, room_id)
        if zone is not None:
            npc.zone = zone
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

    def _route_depth_for(self, npc: NPC) -> int:
        if npc.vnum in {"astergard_guard", "watch_sergeant", "podgrodzie_straznik_miejski", "haldun_wartownik", "dungrim_guard", "dungrim_patrol_guard", "dungrim_sergeant", "straznica_wartownik", "straznica_zwiadowca", "straznica_dowodca", "trakty_straznik", "puszcza_jelen", "puszcza_dzik", "puszcza_wilk", "puszcza_pajak", "puszcza_pajak_lesny", "puszcza_pajak_duzy", "puszcza_wilk_stary", "puszcza_wataha_wilkow", "puszcza_niedzwiedz", "puszcza_niedzwiedzica", "puszcza_bandyta", "puszcza_bandyta_lucznik", "puszcza_bandyta_zwiadowca", "puszcza_lowca", "puszcza_lowczy", "puszcza_bandycki_naczelnik", "puszcza_niedzwiedzi_olbrzym", "puszcza_troll", "bagna_zaba"}:
            return 3
        if npc.vnum in {"podgrodzie_woznica", "podgrodzie_pielgrzym", "haldun_solt", "dungrim_commander", "dungrim_lieutenant", "straznica_przewodnik", "straznica_karawanowy", "straznica_mysliwy", "straznica_woznica", "straznica_podrozny", "straznica_pielgrzym", "trakty_przewodnik", "trakty_karawaniarz", "trakty_kurier", "trakty_woznica", "trakty_podrozny", "trakty_pielgrzym", "trakty_mysliwy", "trakty_drwal", "trakty_handlarz", "puszcza_mysliwy", "puszcza_zielarz", "puszcza_pustelnik", "puszcza_drwal", "puszcza_wilk", "puszcza_pajak", "puszcza_pajak_lesny", "puszcza_pajak_duzy", "puszcza_wilk_stary", "puszcza_wataha_wilkow", "puszcza_niedzwiedz", "puszcza_niedzwiedzica", "puszcza_bandyta", "puszcza_bandyta_lucznik", "puszcza_bandyta_zwiadowca", "puszcza_lowca", "puszcza_lowczy", "puszcza_bandycki_naczelnik", "puszcza_niedzwiedzi_olbrzym", "puszcza_troll", "bagna_zielarz", "bagna_pustelnik", "bagna_mysliwy"}:
            return 3
        if npc.vnum in {"innkeeper", "podgrodzie_karczmarz", "podgrodzie_karczmarka", "merchant", "customs_clerk", "fishmonger", "dockhand", "podgrodzie_handlarz", "podgrodzie_przekupka", "haldun_merchant", "haldun_wellkeeper", "haldun_blacksmith", "haldun_miller", "haldun_farmerka", "dungrim_quartermaster", "dungrim_storekeeper", "dungrim_armorer", "dungrim_military_blacksmith", "dungrim_stablemaster", "dungrim_cook", "puszcza_zielarz", "bagna_zielarz"}:
            return 2
        if npc.vnum in {"blacksmith", "carpenter", "tanner", "bowyer", "armorer", "woodcutter", "podgrodzie_kowal", "podgrodzie_pomocnik_kowala", "fisherman", "podgrodzie_rybak", "podgrodzie_piekarz", "puszcza_drwal", "puszcza_pies_dziki", "puszcza_szczur", "puszcza_kruk", "puszcza_lis", "puszcza_wilk_mlody"}:
            return 2
        if npc.vnum in {"child", "urchin", "podgrodzie_dziecko", "beggar", "vagrant", "podgrodzie_zebrak", "traveler", "podgrodzie_pielgrzym", "haldun_farmerka", "puszcza_pustelnik", "bagna_pustelnik", "trakty_zebrak"}:
            return 2
        if npc.vnum in {"farmer", "woodcutter", "miller", "priest_aide", "podgrodzie_chlop", "podgrodzie_chlopka", "haldun_farmer", "haldun_pasterz", "puszcza_jelen", "puszcza_dzik", "bagna_zaba"}:
            return 3
        return 1

    def _routine_for(self, npc: NPC) -> DailyRoutine:
        return DailyRoutine(activity_by_phase=dict(npc.daily_schedule), route_depth=self._route_depth_for(npc))

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
        weather_by_zone: dict[str, str] | None = None,
    ) -> list[NPCActionEvent]:
        random_source: RandomSource = rng or random
        events: list[NPCActionEvent] = []
        players = players or []
        phase = self._day_phase(hour) if hour is not None else None
        zone_weather = weather_by_zone or {}
        for npc in list(self.npcs.values()):
            if not npc.character.is_alive:
                continue
            if phase is not None:
                daily_event = self._apply_daily_routine(npc, phase)
                if daily_event is not None:
                    events.append(daily_event)
            if npc.ai_state == "PATROL":
                event = self._patrol_tick(npc, random_source, zone_weather)
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

    def _patrol_tick(self, npc: NPC, rng: RandomSource, weather_by_zone: dict[str, str] | None = None) -> NPCActionEvent | None:
        patrol_chance = self.rules.patrol_move_chance
        weather = weather_by_zone.get(npc.zone) if weather_by_zone is not None else None
        if weather in {"mgla", "sniezyca"}:
            patrol_chance *= 0.4
        elif weather == "deszcz":
            patrol_chance *= 0.7
        if rng.random() > patrol_chance:
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

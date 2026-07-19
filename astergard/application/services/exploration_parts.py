from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from astergard.application.use_case_contexts import ExplorationContext
from astergard.characters.models import Character
from astergard.commands.helpers import find_item, find_npc_in_manager
from astergard.commands.polish import normalize_phrase, split_relation, tokens_match
from astergard.engine.events import DomainEventType
from astergard.items.models import Item
from astergard.narrative import infer_exit_kind, join_prose, polish_direction
from astergard.rules.movement import MovementRules, SearchRules

DIRECTIONS: set[str] = {
    "polnoc",
    "poludnie",
    "wschod",
    "zachod",
    "gora",
    "dol",
    "polnocny-wschod",
    "polnocny-zachod",
    "poludniowy-wschod",
    "poludniowy-zachod",
}

MOVE_ALIAS_DIRECTIONS: dict[str, str] = {"wejdz": "gora", "zejdz": "dol"}


@dataclass(slots=True)
class ExplorationTargetResolver:
    def resolve(self, ctx: ExplorationContext, location, phrase: str, index: int) -> str | None:
        direction_arg = normalize_phrase(phrase, drop_stopwords=True)
        ex = location.exits.get(direction_arg)
        if ex:
            target = ctx.world.get_location(ex.target_room)
            if target is None:
                return "W tę stronę prowadzi tylko ciemność."
            target_name = target.name.lower()
            for prefix in ("brama ", "drzwi ", "schody ", "tunel ", "most "):
                if target_name.startswith(prefix):
                    target_name = target_name.removeprefix(prefix)
                    break
            exit_kind = ex.kind if getattr(ex, "kind", "") else infer_exit_kind(location.zone, direction_arg, location.name)
            if exit_kind == "drzwi":
                return f"Ku {polish_direction(direction_arg)} otwarte drzwi prowadzą do {target_name}."
            if exit_kind == "brama":
                return f"Ku {polish_direction(direction_arg)} brama prowadzi do {target_name}."
            if exit_kind == "schody":
                return f"Ku {polish_direction(direction_arg)} schody prowadzą do {target_name}."
            if exit_kind == "tunel":
                return f"Ku {polish_direction(direction_arg)} tunel prowadzi do {target_name}."
            return f"Ku {polish_direction(direction_arg)} widać przejście do {target_name}."
        container_view = self.inspect_container(ctx.character, location, phrase, index)
        if container_view is not None:
            return container_view
        inspectable = self.inspectable(location, phrase)
        if inspectable is not None:
            return inspectable
        npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, phrase)
        if npc:
            return npc.long_desc
        item = find_item(location.items, phrase, index)
        if item:
            return item.description
        return None

    def inspectable(self, location, phrase: str) -> str | None:
        normalized = normalize_phrase(phrase, drop_stopwords=True)
        for aliases, description in location.inspectables.items():
            if tokens_match(normalized, aliases) or tokens_match(phrase, aliases):
                return description
        return None

    def inspect_container(self, character: Character, location, phrase: str, index: int) -> str | None:
        item_name, container_name = split_relation(phrase, {"w", "we"})
        if not container_name:
            container_name = phrase
            item_name = None
        container = self._find_item_tree(character.inventory, container_name)
        if container is None and location is not None:
            container = self._find_item_tree(location.items, container_name)
        if container is None:
            return None
        if not container.is_container:
            return "To nie jest pojemnik."
        if item_name:
            item = find_item(container.contains, item_name, index)
            if item is None:
                return f"Nie ma tego w {container.name}."
            return item.description or item.display_name()
        if not container.contains:
            return f"{container.name} jest pusty."
        return f"W {container.name} widzisz {join_prose([item.display_name() for item in container.contains])}."

    def _find_item_tree(self, roots: list[Item], name: str) -> Item | None:
        for root in roots:
            if tokens_match(name, f"{root.name} {root.vnum}"):
                return root
            child = self._find_item_tree(root.contains, name)
            if child is not None:
                return child
        return None


@dataclass(slots=True)
class ExplorationActionService:
    movement_rules: MovementRules
    search_rules: SearchRules
    target_resolver: ExplorationTargetResolver
    def move_from_command(
        self,
        ctx: ExplorationContext,
        char: Character,
        current_command: str | None,
        arg: str | None,
        look_fn: Callable[[ExplorationContext, str | None, int], str],
    ) -> str:
        direction = current_command or ""
        if direction in MOVE_ALIAS_DIRECTIONS:
            direction = MOVE_ALIAS_DIRECTIONS[direction]
        if direction not in DIRECTIONS and arg in DIRECTIONS:
            direction = arg
        if direction in {"wroc", "dalej", "do srodka", "na zewnatrz"}:
            loc = ctx.world.get_location(char.room_id)
            if loc is not None and len(loc.exits) == 1:
                direction = next(iter(loc.exits))
        if direction not in DIRECTIONS:
            return "Nie rozpoznajesz takiego kierunku."
        return self.move_direct(ctx, char, direction, look_fn)

    def move_direct(
        self,
        ctx: ExplorationContext,
        char: Character,
        direction: str,
        look_fn: Callable[[ExplorationContext, str | None, int], str],
    ) -> str:
        loc = ctx.world.get_location(char.room_id)
        if not loc or direction not in loc.exits:
            return "<red>Nie możesz pójść w tę stronę.</red>"
        if self.movement_rules.movement_blocked(char.wounds.get("prawa_noga", 0), char.wounds.get("lewa_noga", 0)):
            return "<red>Twoje nogi odmawiają posłuszeństwa. Nie zrobisz ani kroku.</red>"
        ex = loc.exits[direction]
        if ex.is_locked:
            return "Przejście pozostaje zamknięte i nie ustąpi bez właściwego klucza."
        cost = self.movement_rules.move_cost(char.wounds.get("prawa_noga", 0), char.wounds.get("lewa_noga", 0))
        old_room_id = char.room_id
        char.stats.kondycja = max(0, char.stats.kondycja - cost)
        char.room_id = ex.target_room
        ctx.location_changes.record(char)
        char.visit_current_room()
        ctx.event_bus.emit(
            DomainEventType.CHARACTER_MOVED,
            username=char.username,
            from_room_id=old_room_id,
            to_room_id=char.room_id,
            direction=direction,
            stamina_cost=cost,
        )
        arrival = look_fn(ctx, None, 1)
        return f"Kierujesz się na {polish_direction(direction)}.\n\n{arrival}"

    def search(self, ctx: ExplorationContext, arg: str | None = None, index: int = 1) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "Nie ma tu miejsca, w którym można by szukać."
        if arg:
            container_view = self.target_resolver.inspect_container(ctx.character, loc, arg, index)
            if container_view is not None:
                return container_view
        stamina_cost = self.search_rules.stamina_cost
        if ctx.character.stats.kondycja < stamina_cost:
            return "Brakuje ci sił na dłuższe szukanie."
        ctx.character.stats.kondycja -= stamina_cost
        from random import randint

        score = self.search_rules.score(randint(1, self.search_rules.perception_roll_sides), ctx.character.stats.percepcja, ctx.character.skills.values["obserwacja"]["level"])
        for hidden in list(loc.hidden_elements):
            difficulty = cast(int | str, hidden["difficulty"])
            if score >= int(difficulty):
                item = hidden["data"]
                if not isinstance(item, Item):
                    continue
                loc.items.append(item)
                loc.hidden_elements.remove(hidden)
                ctx.event_bus.emit("world.hidden_element_discovered", username=ctx.character.username, room_id=loc.id, element=item.vnum or item.name)
                return f"<green>Odkrywasz: {item.name}.</green>"
        return "Nie znajdujesz niczego nowego."

    def sense(
        self,
        ctx: ExplorationContext,
        arg: str | None,
        index: int,
        look_fn: Callable[[ExplorationContext, str | None, int], str],
    ) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "<red>Wokół ciebie nie ma świata, tylko pustka.</red>"
        command = ctx.current_command or "zbadaj"
        if arg:
            look = look_fn(ctx, arg, index)
            if look != "Nic ciekawego tam nie widzisz.":
                return look
        if command == "nasluchuj":
            ambient = ctx.world.pop_ambient_message(loc.zone)
            if ambient:
                return ambient
            return "Słyszysz szum wiatru, cichy ruch i pojedynczy odgłos z oddali."
        if command == "powachaj":
            return self._smell_room(loc.zone)
        if command == "dotknij":
            return self._touch_room(loc.inspectables)
        if command in {"usiadz", "odpocznij"}:
            return "Przysiadasz na chwilę i zbierasz oddech. Świat nie zwalnia, ale ty na moment możesz."
        if command == "rozejrzyj":
            return look_fn(ctx, None, index)
        return look_fn(ctx, None, index)

    def _smell_room(self, zone: str) -> str:
        if zone == "Gory_Mekhara":
            return "Czujesz zimny kamień, mokry pył i metaliczną nutę z głębi gór."
        if zone == "Bagna_Hookri":
            return "W powietrzu unosi się torf, stęchła woda i zapach roślin gnijących bez słońca."
        if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            return "Pachnie żywicą, mokrą korą i liśćmi, które dawno przestały być świeże."
        if zone in {"Centrum_Twierdza", "Podgrodzie"}:
            return "Czujesz dym z palenisk, skórę, mokry bruk i odrobinę pieczonego chleba."
        return "Czujesz wilgoć, kurz i zapach osiadający na murach, deskach i ubraniu."

    def _touch_room(self, inspectables) -> str:
        for aliases in inspectables:
            first_word = aliases.split()[0]
            if "kam" in first_word or "głaz" in first_word or "glaz" in first_word:
                return "Kamień jest zimny i szorstki, z chropowatą krawędzią wyczuwalną pod palcami."
            if "drew" in first_word or "drzew" in first_word or "kora" in first_word:
                return "Kora jest sucha na wierzchu, ale pod spodem trzyma wilgoć i żywą tkankę drzewa."
            if "woda" in first_word or "studnia" in first_word or "cembrowin" in first_word:
                return "Wilgoć osiada na palcach niemal natychmiast."
        return "Dotykasz powierzchni wokół siebie. Jest chłodna, nierówna i naznaczona czasem."

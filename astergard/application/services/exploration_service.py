from __future__ import annotations

import random

from astergard.application.use_case_contexts import ExplorationContext
from astergard.characters.models import Character
from astergard.commands.helpers import find_item, find_npc_in_manager
from astergard.commands.polish import normalize_phrase, split_relation, tokens_match
from astergard.items.models import Item
from typing import cast
from astergard.engine.events import DomainEventType
from astergard.rules.movement import MovementRules, SearchRules, default_movement_rules, default_search_rules

DIRECTIONS: set[str] = {
    "polnoc", "poludnie", "wschod", "zachod", "gora", "dol",
    "polnocny-wschod", "polnocny-zachod", "poludniowy-wschod", "poludniowy-zachod",
}

MOVE_ALIAS_DIRECTIONS: dict[str, str] = {
    "wejdz": "gora",
    "zejdz": "dol",
}


class ExplorationService:
    """Application service for location rendering, movement and searching."""

    def __init__(
        self,
        movement_rules: MovementRules | None = None,
        search_rules: SearchRules | None = None,
    ) -> None:
        self.movement_rules = movement_rules or default_movement_rules()
        self.search_rules = search_rules or default_search_rules()

    def look(self, ctx: ExplorationContext, arg: str | None, index: int) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "<red>Nie ma tu świata.</red>"
        if arg:
            direction_arg = normalize_phrase(arg, drop_stopwords=True)
            ex = loc.exits.get(direction_arg)
            if ex:
                target = ctx.world.get_location(ex.target_room)
                return f"Spoglądając na {direction_arg}, widzisz: {target.name if target else 'ciemność'}."
            container_view = self._look_inside_container(ctx.character, loc, arg, index)
            if container_view is not None:
                return container_view
            inspectable = self._look_at_inspectable(loc, arg)
            if inspectable is not None:
                return inspectable
            npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, arg)
            if npc:
                return npc.long_desc
            item = find_item(loc.items, arg, index)
            if item:
                return item.description
            return "Nic ciekawego tam nie widzisz."
        ambient = self._render_ambient(loc, ctx)
        exits = ", ".join(loc.exits) if loc.exits else "brak oczywistego wyjścia"
        npc_lines = [npc.scene_line() for npc in ctx.npcs.by_room(loc.id)]
        item_lines = [item.display_name() for item in loc.items]
        other_lines = [
            f"{player.username}: {player.equipment_summary()}"
            for player in ctx.players_in_room(loc.id)
            if player is not ctx.character
        ]
        body: list[str] = [
            f"<gold>[ {loc.name} ({loc.zone}) ]</gold>",
            f"<grey>{loc.description}</grey>",
        ]
        if ambient:
            body.append(ambient)
        body.append(f"<light_blue>Drogi stąd: {exits}.</light_blue>")
        if item_lines:
            body.append("Na ziemi czekają: " + ", ".join(item_lines) + ".")
        if npc_lines:
            body.append("W pobliżu kręcą się: " + "; ".join(npc_lines) + ".")
        if other_lines:
            body.append("Przy tobie są jeszcze: " + "; ".join(other_lines) + ".")
        return (
            "\n".join(body).strip()
        )

    def _look_at_inspectable(self, location, phrase: str) -> str | None:
        normalized = normalize_phrase(phrase, drop_stopwords=True)
        for aliases, description in location.inspectables.items():
            if tokens_match(normalized, aliases) or tokens_match(phrase, aliases):
                return description
        return None

    def _render_ambient(self, location, ctx: ExplorationContext) -> str:
        ambient = ctx.world.pop_ambient_message(location.zone)
        if ambient is not None:
            return f"<grey>{ambient}</grey>"
        return ""

    def _look_inside_container(self, character: Character, location, phrase: str, index: int) -> str | None:
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
        return f"W {container.name} widzisz: " + ", ".join(item.display_name() for item in container.contains) + "."

    def _find_item_tree(self, roots: list[Item], name: str) -> Item | None:
        for root in roots:
            if tokens_match(name, f"{root.name} {root.vnum}"):
                return root
            child = self._find_item_tree(root.contains, name)
            if child is not None:
                return child
        return None

    def move_from_command(self, ctx: ExplorationContext, arg: str | None) -> str:
        direction = ctx.current_command
        if direction in MOVE_ALIAS_DIRECTIONS:
            direction = MOVE_ALIAS_DIRECTIONS[direction]
        if direction not in DIRECTIONS and arg in DIRECTIONS:
            direction = arg
        if direction in {"wroc", "dalej", "do srodka", "na zewnatrz"}:
            loc = ctx.world.get_location(ctx.character.room_id)
            if loc is not None and len(loc.exits) == 1:
                direction = next(iter(loc.exits))
        if direction not in DIRECTIONS:
            return "Nie znasz takiego kierunku."
        return self.move_direct(ctx, ctx.character, direction)

    def move_direct(self, ctx: ExplorationContext, char: Character, direction: str) -> str:
        loc = ctx.world.get_location(char.room_id)
        if not loc or direction not in loc.exits:
            return "<red>Nie możesz pójść w tym kierunku.</red>"
        if self.movement_rules.movement_blocked(char.wounds.get("prawa_noga", 0), char.wounds.get("lewa_noga", 0)):
            return "<red>Twoje zgruchotane nogi odmówiły posłuszeństwa. Nie zrobisz ani kroku.</red>"
        ex = loc.exits[direction]
        if ex.is_locked:
            return "Przejście jest zamknięte na klucz i nie ustąpi bez odpowiedniego klucza."
        cost = self.movement_rules.move_cost(char.wounds.get("prawa_noga", 0), char.wounds.get("lewa_noga", 0))
        old_room_id = char.room_id
        char.stats.kondycja = max(0, char.stats.kondycja - cost)
        char.room_id = ex.target_room
        char.visit_current_room()
        ctx.event_bus.emit(DomainEventType.CHARACTER_MOVED, username=char.username, from_room_id=old_room_id, to_room_id=char.room_id, direction=direction, stamina_cost=cost)
        return f"Wychodzisz na {direction}."

    def search(self, ctx: ExplorationContext, arg: str | None = None, index: int = 1) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "Nie ma gdzie szukać."
        if arg:
            container_view = self._look_inside_container(ctx.character, loc, arg, index)
            if container_view is not None:
                return container_view
        if ctx.character.stats.kondycja < 15:
            return "Brakuje ci kondycji."
        ctx.character.stats.kondycja -= 15
        score = random.randint(1, 10) + ctx.character.stats.percepcja + ctx.character.skills.values["obserwacja"]["level"] // 10
        for hidden in list(loc.hidden_elements):
            difficulty = cast(int | str, hidden["difficulty"])
            if score >= int(difficulty):
                item = hidden["data"]
                if not isinstance(item, Item):
                    continue
                loc.items.append(item)
                loc.hidden_elements.remove(hidden)
                ctx.event_bus.emit("world.hidden_element_discovered", username=ctx.character.username, room_id=loc.id, element=item.vnum or item.name)
                return f"<green>Odkrywasz: {item.name}!</green>"
        return "Nie znajdujesz niczego nowego."

    def sense(self, ctx: ExplorationContext, arg: str | None, index: int) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "<red>Nie ma tu świata.</red>"
        command = ctx.current_command or "zbadaj"
        if arg:
            look = self.look(ctx, arg, index)
            if look != "Nic ciekawego tam nie widzisz.":
                return look
        if command == "nasluchuj":
            ambient = ctx.world.pop_ambient_message(loc.zone)
            if ambient:
                return ambient
            return "Słyszysz szum wiatru, cichy ruch i pojedynczy odgłos z oddali."
        if command == "powachaj":
            return self._smell_room(loc)
        if command == "dotknij":
            return self._touch_room(loc)
        if command in {"usiadz", "odpocznij"}:
            return "Przysiadasz na chwilę i zbierasz oddech. Świat nie zwalnia, ale ty na moment możesz."
        if command == "rozejrzyj":
            return self.look(ctx, None, index)
        return self.look(ctx, None, index)

    def _smell_room(self, location) -> str:
        zone = location.zone
        if zone == "Gory_Mekhara":
            return "Czujesz zimny kamień, mokry pył i metaliczną nutę z głębi gór."
        if zone == "Bagna_Hookri":
            return "W powietrzu unosi się torf, stęchła woda i zapach roślin gnijących bez słońca."
        if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            return "Pachnie żywicą, mokrą korą i liśćmi, które dawno przestały być świeże."
        if zone in {"Centrum_Twierdza", "Podgrodzie"}:
            return "Czujesz dym z palenisk, skórę, mokry bruk i odrobinę pieczonego chleba."
        return "W powietrzu miesza się wilgoć, kurz i coś, co mówi ci, że to miejsce ma swój własny zapach."

    def _touch_room(self, location) -> str:
        for aliases in location.inspectables:
            first_word = aliases.split()[0]
            if "kam" in first_word or "głaz" in first_word or "glaz" in first_word:
                return "Kamień jest zimny i szorstki, z chropowatą krawędzią wyczuwalną pod palcami."
            if "drew" in first_word or "drzew" in first_word or "kora" in first_word:
                return "Kora jest sucha na wierzchu, ale pod spodem trzyma wilgoć i żywą tkankę drzewa."
            if "woda" in first_word or "studnia" in first_word or "cembrowin" in first_word:
                return "Wilgoć osiada na palcach niemal natychmiast."
        return "Dotykasz powierzchni wokół siebie. Jest chłodna, nierówna i naznaczona czasem."

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


class ExplorationService:
    """Application service for location rendering, movement and searching."""

    def __init__(self, movement_rules: MovementRules | None = None, search_rules: SearchRules | None = None) -> None:
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
        exits = ", ".join(loc.exits)
        npcs = "\n".join(npc.scene_line() for npc in ctx.npcs.by_room(loc.id))
        items = "\n".join(f"Leży tu: {item.display_name()}." for item in loc.items)
        inspectables = self._render_inspectables(loc)
        others = "\n".join(
            f"<yellow>{player.username} stoi tutaj.</yellow>"
            for player in ctx.players_in_room(loc.id)
            if player is not ctx.character
        )
        return (
            f"<gold>[ {loc.name} ({loc.zone}) ]</gold>\n"
            f"<grey>{loc.description}</grey>\n"
            f"<light_blue>[ Widoczne wyjścia: {exits} ]</light_blue>\n"
            f"{inspectables}\n{items}\n{npcs}\n{others}"
        ).strip()


    def _look_at_inspectable(self, location, phrase: str) -> str | None:
        normalized = normalize_phrase(phrase, drop_stopwords=True)
        for aliases, description in location.inspectables.items():
            if tokens_match(normalized, aliases) or tokens_match(phrase, aliases):
                return description
        return None

    def _render_inspectables(self, location) -> str:
        if not location.inspectables:
            return ""
        visible: list[str] = []
        for aliases in location.inspectables:
            first_alias = aliases.split()[0]
            if first_alias not in visible:
                visible.append(first_alias)
        return "Możesz obejrzeć: " + ", ".join(visible) + "."

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
        if direction not in DIRECTIONS and arg in DIRECTIONS:
            direction = arg
        if direction not in DIRECTIONS:
            return "Nie znasz takiego kierunku."
        return self.move_direct(ctx, ctx.character, direction)

    def move_direct(self, ctx: ExplorationContext, char: Character, direction: str) -> str:
        loc = ctx.world.get_location(char.room_id)
        if not loc or direction not in loc.exits:
            return "<red>Nie możesz pójść w tym kierunku.</red>"
        if self.movement_rules.movement_blocked(char.wounds.get("prawa_noga", 0), char.wounds.get("lewa_noga", 0)):
            return "<red>Twoje zgruchotane nogi odmówiły posłuszeństwa! Nie możesz się ruszyć!</red>"
        ex = loc.exits[direction]
        if ex.is_locked:
            return "Drzwi są zamknięte na klucz."
        cost = self.movement_rules.move_cost(char.wounds.get("prawa_noga", 0), char.wounds.get("lewa_noga", 0))
        old_room_id = char.room_id
        char.stats.kondycja = max(0, char.stats.kondycja - cost)
        char.room_id = ex.target_room
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
        score = random.randint(1, 10) + ctx.character.stats.percepcja + ctx.character.skills.values["spostrzegawczosc"]["level"] // 10
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

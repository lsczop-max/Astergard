from __future__ import annotations

from dataclasses import dataclass

from astergard.characters.models import Character
from astergard.commands.helpers import find_item
from astergard.commands.polish import is_all_phrase, split_relation, tokens_match
from astergard.items.models import EQUIPMENT_SLOTS, equipment_slot_label
from astergard.engine.events import DomainEventType
from astergard.items.models import Item
from astergard.npcs.manager import NPCManager
from astergard.quests.manager import QuestManager, QUESTS
from astergard.world.models import Location


@dataclass(slots=True)
class InventoryView:
    equipment: str
    backpack: str
    current_weight: float
    max_weight: float

    def render(self) -> str:
        return (
            f"Wyposażenie przy tobie: {self.equipment}\n"
            f"W plecaku niesiesz: {self.backpack}\n"
            f"Obciążenie: {self._load_description()}"
        )

    def _load_description(self) -> str:
        if self.max_weight <= 0:
            return "nie do określenia"
        ratio = self.current_weight / self.max_weight
        if ratio < 0.25:
            return "niewielkie"
        if ratio < 0.5:
            return "umiarkowane"
        if ratio < 0.75:
            return "duże"
        if ratio < 1.0:
            return "bardzo duże"
        return "przekroczone"


@dataclass(slots=True)
class ContainerRef:
    item: Item
    parent: list[Item]
    scope: str


class InventoryService:
    """Application service for inventory, equipment and container use cases."""

    def render_inventory(self, character: Character) -> str:
        inventory = ", ".join(self._render_item_with_contents(item) for item in character.inventory) or "nic"
        equipment = self._render_equipment(character)
        return InventoryView(
            equipment=equipment,
            backpack=inventory,
            current_weight=character.total_weight(),
            max_weight=character.stats.get_weight_limit(),
        ).render()

    def get_item(self, character: Character, location: Location | None, name: str | None, index: int, event_bus=None) -> str:
        if not name:
            return "Co chcesz wziąć?"
        item_name, container_name = split_relation(name, {"z", "ze"})
        if container_name:
            return self.take_from_container(character, name, index, event_bus, location)
        if location is None:
            return "Nie ma tu takiego przedmiotu."
        if is_all_phrase(name):
            return self.get_all_items(character, location, event_bus)
        item = find_item(location.items, item_name or name, index)
        if item is None:
            return "Nie ma tu takiego przedmiotu."
        if character.total_weight() + item.total_weight() > character.stats.get_weight_limit():
            return "<red>To jest dla ciebie za ciężkie.</red>"
        location.items.remove(item)
        character.inventory.append(item)
        if event_bus is not None:
            event_bus.emit(DomainEventType.ITEM_PICKED_UP, username=character.username, character=character, room_id=getattr(location, "id", None), item=item.vnum or item.name)
        return f"Podnosisz {item.name}."

    def get_all_items(self, character: Character, location: Location, event_bus=None) -> str:
        if not location.items:
            return "Nie ma tu nic do wzięcia."
        taken: list[Item] = []
        skipped: list[Item] = []
        for item in list(location.items):
            if character.total_weight() + item.total_weight() <= character.stats.get_weight_limit():
                location.items.remove(item)
                character.inventory.append(item)
                taken.append(item)
                if event_bus is not None:
                    event_bus.emit(DomainEventType.ITEM_PICKED_UP, username=character.username, character=character, room_id=getattr(location, "id", None), item=item.vnum or item.name)
            else:
                skipped.append(item)
        if not taken:
            return "Nie uniesiesz żadnego z tych przedmiotów."
        text = "Podnosisz: " + ", ".join(item.name for item in taken) + "."
        if skipped:
            text += "\nNie unosisz: " + ", ".join(item.name for item in skipped) + "."
        return text

    def drop_item(self, character: Character, location: Location | None, name: str | None, index: int, event_bus=None) -> str:
        if not name:
            return "Co chcesz upuścić?"
        if is_all_phrase(name):
            return self.drop_all_items(character, location, event_bus)
        item = find_item(character.inventory, name, index)
        if item is None or location is None:
            return "Nie masz takiego przedmiotu."
        character.inventory.remove(item)
        location.items.append(item)
        if event_bus is not None:
            event_bus.emit(DomainEventType.ITEM_DROPPED, username=character.username, room_id=getattr(location, "id", None), item=item.vnum or item.name)
        return f"Upuszczasz {item.name}."

    def drop_all_items(self, character: Character, location: Location | None, event_bus=None) -> str:
        if location is None:
            return "Nie możesz tego tu zrobić."
        if not character.inventory:
            return "Nie masz nic do upuszczenia."
        dropped = list(character.inventory)
        character.inventory.clear()
        location.items.extend(dropped)
        if event_bus is not None:
            for item in dropped:
                event_bus.emit(DomainEventType.ITEM_DROPPED, username=character.username, room_id=getattr(location, "id", None), item=item.vnum or item.name)
        return "Upuszczasz: " + ", ".join(item.name for item in dropped) + "."

    def put_item(self, character: Character, phrase: str | None, index: int, event_bus=None, location: Location | None = None) -> str:
        item_name, container_name = split_relation(phrase, {"do", "w", "we"})
        if not item_name or not container_name:
            return "Spróbuj: włóż <przedmiot> do <pojemnik>."
        item = find_item(character.inventory, item_name, index)
        if item is None:
            return "Nie masz takiego przedmiotu."
        container_ref = self.find_container_ref(character, container_name, location=location)
        if container_ref is None:
            return "Nie widzisz takiego pojemnika. Szukaj w plecaku, sakwie, worku albo na ziemi."
        return self._move_inventory_item_to_container(character, item, container_ref.item, event_bus)

    def transfer_item(self, character: Character, phrase: str | None, index: int, event_bus=None, location: Location | None = None) -> str:
        if not phrase:
            return "Spróbuj: przełóż <przedmiot> z <pojemnika> do <pojemnika>."
        item_and_source, target_name = split_relation(phrase, {"do", "w", "we"})
        if not item_and_source or not target_name:
            return "Spróbuj: przełóż <przedmiot> z <pojemnika> do <pojemnika>."
        item_name, source_name = split_relation(item_and_source, {"z", "ze"})
        if not item_name or not source_name:
            return "Spróbuj: przełóż <przedmiot> z <pojemnika> do <pojemnika>."
        source_ref = self.find_container_ref(character, source_name, location=location)
        target_ref = self.find_container_ref(character, target_name, location=location)
        if source_ref is None:
            return "Nie widzisz pojemnika źródłowego."
        if target_ref is None:
            return "Nie widzisz pojemnika docelowego."
        if not source_ref.item.is_container or not target_ref.item.is_container:
            return "To nie jest pojemnik."
        if source_ref.item is target_ref.item:
            return "Nie możesz przełożyć przedmiotu do tego samego pojemnika."
        item = find_item(source_ref.item.contains, item_name, index)
        if item is None:
            return f"Nie ma tego w {source_ref.item.name}."
        if item is target_ref.item or self._contains_item(item, target_ref.item):
            return "Nie możesz włożyć pojemnika w samego siebie."
        current = sum(contained.total_weight() for contained in target_ref.item.contains)
        if current + item.total_weight() > target_ref.item.capacity:
            return "To się tam nie zmieści."
        source_ref.item.contains.remove(item)
        target_ref.item.contains.append(item)
        if event_bus is not None:
            event_bus.emit("item.transferred_between_containers", username=character.username, item=item.vnum or item.name, source=source_ref.item.vnum or source_ref.item.name, target=target_ref.item.vnum or target_ref.item.name)
        return f"Przekładasz {item.name} z {source_ref.item.name} do {target_ref.item.name}."

    def give_item(self, character: Character, npcs: NPCManager, quests: QuestManager, phrase: str | None, index: int, event_bus=None) -> str:
        item_name, npc_name = split_relation(phrase, {"npc", "recipient", "komu", "dla"})
        if not item_name or not npc_name:
            return "Spróbuj: daj <przedmiot> <osobie>."
        item = find_item(character.inventory, item_name, index)
        if item is None:
            return "Nie masz takiego przedmiotu."
        npc = next((candidate for candidate in npcs.by_room(character.room_id) if tokens_match(npc_name, f"{candidate.name} {candidate.vnum}")), None)
        if npc is None:
            return "Nie ma tu takiej osoby."
        character.inventory.remove(item)
        npc.character.inventory.append(item)
        if item.vnum == "wolf_pelt" and "wolf_pelt" in character.active_quests:
            character.active_quests["wolf_pelt"]["current"] = 1
        for quest in QUESTS.values():
            if quest.id not in character.active_quests:
                continue
            if not any(
                obj["type"] == "give"
                and (
                    tokens_match(item.vnum or item.name, obj["target"])
                    if isinstance(obj["target"], str)
                    else any(tokens_match(item.vnum or item.name, target) for target in obj["target"])
                )
                for obj in quest.objectives
            ):
                continue
            quests.progress(character, "give", item.vnum or item.name)
            if event_bus is not None:
                event_bus.emit("item.given_to_npc", username=character.username, item=item.vnum or item.name, npc=npc.vnum)
            if quest.auto_complete_on_delivery and quest.completion_npc == npc.vnum and quests.is_ready(character, quest.id):
                completion = quests.complete_if_ready(character, quest.id, event_bus)
                if event_bus is not None:
                    event_bus.emit("quest.progress_updated", username=character.username, quest_id=quest.id, target=item.vnum or item.name, npc=npc.vnum)
                return f"Dajesz {item.name} postaci {npc.name}.\n{completion}"
        return f"Dajesz {item.name} postaci {npc.name}."

    def take_from_container(self, character: Character, phrase: str | None, index: int, event_bus=None, location: Location | None = None) -> str:
        item_name, container_name = split_relation(phrase, {"z", "ze"})
        if not item_name or not container_name:
            return "Spróbuj: wyjmij <przedmiot> z <pojemnik>."
        container_ref = self.find_container_ref(character, container_name, location=location)
        if container_ref is None:
            return "Nie widzisz takiego pojemnika. Szukaj w plecaku, sakwie, worku albo na ziemi."
        container = container_ref.item
        if not container.is_container:
            return "To nie jest pojemnik."
        if not container.contains:
            return f"{container.name} jest pusty."
        if is_all_phrase(item_name):
            return self.take_all_from_container(character, container, event_bus)
        item = find_item(container.contains, item_name, index)
        if item is None:
            return f"Nie ma tego w {container.name}."
        if character.total_weight() + item.total_weight() > character.stats.get_weight_limit():
            return "<red>To jest dla ciebie za ciężkie.</red>"
        container.contains.remove(item)
        character.inventory.append(item)
        if event_bus is not None:
            event_bus.emit("item.taken_from_container", username=character.username, item=item.vnum or item.name, container=container.vnum or container.name)
        return f"Wyjmujesz {item.name} z {container.name}."

    def take_all_from_container(self, character: Character, container: Item, event_bus=None) -> str:
        if not container.contains:
            return f"{container.name} jest pusty."
        moved: list[Item] = []
        skipped: list[Item] = []
        for item in list(container.contains):
            if character.total_weight() + item.total_weight() <= character.stats.get_weight_limit():
                container.contains.remove(item)
                character.inventory.append(item)
                moved.append(item)
                if event_bus is not None:
                    event_bus.emit("item.taken_from_container", username=character.username, item=item.vnum or item.name, container=container.vnum or container.name)
            else:
                skipped.append(item)
        if not moved:
            return "Nie uniesiesz żadnego z tych przedmiotów."
        text = "Wyjmujesz z " + container.name + ": " + ", ".join(item.name for item in moved) + "."
        if skipped:
            text += "\nNie unosisz: " + ", ".join(item.name for item in skipped) + "."
        return text

    def render_container(self, character: Character, phrase: str | None, index: int = 1, location: Location | None = None) -> str:
        item_name, container_name = split_relation(phrase, {"w", "we"})
        if not container_name:
            container_name = phrase
            item_name = None
        if not container_name:
            return "Co chcesz obejrzeć?"
        container_ref = self.find_container_ref(character, container_name, index=index, location=location)
        if container_ref is None:
            return "Nie widzisz takiego pojemnika. Szukaj w plecaku, sakwie, worku albo na ziemi."
        container = container_ref.item
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

    def search_container(self, character: Character, location: Location | None, phrase: str | None, index: int = 1) -> str:
        if not phrase:
            return "Co chcesz przeszukać?"
        return self.render_container(character, phrase, index, location)

    def wear_item(self, character: Character, name: str | None, index: int, event_bus=None) -> str:
        if not name:
            return "Co chcesz założyć?"
        item = find_item(character.inventory, name, index)
        if item is None or not item.is_wearable():
            return f"{name} nie jest częścią wyposażenia, którą możesz założyć."
        slot = item.normalized_slot()
        if slot is None:
            return f"{item.name} nie ma miejsca na ciele, które można by na siebie nałożyć."
        old = character.equipment.get(slot)
        if old is not None:
            slot_name = equipment_slot_label(slot)
            if slot_name == "amulet":
                slot_name = "amuletu"
            return f"Na miejscu {slot_name} już coś nosisz."
        character.inventory.remove(item)
        character.equipment[slot] = item
        if event_bus is not None:
            event_bus.emit(DomainEventType.ITEM_EQUIPPED, username=character.username, slot=slot, item=item.vnum or item.name)
        return f"Zakładasz {item.name}."

    def remove_item(self, character: Character, name: str | None, event_bus=None) -> str:
        if not name:
            return "Co chcesz zdjąć?"
        for slot in EQUIPMENT_SLOTS:
            item = character.equipment.get(slot)
            if item is not None and tokens_match(name, f"{item.name} {item.vnum}"):
                character.equipment[slot] = None
                character.inventory.append(item)
                if event_bus is not None:
                    event_bus.emit(DomainEventType.ITEM_UNEQUIPPED, username=character.username, slot=slot, item=item.vnum or item.name)
                return f"Zdejmujesz {item.name}."
        return "Nie masz tego na sobie. Sprawdź, czy szukasz właściwej rzeczy albo właściwego miejsca."

    def consume_item(self, character: Character, name: str | None, index: int, event_bus=None) -> str:
        if not name:
            return "Czego chcesz użyć?"
        item = find_item(character.inventory, name, index)
        if item is None or not item.is_consumable:
            return f"{name} nie da się użyć w ten sposób."
        self._apply_consumable_effects(character, item)
        character.inventory.remove(item)
        if event_bus is not None:
            event_bus.emit(DomainEventType.ITEM_CONSUMED, username=character.username, item=item.vnum or item.name)
        return f"Używasz {item.name}. Czujesz się lepiej."

    def find_container(self, character: Character, name: str) -> Item | None:
        ref = self.find_container_ref(character, name)
        return ref.item if ref is not None else None

    def find_container_ref(self, character: Character, name: str, *, index: int = 1, location: Location | None = None) -> ContainerRef | None:
        matches: list[ContainerRef] = []
        self._collect_container_refs(character.inventory, name, character.inventory, "inventory", matches)
        for slot, item in character.equipment.items():
            if item is not None:
                self._collect_container_refs([item], name, character.inventory, f"equipment:{slot}", matches)
        if location is not None:
            self._collect_container_refs(location.items, name, location.items, "ground", matches)
        return matches[index - 1] if len(matches) >= index else None

    def _collect_container_refs(self, roots: list[Item], name: str, parent: list[Item], scope: str, matches: list[ContainerRef]) -> None:
        for item in roots:
            if tokens_match(name, f"{item.name} {item.vnum}"):
                matches.append(ContainerRef(item=item, parent=parent, scope=scope))
            if item.contains:
                self._collect_container_refs(item.contains, name, item.contains, scope, matches)

    def _move_inventory_item_to_container(self, character: Character, item: Item, container: Item, event_bus=None) -> str:
        if container is item or self._contains_item(item, container):
            return "Nie możesz włożyć przedmiotu do samego siebie."
        if not container.is_container:
            return "To nie jest pojemnik."
        current = sum(contained.total_weight() for contained in container.contains)
        if current + item.total_weight() > container.capacity:
            return "To się tam nie zmieści."
        character.inventory.remove(item)
        container.contains.append(item)
        if event_bus is not None:
            event_bus.emit("item.put_into_container", username=character.username, item=item.vnum or item.name, container=container.vnum or container.name)
        return f"Wkładasz {item.name} do {container.name}."

    def _find_item_tree(self, roots: list[Item], name: str) -> Item | None:
        for root in roots:
            if tokens_match(name, f"{root.name} {root.vnum}"):
                return root
            child = self._find_item_tree(root.contains, name)
            if child is not None:
                return child
        return None

    def _contains_item(self, root: Item, target: Item) -> bool:
        for child in root.contains:
            if child is target or self._contains_item(child, target):
                return True
        return False

    def _render_item_with_contents(self, item: Item) -> str:
        if item.is_container:
            if item.contains:
                inside = ", ".join(self._render_item_with_contents(child) for child in item.contains)
                return f"{item.display_name()} (w środku: {inside})"
            return f"{item.display_name()} (pusty)"
        return item.display_name()

    def _render_equipment(self, character: Character) -> str:
        worn = [item.display_name() for item in character.equipped_items().values()]
        return ", ".join(worn) if worn else "brak"

    def _apply_consumable_effects(self, character: Character, item: Item) -> None:
        stamina = int(item.effects_on_consume.get("restore_stamina", 0))
        if stamina:
            character.stats.kondycja = min(character.stats.max_kondycja, character.stats.kondycja + stamina)
        wound = item.effects_on_consume.get("heal_wound")
        if isinstance(wound, str) and character.wounds.get(wound, 0) < 4:
            character.wounds[wound] = max(0, character.wounds.get(wound, 0) - 1)

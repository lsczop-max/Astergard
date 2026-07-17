from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from astergard.characters.careers import CareerUserProfile
from astergard.items.models import EQUIPMENT_SLOTS, EquipmentSet, Item, starter_items
from astergard.rules.combat_specialization import CombatSpecializationLoadout
from astergard.rules.combat_specialization import defense_style_label, resolve_active_defense_style
from astergard.rules.skills import (
    apply_skill_use,
    apply_starting_skill_bonus,
    canonicalize_skill_values,
    export_skill_values,
    default_skill_rules,
    default_skill_values,
    resolve_skill,
)
from astergard.state import CHARACTER_STATE_MACHINE, CharacterState, parse_character_state

BODY_PARTS = ["glowa", "korpus", "prawa_reka", "lewa_reka", "prawa_noga", "lewa_noga"]


def _normalize_unique_texts(values: object) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple, set)):
        return ()
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(text)
    return tuple(normalized)


@dataclass
class CharacterStats:
    sila: int = 10
    zrecznosc: int = 10
    wytrzymalosc: int = 10
    percepcja: int = 10
    sila_woli: int = 10
    kondycja: int = 100

    @property
    def max_kondycja(self) -> int:
        return self.wytrzymalosc * 10

    def get_weight_limit(self) -> float:
        return self.sila * 5.0

    def describe_stat(self, value: int) -> str:
        if value <= 5:
            return "wątły"
        if value <= 10:
            return "przeciętny"
        if value <= 15:
            return "silny"
        return "potężny"

    def describe_kondycja(self) -> str:
        ratio = 0.0 if self.max_kondycja <= 0 else self.kondycja / self.max_kondycja
        if ratio >= 0.9:
            return "w pełni sił"
        if ratio >= 0.7:
            return "lekko zmęczony"
        if ratio >= 0.5:
            return "zmęczony"
        if ratio >= 0.25:
            return "wyczerpany"
        if self.kondycja > 0:
            return "ledwo stoi"
        return "na skraju upadku"


@dataclass
class CharacterSkills:
    values: dict[str, dict[str, int]] = field(default_factory=default_skill_values)

    def __post_init__(self) -> None:
        self.values = canonicalize_skill_values(self.values)

    def state(self, name: str) -> dict[str, int]:
        definition = resolve_skill(name)
        return self.values.setdefault(definition.key, {"level": 1, "progress": 0})

    def level(self, name: str) -> int:
        return self.state(name)["level"]

    def progress(self, name: str) -> int:
        return self.state(name)["progress"]

    def to_dict(self) -> dict[str, dict[str, int]]:
        return export_skill_values(self.values)

    def grant_starting_bonus(self, name: str, bonus: int, *, cap: int = 3) -> None:
        apply_starting_skill_bonus(self.values, name, bonus, cap=cap)

    def train(self, name: str, amount: int) -> bool:
        return apply_skill_use(self.values, name, amount, rules=default_skill_rules())


@dataclass
class Effect:
    name: str
    modifier_stat: str
    value: int
    duration_ticks: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "modifier_stat": self.modifier_stat,
            "value": self.value,
            "duration_ticks": self.duration_ticks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Effect":
        return cls(
            name=str(data["name"]),
            modifier_stat=str(data["modifier_stat"]),
            value=int(data["value"]),
            duration_ticks=int(data["duration_ticks"]),
        )


@dataclass
class Character:
    username: str
    room_id: int = 0
    visited_room_ids: set[int] = field(default_factory=set)
    name: str = ""
    gender_description: str = ""
    age: int = 0
    origin: str = ""
    childhood: str = ""
    birth_region: str = ""
    culture: str = ""
    religion: str = ""
    main_profession: str = ""
    secondary_profession: str = ""
    appearance: str = ""
    history: str = ""
    starting_reputation: int = 0
    stats: CharacterStats = field(default_factory=CharacterStats)
    skills: CharacterSkills = field(default_factory=CharacterSkills)
    inventory: list[Item] = field(default_factory=starter_items)
    equipment: EquipmentSet = field(default_factory=EquipmentSet.default)
    wounds: dict[str, int] = field(default_factory=lambda: {part: 0 for part in BODY_PARTS})
    gold: int = 25
    reputation: dict[str, int] = field(default_factory=lambda: {"MEEKHAN": 0, "SE_HARIEN": 0, "REBELS": 0})
    global_reputation: int = 0
    local_reputation: dict[str, int] = field(default_factory=dict)
    renown: int = 0
    title: str = "Wędrowiec"
    crimes: dict[str, int] = field(default_factory=lambda: {"kradzież": 0, "napaść": 0, "zabójstwo": 0})
    wanted_level: int = 0
    wanted_posts: list[str] = field(default_factory=list)
    active_effects: list[Effect] = field(default_factory=list)
    active_quests: dict[str, dict[str, int]] = field(default_factory=dict)
    completed_quests: list[str] = field(default_factory=list)
    career_id: str | None = None
    organization_id: str | None = None
    school_id: str | None = None
    organization_rank: int | None = None
    combat_identity: str | None = None
    active_defense_style: str | None = None
    combat_specializations: CombatSpecializationLoadout = field(default_factory=CombatSpecializationLoadout)
    known_techniques: tuple[str, ...] = field(default_factory=tuple)
    is_alive: bool = True
    in_combat: bool = False
    combat_style: str = "zrownowazony"
    formation: str = "front"
    battle_morale: int = 10
    combat_events: list[str] = field(default_factory=list)
    state: str = CharacterState.ALIVE.value
    admin_role: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.visited_room_ids, set):
            self.visited_room_ids = {int(room_id) for room_id in self.visited_room_ids}
        if not isinstance(self.equipment, EquipmentSet):
            self.equipment = EquipmentSet.from_dict(self.equipment)
        if not isinstance(self.combat_specializations, CombatSpecializationLoadout):
            self.combat_specializations = CombatSpecializationLoadout.from_dict(self.combat_specializations)
        self.career_id = None if self.career_id is None else (str(self.career_id).strip() or None)
        self.organization_id = None if self.organization_id is None else (str(self.organization_id).strip() or None)
        self.school_id = None if self.school_id is None else (str(self.school_id).strip() or None)
        if self.organization_rank is not None:
            text = str(self.organization_rank).strip()
            self.organization_rank = None if not text else int(text)
        self.combat_identity = None if self.combat_identity is None else (str(self.combat_identity).strip() or None)
        resolved_defense_style = resolve_active_defense_style(self.active_defense_style)
        self.active_defense_style = resolved_defense_style.value if resolved_defense_style is not None else None
        self.known_techniques = _normalize_unique_texts(self.known_techniques)
        for slot in EQUIPMENT_SLOTS:
            self.equipment.setdefault(slot, None)

    @property
    def awans(self) -> int | None:
        return self.organization_rank

    @awans.setter
    def awans(self, value: int | str | None) -> None:
        if value is None:
            self.organization_rank = None
            return
        text = str(value).strip()
        self.organization_rank = None if not text else int(text)

    def career_profile(self) -> CareerUserProfile:
        return CareerUserProfile(
            career_id=self.career_id,
            organization_id=self.organization_id,
            school_id=self.school_id,
            organization_rank=self.organization_rank,
        )

    def active_defense_style_label(self) -> str:
        return defense_style_label(self.active_defense_style)

    def add_local_reputation(self, zone: str, amount: int) -> None:
        self.local_reputation[zone] = self.local_reputation.get(zone, 0) + amount

    def add_global_reputation(self, amount: int) -> None:
        self.global_reputation += amount

    def add_renown(self, amount: int) -> None:
        if amount > 0:
            self.renown += amount

    def record_crime(self, crime: str, zone: str | None = None, detail: str | None = None) -> None:
        normalized = crime.strip().lower()
        self.crimes[normalized] = self.crimes.get(normalized, 0) + 1
        entry = normalized
        if zone:
            entry += f" @ {zone}"
        if detail:
            entry += f" - {detail}"
        self.wanted_posts.insert(0, entry)
        del self.wanted_posts[10:]

    def sync_identity(self, title: str | None = None, wanted_level: int | None = None) -> None:
        if title is not None:
            self.title = title
        if wanted_level is not None:
            self.wanted_level = wanted_level

    def visit_room(self, room_id: int | None = None) -> None:
        self.visited_room_ids.add(self.room_id if room_id is None else room_id)

    def visit_current_room(self) -> None:
        self.visit_room(self.room_id)

    def equipped_items(self) -> dict[str, Item]:
        return {slot: item for slot, item in self.equipment.items() if item is not None}

    def has_light_source(self) -> bool:
        def item_emits_light(item: Item) -> bool:
            text = f"{item.name} {item.vnum or ''}".lower()
            return any(token in text for token in ("latarnia", "pochodnia", "lampa", "swieca", "świeca", "lazik"))

        if any(item_emits_light(item) for item in self.equipped_items().values()):
            return True
        return any(item_emits_light(item) for item in self.inventory)

    def _describe_equipped_piece(self, slot: str, item: Item) -> str:
        slot_labels = {
            "glowa": "na głowie",
            "szyja": "na szyi",
            "korpus": "na korpusie",
            "plecy": "na plecach",
            "rece": "na rękach",
            "dlonie": "na dłoniach",
            "pas": "przy pasie",
            "nogi": "na nogach",
            "stopy": "na stopach",
            "bron_glowna": "w prawej dłoni",
            "bron_pomocnicza": "w lewej dłoni",
            "tarcza": "przy lewym boku",
            "pierscien_1": "na palcu",
            "pierscien_2": "na drugim palcu",
            "amulet": "na piersi",
        }
        return f"{item.display_name()} {slot_labels.get(slot, 'przy tobie')}"

    def armor_items(self) -> list[Item]:
        return [item for item in self.equipment.values() if item is not None and item.item_type in {"armor", "shield"}]

    def armor_weight(self) -> float:
        return sum(item.weight for item in self.armor_items())

    def armor_burden_penalty(self) -> int:
        armor_protection = sum(max(0, item.protection) + max(0, item.armor_value) for item in self.armor_items())
        return max(0, int(self.armor_weight() // 2) + armor_protection // 3)

    def set_equipment(self, slot: str, item: Item | None) -> None:
        self.equipment[slot] = item

    def clear_equipment(self, slot: str) -> Item | None:
        item = self.equipment.get(slot)
        self.equipment[slot] = None
        return item

    def equipment_summary(self) -> str:
        worn = self.equipped_items()
        if not worn:
            return "Nie nosisz teraz żadnego wyposażenia."
        parts: list[str] = []
        body_items = [
            self._describe_equipped_piece(slot, worn[slot])
            for slot in ("glowa", "szyja", "korpus", "plecy", "rece", "dlonie", "pas", "nogi", "stopy")
            if worn.get(slot) is not None
        ]
        parts.append("Masz na sobie: " + (", ".join(body_items) if body_items else "brak typowego odzienia") + ".")
        hand_items = [
            self._describe_equipped_piece(slot, worn[slot])
            for slot in ("bron_glowna", "bron_pomocnicza")
            if worn.get(slot) is not None
        ]
        shield = worn.get("tarcza")
        accessories = [
            self._describe_equipped_piece(slot, worn[slot])
            for slot in ("pierscien_1", "pierscien_2", "amulet")
            if worn.get(slot) is not None
        ]
        if hand_items:
            parts.append("W dłoniach masz: " + ", ".join(hand_items) + ".")
        if shield is not None:
            parts.append(f"Przy boku nosisz {shield.display_name()}.")
        if accessories:
            parts.append("Drobne dodatki to: " + ", ".join(accessories) + ".")
        return " ".join(parts)

    def sync_flags_from_state(self) -> None:
        state = parse_character_state(self.state)
        self.is_alive = state is not CharacterState.DEAD
        self.in_combat = state is CharacterState.IN_COMBAT

    def sync_state_from_flags(self) -> None:
        if not self.is_alive:
            self.state = CharacterState.DEAD.value
        elif self.in_combat:
            self.state = CharacterState.IN_COMBAT.value
        else:
            self.state = CharacterState.ALIVE.value

    def transition_state(self, target: str | CharacterState) -> None:
        self.sync_state_from_flags()
        current = parse_character_state(self.state)
        next_state = parse_character_state(target)
        self.state = CHARACTER_STATE_MACHINE.validate(current, next_state).value
        self.sync_flags_from_state()

    def enter_combat(self) -> None:
        self.transition_state(CharacterState.IN_COMBAT)

    def leave_combat(self) -> None:
        self.transition_state(CharacterState.ALIVE)

    def die(self) -> None:
        self.transition_state(CharacterState.DEAD)

    def total_weight(self) -> float:
        carried = sum(item.total_weight() for item in self.inventory)
        equipped = sum(item.total_weight() for item in self.equipment.values() if item is not None)
        coins = self.gold * 0.005
        return carried + equipped + coins

    def weapon(self) -> Item | None:
        for slot in ("bron_glowna", "bron_pomocnicza", "prawa_reka", "lewa_reka"):
            item = self.equipment.get(slot)
            if item is not None and item.item_type == "weapon" and item.durability > 0:
                return item
        return None

    def armor_for(self, body_part: str) -> Item | None:
        slots: list[str]
        if body_part == "glowa":
            slots = ["glowa", "szyja", "amulet"]
        elif body_part == "korpus":
            slots = ["korpus", "plecy", "pas"]
        elif "reka" in body_part:
            slots = ["rece", "dlonie", "bron_pomocnicza"]
        elif "noga" in body_part:
            slots = ["nogi", "stopy"]
        else:
            slots = [body_part]
        for slot in slots:
            item = self.equipment.get(slot)
            if item is not None and item.item_type in {"armor", "shield"} and item.durability > 0:
                return item
        return None

    def shield(self) -> Item | None:
        for slot in ("tarcza", "bron_pomocnicza", "lewa_reka"):
            item = self.equipment.get(slot)
            if item is not None and item.item_type == "shield" and item.durability > 0:
                return item
        return None

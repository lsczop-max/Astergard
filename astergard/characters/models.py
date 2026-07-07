from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from astergard.items.models import Item, starter_items
from astergard.rules.skills import default_skill_rules
from astergard.state import CHARACTER_STATE_MACHINE, CharacterState, parse_character_state

BODY_PARTS = ["glowa", "korpus", "prawa_reka", "lewa_reka", "prawa_noga", "lewa_noga"]


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


@dataclass
class CharacterSkills:
    values: dict[str, dict[str, int]] = field(default_factory=lambda: {
        "bron_cieta": {"level": 1, "progress": 0},
        "bron_obuchowa": {"level": 1, "progress": 0},
        "wlocznie": {"level": 1, "progress": 0},
        "uniki": {"level": 1, "progress": 0},
        "parowanie": {"level": 1, "progress": 0},
        "spostrzegawczosc": {"level": 1, "progress": 0},
    })

    def train(self, name: str, amount: int) -> bool:
        skill = self.values.setdefault(name, {"level": 1, "progress": 0})
        rules = default_skill_rules()
        if not rules.can_train(skill["level"]):
            return False
        skill["progress"] += amount
        threshold = rules.threshold(skill["level"])
        if skill["progress"] >= threshold:
            skill["level"] += 1
            skill["progress"] = 0
            return True
        return False


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
    stats: CharacterStats = field(default_factory=CharacterStats)
    skills: CharacterSkills = field(default_factory=CharacterSkills)
    inventory: list[Item] = field(default_factory=starter_items)
    equipment: dict[str, Item | None] = field(default_factory=lambda: {
        "prawa_reka": None, "lewa_reka": None, "glowa": None, "korpus": None, "nogi": None,
    })
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
    is_alive: bool = True
    in_combat: bool = False
    combat_style: str = "zrownowazony"
    combat_events: list[str] = field(default_factory=list)
    state: str = CharacterState.ALIVE.value
    admin_role: str | None = None

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
        right = self.equipment.get("prawa_reka")
        if right and right.item_type == "weapon":
            return right
        for item in self.inventory:
            if item.item_type == "weapon":
                return item
        return None

    def armor_for(self, body_part: str) -> Item | None:
        slot = "korpus" if body_part == "korpus" else "glowa" if body_part == "glowa" else "nogi" if "noga" in body_part else None
        return self.equipment.get(slot) if slot else None

    def shield(self) -> Item | None:
        left = self.equipment.get("lewa_reka")
        if left and left.item_type == "shield" and left.durability > 0:
            return left
        return None

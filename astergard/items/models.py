from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class Item:
    name: str
    description: str
    weight: float
    value: int = 0
    vnum: str | None = None
    item_type: str = "misc"
    slot: str | None = None
    is_container: bool = False
    capacity: float = 0.0
    contains: list["Item"] = field(default_factory=list)
    damage_type: str | None = None
    base_damage: int = 0
    protection: int = 0
    durability: float = 10.0
    max_durability: float = 10.0
    is_consumable: bool = False
    effects_on_consume: dict[str, int | str] = field(default_factory=dict)
    reach: int = 1
    initiative_modifier: int = 0
    parry_bonus: int = 0
    shield_block: int = 0
    id: str = field(default_factory=lambda: uuid4().hex)

    def total_weight(self) -> float:
        return self.weight + sum(item.total_weight() for item in self.contains)

    def display_name(self) -> str:
        if self.durability <= 0 and self.item_type in {"weapon", "armor", "shield"}:
            return f"{self.name} (zniszczony)"
        return self.name

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "value": self.value,
            "vnum": self.vnum,
            "item_type": self.item_type,
            "slot": self.slot,
            "is_container": self.is_container,
            "capacity": self.capacity,
            "contains": [item.to_dict() for item in self.contains],
            "damage_type": self.damage_type,
            "base_damage": self.base_damage,
            "protection": self.protection,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "is_consumable": self.is_consumable,
            "effects_on_consume": dict(self.effects_on_consume),
            "reach": self.reach,
            "initiative_modifier": self.initiative_modifier,
            "parry_bonus": self.parry_bonus,
            "shield_block": self.shield_block,
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Item":
        contains_raw = data.get("contains", [])
        contains = [cls.from_dict(item) for item in contains_raw if isinstance(item, dict)]
        return cls(
            name=str(data.get("name", "nieznany przedmiot")),
            description=str(data.get("description", "")),
            weight=float(data.get("weight", 0.0)),
            value=int(data.get("value", 0)),
            vnum=data.get("vnum"),
            item_type=str(data.get("item_type", "misc")),
            slot=data.get("slot"),
            is_container=bool(data.get("is_container", False)),
            capacity=float(data.get("capacity", 0.0)),
            contains=contains,
            damage_type=data.get("damage_type"),
            base_damage=int(data.get("base_damage", 0)),
            protection=int(data.get("protection", 0)),
            durability=float(data.get("durability", 10.0)),
            max_durability=float(data.get("max_durability", 10.0)),
            is_consumable=bool(data.get("is_consumable", False)),
            effects_on_consume=dict(data.get("effects_on_consume", {})),
            reach=int(data.get("reach", 1)),
            initiative_modifier=int(data.get("initiative_modifier", 0)),
            parry_bonus=int(data.get("parry_bonus", 0)),
            shield_block=int(data.get("shield_block", 0)),
            id=str(data.get("id", uuid4().hex)),
        )


def starter_items() -> list[Item]:
    return [
        Item("prosty miecz", "Krótki miecz o zużytej rękojeści.", 1.8, 25, "simple_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1),
        Item("drewniana tarcza", "Tarcza z ciemnego drewna.", 2.5, 15, "wooden_shield", "shield", "lewa_reka", protection=1, shield_block=3),
        Item("skórzana kurtka", "Utwardzana kurtka podróżna.", 3.0, 20, "leather_jacket", "armor", "korpus", protection=1),
        Item("chleb", "Twardy bochen podróżny.", 0.4, 2, "bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
    ]

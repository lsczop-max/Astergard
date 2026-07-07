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


def innkeeper_shop_inventory() -> list[Item]:
    return [
        Item("woda źródlana", "Dzban czystej wody na drogę.", 1.0, 1, "innkeeper_spring_water", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("napój ziołowy", "Lekki napój z ziół i miodu.", 0.5, 2, "innkeeper_herbal_drink", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("chleb", "Twardy bochen z pieca.", 0.4, 2, "innkeeper_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
        Item("racja podróżna", "Sucha racja na marsz i nocleg w drodze.", 0.7, 4, "innkeeper_travel_ration", "food", is_consumable=True, effects_on_consume={"restore_stamina": 10}),
    ]


def baker_shop_inventory() -> list[Item]:
    return [
        Item("chleb", "Jeszcze ciepły bochen z miejskiego pieca.", 0.4, 2, "baker_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
        Item("podpłomyk", "Cienki placek na szybki posiłek.", 0.2, 1, "baker_flatbread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("mąka", "Sakwa drobno mielonej mąki.", 1.0, 2, "baker_flour", "misc"),
        Item("bułka", "Miękka bułka na śniadanie.", 0.2, 1, "baker_roll", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
    ]


def blacksmith_shop_inventory() -> list[Item]:
    return [
        Item("pilnik", "Pilnik do ostrzenia i wygładzania metalu.", 0.4, 3, "smith_file", "tool"),
        Item("młotek warsztatowy", "Niewielki młotek do drobnych napraw.", 1.2, 5, "smith_work_hammer", "tool"),
        Item("naprawione ostrze", "Stare ostrze po naprawie, dobre do lekkiej służby.", 1.6, 9, "smith_reforged_blade", "weapon", "prawa_reka", damage_type="cieta", base_damage=3, reach=1, initiative_modifier=0, parry_bonus=1),
        Item("krótki nóż", "Krótki nóż do cięcia sznurów i skóry.", 0.3, 4, "smith_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
    ]


def merchant_shop_inventory() -> list[Item]:
    return [
        Item("krzesiwo", "Krzesiwo i krzemień w skórzanym woreczku.", 0.2, 2, "merchant_flint", "tool"),
        Item("bukłak", "Mały bukłak na wodę.", 0.6, 3, "merchant_waterskin", "tool"),
        Item("latarnia podróżna", "Prosta latarnia z grubym szkłem.", 1.4, 6, "merchant_lantern", "tool"),
        Item("sakwa podróżna", "Sakwa z jedną dużą przegródką i mocnym paskiem.", 1.0, 5, "merchant_travel_sack", is_container=True, capacity=12),
        Item("zwój liny", "Zwój grubej liny, przydatny przy drodze.", 2.8, 4, "merchant_rope", "tool"),
    ]


def fisher_shop_inventory() -> list[Item]:
    return [
        Item("świeża ryba", "Świeżo złowiona ryba z lokalnego nurtu.", 0.6, 2, "fisher_fresh_fish", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("sieć rybacka", "Mokra sieć do połowu i napraw.", 2.2, 9, "fisher_net", "tool"),
        Item("haczyk", "Mały haczyk do lin i sieci.", 0.1, 1, "fisher_hook", "tool"),
        Item("sznur do sieci", "Krótki sznur do łatania sieci.", 0.2, 2, "fisher_net_cord", "tool"),
    ]


def vendor_shop_inventory() -> list[Item]:
    return [
        Item("cebula", "Cebula z chłodnego składu.", 0.1, 1, "vendor_onion", "food", is_consumable=True, effects_on_consume={"restore_stamina": 2}),
        Item("marchew", "Twarda, świeża marchew.", 0.1, 1, "vendor_carrot", "food", is_consumable=True, effects_on_consume={"restore_stamina": 2}),
        Item("łatana koszula", "Tania koszula połatana na łokciach.", 0.8, 3, "vendor_patched_shirt", "armor", "korpus", protection=0),
        Item("lniana chusta", "Lekka chusta chroniąca przed kurzem.", 0.2, 2, "vendor_linen_scarf", "armor", "glowa", protection=0),
        Item("guziki", "Pęk drewnianych guzików do prostych napraw.", 0.05, 1, "vendor_buttons", "misc"),
    ]


def innkeeper_favor_item() -> Item:
    return Item("gorący posiłek", "Ciepły, prosty posiłek dla zaufanego gościa.", 0.8, 5, "innkeeper_favor_meal", "food", is_consumable=True, effects_on_consume={"restore_stamina": 14})

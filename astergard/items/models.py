from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


EQUIPMENT_SLOTS: tuple[str, ...] = (
    "glowa",
    "szyja",
    "korpus",
    "plecy",
    "rece",
    "dlonie",
    "pas",
    "nogi",
    "stopy",
    "bron_glowna",
    "bron_pomocnicza",
    "tarcza",
    "pierscien_1",
    "pierscien_2",
    "amulet",
)

EQUIPMENT_SLOT_LABELS: dict[str, str] = {
    "glowa": "głowa",
    "szyja": "szyja",
    "korpus": "korpus",
    "plecy": "plecy",
    "rece": "ręce",
    "dlonie": "dłonie",
    "pas": "pas",
    "nogi": "nogi",
    "stopy": "stopy",
    "bron_glowna": "broń główna",
    "bron_pomocnicza": "broń pomocnicza",
    "tarcza": "tarcza",
    "pierscien_1": "pierścień 1",
    "pierscien_2": "pierścień 2",
    "amulet": "amulet",
}

EQUIPMENT_SLOT_ALIASES: dict[str, str] = {
    "prawa_reka": "bron_glowna",
    "lewa_reka": "bron_pomocnicza",
}


def normalize_equipment_slot(slot: str | None) -> str | None:
    if slot is None:
        return None
    return EQUIPMENT_SLOT_ALIASES.get(slot, slot)


def equipment_slot_label(slot: str) -> str:
    return EQUIPMENT_SLOT_LABELS.get(slot, slot)


class EquipmentSet(dict[str, "Item | None"]):
    def __init__(self, initial: Mapping[str, "Item | None"] | None = None) -> None:
        super().__init__()
        for slot in EQUIPMENT_SLOTS:
            super().__setitem__(slot, None)
        if initial:
            self.update(initial)

    @classmethod
    def default(cls) -> "EquipmentSet":
        return cls()

    @classmethod
    def from_dict(cls, data: Mapping[str, "Item | None"]) -> "EquipmentSet":
        return cls(data)

    def _canonical(self, slot: str) -> str:
        return normalize_equipment_slot(slot) or slot

    def __setitem__(self, slot: str, item: "Item | None") -> None:
        super().__setitem__(self._canonical(slot), item)

    def __getitem__(self, slot: str) -> "Item | None":
        return super().__getitem__(self._canonical(slot))

    def __delitem__(self, slot: str) -> None:
        super().__delitem__(self._canonical(slot))

    def __contains__(self, slot: object) -> bool:
        if not isinstance(slot, str):
            return super().__contains__(slot)
        return super().__contains__(self._canonical(slot))

    def get(self, slot: str, default: "Item | None" = None) -> "Item | None":  # type: ignore[override]
        return super().get(self._canonical(slot), default)

    def setdefault(self, slot: str, default: "Item | None" = None) -> "Item | None":
        return super().setdefault(self._canonical(slot), default)

    def pop(self, slot: str, default: "Item | None" = None) -> "Item | None":  # type: ignore[override]
        canonical = self._canonical(slot)
        if default is None:
            return super().pop(canonical)
        return super().pop(canonical, default)

    def update(self, other: Mapping[str, "Item | None"] | Iterable[tuple[str, "Item | None"]] = (), /, **kwargs: "Item | None") -> None:  # type: ignore[override]
        items: list[tuple[str, "Item | None"]] = []
        if isinstance(other, Mapping):
            items.extend(other.items())
        else:
            items.extend(other)
        items.extend(kwargs.items())
        for slot, item in items:
            super().__setitem__(self._canonical(slot), item)

    def copy(self) -> "EquipmentSet":
        return EquipmentSet(self)


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
    wearable: bool | None = None
    armor_value: int = 0
    weapon_type: str | None = None
    damage_type: str | None = None
    base_damage: int = 0
    protection: int = 0
    durability: float = 10.0
    max_durability: float = 10.0
    is_consumable: bool = False
    effects_on_consume: dict[str, int | str] = field(default_factory=dict)
    can_be_sold_to_merchants: bool = True
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

    def is_wearable(self) -> bool:
        if self.wearable is not None:
            return self.wearable
        return self.slot is not None or self.item_type in {"weapon", "armor", "shield"}

    def normalized_slot(self) -> str | None:
        slot = normalize_equipment_slot(self.slot)
        if slot is not None:
            return slot
        if self.weapon_type == "tarcza" or self.item_type == "shield":
            return "tarcza"
        if self.item_type == "weapon":
            return "bron_glowna"
        return None

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
            "wearable": self.wearable,
            "armor_value": self.armor_value,
            "weapon_type": self.weapon_type,
            "damage_type": self.damage_type,
            "base_damage": self.base_damage,
            "protection": self.protection,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "is_consumable": self.is_consumable,
            "effects_on_consume": dict(self.effects_on_consume),
            "can_be_sold_to_merchants": self.can_be_sold_to_merchants,
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
            wearable=data.get("wearable"),
            armor_value=int(data.get("armor_value", data.get("protection", 0))),
            weapon_type=data.get("weapon_type"),
            damage_type=data.get("damage_type"),
            base_damage=int(data.get("base_damage", 0)),
            protection=int(data.get("protection", 0)),
            durability=float(data.get("durability", 10.0)),
            max_durability=float(data.get("max_durability", 10.0)),
            is_consumable=bool(data.get("is_consumable", False)),
            effects_on_consume=dict(data.get("effects_on_consume", {})),
            can_be_sold_to_merchants=bool(data.get("can_be_sold_to_merchants", True)),
            reach=int(data.get("reach", 1)),
            initiative_modifier=int(data.get("initiative_modifier", 0)),
            parry_bonus=int(data.get("parry_bonus", 0)),
            shield_block=int(data.get("shield_block", 0)),
            id=str(data.get("id", uuid4().hex)),
        )


def starter_items() -> list[Item]:
    return [
        Item("prosty miecz", "Krótki miecz o zużytej rękojeści.", 1.8, 25, "simple_sword", "weapon", "bron_glowna", wearable=True, weapon_type="miecz", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1),
        Item("drewniana tarcza", "Tarcza z ciemnego drewna.", 2.5, 15, "wooden_shield", "shield", "tarcza", wearable=True, weapon_type="tarcza", protection=1, shield_block=3),
        Item("skórzana kurtka", "Utwardzana kurtka podróżna.", 3.0, 20, "leather_jacket", "armor", "korpus", wearable=True, armor_value=1, protection=1),
        Item("chleb", "Twardy bochen podróżny.", 0.4, 2, "bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
    ]


def dueling_blade() -> Item:
    return Item("szpada ćwiczebna", "Lekka broń do nauki fechtunku.", 1.4, 18, "dueling_blade", "weapon", "bron_glowna", wearable=True, weapon_type="szpada", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=2, parry_bonus=2)


def training_spear() -> Item:
    return Item("włócznia treningowa", "Prosta włócznia do nauki dystansu i kontroli przestrzeni.", 2.4, 16, "training_spear", "weapon", "bron_glowna", wearable=True, weapon_type="włócznia", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0)


def battle_axe() -> Item:
    return Item("topór bojowy", "Cięższy topór do bezpośredniego starcia.", 3.4, 22, "battle_axe", "weapon", "bron_glowna", wearable=True, weapon_type="topór", damage_type="obuchowa", base_damage=5, reach=1, initiative_modifier=0, parry_bonus=0)


def hunting_bow() -> Item:
    return Item("łuk myśliwski", "Lekki łuk do polowań i szkolenia z dystansu.", 1.2, 18, "hunting_bow", "weapon", "bron_glowna", wearable=True, weapon_type="łuk", damage_type="pociskowa", base_damage=4, reach=2, initiative_modifier=1, parry_bonus=0)


def light_crossbow() -> Item:
    return Item("kusza lekka", "Prosta kusza o umiarkowanym naciągu.", 2.8, 22, "light_crossbow", "weapon", "bron_glowna", wearable=True, weapon_type="kusza", damage_type="pociskowa", base_damage=5, reach=2, initiative_modifier=0, parry_bonus=0)


def command_whistle() -> Item:
    return Item("gwizdek dowódcy", "Krótkie narzędzie do wydawania sygnałów i porządkowania ludzi.", 0.1, 4, "command_whistle", "tool")


def prayer_book() -> Item:
    return Item("modlitewnik", "Niewielki modlitewnik do rozmyślań i społecznej służby.", 0.2, 4, "prayer_book", "tool")


def smith_tools() -> Item:
    return Item("młotek czeladniczy", "Porządny młotek do warsztatu i prostych napraw.", 1.1, 8, "smith_tools", "tool")


def cyrulik_kit() -> Item:
    return Item("zestaw cyrulika", "Narzędzia do opatrunków, strzyżenia i drobnych zabiegów.", 0.8, 10, "barber_kit", "tool")


def lute() -> Item:
    return Item("lutnia", "Prosta lutnia do śpiewu i opowieści przy ogniu.", 1.5, 12, "lute", "tool")


def bowyer_tools() -> Item:
    return Item("narzędzia łuczarza", "Piła, klej i sznur przydatne przy strzałach i łukach.", 1.0, 9, "bowyer_tools", "tool")


def innkeeper_shop_inventory() -> list[Item]:
    return [
        Item("woda źródlana", "Dzban czystej wody na drogę.", 1.0, 1, "innkeeper_spring_water", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("piwo jasne", "Lekkie piwo warzone na bieżący wieczór.", 0.6, 3, "innkeeper_light_ale", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("piwo ciemne", "Ciemniejsze piwo podawane do sytego posiłku.", 0.7, 4, "innkeeper_dark_ale", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("miód pitny", "Słodszy napój na spokojny wieczór.", 0.5, 5, "innkeeper_mead", "food", is_consumable=True, effects_on_consume={"restore_stamina": 7}),
        Item("chleb", "Twardy bochen z pieca.", 0.4, 2, "innkeeper_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
        Item("gulasz karczemny", "Gęsty gulasz z prostych składników.", 0.8, 6, "innkeeper_stew", "food", is_consumable=True, effects_on_consume={"restore_stamina": 11}),
        Item("ser z chleba", "Porcja sera podawana z kromką chleba.", 0.5, 4, "innkeeper_cheese_plate", "food", is_consumable=True, effects_on_consume={"restore_stamina": 8}),
    ]


def karczmarz_shop_inventory() -> list[Item]:
    return [
        Item("piwo z beczki", "Świeżo nalane piwo o prostym, uczciwym smaku.", 0.6, 3, "innkeeper_cask_ale", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("piwo ciemne", "Gęstsze piwo dla tych, którzy zostają dłużej.", 0.7, 4, "innkeeper_dark_ale", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("miód pitny", "Słodki trunek na zakończenie dnia.", 0.5, 5, "innkeeper_mead", "food", is_consumable=True, effects_on_consume={"restore_stamina": 7}),
        Item("chleb z pieca", "Bochen jeszcze ciepły od pieca karczmy.", 0.4, 2, "innkeeper_oven_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
        Item("gulasz z kotła", "Gęsty gulasz, którym da się najeść do syta.", 0.9, 6, "innkeeper_pot_stew", "food", is_consumable=True, effects_on_consume={"restore_stamina": 11}),
        Item("kiszone ogórki", "Słój ogórków do piwa i do obiadu.", 0.5, 3, "innkeeper_pickles", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
    ]


def karczmarka_shop_inventory() -> list[Item]:
    return [
        Item("bułka maślana", "Miękka bułka na szybkie śniadanie.", 0.2, 2, "innkeeper_butter_roll", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("jajka", "Koszyczek świeżych jaj od pobliskich gospodarzy.", 0.3, 3, "innkeeper_eggs", "food", is_consumable=True, effects_on_consume={"restore_stamina": 3}),
        Item("ser biały", "Świeży ser zawinięty w płótno.", 0.4, 4, "innkeeper_white_cheese", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("kasza z boczkiem", "Prosta porcja kaszy z kawałkami boczku.", 0.8, 5, "innkeeper_groats_bacon", "food", is_consumable=True, effects_on_consume={"restore_stamina": 10}),
        Item("zupa jarzynowa", "Lekka zupa z warzyw z kuchennego kotła.", 0.7, 4, "innkeeper_vegetable_soup", "food", is_consumable=True, effects_on_consume={"restore_stamina": 8}),
        Item("miód stołowy", "Łagodny miód podawany do posiłku.", 0.4, 4, "innkeeper_table_honey", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
    ]


def baker_shop_inventory() -> list[Item]:
    return [
        Item("chleb", "Jeszcze ciepły bochen z miejskiego pieca.", 0.4, 2, "baker_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
        Item("podpłomyk", "Cienki placek na szybki posiłek.", 0.2, 1, "baker_flatbread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("bułka", "Miękka bułka na śniadanie.", 0.2, 1, "baker_roll", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("precel", "Zwykły precel z solą.", 0.1, 1, "baker_pretzel", "food", is_consumable=True, effects_on_consume={"restore_stamina": 3}),
        Item("placek drożdżowy", "Słodki placek na popołudniowy głód.", 0.4, 3, "baker_yeast_cake", "food", is_consumable=True, effects_on_consume={"restore_stamina": 7}),
        Item("mąka", "Sakwa drobno mielonej mąki.", 1.0, 2, "baker_flour", "misc"),
        Item("drożdże", "Mały woreczek drożdży do domowego wypieku.", 0.1, 1, "baker_yeast", "misc"),
        Item("bułka maślana", "Bułka z dodatkiem masła, jeszcze ciepła.", 0.2, 2, "baker_butter_roll", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
    ]


def blacksmith_shop_inventory() -> list[Item]:
    return [
        Item("pilnik", "Pilnik do ostrzenia i wygładzania metalu.", 0.4, 3, "smith_file", "tool"),
        Item("młotek warsztatowy", "Niewielki młotek do drobnych napraw.", 1.2, 5, "smith_work_hammer", "tool"),
        Item("kowadło podręczne", "Małe kowadło do napraw w warsztacie.", 4.5, 12, "smith_hand_anvil", "tool"),
        Item("krótki nóż", "Krótki nóż do cięcia sznurów i skóry.", 0.3, 4, "smith_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
        Item("podkowa", "Zwykła podkowa do naprawy chodzących zwierząt.", 0.8, 4, "smith_horseshoe", "tool"),
        Item("gwoździe", "Pakiet mocnych gwoździ do płotów i belek.", 0.3, 2, "smith_nails", "tool"),
        Item("zawias", "Solidny zawias do drzwi i skrzyń.", 0.4, 3, "smith_hinge", "tool"),
        Item("szczypce kowalskie", "Długie szczypce do rozgrzanego metalu.", 1.0, 5, "smith_tongs", "tool"),
    ]


def merchant_shop_inventory() -> list[Item]:
    return [
        Item("krzesiwo", "Krzesiwo i krzemień w skórzanym woreczku.", 0.2, 2, "merchant_flint", "tool"),
        Item("bukłak", "Mały bukłak na wodę.", 0.6, 3, "merchant_waterskin", "tool"),
        Item("latarnia podróżna", "Prosta latarnia z grubym szkłem.", 1.4, 6, "merchant_lantern", "tool"),
        Item("sakwa podróżna", "Sakwa z jedną dużą przegródką i mocnym paskiem.", 1.0, 5, "merchant_travel_sack", is_container=True, capacity=12),
        Item("zwój liny", "Zwój grubej liny, przydatny przy drodze.", 2.8, 4, "merchant_rope", "tool"),
        Item("sól w worku", "Niewielki worek soli do drogi i kuchni.", 1.2, 3, "merchant_salt_bag", "food", is_consumable=False),
        Item("świeca łojowa", "Zwykła świeca na wieczorne postoje.", 0.1, 1, "merchant_tallow_candle", "tool"),
        Item("igła i nitka", "Zestaw do prostych napraw odzieży.", 0.1, 2, "merchant_needle_thread", "tool"),
    ]


def tanner_shop_inventory() -> list[Item]:
    return [
        Item("garbarski garnek", "Pojemnik do mieszania garbników i wody.", 1.4, 6, "tanner_tub", "tool"),
        Item("sól do skór", "Worek soli do konserwowania świeżych skór.", 1.0, 4, "tanner_hide_salt", "tool"),
        Item("sznur do suszenia", "Mocny sznur do wieszania wyprawionych skór.", 0.4, 3, "tanner_drying_line", "tool"),
        Item("wyprawiona skóra", "Dobrze przygotowana skóra gotowa do szycia.", 1.2, 9, "tanner_cured_hide", "tool"),
        Item("futrzana podszewka", "Miękka podszewka do zimowych ubrań.", 0.8, 8, "tanner_fur_lining", "armor", "korpus", protection=0),
    ]


def butcher_shop_inventory() -> list[Item]:
    return [
        Item("topór rzeźnicki", "Krótki topór do rozbijania kości i porcjowania mięsa.", 1.8, 8, "butcher_cleaver", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=3, reach=1, initiative_modifier=0, parry_bonus=0),
        Item("hak rzeźnicki", "Metalowy hak do wieszania tusz.", 0.6, 4, "butcher_hook", "tool"),
        Item("sól peklowa", "Sól do konserwacji mięsa i skór.", 1.2, 5, "butcher_curing_salt", "food", is_consumable=False),
        Item("surowe mięso", "Porcja świeżego mięsa z dziennego uboju.", 0.7, 6, "butcher_raw_meat", "food", is_consumable=True, effects_on_consume={"restore_stamina": 9}),
        Item("wędzonka", "Paski mięsa uwędzone na zapas.", 0.5, 7, "butcher_smoked_meat", "food", is_consumable=True, effects_on_consume={"restore_stamina": 11}),
    ]


def skin_trader_shop_inventory() -> list[Item]:
    return [
        Item("skóra wilka", "Szorstka skóra z wilka, dobra na rękawice albo kaptur.", 1.0, 8, "skin_trader_wolf_pelt", "tool"),
        Item("skóra jelenia", "Wytrzymała skóra z jelenia, ceniona przez rzemieślników.", 1.2, 10, "skin_trader_deer_hide", "tool"),
        Item("futro leśne", "Grube futro odporne na chłód i wilgoć.", 1.4, 11, "skin_trader_forest_fur", "armor", "korpus", protection=1),
        Item("pióra ozdobne", "Garść lekkich piór na ozdoby i groty.", 0.1, 3, "skin_trader_ornamental_feathers", "tool"),
        Item("rogi szlachetne", "Ozdobne rogi przydatne do prostych wyrobów.", 0.9, 9, "skin_trader_horns", "tool"),
    ]


def fisher_shop_inventory() -> list[Item]:
    return [
        Item("świeża ryba", "Świeżo złowiona ryba z lokalnego nurtu.", 0.6, 2, "fisher_fresh_fish", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
        Item("wędzona ryba", "Ryba uwędzona na długie dni.", 0.5, 3, "fisher_smoked_fish", "food", is_consumable=True, effects_on_consume={"restore_stamina": 8}),
        Item("sieć rybacka", "Mokra sieć do połowu i napraw.", 2.2, 9, "fisher_net", "tool"),
        Item("haczyk", "Mały haczyk do lin i sieci.", 0.1, 1, "fisher_hook", "tool"),
        Item("sznur do sieci", "Krótki sznur do łatania sieci.", 0.2, 2, "fisher_net_cord", "tool"),
        Item("pławik", "Korek i pióro do szybkiego zestawu wędkarskiego.", 0.1, 1, "fisher_float", "tool"),
        Item("sól do ryb", "Mały worek soli do peklowania połowu.", 0.2, 2, "fisher_fish_salt", "food", is_consumable=False),
    ]


def vendor_shop_inventory() -> list[Item]:
    return [
        Item("cebula", "Cebula z chłodnego składu.", 0.1, 1, "vendor_onion", "food", is_consumable=True, effects_on_consume={"restore_stamina": 2}),
        Item("marchew", "Twarda, świeża marchew.", 0.1, 1, "vendor_carrot", "food", is_consumable=True, effects_on_consume={"restore_stamina": 2}),
        Item("ziemniaki", "Workowana porcja ziemniaków na zupę albo ognisko.", 0.7, 2, "vendor_potatoes", "food", is_consumable=True, effects_on_consume={"restore_stamina": 3}),
        Item("jabłka", "Kosz zwykłych jabłek z targu.", 0.6, 2, "vendor_apples", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("jajka", "Kilka jaj od pobliskich gospodarzy.", 0.3, 3, "vendor_eggs", "food", is_consumable=True, effects_on_consume={"restore_stamina": 3}),
        Item("łatana koszula", "Tania koszula połatana na łokciach.", 0.8, 3, "vendor_patched_shirt", "armor", "korpus", protection=0),
        Item("lniana chusta", "Lekka chusta chroniąca przed kurzem.", 0.2, 2, "vendor_linen_scarf", "armor", "glowa", protection=0),
        Item("guziki", "Pęk drewnianych guzików do prostych napraw.", 0.05, 1, "vendor_buttons", "misc"),
    ]


def haldun_market_inventory() -> list[Item]:
    return [
        Item("chleb wiejski", "Bochen na zakwasie, jeszcze ciepły po porannym wypieku.", 0.5, 2, "haldun_country_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 10}),
        Item("jabłka z sadu", "Koszyk kwaśnych jabłek z lokalnego sadu.", 1.0, 4, "haldun_orchard_apples", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("ser wiejski", "Twardy ser zawinięty w płótno.", 0.7, 5, "haldun_country_cheese", "food", is_consumable=True, effects_on_consume={"restore_stamina": 8}),
        Item("worek nasion", "Mieszanka nasion gotowa na wiosenny zasiew.", 1.4, 6, "haldun_seed_sack", is_container=True, capacity=14),
    ]


def haldun_forge_inventory() -> list[Item]:
    return [
        Item("podkowa", "Prosta podkowa do naprawy końskiego kopyta.", 0.8, 4, "haldun_horseshoe", "tool"),
        Item("gwoździe", "Pakiet mocnych gwoździ do płotów i stajen.", 0.3, 2, "haldun_nails", "tool"),
        Item("sierp", "Lekki sierp do żniw.", 0.8, 6, "haldun_scythe", "weapon", "prawa_reka", damage_type="cieta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
        Item("łopata", "Płaska łopata do rowów i błota.", 1.6, 5, "haldun_shovel", "tool"),
    ]


def haldun_mill_inventory() -> list[Item]:
    return [
        Item("mąka razowa", "Workowana mąka z lokalnego młyna.", 1.0, 3, "haldun_wholemeal_flour", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("worek zboża", "Ciężki worek z jęczmieniem.", 6.8, 8, "haldun_grain_sack", is_container=True, capacity=24),
        Item("otręby", "Tani, pożywny worek otrębów.", 1.1, 2, "haldun_bran", "food", is_consumable=True, effects_on_consume={"restore_stamina": 3}),
        Item("babka na zakwasie", "Płaski chleb na szybki posiłek.", 0.4, 2, "haldun_flat_loaf", "food", is_consumable=True, effects_on_consume={"restore_stamina": 6}),
    ]


def dungrim_armory_inventory() -> list[Item]:
    return [
        Item("hełm garnizonowy", "Prosty hełm używany przez wartowników fortecy.", 2.8, 18, "dungrim_garrison_helm", "armor", "glowa", protection=1),
        Item("płaszcz patrolowy", "Ciężki płaszcz chroniący przed wiatrem na murach.", 3.4, 24, "dungrim_patrol_cloak", "armor", "korpus", protection=1),
        Item("tarcza forteczna", "Tarcza okuta żelazem, zrobiona do długiej służby.", 4.0, 30, "dungrim_fortress_shield", "shield", "lewa_reka", protection=2, shield_block=3),
        Item("miecz wartowniczy", "Krótki miecz dla straży i oficerów.", 1.9, 28, "dungrim_watch_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1),
    ]


def dungrim_quartermaster_inventory() -> list[Item]:
    return [
        Item("racja żołnierska", "Sucha porcja do marszu i nocnej wachty.", 0.6, 4, "dungrim_ration", "food", is_consumable=True, effects_on_consume={"restore_stamina": 8}),
        Item("oliwa do lamp", "Mała butelka oliwy do lamp i pochodni.", 0.4, 3, "dungrim_lamp_oil", "tool"),
        Item("zwój bełtów", "Zwój bełtów do fortecznych kusz.", 1.4, 10, "dungrim_bolt_bundle", "tool"),
        Item("stara latarnia", "Latarnia z grubym szkłem, dobra na patrol.", 1.3, 8, "dungrim_lantern", "tool"),
    ]


def dungrim_stable_inventory() -> list[Item]:
    return [
        Item("siano wojskowe", "Zapas siana dla koni patrolowych.", 3.0, 4, "dungrim_hay_bundle", "food", is_consumable=False),
        Item("uzda patrolowa", "Mocna uzda do służbowych koni.", 1.1, 7, "dungrim_patrol_bridle", "tool"),
        Item("podkowa forteczna", "Cięższa podkowa do końskiej służby.", 0.9, 5, "dungrim_fortress_horseshoe", "tool"),
    ]


def dungrim_kitchen_inventory() -> list[Item]:
    return [
        Item("gulasz garnizonowy", "Gęsty, prosty gulasz dla załogi.", 0.9, 5, "dungrim_garrison_stew", "food", is_consumable=True, effects_on_consume={"restore_stamina": 12}),
        Item("chleb koszarowy", "Twardy bochen z wojskowego pieca.", 0.5, 2, "dungrim_barracks_bread", "food", is_consumable=True, effects_on_consume={"restore_stamina": 9}),
        Item("worek soli", "Worek soli do kuchni i konserwacji zapasów.", 2.6, 4, "dungrim_kitchen_salt", is_container=True, capacity=18),
    ]


def straznica_supply_inventory() -> list[Item]:
    return [
        Item("olej do lamp", "Mała butelka oleju na nocne czuwanie przy przełęczy.", 0.4, 3, "straznica_lamp_oil", "tool"),
        Item("zwój mapy", "Zwijana mapa przełęczy z zaznaczonymi ścieżkami i punktami widokowymi.", 0.2, 8, "straznica_pass_map", "tool"),
        Item("zwój liny", "Mocny zwój liny do wozów, noszy i mocowania ładunku.", 2.6, 4, "straznica_rope", "tool"),
        Item("koc podróżny", "Gruby koc chroniący przed wiatrem na nocnym postoju.", 1.8, 5, "straznica_travel_blanket", "tool"),
    ]


def straznica_caravan_inventory() -> list[Item]:
    return [
        Item("list przewozowy", "Papier z rozpisaną karawaną, ładunkiem i pieczęcią przejazdu.", 0.1, 4, "straznica_manifest_129", "tool"),
        Item("smar do osi", "Czarny smar przydatny przy naprawie kół wozu.", 0.5, 3, "straznica_axle_grease", "tool"),
        Item("klin pod koło", "Drewniany klin do unieruchamiania wozu na zboczu.", 0.7, 2, "straznica_wheel_wedge", "tool"),
        Item("suszone mięso", "Twardy kawałek mięsa na długą drogę.", 0.6, 4, "straznica_dried_meat", "food", is_consumable=True, effects_on_consume={"restore_stamina": 9}),
        Item("woda w bukłaku", "Bukłak z zimną wodą dla karawany.", 1.0, 2, "straznica_waterskin", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
    ]


def straznica_hunter_inventory() -> list[Item]:
    return [
        Item("wiązka grotów", "Wiązka prostych grotów do strzał i bełtów.", 0.7, 5, "straznica_arrowheads", "tool"),
        Item("skórzane rękawice", "Rękawice z wyprawionej skóry, dobre na wiatr i kamień.", 0.4, 4, "straznica_leather_gloves", "armor", "lewa_reka", protection=0),
        Item("sakwa ziołowa", "Mała sakwa z suszonymi ziołami i gorzkimi liśćmi.", 0.5, 4, "straznica_herb_sack", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("futro z kozicy", "Ciepłe futro z górskiej kozicy.", 1.9, 11, "straznica_chamois_fur", "armor", "korpus", protection=1),
    ]


def trakty_route_inventory() -> list[Item]:
    return [
        Item("olej do lamp", "Mała butelka oleju na nocne czuwanie przy trakcie.", 0.4, 3, "trakty_lamp_oil_135", "tool"),
        Item("zwój mapy", "Zwijana mapa z kamieniami milowymi i zaznaczonymi rozstajami.", 0.2, 8, "trakty_route_map_135", "tool"),
        Item("zwój liny", "Mocny zwój liny do wozów, mostków i ładunku.", 2.6, 4, "trakty_rope_141", "tool"),
        Item("koc podróżny", "Gruby koc chroniący przed wiatrem na nocnym postoju.", 1.8, 5, "trakty_travel_blanket_136", "tool"),
    ]


def trakty_caravan_inventory() -> list[Item]:
    return [
        Item("list przewozowy", "Papier z rozpisaną karawaną, ładunkiem i pieczęcią przejazdu.", 0.1, 4, "trakty_manifest_138", "tool"),
        Item("smar do osi", "Czarny smar przydatny przy naprawie kół wozu.", 0.5, 3, "trakty_axle_grease", "tool"),
        Item("klin pod koło", "Drewniany klin do unieruchamiania wozu na zboczu.", 0.7, 2, "trakty_wheel_wedge", "tool"),
        Item("suszone mięso", "Twardy kawałek mięsa na długą drogę.", 0.6, 4, "trakty_dried_meat", "food", is_consumable=True, effects_on_consume={"restore_stamina": 9}),
        Item("woda w bukłaku", "Bukłak z zimną wodą dla karawany.", 1.0, 2, "trakty_waterskin", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
    ]


def trakty_courier_inventory() -> list[Item]:
    return [
        Item("zapieczętowany list", "Krótkie pismo owinięte woskowym sznurkiem.", 0.1, 2, "trakty_sealed_note_140", "tool"),
        Item("wosk do pieczęci", "Twardy wosk do zamykania listów i worków.", 0.2, 2, "trakty_seal_wax", "tool"),
        Item("atramentowy fiolek", "Mała fiolka atramentu na meldunki i notatki.", 0.1, 2, "trakty_ink_vial", "tool"),
        Item("gwizdek pocztowy", "Krótki gwizdek przydatny w drodze.", 0.1, 1, "trakty_whistle", "tool"),
    ]


def trakty_hunter_inventory() -> list[Item]:
    return [
        Item("wiązka grotów", "Wiązka prostych grotów do strzał i bełtów.", 0.7, 5, "trakty_arrowheads", "tool"),
        Item("skórzane rękawice", "Rękawice z wyprawionej skóry, dobre na wiatr i kamień.", 0.4, 4, "trakty_leather_gloves", "armor", "lewa_reka", protection=0),
        Item("sakwa ziołowa", "Mała sakwa z suszonymi ziołami i gorzkimi liśćmi.", 0.5, 4, "trakty_herb_sack", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("futro z kozicy", "Ciepłe futro z górskiej kozicy.", 1.9, 11, "trakty_chamois_fur", "armor", "korpus", protection=1),
    ]


def trakty_lumber_inventory() -> list[Item]:
    return [
        Item("topór rozłupujący", "Ciężki topór do rąbania drewna przy drodze.", 3.1, 9, "trakty_lumber_axe", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=0),
        Item("klin do drewna", "Metalowy klin do rozszczepiania pieńków.", 0.8, 3, "trakty_wood_wedge", "tool"),
        Item("żywica sosnowa", "Lepka żywica do napraw i uszczelnień.", 0.3, 3, "trakty_resin", "tool"),
        Item("wiązka chrustu", "Suchy chrust przydatny na ognisko.", 1.0, 2, "trakty_kindling", "food"),
    ]


def puszcza_herbal_inventory() -> list[Item]:
    return [
        Item("wiązka leśnych ziół", "Zioła zebrane z mokrego poszycia i cienistych polan.", 0.2, 4, "puszcza_herb_bundle", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("suszone grzyby", "Pęk suszonych grzybów na długą drogę.", 0.3, 3, "puszcza_dry_mushrooms", "food", is_consumable=True, effects_on_consume={"restore_stamina": 5}),
        Item("maść na ukąszenia", "Prosta maść z tłuszczu i ziół.", 0.2, 5, "puszcza_bite_ointment", "tool"),
        Item("woreczek nasion", "Nasiona roślin potrzebnych w lesie i przy obejściu.", 0.5, 4, "puszcza_seed_pouch", is_container=True, capacity=8),
    ]


def puszcza_hunter_inventory() -> list[Item]:
    return [
        Item("kołczan strzał", "Skórzany kołczan z długimi strzałami.", 1.6, 10, "puszcza_arrows", "tool"),
        Item("sidła leśne", "Zestaw sidel i pętli na zwierzynę.", 1.0, 8, "puszcza_traps", "tool"),
        Item("futro sarny", "Cienkie, miękkie futro z lasu.", 1.5, 7, "puszcza_deer_fur", "armor", "korpus", protection=0),
        Item("nóż tropiciela", "Krótki nóż do skór, lin i tropów.", 0.3, 6, "puszcza_tracker_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
    ]


def puszcza_hermit_inventory() -> list[Item]:
    return [
        Item("skórzana torba", "Torba pełna notatek, sznurków i drobnych znalezisk.", 1.0, 6, "puszcza_hermit_bag", is_container=True, capacity=10),
        Item("stary medalik", "Wytarty medalik noszony na sznurku.", 0.1, 5, "puszcza_hermit_medallion", "tool"),
        Item("kubek z kory", "Kubek wyrzeźbiony z kory i drewna.", 0.2, 2, "puszcza_bark_cup", "tool"),
    ]


def bagna_herbal_inventory() -> list[Item]:
    return [
        Item("torfowe ziele", "Wilgotne, ostre ziele zebrane na skraju mokradła.", 0.1, 4, "bagna_bog_herb", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        Item("suszone pałki", "Szkliście suche pałki i sitowie do naparów.", 0.2, 3, "bagna_reed_bundle", "tool"),
        Item("maść przeciw wilgoci", "Lepka maść chroniąca skórę przed mokradłem.", 0.3, 5, "bagna_moisture_salve", "tool"),
    ]


def bagna_hermit_inventory() -> list[Item]:
    return [
        Item("talizman z kości", "Niewielki talizman wystrugany z kości i drewna.", 0.1, 4, "bagna_bone_talisman", "tool"),
        Item("stary kij", "Kij do chodzenia po kładkach i trzcinie.", 0.8, 3, "bagna_old_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
        Item("sznur ostów", "Sznur mokrych ostów i wiązanych trzcin.", 0.2, 2, "bagna_reed_rope", "tool"),
    ]


def innkeeper_favor_item() -> Item:
    return Item("gorący posiłek", "Ciepły, prosty posiłek dla zaufanego gościa.", 0.8, 5, "innkeeper_favor_meal", "food", is_consumable=True, effects_on_consume={"restore_stamina": 14})

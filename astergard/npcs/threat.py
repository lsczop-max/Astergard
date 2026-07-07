from __future__ import annotations

from dataclasses import dataclass

from astergard.characters.models import Character
from astergard.items.models import Item


@dataclass(frozen=True, slots=True)
class ThreatProfile:
    tier: str
    label: str
    stat_bonus: int
    stamina_bonus: int
    damage_bonus: int
    protection_bonus: int
    respawn_multiplier: float


THREAT_PROFILES: dict[str, ThreatProfile] = {
    "trash": ThreatProfile("trash", "pomniejszy przeciwnik", -1, -10, 0, 0, 0.75),
    "standard": ThreatProfile("standard", "standardowy przeciwnik", 0, 0, 0, 0, 1.0),
    "elite": ThreatProfile("elite", "elitarny przeciwnik", 2, 20, 1, 1, 1.5),
    "boss": ThreatProfile("boss", "boss", 4, 50, 2, 2, 3.0),
}

NPC_THREAT_BY_VNUM: dict[str, str] = {
    "merchant": "trash",
    "wolf": "trash",
    "meekhan_soldier": "standard",
    "mountain_troll": "elite",
    "warband_captain": "boss",
    "astergard_guard": "standard",
    "innkeeper": "trash",
    "blacksmith": "standard",
    "farmer": "trash",
    "fisherman": "trash",
    "traveler": "standard",
    "child": "trash",
    "beggar": "trash",
    "carpenter": "trash",
    "tanner": "trash",
    "bowyer": "trash",
    "armorer": "standard",
    "dockhand": "trash",
    "miller": "trash",
    "priest_aide": "trash",
    "watch_sergeant": "standard",
    "customs_clerk": "trash",
    "fishmonger": "trash",
    "woodcutter": "trash",
    "urchin": "trash",
    "vagrant": "trash",
    "podgrodzie_woznica": "trash",
    "podgrodzie_karczmarz": "trash",
    "podgrodzie_karczmarka": "trash",
    "podgrodzie_piekarz": "trash",
    "podgrodzie_handlarz": "trash",
    "podgrodzie_przekupka": "trash",
    "podgrodzie_kowal": "standard",
    "podgrodzie_pomocnik_kowala": "trash",
    "podgrodzie_straznik_miejski": "standard",
    "podgrodzie_rybak": "trash",
    "podgrodzie_dziecko": "trash",
    "podgrodzie_zebrak": "trash",
    "podgrodzie_pielgrzym": "trash",
    "podgrodzie_chlop": "trash",
    "podgrodzie_chlopka": "trash",
}


def threat_for_vnum(vnum: str) -> ThreatProfile:
    return THREAT_PROFILES[NPC_THREAT_BY_VNUM.get(vnum, "standard")]


def apply_threat_profile(character: Character, profile: ThreatProfile) -> None:
    character.stats.sila = max(1, character.stats.sila + profile.stat_bonus)
    character.stats.zrecznosc = max(1, character.stats.zrecznosc + profile.stat_bonus)
    character.stats.wytrzymalosc = max(1, character.stats.wytrzymalosc + profile.stat_bonus)
    character.stats.percepcja = max(1, character.stats.percepcja + profile.stat_bonus)
    character.stats.kondycja = max(1, character.stats.max_kondycja + profile.stamina_bonus)
    for item in character.equipment.values():
        _apply_item_bonus(item, profile)
    for item in character.inventory:
        _apply_item_bonus(item, profile)


def _apply_item_bonus(item: Item | None, profile: ThreatProfile) -> None:
    if item is None:
        return
    if item.item_type == "weapon":
        item.base_damage += profile.damage_bonus
    if item.item_type in {"armor", "shield"}:
        item.protection += profile.protection_bonus
        if item.item_type == "shield":
            item.shield_block += profile.protection_bonus

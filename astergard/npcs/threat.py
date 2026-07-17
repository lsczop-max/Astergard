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
    "haldun_solt": "standard",
    "haldun_wellkeeper": "trash",
    "haldun_blacksmith": "standard",
    "haldun_miller": "trash",
    "haldun_merchant": "trash",
    "haldun_farmer": "trash",
    "haldun_farmerka": "trash",
    "haldun_pasterz": "trash",
    "haldun_wartownik": "standard",
    "dungrim_commander": "boss",
    "dungrim_lieutenant": "standard",
    "dungrim_sergeant": "standard",
    "dungrim_guard": "standard",
    "dungrim_patrol_guard": "standard",
    "dungrim_armorer": "standard",
    "dungrim_military_blacksmith": "standard",
    "dungrim_quartermaster": "trash",
    "dungrim_storekeeper": "trash",
    "dungrim_stablemaster": "trash",
    "dungrim_cook": "trash",
    "straznica_dowodca": "standard",
    "straznica_wartownik": "standard",
    "straznica_zwiadowca": "standard",
    "straznica_przewodnik": "trash",
    "straznica_karawanowy": "trash",
    "straznica_woznica": "trash",
    "straznica_podrozny": "trash",
    "straznica_pielgrzym": "trash",
    "straznica_mysliwy": "trash",
    "trakty_przewodnik": "trash",
    "trakty_karawaniarz": "trash",
    "trakty_kurier": "trash",
    "trakty_woznica": "trash",
    "trakty_podrozny": "trash",
    "trakty_pielgrzym": "trash",
    "trakty_zebrak": "trash",
    "trakty_mysliwy": "trash",
    "trakty_drwal": "trash",
    "trakty_straznik": "standard",
    "trakty_handlarz": "trash",
    "puszcza_mysliwy": "trash",
    "puszcza_zielarz": "trash",
    "puszcza_pustelnik": "trash",
    "puszcza_drwal": "trash",
    "puszcza_szczur": "trash",
    "puszcza_kruk": "trash",
    "puszcza_lis": "trash",
    "puszcza_pies_dziki": "standard",
    "puszcza_wilk_mlody": "trash",
    "puszcza_wilk": "standard",
    "puszcza_jelen": "trash",
    "puszcza_dzik": "trash",
    "puszcza_pajak": "trash",
    "puszcza_pajak_lesny": "standard",
    "puszcza_pajak_duzy": "standard",
    "puszcza_wilk_stary": "standard",
    "puszcza_wataha_wilkow": "standard",
    "puszcza_niedzwiedz": "standard",
    "puszcza_niedzwiedzica": "standard",
    "puszcza_bandyta": "standard",
    "puszcza_bandyta_zwiadowca": "standard",
    "puszcza_lowca": "standard",
    "puszcza_lowczy": "standard",
    "puszcza_bandycki_naczelnik": "elite",
    "puszcza_niedzwiedzi_olbrzym": "elite",
    "puszcza_troll": "boss",
    "bagna_zielarz": "trash",
    "bagna_pustelnik": "trash",
    "bagna_zaba": "trash",
    "bagna_mysliwy": "trash",
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

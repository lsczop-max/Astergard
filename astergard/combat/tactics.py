from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
import unicodedata

if TYPE_CHECKING:
    from astergard.characters.models import Character
    from astergard.items.models import Item


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).casefold().strip()


FRONT = "front"
BACK = "back"
RESERVE = "reserve"


@dataclass(frozen=True, slots=True)
class TacticalModifiers:
    attack: int = 0
    defense: int = 0
    damage: int = 0
    initiative: int = 0
    morale: int = 0
    note: str = ""


def normalize_formation(value: str | None) -> str:
    raw = _fold(value or "")
    aliases = {
        "front": FRONT,
        "przod": FRONT,
        "linia": FRONT,
        "back": BACK,
        "tyl": BACK,
        "tył": BACK,
        "flank": BACK,
        "rezerwa": RESERVE,
        "reserve": RESERVE,
        "rezerwy": RESERVE,
    }
    return aliases.get(raw, FRONT)


def _is_ranged_weapon(weapon: Item | None) -> bool:
    return weapon is not None and weapon.item_type == "weapon" and weapon.reach >= 2 and weapon.damage_type == "pociskowa"


def _weapon_skill_name(weapon: Item | None) -> str:
    if weapon is None or weapon.durability <= 0:
        return "bron_jednoraczna"
    if weapon.damage_type == "obuchowa":
        return "bron_dwureczna"
    if weapon.damage_type == "kluta":
        return "wlocznie"
    if weapon.damage_type == "pociskowa":
        if weapon.vnum and "crossbow" in weapon.vnum:
            return "kusze"
        if "kusz" in weapon.name.casefold():
            return "kusze"
        return "luki"
    return "bron_jednoraczna"


def skill_for_weapon(weapon: Item | None) -> str:
    return _weapon_skill_name(weapon)


def wound_attack_penalty(character: Character) -> int:
    return character.wounds.get("prawa_reka", 0) + character.wounds.get("lewa_reka", 0) + character.wounds.get("glowa", 0) // 2


def wound_defense_penalty(character: Character) -> int:
    return character.wounds.get("prawa_reka", 0) + character.wounds.get("lewa_reka", 0) + character.wounds.get("prawa_noga", 0) + character.wounds.get("lewa_noga", 0)


def wound_initiative_penalty(character: Character) -> int:
    return character.wounds.get("glowa", 0) + character.wounds.get("prawa_noga", 0) + character.wounds.get("lewa_noga", 0)


def wound_morale_penalty(character: Character) -> int:
    return sum(character.wounds.values()) // 2


def fatigue_attack_penalty(character: Character) -> int:
    if character.stats.max_kondycja <= 0:
        return 0
    if character.stats.kondycja <= max(1, character.stats.max_kondycja // 4):
        return 2
    if character.stats.kondycja <= max(1, character.stats.max_kondycja // 2):
        return 1
    return 0


def fatigue_defense_penalty(character: Character) -> int:
    if character.stats.max_kondycja <= 0:
        return 0
    if character.stats.kondycja <= max(1, character.stats.max_kondycja // 4):
        return 1
    return 0


def morale_score(character: Character) -> int:
    morale_skill = character.skills.level("morale") if hasattr(character.skills, "level") else character.skills.values.get("morale", {"level": 1})["level"]
    command_skill = character.skills.level("dowodzenie") if hasattr(character.skills, "level") else character.skills.values.get("dowodzenie", {"level": 1})["level"]
    will = character.stats.sila_woli
    score = 10 + morale_skill // 2 + command_skill // 4 + will // 4 - wound_morale_penalty(character) - fatigue_attack_penalty(character)
    if character.main_profession == "dowodca":
        score += 2
    elif character.main_profession == "kaplan":
        score += 1
    elif character.main_profession == "berserker":
        score += 1 if character.stats.kondycja > character.stats.max_kondycja // 2 else 0
    return max(1, min(20, score))


def formation_attack_modifier(attacker: Character, defender: Character, weapon: Item | None) -> int:
    attacker_formation = normalize_formation(attacker.formation)
    defender_formation = normalize_formation(defender.formation)
    if attacker_formation == RESERVE:
        return -2
    if attacker_formation == BACK and defender_formation == FRONT:
        return 1 if _is_ranged_weapon(weapon) or (weapon is not None and weapon.reach >= 2) else -1
    if attacker_formation == FRONT and defender_formation == BACK:
        return 2
    if defender_formation == RESERVE:
        return 1
    return 0


def formation_defense_modifier(defender: Character, attacker: Character) -> int:
    defender_formation = normalize_formation(defender.formation)
    attacker_formation = normalize_formation(attacker.formation)
    modifier = 0
    if defender_formation == BACK:
        modifier += 1
    elif defender_formation == RESERVE:
        modifier += 2
    if attacker_formation == BACK and defender_formation == FRONT:
        modifier += 1
    return modifier


def formation_initiative_modifier(character: Character) -> int:
    formation = normalize_formation(character.formation)
    if formation == BACK:
        return -1
    if formation == RESERVE:
        return -2
    return 0


def profession_tactical_modifiers(character: Character, weapon: Item | None) -> TacticalModifiers:
    profession = _fold(character.main_profession)
    secondary = _fold(character.secondary_profession)
    weapon_skill = _weapon_skill_name(weapon)
    modifiers = TacticalModifiers()
    if profession == "wojownik":
        if weapon_skill in {"bron_jednoraczna", "bron_dwureczna", "bron_cieta", "bron_obuchowa"}:
            modifiers = TacticalModifiers(attack=1, damage=1)
    elif profession == "tarczownik":
        modifiers = TacticalModifiers(defense=1, morale=1)
        if character.shield() is not None:
            modifiers = TacticalModifiers(defense=2, morale=1)
    elif profession == "wlocznik":
        if weapon_skill == "wlocznie":
            modifiers = TacticalModifiers(attack=2 if weapon is not None and weapon.reach >= 2 else 1, initiative=1)
    elif profession == "szermierz":
        if weapon_skill == "bron_jednoraczna":
            modifiers = TacticalModifiers(attack=1, defense=1, initiative=1)
    elif profession == "berserker":
        if weapon_skill == "bron_dwureczna":
            modifiers = TacticalModifiers(attack=1, damage=2)
    elif profession == "lucznik":
        if weapon_skill == "luki":
            modifiers = TacticalModifiers(attack=2, initiative=1)
    elif profession == "kusznik":
        if weapon_skill == "kusze":
            modifiers = TacticalModifiers(attack=2, damage=1)

    if secondary == "dowodca":
        modifiers = TacticalModifiers(
            attack=modifiers.attack,
            defense=modifiers.defense + 1,
            damage=modifiers.damage,
            initiative=modifiers.initiative,
            morale=modifiers.morale + 1,
            note=modifiers.note,
        )
    elif secondary == "kaplan":
        modifiers = TacticalModifiers(
            attack=modifiers.attack,
            defense=modifiers.defense,
            damage=modifiers.damage,
            initiative=modifiers.initiative,
            morale=modifiers.morale + 1,
            note=modifiers.note,
        )
    elif secondary == "kowal":
        modifiers = TacticalModifiers(
            attack=modifiers.attack + (1 if character.equipment.get("korpus") is not None else 0),
            defense=modifiers.defense + 1,
            damage=modifiers.damage,
            initiative=modifiers.initiative,
            morale=modifiers.morale,
            note=modifiers.note,
        )
    elif secondary == "cyrulik":
        modifiers = TacticalModifiers(
            attack=modifiers.attack,
            defense=modifiers.defense + 1,
            damage=modifiers.damage,
            initiative=modifiers.initiative,
            morale=modifiers.morale + 1,
            note=modifiers.note,
        )
    elif secondary == "bard":
        modifiers = TacticalModifiers(
            attack=modifiers.attack,
            defense=modifiers.defense,
            damage=modifiers.damage,
            initiative=modifiers.initiative,
            morale=modifiers.morale + 2,
            note=modifiers.note,
        )
    elif secondary == "luczarz" and weapon_skill in {"luki", "kusze"}:
        modifiers = TacticalModifiers(
            attack=modifiers.attack + 1,
            defense=modifiers.defense,
            damage=modifiers.damage,
            initiative=modifiers.initiative,
            morale=modifiers.morale,
            note=modifiers.note,
        )
    return modifiers


def weapon_reach_modifier(attacker_weapon: Item | None, defender_weapon: Item | None) -> int:
    attacker_reach = attacker_weapon.reach if attacker_weapon is not None and attacker_weapon.durability > 0 else 1
    defender_reach = defender_weapon.reach if defender_weapon is not None and defender_weapon.durability > 0 else 1
    gap = attacker_reach - defender_reach
    if gap > 0:
        return min(2, gap)
    if gap < 0:
        return max(-2, gap)
    return 0


def tactical_hit_modifier(attacker: Character, defender: Character, weapon: Item | None) -> TacticalModifiers:
    attacker_weapon = weapon
    defender_weapon = defender.weapon()
    formation_attack = formation_attack_modifier(attacker, defender, attacker_weapon)
    formation_defense = formation_defense_modifier(defender, attacker)
    reach_modifier = weapon_reach_modifier(attacker_weapon, defender_weapon)
    attacker_morale = morale_score(attacker)
    defender_morale = morale_score(defender)
    attacker_prof = profession_tactical_modifiers(attacker, attacker_weapon)
    defender_prof = profession_tactical_modifiers(defender, defender_weapon)
    morale_edge = (attacker_morale - defender_morale) // 4
    return TacticalModifiers(
        attack=formation_attack + reach_modifier + attacker_prof.attack + morale_edge,
        defense=formation_defense + defender_prof.defense - max(0, -reach_modifier),
        damage=attacker_prof.damage,
        initiative=attacker_prof.initiative + formation_initiative_modifier(attacker) + (attacker_morale - 10) // 5,
        morale=attacker_morale,
        note="flank" if normalize_formation(attacker.formation) == FRONT and normalize_formation(defender.formation) == BACK else "",
    )

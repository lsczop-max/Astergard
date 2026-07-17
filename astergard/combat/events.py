from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from astergard.items.models import Item
from astergard.combat.hit_locations import BodyLocation, body_location_label


WEAPON_FAMILY_LABELS: dict[str, str] = {
    "miecze": "miecz",
    "sztylety": "sztylet",
    "topory": "topór",
    "maczugi": "maczuga",
    "mloty": "młot",
    "wlocznie": "włócznia",
    "bron_drzewcowa": "broń drzewcowa",
    "luki": "łuk",
    "kusze": "kusza",
    "improwizowana": "broń improwizowana",
    "bez_broni": "walka bez broni",
}


def normalize_weapon_family(weapon: Item | None) -> str:
    if weapon is None or weapon.durability <= 0:
        return "bez_broni"
    weapon_type = (weapon.weapon_type or "").strip().casefold()
    damage_type = (weapon.damage_type or "").strip().casefold()
    name = weapon.name.casefold()
    vnum = (weapon.vnum or "").casefold()
    tokens = f"{weapon_type} {damage_type} {name} {vnum}"
    if weapon_type in {"miecz", "szabla", "szpada", "rapier"}:
        return "miecze"
    if any(term in tokens for term in {"sword", "miecz", "szabla", "szpada", "rapier", "longsword", "broadsword"}):
        return "miecze"
    if weapon_type in {"sztylet", "nóż", "noz", "kord"}:
        return "sztylety"
    if any(term in tokens for term in {"dagger", "knife", "sztylet", "noz", "nóż", "kord"}):
        return "sztylety"
    if weapon_type in {"topór", "topor", "siekiera"} or damage_type == "obuchowa" and weapon.base_damage >= 5:
        return "topory"
    if any(term in tokens for term in {"axe", "topor", "topór", "siekiera"}):
        return "topory"
    if weapon_type in {"maczuga", "kij", "berło"}:
        return "maczugi"
    if any(term in tokens for term in {"club", "mace", "maczuga", "kij", "berlo", "berło"}):
        return "maczugi"
    if weapon_type in {"młot", "mlot"}:
        return "mloty"
    if any(term in tokens for term in {"hammer", "młot", "mlot"}):
        return "mloty"
    if weapon_type in {"włócznia", "wlocznia", "oszczep", "glewia"}:
        return "wlocznie"
    if any(term in tokens for term in {"spear", "wlocznia", "włócznia", "oszczep", "glewia", "pike"}):
        return "wlocznie"
    if weapon_type in {"halabarda", "berdysz", "gizarma", "partyzana"}:
        return "bron_drzewcowa"
    if any(term in tokens for term in {"halberd", "berdysz", "gizarma", "partyzana", "polearm", "poleaxe", "glaive"}):
        return "bron_drzewcowa"
    if weapon_type in {"łuk", "luk", "kusza", "crossbow"}:
        if weapon_type in {"kusza", "crossbow"} or "kusz" in weapon.name.casefold():
            return "kusze"
        return "luki"
    if any(term in tokens for term in {"bow", "luk", "łuk"}):
        return "luki"
    if any(term in tokens for term in {"crossbow", "kusza"}):
        return "kusze"
    if weapon_type in {"proca", "miotacz", "kamień", "kij"}:
        return "improwizowana"
    if weapon.item_type == "weapon" and weapon.reach <= 1 and damage_type == "pociskowa":
        return "luki"
    return "improwizowana"


def weapon_family_label(weapon_family: str) -> str:
    return WEAPON_FAMILY_LABELS.get(weapon_family, weapon_family)


def body_part_label(body_part: str | None) -> str:
    if body_part is None:
        return "ciało"
    try:
        return body_location_label(BodyLocation(str(body_part)))
    except ValueError:
        pass
    return {
        "glowa": "głowę",
        "korpus": "korpus",
        "brzuch": "brzuch",
        "szyja": "szyję",
        "plecy": "plecy",
        "prawa_reka": "prawą rękę",
        "lewa_reka": "lewą rękę",
        "prawa_dlon": "prawą dłoń",
        "lewa_dlon": "lewą dłoń",
        "prawa_noga": "prawą nogę",
        "lewa_noga": "lewą nogę",
        "stopa": "stopę",
    }.get(body_part or "", body_part or "ciało")


@dataclass(frozen=True, slots=True)
class CombatEvent:
    event_id: str = field(default_factory=lambda: uuid4().hex)
    action_id: str | None = None
    action_type: str = "BASIC_ATTACK"
    event_type: str = "attack"
    attacker_id: str = ""
    attacker_name: str = ""
    defender_id: str = ""
    defender_name: str = ""
    parent_action_id: str | None = None
    reaction_id: str | None = None
    reaction_type: str | None = None
    reaction_depth: int = 0
    observers: tuple[str, ...] = ()
    weapon_name: str | None = None
    weapon_family: str = "bez_broni"
    hand: str | None = None
    technique: str = ""
    intent: str = ""
    result: str = "miss"
    defense: str = "none"
    hit_location: str | None = None
    body_side: str | None = None
    damage_type: str | None = None
    raw_force: int = 0
    reduced_force: int = 0
    body_location: str | None = None
    body_location_group: str | None = None
    hit_quality: str | None = None
    armor_name: str | None = None
    armor_contact: str | None = None
    armor_layer: str | None = None
    armor_layers: tuple[str, ...] = ()
    armor_coverage_indicator: float = 0.0
    wound_level: int = 0
    special_effects: tuple[str, ...] = ()
    attacker_state: str = ""
    defender_state: str = ""
    environment: tuple[str, ...] = ()
    narrative_tags: tuple[str, ...] = ()
    outcome_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "action_id": self.action_id,
            "action_type": self.action_type,
            "event_type": self.event_type,
            "attacker_id": self.attacker_id,
            "attacker_name": self.attacker_name,
            "defender_id": self.defender_id,
            "defender_name": self.defender_name,
            "parent_action_id": self.parent_action_id,
            "reaction_id": self.reaction_id,
            "reaction_type": self.reaction_type,
            "reaction_depth": self.reaction_depth,
            "observers": list(self.observers),
            "weapon_name": self.weapon_name,
            "weapon_family": self.weapon_family,
            "hand": self.hand,
            "technique": self.technique,
            "intent": self.intent,
            "result": self.result,
            "defense": self.defense,
            "hit_location": self.hit_location,
            "body_side": self.body_side,
            "damage_type": self.damage_type,
            "raw_force": self.raw_force,
            "reduced_force": self.reduced_force,
            "body_location": self.body_location,
            "body_location_group": self.body_location_group,
            "hit_quality": self.hit_quality,
            "armor_name": self.armor_name,
            "armor_contact": self.armor_contact,
            "armor_layer": self.armor_layer,
            "armor_layers": list(self.armor_layers),
            "armor_coverage_indicator": self.armor_coverage_indicator,
            "wound_level": self.wound_level,
            "special_effects": list(self.special_effects),
            "attacker_state": self.attacker_state,
            "defender_state": self.defender_state,
            "environment": list(self.environment),
            "narrative_tags": list(self.narrative_tags),
            "outcome_notes": list(self.outcome_notes),
        }

from __future__ import annotations

import json
import hashlib
import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

from astergard.combat.weapons import DamageType, HandRequirement, WeaponProfile, load_default_weapon_profile_catalog

if TYPE_CHECKING:
    from astergard.combat.actions import CombatAction
    from astergard.characters.models import Character
    from astergard.items.models import Item


class BodyLocation(StrEnum):
    HEAD = "HEAD"
    NECK = "NECK"
    CHEST = "CHEST"
    ABDOMEN = "ABDOMEN"
    BACK = "BACK"
    LEFT_SHOULDER = "LEFT_SHOULDER"
    RIGHT_SHOULDER = "RIGHT_SHOULDER"
    LEFT_ARM = "LEFT_ARM"
    RIGHT_ARM = "RIGHT_ARM"
    LEFT_HAND = "LEFT_HAND"
    RIGHT_HAND = "RIGHT_HAND"
    LEFT_THIGH = "LEFT_THIGH"
    RIGHT_THIGH = "RIGHT_THIGH"
    LEFT_LEG = "LEFT_LEG"
    RIGHT_LEG = "RIGHT_LEG"
    LEFT_FOOT = "LEFT_FOOT"
    RIGHT_FOOT = "RIGHT_FOOT"


class BodyLocationGroup(StrEnum):
    HEAD_GROUP = "HEAD_GROUP"
    TORSO_GROUP = "TORSO_GROUP"
    ARM_GROUP = "ARM_GROUP"
    HAND_GROUP = "HAND_GROUP"
    LEG_GROUP = "LEG_GROUP"
    FOOT_GROUP = "FOOT_GROUP"


class AttackType(StrEnum):
    SLASH = "SLASH"
    THRUST = "THRUST"
    OVERHEAD = "OVERHEAD"
    SWEEP = "SWEEP"
    BLUNT_STRIKE = "BLUNT_STRIKE"
    STANDARD = "STANDARD"


class HitQuality(StrEnum):
    GLANCING = "GLANCING"
    CLEAN = "CLEAN"
    POWERFUL = "POWERFUL"
    DEVASTATING = "DEVASTATING"


BODY_LOCATION_TO_GROUP: dict[BodyLocation, BodyLocationGroup] = {
    BodyLocation.HEAD: BodyLocationGroup.HEAD_GROUP,
    BodyLocation.NECK: BodyLocationGroup.HEAD_GROUP,
    BodyLocation.CHEST: BodyLocationGroup.TORSO_GROUP,
    BodyLocation.ABDOMEN: BodyLocationGroup.TORSO_GROUP,
    BodyLocation.BACK: BodyLocationGroup.TORSO_GROUP,
    BodyLocation.LEFT_SHOULDER: BodyLocationGroup.ARM_GROUP,
    BodyLocation.RIGHT_SHOULDER: BodyLocationGroup.ARM_GROUP,
    BodyLocation.LEFT_ARM: BodyLocationGroup.ARM_GROUP,
    BodyLocation.RIGHT_ARM: BodyLocationGroup.ARM_GROUP,
    BodyLocation.LEFT_HAND: BodyLocationGroup.HAND_GROUP,
    BodyLocation.RIGHT_HAND: BodyLocationGroup.HAND_GROUP,
    BodyLocation.LEFT_THIGH: BodyLocationGroup.LEG_GROUP,
    BodyLocation.RIGHT_THIGH: BodyLocationGroup.LEG_GROUP,
    BodyLocation.LEFT_LEG: BodyLocationGroup.LEG_GROUP,
    BodyLocation.RIGHT_LEG: BodyLocationGroup.LEG_GROUP,
    BodyLocation.LEFT_FOOT: BodyLocationGroup.FOOT_GROUP,
    BodyLocation.RIGHT_FOOT: BodyLocationGroup.FOOT_GROUP,
}

COARSE_LOCATION_BY_GROUP: dict[BodyLocationGroup, str] = {
    BodyLocationGroup.HEAD_GROUP: "glowa",
    BodyLocationGroup.TORSO_GROUP: "korpus",
    BodyLocationGroup.ARM_GROUP: "prawa_reka",
    BodyLocationGroup.HAND_GROUP: "prawa_reka",
    BodyLocationGroup.LEG_GROUP: "prawa_noga",
    BodyLocationGroup.FOOT_GROUP: "prawa_noga",
}

BODY_LOCATION_LABELS: dict[BodyLocation, str] = {
    BodyLocation.HEAD: "głowę",
    BodyLocation.NECK: "szyję",
    BodyLocation.CHEST: "klatkę piersiową",
    BodyLocation.ABDOMEN: "brzuch",
    BodyLocation.BACK: "plecy",
    BodyLocation.LEFT_SHOULDER: "lewy bark",
    BodyLocation.RIGHT_SHOULDER: "prawy bark",
    BodyLocation.LEFT_ARM: "lewe ramię",
    BodyLocation.RIGHT_ARM: "prawe ramię",
    BodyLocation.LEFT_HAND: "lewą dłoń",
    BodyLocation.RIGHT_HAND: "prawą dłoń",
    BodyLocation.LEFT_THIGH: "lewe udo",
    BodyLocation.RIGHT_THIGH: "prawe udo",
    BodyLocation.LEFT_LEG: "lewą nogę",
    BodyLocation.RIGHT_LEG: "prawą nogę",
    BodyLocation.LEFT_FOOT: "lewą stopę",
    BodyLocation.RIGHT_FOOT: "prawą stopę",
}

ATTACK_TYPE_LABELS: dict[AttackType, str] = {
    AttackType.SLASH: "cięcie",
    AttackType.THRUST: "pchnięcie",
    AttackType.OVERHEAD: "cios znad głowy",
    AttackType.SWEEP: "zamach",
    AttackType.BLUNT_STRIKE: "cios obuchowy",
    AttackType.STANDARD: "atak",
}


def _coerce_body_location(value: object, default: BodyLocation = BodyLocation.CHEST) -> BodyLocation:
    try:
        return BodyLocation(str(value))
    except ValueError as exc:
        raise ValueError(f"Nieznana lokalizacja ciała: {value}") from exc


def _coerce_body_location_group(value: object, default: BodyLocationGroup = BodyLocationGroup.TORSO_GROUP) -> BodyLocationGroup:
    try:
        return BodyLocationGroup(str(value))
    except ValueError as exc:
        raise ValueError(f"Nieznana grupa lokalizacji ciała: {value}") from exc


def _coerce_attack_type(value: object) -> AttackType:
    try:
        return AttackType(str(value))
    except ValueError as exc:
        raise ValueError(f"Nieznany typ ataku: {value}") from exc


def _coerce_hit_quality(value: object) -> HitQuality:
    try:
        return HitQuality(str(value))
    except ValueError as exc:
        raise ValueError(f"Nieznana jakość trafienia: {value}") from exc


def _coerce_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            return float(text)
        except ValueError:
            return default
    return default


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            return int(text)
        except ValueError:
            return default
    return default


def _stable_roll(rng: object, salt: str, counter_attr: str) -> float:
    random_fn = getattr(rng, "random", None)
    if not callable(random_fn):
        return 0.5
    if hasattr(rng, "getstate") and hasattr(rng, "setstate"):
        counter = int(getattr(rng, counter_attr, 0) or 0)
        try:
            state = rng.getstate()
        except Exception:
            return float(random_fn())
        setattr(rng, counter_attr, counter + 1)
        payload = f"{repr(state)}|{salt}|{counter}".encode("utf-8")
        seed = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")
        return random.Random(seed).random()
    return float(random_fn())


def body_location_label(location: BodyLocation | str | None) -> str:
    if location is None:
        return "ciało"
    try:
        resolved = BodyLocation(str(location))
    except ValueError:
        return str(location)
    return BODY_LOCATION_LABELS.get(resolved, str(resolved).lower())


def body_location_group_label(group: BodyLocationGroup | str | None) -> str:
    if group is None:
        return "obrońca"
    try:
        resolved = BodyLocationGroup(str(group))
    except ValueError:
        return str(group)
    return resolved.value.lower().replace("_group", "").replace("_", " ")


def attack_type_label(attack_type: AttackType | str | None) -> str:
    if attack_type is None:
        return "atak"
    try:
        resolved = AttackType(str(attack_type))
    except ValueError:
        return str(attack_type)
    return ATTACK_TYPE_LABELS.get(resolved, resolved.value.lower())


def coarse_location_for_group(group: BodyLocationGroup) -> str:
    return COARSE_LOCATION_BY_GROUP[group]


def legacy_body_part_for_location(location: BodyLocation | str | None) -> str:
    if location is None:
        return "korpus"
    try:
        resolved = BodyLocation(str(location))
    except ValueError:
        return str(location)
    if resolved in {BodyLocation.HEAD, BodyLocation.NECK}:
        return "glowa"
    if resolved in {BodyLocation.CHEST, BodyLocation.ABDOMEN, BodyLocation.BACK}:
        return "korpus"
    if resolved in {
        BodyLocation.LEFT_SHOULDER,
        BodyLocation.LEFT_ARM,
        BodyLocation.LEFT_HAND,
    }:
        return "lewa_reka"
    if resolved in {
        BodyLocation.RIGHT_SHOULDER,
        BodyLocation.RIGHT_ARM,
        BodyLocation.RIGHT_HAND,
    }:
        return "prawa_reka"
    if resolved in {
        BodyLocation.LEFT_THIGH,
        BodyLocation.LEFT_LEG,
        BodyLocation.LEFT_FOOT,
    }:
        return "lewa_noga"
    if resolved in {
        BodyLocation.RIGHT_THIGH,
        BodyLocation.RIGHT_LEG,
        BodyLocation.RIGHT_FOOT,
    }:
        return "prawa_noga"
    return "korpus"


def quality_for_margin(hit_score: int, dodge_score: int) -> HitQuality:
    margin = hit_score - dodge_score
    if margin <= 3:
        return HitQuality.GLANCING
    if margin <= 9:
        return HitQuality.CLEAN
    if margin <= 16:
        return HitQuality.POWERFUL
    return HitQuality.DEVASTATING


def attack_type_for_weapon(weapon: "Item | None", profile: WeaponProfile | None = None) -> AttackType:
    if weapon is None or getattr(weapon, "durability", 0) <= 0:
        return AttackType.STANDARD
    damage_type = str(getattr(weapon, "damage_type", "") or "").strip().casefold()
    weapon_type = str(getattr(weapon, "weapon_type", "") or "").strip().casefold()
    profile = profile or load_default_weapon_profile_catalog().resolve(weapon)
    profile_damage_types = tuple(profile.damage_types) if profile is not None else ()
    if damage_type in {"cieta", "cięta", "slash"}:
        return AttackType.SLASH
    if damage_type in {"kluta", "thrust"}:
        return AttackType.THRUST
    if damage_type in {"obuchowa", "blunt"}:
        if profile is not None and profile.weapon_class.value == "POLEARM" and "hooked" in profile.tags:
            return AttackType.OVERHEAD
        return AttackType.BLUNT_STRIKE
    if damage_type in {"pociskowa", "projectile"}:
        return AttackType.STANDARD
    if profile_damage_types:
        if DamageType.THRUST in profile_damage_types:
            return AttackType.THRUST
        if DamageType.SLASH in profile_damage_types:
            if profile is not None and "hooked" in profile.tags:
                return AttackType.OVERHEAD
            return AttackType.SLASH
        if DamageType.BLUNT in profile_damage_types:
            if profile is not None and "flexible" in profile.tags:
                return AttackType.SWEEP
            return AttackType.BLUNT_STRIKE
    if profile is not None:
        if "hooked" in profile.tags or (profile.weapon_class.value == "POLEARM" and profile.hand_requirement == HandRequirement.TWO_HANDED):
            return AttackType.OVERHEAD
        if "flexible" in profile.tags:
            return AttackType.SWEEP
        if "blunt" in profile.tags:
            return AttackType.BLUNT_STRIKE
        if "pointed" in profile.tags:
            return AttackType.THRUST
        if "blade" in profile.tags:
            return AttackType.SLASH
    if weapon_type in {"młot", "mlot", "buława", "bulawa", "mace", "hammer"}:
        return AttackType.BLUNT_STRIKE
    if weapon_type in {"włócznia", "wlocznia", "spear", "halabarda", "halberd"}:
        return AttackType.THRUST
    if weapon_type in {"cep", "flail"}:
        return AttackType.SWEEP
    return AttackType.STANDARD


@dataclass(frozen=True, slots=True)
class HitLocationOutcome:
    location: BodyLocation
    location_group: BodyLocationGroup
    base_weight: float
    weapon_weight_modifier: float
    quality_modifier: float
    attack_type_modifier: float
    final_weight: float
    reason_code: str

    def to_dict(self) -> dict[str, object]:
        return {
            "location": self.location.value,
            "location_group": self.location_group.value,
            "base_weight": self.base_weight,
            "weapon_weight_modifier": self.weapon_weight_modifier,
            "quality_modifier": self.quality_modifier,
            "attack_type_modifier": self.attack_type_modifier,
            "final_weight": self.final_weight,
            "reason_code": self.reason_code,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "HitLocationOutcome":
        return cls(
            location=BodyLocation(str(data.get("location", BodyLocation.CHEST.value))),
            location_group=BodyLocationGroup(str(data.get("location_group", BodyLocationGroup.TORSO_GROUP.value))),
            base_weight=_coerce_float(data.get("base_weight", 0.0)),
            weapon_weight_modifier=_coerce_float(data.get("weapon_weight_modifier", 1.0)),
            quality_modifier=_coerce_float(data.get("quality_modifier", 1.0)),
            attack_type_modifier=_coerce_float(data.get("attack_type_modifier", 1.0)),
            final_weight=_coerce_float(data.get("final_weight", 0.0)),
            reason_code=str(data.get("reason_code", "")),
        )


@dataclass(frozen=True, slots=True)
class ArmorLayerSnapshot:
    item_id: str
    profile_id: str | None
    material: str
    armor_category: str
    coverage_fraction: float
    layer_order: int
    condition: float
    location: BodyLocation

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "profile_id": self.profile_id,
            "material": self.material,
            "armor_category": self.armor_category,
            "coverage_fraction": self.coverage_fraction,
            "layer_order": self.layer_order,
            "condition": self.condition,
            "location": self.location.value,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ArmorLayerSnapshot":
        return cls(
            item_id=str(data.get("item_id", "")),
            profile_id=str(data["profile_id"]) if data.get("profile_id") not in {None, ""} else None,
            material=str(data.get("material", "unknown")),
            armor_category=str(data.get("armor_category", "unknown")),
            coverage_fraction=_coerce_float(data.get("coverage_fraction", 0.0)),
            layer_order=_coerce_int(data.get("layer_order", 0)),
            condition=_coerce_float(data.get("condition", 0.0)),
            location=BodyLocation(str(data.get("location", BodyLocation.CHEST.value))),
        )


@dataclass(frozen=True, slots=True)
class ArmorCoverageOutcome:
    body_location: BodyLocation
    covering_layers: tuple[ArmorLayerSnapshot, ...]
    fully_unarmored: bool
    partial_coverage: bool
    total_coverage_indicator: float

    def to_dict(self) -> dict[str, object]:
        return {
            "body_location": self.body_location.value,
            "covering_layers": [layer.to_dict() for layer in self.covering_layers],
            "fully_unarmored": self.fully_unarmored,
            "partial_coverage": self.partial_coverage,
            "total_coverage_indicator": self.total_coverage_indicator,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ArmorCoverageOutcome":
        layers_raw = data.get("covering_layers", ())
        layers = tuple(
            ArmorLayerSnapshot.from_dict(layer)
            for layer in layers_raw
            if isinstance(layer, Mapping)
        ) if isinstance(layers_raw, list) else ()
        return cls(
            body_location=BodyLocation(str(data.get("body_location", BodyLocation.CHEST.value))),
            covering_layers=layers,
            fully_unarmored=bool(data.get("fully_unarmored", False)),
            partial_coverage=bool(data.get("partial_coverage", False)),
            total_coverage_indicator=_coerce_float(data.get("total_coverage_indicator", 0.0)),
        )


@dataclass(frozen=True, slots=True)
class HitLocationRule:
    location: BodyLocation
    group: BodyLocationGroup
    base_weight: float
    attack_modifiers: Mapping[AttackType, float] = field(default_factory=dict)
    quality_modifiers: Mapping[HitQuality, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ArmorCoverageProfile:
    profile_id: str
    name: str
    armor_material: str
    armor_category: str
    layer_order: int
    coverage_fraction: float
    location_fractions: Mapping[BodyLocation, float] = field(default_factory=dict)
    kind: str = "armor"
    enabled: bool = True
    legacy: bool = False

    def fraction_for(self, location: BodyLocation) -> float:
        return float(self.location_fractions.get(location, 0.0))

    def covers(self, location: BodyLocation) -> bool:
        return self.fraction_for(location) > 0.0


@dataclass(frozen=True, slots=True)
class HitLocationCatalog:
    rules: tuple[HitLocationRule, ...]
    rules_by_location: Mapping[BodyLocation, HitLocationRule] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_location: dict[BodyLocation, HitLocationRule] = {}
        for rule in self.rules:
            if rule.location in by_location:
                raise ValueError(f"Zduplikowana lokalizacja trafienia: {rule.location}")
            by_location[rule.location] = rule
        object.__setattr__(self, "rules", tuple(self.rules))
        object.__setattr__(self, "rules_by_location", MappingProxyType(by_location))

    @classmethod
    def from_json(cls, path: str | Path) -> "HitLocationCatalog":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Katalog lokalizacji trafień musi być listą.")
        rules: list[HitLocationRule] = []
        for entry in raw:
            if not isinstance(entry, Mapping):
                raise ValueError("Każda lokalizacja trafienia musi być obiektem JSON.")
            location = _coerce_body_location(entry.get("location", BodyLocation.CHEST.value))
            group = _coerce_body_location_group(entry.get("group", BodyLocationGroup.TORSO_GROUP.value))
            base_weight = float(entry.get("base_weight", 0.0))
            attack_modifiers_raw = entry.get("attack_modifiers", {})
            quality_modifiers_raw = entry.get("quality_modifiers", {})
            if not isinstance(attack_modifiers_raw, Mapping) or not isinstance(quality_modifiers_raw, Mapping):
                raise ValueError("Modyfikatory lokalizacji trafień muszą być obiektami JSON.")
            attack_modifiers = {
                _coerce_attack_type(key): float(value)
                for key, value in attack_modifiers_raw.items()
            }
            quality_modifiers = {
                _coerce_hit_quality(key): float(value)
                for key, value in quality_modifiers_raw.items()
            }
            rules.append(
                HitLocationRule(
                    location=location,
                    group=group,
                    base_weight=base_weight,
                    attack_modifiers=MappingProxyType(attack_modifiers),
                    quality_modifiers=MappingProxyType(quality_modifiers),
                )
            )
        return cls(tuple(rules))

    def rule_for(self, location: BodyLocation) -> HitLocationRule:
        return self.rules_by_location[location]

    def resolve(self, weapon_profile: WeaponProfile | None, action: CombatAction, hit_quality: HitQuality, attacker_state: object, target_state: object, rng: object, attack_type: AttackType | None = None) -> HitLocationOutcome:
        del attacker_state, target_state
        attack_type = attack_type or AttackType.STANDARD
        rules = self.rules
        weighted: list[tuple[HitLocationRule, float, float, float, float]] = []
        total = 0.0
        for rule in rules:
            attack_modifier = rule.attack_modifiers.get(attack_type, rule.attack_modifiers.get(AttackType.STANDARD, 1.0))
            quality_modifier = rule.quality_modifiers.get(hit_quality, rule.quality_modifiers.get(HitQuality.CLEAN, 1.0))
            weapon_modifier = _weapon_weight_modifier(weapon_profile, attack_type)
            final_weight = max(0.0, rule.base_weight * attack_modifier * quality_modifier * weapon_modifier)
            total += final_weight
            weighted.append((rule, final_weight, weapon_modifier, quality_modifier, attack_modifier))
        if total <= 0:
            first = rules[0]
            return HitLocationOutcome(
                location=first.location,
                location_group=first.group,
                base_weight=first.base_weight,
                weapon_weight_modifier=1.0,
                quality_modifier=1.0,
                attack_type_modifier=1.0,
                final_weight=1.0,
                reason_code="FALLBACK",
            )
        random_fn = getattr(rng, "random", None)
        threshold = float(random_fn()) if callable(random_fn) else 0.5
        cumulative = 0.0
        chosen_rule = rules[-1]
        chosen_weight = weighted[-1][1]
        chosen_weapon_modifier = weighted[-1][2]
        chosen_quality_modifier = weighted[-1][3]
        chosen_attack_modifier = weighted[-1][4]
        for rule, final_weight, weapon_modifier, quality_modifier, attack_modifier in weighted:
            cumulative += final_weight / total
            if threshold <= cumulative:
                chosen_rule = rule
                chosen_weight = final_weight
                chosen_weapon_modifier = weapon_modifier
                chosen_quality_modifier = quality_modifier
                chosen_attack_modifier = attack_modifier
                break
        return HitLocationOutcome(
            location=chosen_rule.location,
            location_group=chosen_rule.group,
            base_weight=chosen_rule.base_weight,
            weapon_weight_modifier=chosen_weapon_modifier,
            quality_modifier=chosen_quality_modifier,
            attack_type_modifier=chosen_attack_modifier,
            final_weight=chosen_weight,
            reason_code="OK",
        )


@dataclass(frozen=True, slots=True)
class ArmorCoverageCatalog:
    profiles: tuple[ArmorCoverageProfile, ...]
    profiles_by_id: Mapping[str, ArmorCoverageProfile] = field(init=False, repr=False, compare=False)
    legacy_profiles_by_slot: Mapping[str, ArmorCoverageProfile] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_id: dict[str, ArmorCoverageProfile] = {}
        for profile in self.profiles:
            key = profile.profile_id.casefold()
            if key in by_id:
                raise ValueError(f"Zduplikowany profil pokrycia pancerza: {profile.profile_id}")
            by_id[key] = profile
        legacy_profiles = {
            "glowa": ArmorCoverageProfile("legacy_head", "legacy head", "unknown", "helmet", 30, 1.0, {BodyLocation.HEAD: 1.0, BodyLocation.NECK: 0.5}, kind="armor", legacy=True),
            "szyja": ArmorCoverageProfile("legacy_neck", "legacy neck", "unknown", "gorget", 30, 1.0, {BodyLocation.NECK: 1.0, BodyLocation.HEAD: 0.2}, kind="armor", legacy=True),
            "korpus": ArmorCoverageProfile("legacy_torso", "legacy torso", "unknown", "body_armor", 20, 1.0, {
                BodyLocation.CHEST: 1.0,
                BodyLocation.ABDOMEN: 1.0,
                BodyLocation.BACK: 1.0,
                BodyLocation.LEFT_SHOULDER: 0.6,
                BodyLocation.RIGHT_SHOULDER: 0.6,
                BodyLocation.LEFT_ARM: 0.35,
                BodyLocation.RIGHT_ARM: 0.35,
                BodyLocation.LEFT_THIGH: 0.2,
                BodyLocation.RIGHT_THIGH: 0.2,
            }, kind="armor", legacy=True),
            "plecy": ArmorCoverageProfile("legacy_back", "legacy back", "unknown", "cloak", 10, 1.0, {BodyLocation.BACK: 1.0, BodyLocation.LEFT_SHOULDER: 0.4, BodyLocation.RIGHT_SHOULDER: 0.4}, kind="armor", legacy=True),
            "rece": ArmorCoverageProfile("legacy_arms", "legacy arms", "unknown", "sleeves", 15, 1.0, {BodyLocation.LEFT_ARM: 1.0, BodyLocation.RIGHT_ARM: 1.0, BodyLocation.LEFT_HAND: 0.3, BodyLocation.RIGHT_HAND: 0.3}, kind="armor", legacy=True),
            "dlonie": ArmorCoverageProfile("legacy_hands", "legacy hands", "unknown", "gloves", 15, 1.0, {BodyLocation.LEFT_HAND: 1.0, BodyLocation.RIGHT_HAND: 1.0}, kind="armor", legacy=True),
            "nogi": ArmorCoverageProfile("legacy_legs", "legacy legs", "unknown", "greaves", 15, 1.0, {BodyLocation.LEFT_THIGH: 1.0, BodyLocation.RIGHT_THIGH: 1.0, BodyLocation.LEFT_LEG: 1.0, BodyLocation.RIGHT_LEG: 1.0}, kind="armor", legacy=True),
            "stopy": ArmorCoverageProfile("legacy_feet", "legacy feet", "unknown", "boots", 15, 1.0, {BodyLocation.LEFT_FOOT: 1.0, BodyLocation.RIGHT_FOOT: 1.0}, kind="armor", legacy=True),
            "tarcza": ArmorCoverageProfile("legacy_shield", "legacy shield", "unknown", "shield", 100, 1.0, {
                BodyLocation.LEFT_SHOULDER: 0.7,
                BodyLocation.LEFT_ARM: 1.0,
                BodyLocation.LEFT_HAND: 0.8,
                BodyLocation.CHEST: 0.35,
                BodyLocation.ABDOMEN: 0.25,
                BodyLocation.BACK: 0.15,
            }, kind="shield", legacy=True),
        }
        object.__setattr__(self, "profiles", tuple(self.profiles))
        object.__setattr__(self, "profiles_by_id", MappingProxyType(by_id))
        object.__setattr__(self, "legacy_profiles_by_slot", MappingProxyType(legacy_profiles))

    @classmethod
    def from_json(cls, path: str | Path) -> "ArmorCoverageCatalog":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Katalog pokryć pancerza musi być listą.")
        profiles: list[ArmorCoverageProfile] = []
        for entry in raw:
            if not isinstance(entry, Mapping):
                raise ValueError("Każdy profil pokrycia pancerza musi być obiektem JSON.")
            location_fractions_raw = entry.get("location_fractions", {})
            if not isinstance(location_fractions_raw, Mapping):
                raise ValueError("location_fractions musi być obiektem JSON.")
            location_fractions = {
                _coerce_body_location(key): float(value)
                for key, value in location_fractions_raw.items()
            }
            for location, fraction in location_fractions.items():
                if fraction < 0.0 or fraction > 1.0:
                    raise ValueError(f"Nieprawidłowa wartość pokrycia dla {location.value}: {fraction}")
            profiles.append(
                ArmorCoverageProfile(
                    profile_id=str(entry["profile_id"]),
                    name=str(entry["name"]),
                    armor_material=str(entry.get("armor_material", "unknown")),
                    armor_category=str(entry.get("armor_category", "unknown")),
                    layer_order=int(entry.get("layer_order", 0)),
                    coverage_fraction=float(entry.get("coverage_fraction", 0.0)),
                    location_fractions=MappingProxyType(location_fractions),
                    kind=str(entry.get("kind", "armor")),
                    enabled=bool(entry.get("enabled", True)),
                    legacy=bool(entry.get("legacy", False)),
                )
            )
        return cls(tuple(profiles))

    def resolve(self, item: "Item | None") -> ArmorCoverageProfile | None:
        if item is None or getattr(item, "durability", 0) <= 0:
            return None
        profile_id = getattr(item, "armor_profile_id", None)
        if profile_id is None and getattr(item, "shield_profile_id", None) is not None:
            profile_id = getattr(item, "shield_profile_id", None)
        if profile_id is not None:
            profile = self.profiles_by_id.get(str(profile_id).casefold())
            if profile is not None:
                return profile
        slot = str(getattr(item, "slot", "") or "").strip().casefold()
        return self.legacy_profiles_by_slot.get(slot)


def _weapon_weight_modifier(profile: WeaponProfile | None, attack_type: AttackType) -> float:
    if profile is None or profile.legacy:
        return 1.0
    modifier = 1.0
    if "reach" in profile.tags and attack_type in {AttackType.THRUST, AttackType.OVERHEAD}:
        modifier *= 1.05
    if "flexible" in profile.tags:
        modifier *= 0.95
    if attack_type == AttackType.BLUNT_STRIKE and "blunt" in profile.tags:
        modifier *= 1.02
    return modifier


def _default_hit_location_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "hit_locations.json"


def _default_armor_coverage_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "armor_coverage_profiles.json"


@lru_cache(maxsize=1)
def load_default_hit_location_catalog() -> HitLocationCatalog:
    return HitLocationCatalog.from_json(_default_hit_location_catalog_path())


@lru_cache(maxsize=1)
def load_default_armor_coverage_catalog() -> ArmorCoverageCatalog:
    return ArmorCoverageCatalog.from_json(_default_armor_coverage_catalog_path())


def resolve_hit_location(
    weapon_profile: WeaponProfile | None,
    action: CombatAction,
    hit_quality: HitQuality,
    attacker_state: object,
    target_state: object,
    rng: object,
    attack_type: AttackType | None = None,
) -> HitLocationOutcome:
    del attacker_state, target_state
    catalog = load_default_hit_location_catalog()
    attack_type = attack_type or AttackType.STANDARD
    weighted: list[tuple[HitLocationRule, float]] = []
    total = 0.0
    for rule in catalog.rules:
        attack_modifier = rule.attack_modifiers.get(attack_type, rule.attack_modifiers.get(AttackType.STANDARD, 1.0))
        quality_modifier = rule.quality_modifiers.get(hit_quality, rule.quality_modifiers.get(HitQuality.CLEAN, 1.0))
        weapon_modifier = _weapon_weight_modifier(weapon_profile, attack_type)
        final_weight = max(0.0, rule.base_weight * attack_modifier * quality_modifier * weapon_modifier)
        total += final_weight
        weighted.append((rule, final_weight))
    if total <= 0:
        first = catalog.rules[0]
        return HitLocationOutcome(
            location=first.location,
            location_group=first.group,
            base_weight=first.base_weight,
            weapon_weight_modifier=_weapon_weight_modifier(weapon_profile, attack_type),
            quality_modifier=first.quality_modifiers.get(hit_quality, first.quality_modifiers.get(HitQuality.CLEAN, 1.0)),
            attack_type_modifier=first.attack_modifiers.get(attack_type, first.attack_modifiers.get(AttackType.STANDARD, 1.0)),
            final_weight=1.0,
            reason_code="FALLBACK",
        )
    threshold = _stable_roll(rng, f"{attack_type.value}:{hit_quality.value}", "_hit_location_roll")
    cumulative = 0.0
    chosen = catalog.rules[-1]
    chosen_weight = weighted[-1][1]
    chosen_weapon_modifier = _weapon_weight_modifier(weapon_profile, attack_type)
    chosen_quality_modifier = chosen.quality_modifiers.get(hit_quality, chosen.quality_modifiers.get(HitQuality.CLEAN, 1.0))
    chosen_attack_modifier = chosen.attack_modifiers.get(attack_type, chosen.attack_modifiers.get(AttackType.STANDARD, 1.0))
    for rule, final_weight in weighted:
        cumulative += final_weight / total
        if threshold <= cumulative:
            chosen = rule
            chosen_weight = final_weight
            chosen_weapon_modifier = _weapon_weight_modifier(weapon_profile, attack_type)
            chosen_quality_modifier = rule.quality_modifiers.get(hit_quality, rule.quality_modifiers.get(HitQuality.CLEAN, 1.0))
            chosen_attack_modifier = rule.attack_modifiers.get(attack_type, rule.attack_modifiers.get(AttackType.STANDARD, 1.0))
            break
    return HitLocationOutcome(
        location=chosen.location,
        location_group=chosen.group,
        base_weight=chosen.base_weight,
        weapon_weight_modifier=chosen_weapon_modifier,
        quality_modifier=chosen_quality_modifier,
        attack_type_modifier=chosen_attack_modifier,
        final_weight=chosen_weight,
        reason_code="OK",
    )


def resolve_armor_coverage(target: "Character", location: BodyLocation, rng: object, catalog: ArmorCoverageCatalog | None = None) -> ArmorCoverageOutcome:
    active_catalog = catalog or load_default_armor_coverage_catalog()
    equipped_items = [item for item in target.armor_items() if item is not None and item.durability > 0]
    if not equipped_items:
        return ArmorCoverageOutcome(
            body_location=location,
            covering_layers=(),
            fully_unarmored=True,
            partial_coverage=False,
            total_coverage_indicator=0.0,
        )
    layers: list[ArmorLayerSnapshot] = []
    total_indicator = 0.0
    partial = False
    for item in equipped_items:
        profile = active_catalog.resolve(item)
        if profile is None:
            continue
        fraction = profile.fraction_for(location)
        if fraction <= 0:
            continue
        partial = partial or fraction < 1.0
        apply_layer = fraction >= 1.0
        if not apply_layer:
            roll = _stable_roll(rng, f"{location.value}:{item.id}", "_armor_coverage_roll")
            apply_layer = roll < fraction
        if not apply_layer:
            continue
        layers.append(
            ArmorLayerSnapshot(
                item_id=item.id,
                profile_id=profile.profile_id,
                material=profile.armor_material,
                armor_category=profile.armor_category,
                coverage_fraction=fraction,
                layer_order=profile.layer_order,
                condition=0.0 if item.max_durability <= 0 else max(0.0, min(1.0, item.durability / item.max_durability)),
                location=location,
            )
        )
        total_indicator = 1.0 - (1.0 - total_indicator) * (1.0 - fraction)
    layers.sort(key=lambda layer: (-layer.layer_order, layer.profile_id or "", layer.item_id))
    return ArmorCoverageOutcome(
        body_location=location,
        covering_layers=tuple(layers),
        fully_unarmored=not layers,
        partial_coverage=partial,
        total_coverage_indicator=max(0.0, min(1.0, total_indicator)),
    )

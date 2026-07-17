from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from astergard.combat.hit_locations import (
    ArmorCoverageOutcome,
    ArmorLayerSnapshot,
    AttackType,
    BodyLocation,
    BodyLocationGroup,
    HitQuality,
    legacy_body_part_for_location,
)

if TYPE_CHECKING:
    from astergard.characters.models import Character
    from astergard.items.models import Item
    from astergard.combat.weapons import WeaponProfile


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _float_or_default(value: object, default: float = 0.0) -> float:
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


def _int_or_default(value: object, default: int = 0) -> int:
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


class DamageChannel(StrEnum):
    IMPACT = "IMPACT"
    CUTTING = "CUTTING"
    PIERCING = "PIERCING"


class WoundSeverity(StrEnum):
    NO_INJURY = "NO_INJURY"
    SCRATCH = "SCRATCH"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SERIOUS = "SERIOUS"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class CriticalCondition(StrEnum):
    VITAL_LOCATION = "VITAL_LOCATION"
    ARMOR_BYPASSED = "ARMOR_BYPASSED"
    MASSIVE_PENETRATION = "MASSIVE_PENETRATION"
    MASSIVE_IMPACT = "MASSIVE_IMPACT"
    SEVERE_CUT = "SEVERE_CUT"
    COMBINED_TRAUMA = "COMBINED_TRAUMA"


@dataclass(frozen=True, slots=True)
class WeaponDamageProfile:
    weapon_profile_id: str | None
    weapon_name: str
    attack_type: AttackType
    base_impact: float
    base_cutting: float
    base_piercing: float
    armor_penetration: float
    mass_factor: float
    strength_scaling: float
    quality_scaling: float
    tags: tuple[str, ...] = ()
    base_damage: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "WeaponDamageProfile":
        attack_type_raw = data.get("attack_type", AttackType.STANDARD.value)
        weapon_profile_id_raw = data.get("weapon_profile_id")
        tags_raw = data.get("tags", ())
        return cls(
            weapon_profile_id=str(weapon_profile_id_raw) if weapon_profile_id_raw not in {None, ""} else None,
            weapon_name=str(data.get("weapon_name", "goła ręka")),
            attack_type=AttackType(str(attack_type_raw)),
            base_impact=_float_or_default(data.get("base_impact", 0.0)),
            base_cutting=_float_or_default(data.get("base_cutting", 0.0)),
            base_piercing=_float_or_default(data.get("base_piercing", 0.0)),
            armor_penetration=_float_or_default(data.get("armor_penetration", 1.0), 1.0),
            mass_factor=_float_or_default(data.get("mass_factor", 1.0), 1.0),
            strength_scaling=_float_or_default(data.get("strength_scaling", 1.0), 1.0),
            quality_scaling=_float_or_default(data.get("quality_scaling", 1.0), 1.0),
            tags=tuple(str(tag) for tag in tags_raw if isinstance(tag, str)) if isinstance(tags_raw, (list, tuple)) else (),
            base_damage=_float_or_default(data.get("base_damage", 0.0)),
        )


@dataclass(frozen=True, slots=True)
class ArmorResistanceProfile:
    impact_absorption: float
    cutting_resistance: float
    piercing_resistance: float
    rigidity: float


@dataclass(frozen=True, slots=True)
class AttackPhysicalOutcome:
    action_id: str
    body_location: BodyLocation
    body_location_group: BodyLocationGroup
    hit_quality: HitQuality
    weapon_profile_id: str | None
    attack_type: AttackType
    weapon_damage_profile: WeaponDamageProfile
    armor_layers: tuple[ArmorLayerSnapshot, ...]
    base_impact: float
    effective_impact: float
    base_cutting: float
    effective_cutting: float
    base_piercing: float
    effective_piercing: float
    absorbed_impact: float
    blocked_cutting: float
    blocked_piercing: float
    remaining_impact: float
    remaining_cutting: float
    remaining_piercing: float
    penetration_margin: float
    severity_score: float
    critical_condition: CriticalCondition | None
    severity: WoundSeverity
    final_damage: int
    reason_code: str

    def to_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "body_location": self.body_location.value,
            "body_location_group": self.body_location_group.value,
            "hit_quality": self.hit_quality.value,
            "weapon_profile_id": self.weapon_profile_id,
            "attack_type": self.attack_type.value,
            "weapon_damage_profile": {
                "weapon_profile_id": self.weapon_damage_profile.weapon_profile_id,
                "weapon_name": self.weapon_damage_profile.weapon_name,
                "attack_type": self.weapon_damage_profile.attack_type.value,
                "base_impact": self.weapon_damage_profile.base_impact,
                "base_cutting": self.weapon_damage_profile.base_cutting,
                "base_piercing": self.weapon_damage_profile.base_piercing,
                "armor_penetration": self.weapon_damage_profile.armor_penetration,
                "mass_factor": self.weapon_damage_profile.mass_factor,
                "strength_scaling": self.weapon_damage_profile.strength_scaling,
                "quality_scaling": self.weapon_damage_profile.quality_scaling,
                "tags": list(self.weapon_damage_profile.tags),
                "base_damage": self.weapon_damage_profile.base_damage,
            },
            "armor_layers": [layer.to_dict() for layer in self.armor_layers],
            "base_impact": self.base_impact,
            "effective_impact": self.effective_impact,
            "base_cutting": self.base_cutting,
            "effective_cutting": self.effective_cutting,
            "base_piercing": self.base_piercing,
            "effective_piercing": self.effective_piercing,
            "absorbed_impact": self.absorbed_impact,
            "blocked_cutting": self.blocked_cutting,
            "blocked_piercing": self.blocked_piercing,
            "remaining_impact": self.remaining_impact,
            "remaining_cutting": self.remaining_cutting,
            "remaining_piercing": self.remaining_piercing,
            "penetration_margin": self.penetration_margin,
            "severity_score": self.severity_score,
            "critical_condition": self.critical_condition.value if self.critical_condition is not None else None,
            "severity": self.severity.value,
            "final_damage": self.final_damage,
            "reason_code": self.reason_code,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AttackPhysicalOutcome":
        armor_layers_raw = data.get("armor_layers", ())
        weapon_damage_profile_raw = data.get("weapon_damage_profile", {})
        if not isinstance(weapon_damage_profile_raw, dict):
            weapon_damage_profile_raw = {}
        return cls(
            action_id=str(data.get("action_id", "")),
            body_location=BodyLocation(str(data.get("body_location", BodyLocation.CHEST.value))),
            body_location_group=BodyLocationGroup(str(data.get("body_location_group", BodyLocationGroup.TORSO_GROUP.value))),
            hit_quality=HitQuality(str(data.get("hit_quality", HitQuality.CLEAN.value))),
            weapon_profile_id=str(data.get("weapon_profile_id")) if data.get("weapon_profile_id") not in {None, ""} else None,
            attack_type=AttackType(str(data.get("attack_type", AttackType.STANDARD.value))),
            weapon_damage_profile=WeaponDamageProfile.from_dict(weapon_damage_profile_raw),
            armor_layers=tuple(
                ArmorLayerSnapshot.from_dict(layer)
                for layer in armor_layers_raw
                if isinstance(layer, dict)
            ) if isinstance(armor_layers_raw, list) else (),
            base_impact=_float_or_default(data.get("base_impact", 0.0)),
            effective_impact=_float_or_default(data.get("effective_impact", 0.0)),
            base_cutting=_float_or_default(data.get("base_cutting", 0.0)),
            effective_cutting=_float_or_default(data.get("effective_cutting", 0.0)),
            base_piercing=_float_or_default(data.get("base_piercing", 0.0)),
            effective_piercing=_float_or_default(data.get("effective_piercing", 0.0)),
            absorbed_impact=_float_or_default(data.get("absorbed_impact", 0.0)),
            blocked_cutting=_float_or_default(data.get("blocked_cutting", 0.0)),
            blocked_piercing=_float_or_default(data.get("blocked_piercing", 0.0)),
            remaining_impact=_float_or_default(data.get("remaining_impact", 0.0)),
            remaining_cutting=_float_or_default(data.get("remaining_cutting", 0.0)),
            remaining_piercing=_float_or_default(data.get("remaining_piercing", 0.0)),
            penetration_margin=_float_or_default(data.get("penetration_margin", 0.0)),
            severity_score=_float_or_default(data.get("severity_score", 0.0)),
            critical_condition=CriticalCondition(str(data.get("critical_condition"))) if data.get("critical_condition") not in {None, ""} else None,
            severity=WoundSeverity(str(data.get("severity", WoundSeverity.NO_INJURY.value))),
            final_damage=_int_or_default(data.get("final_damage", 0)),
            reason_code=str(data.get("reason_code", "")),
        )


@dataclass(frozen=True, slots=True)
class WoundOutcome:
    action_id: str
    source_body_location: BodyLocation
    legacy_body_part: str
    severity: WoundSeverity
    wound_level: int
    damage: int
    critical_condition: CriticalCondition | None
    lethal: bool
    reason_code: str

    def to_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "source_body_location": self.source_body_location.value,
            "legacy_body_part": self.legacy_body_part,
            "severity": self.severity.value,
            "wound_level": self.wound_level,
            "damage": self.damage,
            "critical_condition": self.critical_condition.value if self.critical_condition is not None else None,
            "lethal": self.lethal,
            "reason_code": self.reason_code,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "WoundOutcome":
        critical_raw = data.get("critical_condition")
        return cls(
            action_id=str(data.get("action_id", "")),
            source_body_location=BodyLocation(str(data.get("source_body_location", BodyLocation.CHEST.value))),
            legacy_body_part=str(data.get("legacy_body_part", "korpus")),
            severity=WoundSeverity(str(data.get("severity", WoundSeverity.NO_INJURY.value))),
            wound_level=_int_or_default(data.get("wound_level", 0)),
            damage=_int_or_default(data.get("damage", 0)),
            critical_condition=CriticalCondition(str(critical_raw)) if critical_raw not in {None, ""} else None,
            lethal=bool(data.get("lethal", False)),
            reason_code=str(data.get("reason_code", "")),
        )


_DEFAULT_WEAPON_TAG_WEIGHTS: dict[AttackType, tuple[float, float, float]] = {
    AttackType.SLASH: (0.28, 0.57, 0.15),
    AttackType.THRUST: (0.17, 0.10, 0.73),
    AttackType.OVERHEAD: (0.55, 0.33, 0.12),
    AttackType.SWEEP: (0.44, 0.46, 0.10),
    AttackType.BLUNT_STRIKE: (0.78, 0.11, 0.11),
    AttackType.STANDARD: (0.34, 0.40, 0.26),
}

_HEAVY_WEAPON_CLASS_BONUS = {
    "LIGHT": 0.92,
    "MEDIUM": 1.00,
    "HEAVY": 1.10,
    "POLEARM": 1.04,
}

_QUALITY_MODIFIERS = {
    HitQuality.GLANCING: (0.60, 0.56, 0.54, 0.88),
    HitQuality.CLEAN: (1.00, 1.00, 1.00, 1.00),
    HitQuality.POWERFUL: (1.14, 1.10, 1.08, 1.10),
    HitQuality.DEVASTATING: (1.28, 1.18, 1.14, 1.22),
}

_LOCATION_SEVERITY: dict[BodyLocation, float] = {
    BodyLocation.HEAD: 1.45,
    BodyLocation.NECK: 1.70,
    BodyLocation.CHEST: 1.20,
    BodyLocation.ABDOMEN: 1.15,
    BodyLocation.BACK: 1.08,
    BodyLocation.LEFT_SHOULDER: 0.92,
    BodyLocation.RIGHT_SHOULDER: 0.92,
    BodyLocation.LEFT_ARM: 0.78,
    BodyLocation.RIGHT_ARM: 0.78,
    BodyLocation.LEFT_HAND: 0.55,
    BodyLocation.RIGHT_HAND: 0.55,
    BodyLocation.LEFT_THIGH: 0.90,
    BodyLocation.RIGHT_THIGH: 0.90,
    BodyLocation.LEFT_LEG: 0.82,
    BodyLocation.RIGHT_LEG: 0.82,
    BodyLocation.LEFT_FOOT: 0.60,
    BodyLocation.RIGHT_FOOT: 0.60,
}

_ARMOR_RESISTANCE_BY_CATEGORY: dict[str, ArmorResistanceProfile] = {
    "helmet": ArmorResistanceProfile(0.42, 0.76, 0.68, 0.88),
    "gorget": ArmorResistanceProfile(0.35, 0.68, 0.60, 0.74),
    "body_armor": ArmorResistanceProfile(0.34, 0.70, 0.58, 0.82),
    "cloak": ArmorResistanceProfile(0.16, 0.22, 0.12, 0.18),
    "sleeves": ArmorResistanceProfile(0.18, 0.34, 0.22, 0.20),
    "gloves": ArmorResistanceProfile(0.12, 0.18, 0.14, 0.10),
    "greaves": ArmorResistanceProfile(0.28, 0.50, 0.40, 0.34),
    "boots": ArmorResistanceProfile(0.18, 0.30, 0.20, 0.22),
    "shield": ArmorResistanceProfile(0.58, 0.42, 0.38, 0.40),
    "unknown": ArmorResistanceProfile(0.24, 0.28, 0.22, 0.20),
}


def _quality_channel_multiplier(hit_quality: HitQuality) -> tuple[float, float, float, float]:
    return _QUALITY_MODIFIERS.get(hit_quality, _QUALITY_MODIFIERS[HitQuality.CLEAN])


def _location_multiplier(location: BodyLocation) -> float:
    return _LOCATION_SEVERITY.get(location, 1.0)


def _weapon_class_multiplier(weapon_profile: "WeaponProfile | None") -> float:
    if weapon_profile is None:
        return 1.0
    weapon_class = getattr(weapon_profile.weapon_class, "value", str(weapon_profile.weapon_class))
    return _HEAVY_WEAPON_CLASS_BONUS.get(str(weapon_class).upper(), 1.0)


def _attack_type_weights(attack_type: AttackType) -> tuple[float, float, float]:
    return _DEFAULT_WEAPON_TAG_WEIGHTS.get(attack_type, _DEFAULT_WEAPON_TAG_WEIGHTS[AttackType.STANDARD])


def _weapon_tag_adjustments(tags: tuple[str, ...]) -> tuple[float, float, float]:
    impact = 1.0
    cutting = 1.0
    piercing = 1.0
    if "blunt" in tags or "crushing" in tags:
        impact *= 1.15
        cutting *= 0.65
        piercing *= 0.80
    if "blade" in tags:
        cutting *= 1.10
    if "pointed" in tags:
        piercing *= 1.10
    if "shafted" in tags:
        impact *= 1.04
        piercing *= 1.03
    if "flexible" in tags:
        impact *= 0.92
        cutting *= 0.85
        piercing *= 0.90
    if "hooked" in tags:
        cutting *= 1.03
    if "armor_breaker" in tags:
        impact *= 1.06
        piercing *= 1.05
    return impact, cutting, piercing


def _weapon_strength_scaling(weapon_profile: "WeaponProfile | None", attacker: "Character | None") -> float:
    if attacker is None:
        return 1.0
    strength = getattr(getattr(attacker, "stats", None), "sila", 10)
    if weapon_profile is None:
        return _clamp(1.0 + (strength - 10) * 0.010, 0.85, 1.18)
    weapon_class = getattr(weapon_profile.weapon_class, "value", str(weapon_profile.weapon_class))
    bias = {
        "LIGHT": 0.45,
        "MEDIUM": 0.70,
        "HEAVY": 1.00,
        "POLEARM": 0.82,
    }.get(str(weapon_class).upper(), 0.65)
    return _clamp(1.0 + max(-0.20, min(0.24, (strength - 10) * 0.015 * bias)), 0.80, 1.24)


def _armor_resistance(layer: ArmorLayerSnapshot) -> ArmorResistanceProfile:
    category = (layer.armor_category or "").casefold().strip()
    material = (layer.material or "").casefold().strip()
    if category in _ARMOR_RESISTANCE_BY_CATEGORY:
        return _ARMOR_RESISTANCE_BY_CATEGORY[category]
    if material in _ARMOR_RESISTANCE_BY_CATEGORY:
        return _ARMOR_RESISTANCE_BY_CATEGORY[material]
    return _ARMOR_RESISTANCE_BY_CATEGORY["unknown"]


def weapon_damage_profile_for(
    weapon: "Item | None",
    weapon_profile: "WeaponProfile | None",
    attack_type: AttackType,
    attacker: "Character | None",
) -> WeaponDamageProfile:
    weapon_name = getattr(weapon, "display_name", lambda: "goła ręka")()
    base_damage = float(getattr(weapon, "base_damage", 0) if weapon is not None else 2.0)
    if base_damage <= 0:
        base_damage = 2.0
    class_multiplier = _weapon_class_multiplier(weapon_profile)
    mass_factor = _clamp(1.0 + max(0.0, float(getattr(weapon, "weight", 1.0)) - 1.0) * 0.08, 0.90, 1.30)
    weapon_tags = tuple(getattr(weapon_profile, "tags", ()) or ())
    attack_weights = list(_attack_type_weights(attack_type))
    tag_impact, tag_cutting, tag_piercing = _weapon_tag_adjustments(weapon_tags)
    attack_weights[0] *= tag_impact
    attack_weights[1] *= tag_cutting
    attack_weights[2] *= tag_piercing
    total_weights = sum(attack_weights) or 1.0
    normalized_weights = tuple(weight / total_weights for weight in attack_weights)
    weapon_strength = _weapon_strength_scaling(weapon_profile, attacker)
    base_total = base_damage * class_multiplier * mass_factor
    return WeaponDamageProfile(
        weapon_profile_id=getattr(weapon_profile, "id", None),
        weapon_name=weapon_name,
        attack_type=attack_type,
        base_impact=base_total * normalized_weights[0],
        base_cutting=base_total * normalized_weights[1],
        base_piercing=base_total * normalized_weights[2],
        armor_penetration=float(getattr(weapon_profile, "armor_penetration", 1.0) if weapon_profile is not None else 1.0),
        mass_factor=mass_factor,
        strength_scaling=weapon_strength,
        quality_scaling=1.0,
        tags=weapon_tags,
        base_damage=base_total,
    )


def _apply_layer(
    current_impact: float,
    current_cutting: float,
    current_piercing: float,
    layer: ArmorLayerSnapshot,
) -> tuple[float, float, float, float, float, float, float]:
    resistance = _armor_resistance(layer)
    condition_modifier = _clamp(layer.condition if layer.condition > 0 else 0.25, 0.25, 1.0)
    impact_absorbed = min(current_impact, current_impact * resistance.impact_absorption * condition_modifier)
    blocked_cutting = min(current_cutting, current_cutting * resistance.cutting_resistance * condition_modifier)
    blocked_piercing = min(current_piercing, current_piercing * resistance.piercing_resistance * condition_modifier)
    rigidity_drag = resistance.rigidity * condition_modifier
    impact_absorbed = min(current_impact, impact_absorbed + current_impact * rigidity_drag * 0.08)
    blocked_cutting = min(current_cutting, blocked_cutting + current_cutting * rigidity_drag * 0.06)
    blocked_piercing = min(current_piercing, blocked_piercing + current_piercing * rigidity_drag * 0.05)
    return (
        current_impact - impact_absorbed,
        current_cutting - blocked_cutting,
        current_piercing - blocked_piercing,
        impact_absorbed,
        blocked_cutting,
        blocked_piercing,
        rigidity_drag,
    )


def resolve_attack_physical_damage(
    *,
    action_id: str,
    attacker: "Character",
    defender: "Character",
    weapon: "Item | None",
    weapon_profile: "WeaponProfile | None",
    attack_type: AttackType,
    hit_quality: HitQuality,
    body_location: BodyLocation,
    body_location_group: BodyLocationGroup,
    armor_coverage: ArmorCoverageOutcome,
    style_damage: float = 0.0,
    profession_damage: float = 0.0,
) -> tuple[AttackPhysicalOutcome, WoundOutcome]:
    profile = weapon_damage_profile_for(weapon, weapon_profile, attack_type, attacker)
    quality_impact, quality_cutting, quality_piercing, quality_overall = _quality_channel_multiplier(hit_quality)
    profile = WeaponDamageProfile(
        weapon_profile_id=profile.weapon_profile_id,
        weapon_name=profile.weapon_name,
        attack_type=profile.attack_type,
        base_impact=profile.base_impact,
        base_cutting=profile.base_cutting,
        base_piercing=profile.base_piercing,
        armor_penetration=profile.armor_penetration,
        mass_factor=profile.mass_factor,
        strength_scaling=profile.strength_scaling,
        quality_scaling=quality_overall,
        tags=profile.tags,
        base_damage=profile.base_damage,
    )
    effective_impact = profile.base_impact * profile.strength_scaling * quality_impact
    effective_cutting = profile.base_cutting * profile.strength_scaling * quality_cutting
    effective_piercing = profile.base_piercing * profile.strength_scaling * quality_piercing
    if style_damage:
        effective_impact += max(0.0, style_damage) * 0.20
        effective_cutting += max(0.0, style_damage) * 0.12
        effective_piercing += max(0.0, style_damage) * 0.08
    if profession_damage:
        effective_impact += max(0.0, profession_damage) * 0.15
        effective_cutting += max(0.0, profession_damage) * 0.10
        effective_piercing += max(0.0, profession_damage) * 0.05
    remaining_impact = effective_impact
    remaining_cutting = effective_cutting
    remaining_piercing = effective_piercing
    absorbed_impact = 0.0
    blocked_cutting = 0.0
    blocked_piercing = 0.0
    rigidity_total = 0.0
    for layer in armor_coverage.covering_layers:
        remaining_impact, remaining_cutting, remaining_piercing, layer_absorbed, layer_blocked_cutting, layer_blocked_piercing, rigidity_drag = _apply_layer(
            remaining_impact,
            remaining_cutting,
            remaining_piercing,
            layer,
        )
        absorbed_impact += layer_absorbed
        blocked_cutting += layer_blocked_cutting
        blocked_piercing += layer_blocked_piercing
        rigidity_total += rigidity_drag
    location_multiplier = _location_multiplier(body_location)
    penetration_margin = max(0.0, (remaining_piercing * profile.armor_penetration) + (remaining_cutting * 0.45) + (remaining_impact * 0.25) - rigidity_total * 0.40)
    raw_remaining = max(0.0, remaining_impact + remaining_cutting + remaining_piercing)
    severity_score = max(0.0, (raw_remaining * quality_overall * location_multiplier) + penetration_margin)
    if severity_score <= 0.2:
        severity = WoundSeverity.NO_INJURY
    elif severity_score <= 1.5:
        severity = WoundSeverity.SCRATCH
    elif severity_score <= 3.5:
        severity = WoundSeverity.MINOR
    elif severity_score <= 6.0:
        severity = WoundSeverity.MODERATE
    elif severity_score <= 9.0:
        severity = WoundSeverity.SERIOUS
    elif severity_score <= 13.0:
        severity = WoundSeverity.SEVERE
    else:
        severity = WoundSeverity.CRITICAL
    critical_condition: CriticalCondition | None = None
    if severity is WoundSeverity.CRITICAL:
        if body_location in {BodyLocation.HEAD, BodyLocation.NECK} and severity_score >= 6.0:
            critical_condition = CriticalCondition.VITAL_LOCATION
        elif penetration_margin >= 2.0:
            critical_condition = CriticalCondition.MASSIVE_PENETRATION
        elif remaining_impact >= 2.5:
            critical_condition = CriticalCondition.MASSIVE_IMPACT
        elif remaining_cutting >= 2.0:
            critical_condition = CriticalCondition.SEVERE_CUT
        else:
            critical_condition = CriticalCondition.COMBINED_TRAUMA
    elif body_location in {BodyLocation.HEAD, BodyLocation.NECK} and severity_score >= 4.5:
        critical_condition = CriticalCondition.VITAL_LOCATION
    elif penetration_margin >= 2.5:
        critical_condition = CriticalCondition.ARMOR_BYPASSED
    wound_level_map: dict[WoundSeverity, int] = {
        WoundSeverity.NO_INJURY: 0,
        WoundSeverity.SCRATCH: 1,
        WoundSeverity.MINOR: 1,
        WoundSeverity.MODERATE: 2,
        WoundSeverity.SERIOUS: 2,
        WoundSeverity.SEVERE: 3,
        WoundSeverity.CRITICAL: 4,
    }
    wound_level = wound_level_map[severity]
    final_damage = max(0, int(round(severity_score)))
    attack_physical_outcome = AttackPhysicalOutcome(
        action_id=action_id,
        body_location=body_location,
        body_location_group=body_location_group,
        hit_quality=hit_quality,
        weapon_profile_id=profile.weapon_profile_id,
        attack_type=attack_type,
        weapon_damage_profile=profile,
        armor_layers=armor_coverage.covering_layers,
        base_impact=profile.base_impact,
        effective_impact=effective_impact,
        base_cutting=profile.base_cutting,
        effective_cutting=effective_cutting,
        base_piercing=profile.base_piercing,
        effective_piercing=effective_piercing,
        absorbed_impact=absorbed_impact,
        blocked_cutting=blocked_cutting,
        blocked_piercing=blocked_piercing,
        remaining_impact=max(0.0, remaining_impact),
        remaining_cutting=max(0.0, remaining_cutting),
        remaining_piercing=max(0.0, remaining_piercing),
        penetration_margin=penetration_margin,
        severity_score=severity_score,
        critical_condition=critical_condition,
        severity=severity,
        final_damage=final_damage,
        reason_code="OK" if final_damage > 0 or severity is WoundSeverity.NO_INJURY else "NO_INJURY",
    )
    wound_outcome = WoundOutcome(
        action_id=action_id,
        source_body_location=body_location,
        legacy_body_part=legacy_body_part_for_location(body_location),
        severity=severity,
        wound_level=wound_level,
        damage=final_damage,
        critical_condition=critical_condition,
        lethal=body_location in {BodyLocation.HEAD, BodyLocation.NECK, BodyLocation.CHEST, BodyLocation.ABDOMEN} and wound_level >= 4,
        reason_code=attack_physical_outcome.reason_code,
    )
    return attack_physical_outcome, wound_outcome

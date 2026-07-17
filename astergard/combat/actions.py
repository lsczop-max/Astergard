from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4

from astergard.combat.hit_locations import ArmorCoverageOutcome, BodyLocation, BodyLocationGroup, HitQuality, legacy_body_part_for_location
from astergard.combat.physical_damage import AttackPhysicalOutcome, WoundOutcome
from astergard.combat.weapons import HandRequirement


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


class CombatActionType(StrEnum):
    BASIC_ATTACK = "BASIC_ATTACK"
    TECHNIQUE = "TECHNIQUE"
    COUNTERATTACK = "COUNTERATTACK"
    REACTION = "REACTION"
    FLEE = "FLEE"


class CombatOutcomeType(StrEnum):
    HIT = "HIT"
    MISS = "MISS"
    DEFENDED = "DEFENDED"
    INVALID = "INVALID"
    NO_TARGET = "NO_TARGET"
    TARGET_DEFEATED = "TARGET_DEFEATED"


class DefenseResolution(StrEnum):
    NONE = "NONE"
    DODGED = "DODGED"
    PARRIED = "PARRIED"
    BLOCKED = "BLOCKED"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    UNKNOWN_DEFENSE = "UNKNOWN_DEFENSE"


class DefenseType(StrEnum):
    DODGE = "DODGE"
    PARRY = "PARRY"
    SHIELD_BLOCK = "SHIELD_BLOCK"


@dataclass(frozen=True, slots=True)
class DefenseAttempt:
    defense_type: DefenseType
    available: bool
    attempted: bool
    success: bool
    chance: int | None = None
    roll: int | None = None
    reason_code: str = ""
    attack_pressure: float | None = None
    contested_effective_value: float | None = None
    base_probability: float | None = None
    sequence_multiplier: float | None = None
    final_probability: float | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "defense_type": self.defense_type.value,
            "available": self.available,
            "attempted": self.attempted,
            "success": self.success,
            "chance": self.chance,
            "roll": self.roll,
            "reason_code": self.reason_code,
            "attack_pressure": self.attack_pressure,
            "contested_effective_value": self.contested_effective_value,
            "base_probability": self.base_probability,
            "sequence_multiplier": self.sequence_multiplier,
            "final_probability": self.final_probability,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DefenseAttempt":
        def _int_or_none(value: object) -> int | None:
            if value is None:
                return None
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    return None
            if isinstance(value, float):
                return int(value)
            return None

        def _float_or_none(value: object) -> float | None:
            if value is None:
                return None
            if isinstance(value, bool):
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                text = value.strip()
                if not text:
                    return None
                try:
                    return float(text)
                except ValueError:
                    return None
            return None

        return cls(
            defense_type=DefenseType(str(data.get("defense_type", DefenseType.DODGE.value))),
            available=bool(data.get("available", False)),
            attempted=bool(data.get("attempted", False)),
            success=bool(data.get("success", False)),
            chance=_int_or_none(data.get("chance")),
            roll=_int_or_none(data.get("roll")),
            reason_code=str(data.get("reason_code", "")),
            attack_pressure=_float_or_none(data.get("attack_pressure")),
            contested_effective_value=_float_or_none(data.get("contested_effective_value")),
            base_probability=_float_or_none(data.get("base_probability")),
            sequence_multiplier=_float_or_none(data.get("sequence_multiplier")),
            final_probability=_float_or_none(data.get("final_probability")),
        )


@dataclass(frozen=True, slots=True)
class DefenseOutcome:
    resolution: DefenseResolution
    successful_defense: bool
    attempts: tuple[DefenseAttempt, ...]
    selected_defense: DefenseType | None = None
    reason_code: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "resolution": self.resolution.value,
            "successful_defense": self.successful_defense,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "selected_defense": self.selected_defense.value if self.selected_defense is not None else None,
            "reason_code": self.reason_code,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DefenseOutcome":
        attempts_raw = data.get("attempts", ())
        attempts = tuple(
            DefenseAttempt.from_dict(item)
            for item in attempts_raw
            if isinstance(item, dict)
        ) if isinstance(attempts_raw, list) else ()
        selected_raw = data.get("selected_defense")
        selected_defense = DefenseType(str(selected_raw)) if selected_raw not in {None, ""} else None
        return cls(
            resolution=DefenseResolution(str(data.get("resolution", DefenseResolution.UNKNOWN_DEFENSE.value))),
            successful_defense=bool(data.get("successful_defense", False)),
            attempts=attempts,
            selected_defense=selected_defense,
            reason_code=str(data.get("reason_code", "")),
        )


@dataclass(frozen=True, slots=True)
class CombatAction:
    action_id: str = field(default_factory=lambda: uuid4().hex)
    actor_id: str = ""
    target_id: str = ""
    action_type: CombatActionType = CombatActionType.BASIC_ATTACK
    parent_action_id: str | None = None
    reaction_id: str | None = None
    reaction_depth: int = 0
    weapon_id: str | None = None
    weapon_profile_id: str | None = None
    weapon_specialization_id: str | None = None
    weapon_tags: tuple[str, ...] = ()
    hand_requirement: HandRequirement | None = None
    technique_id: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "action_type": self.action_type.value,
            "parent_action_id": self.parent_action_id,
            "reaction_id": self.reaction_id,
            "reaction_depth": self.reaction_depth,
            "weapon_id": self.weapon_id,
            "weapon_profile_id": self.weapon_profile_id,
            "weapon_specialization_id": self.weapon_specialization_id,
            "weapon_tags": list(self.weapon_tags),
            "hand_requirement": self.hand_requirement.value if self.hand_requirement is not None else None,
            "technique_id": self.technique_id,
            "metadata": list(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CombatAction":
        metadata_raw = data.get("metadata", ())
        metadata: tuple[tuple[str, str], ...] = ()
        if isinstance(metadata_raw, list):
            metadata = tuple(
                (str(key), str(value))
                for item in metadata_raw
                if isinstance(item, (list, tuple)) and len(item) == 2
                for key, value in [item]
            )
        weapon_tags_raw = data.get("weapon_tags", ())
        if isinstance(weapon_tags_raw, (list, tuple)):
            weapon_tags = tuple(str(tag).strip() for tag in weapon_tags_raw if isinstance(tag, str) and str(tag).strip())
        else:
            weapon_tags = ()
        hand_requirement_raw = data.get("hand_requirement")
        hand_requirement = None
        if isinstance(hand_requirement_raw, str) and hand_requirement_raw.strip():
            try:
                hand_requirement = HandRequirement(hand_requirement_raw.strip())
            except ValueError:
                hand_requirement = None
        return cls(
            action_id=str(data.get("action_id") or uuid4().hex),
            actor_id=str(data.get("actor_id", "")),
            target_id=str(data.get("target_id", "")),
            action_type=CombatActionType(str(data.get("action_type", CombatActionType.BASIC_ATTACK.value))),
            parent_action_id=str(data["parent_action_id"]) if data.get("parent_action_id") not in {None, ""} else None,
            reaction_id=str(data["reaction_id"]) if data.get("reaction_id") not in {None, ""} else None,
            reaction_depth=_coerce_int(data.get("reaction_depth", 0), 0),
            weapon_id=str(data["weapon_id"]) if data.get("weapon_id") not in {None, ""} else None,
            weapon_profile_id=str(data["weapon_profile_id"]) if data.get("weapon_profile_id") not in {None, ""} else None,
            weapon_specialization_id=str(data["weapon_specialization_id"]) if data.get("weapon_specialization_id") not in {None, ""} else None,
            weapon_tags=weapon_tags,
            hand_requirement=hand_requirement,
            technique_id=str(data["technique_id"]) if data.get("technique_id") not in {None, ""} else None,
            metadata=metadata,
        )


@dataclass(frozen=True, slots=True)
class CombatOutcome:
    action_id: str
    actor_id: str
    target_id: str
    result_type: CombatOutcomeType
    hit: bool | None = None
    defense_result: DefenseResolution = DefenseResolution.UNKNOWN_DEFENSE
    defense_outcome: DefenseOutcome | None = None
    damage: int = 0
    hit_location: str | None = None
    legacy_body_part: str | None = None
    body_location: BodyLocation | None = None
    body_location_group: BodyLocationGroup | None = None
    hit_quality: HitQuality | None = None
    armor_layers: tuple[str, ...] = ()
    armor_coverage_indicator: float = 0.0
    armor_coverage_outcome: ArmorCoverageOutcome | None = None
    physical_outcome: AttackPhysicalOutcome | None = None
    wound_outcome: WoundOutcome | None = None
    wound_ids: tuple[str, ...] = ()
    effect_ids: tuple[str, ...] = ()
    target_defeated: bool = False
    combat_ended: bool = False
    reason_code: str = ""
    metadata: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict[str, object]:
        defense_outcome = self.defense_outcome.to_dict() if self.defense_outcome is not None else None
        return {
            "action_id": self.action_id,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "result_type": self.result_type.value,
            "hit": self.hit,
            "defense_result": self.defense_result.value,
            "defense_outcome": defense_outcome,
            "damage": self.damage,
            "hit_location": self.hit_location,
            "legacy_body_part": self.legacy_body_part,
            "body_location": self.body_location.value if self.body_location is not None else None,
            "body_location_group": self.body_location_group.value if self.body_location_group is not None else None,
            "hit_quality": self.hit_quality.value if self.hit_quality is not None else None,
            "armor_layers": list(self.armor_layers),
            "armor_coverage_indicator": self.armor_coverage_indicator,
            "armor_coverage_outcome": self.armor_coverage_outcome.to_dict() if self.armor_coverage_outcome is not None else None,
            "physical_outcome": self.physical_outcome.to_dict() if self.physical_outcome is not None else None,
            "wound_outcome": self.wound_outcome.to_dict() if self.wound_outcome is not None else None,
            "wound_ids": list(self.wound_ids),
            "effect_ids": list(self.effect_ids),
            "target_defeated": self.target_defeated,
            "combat_ended": self.combat_ended,
            "reason_code": self.reason_code,
            "metadata": list(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CombatOutcome":
        def _bool_or_none(value: object) -> bool | None:
            if isinstance(value, bool) or value is None:
                return value
            return bool(value)

        def _int_or_zero(value: object) -> int:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    return 0
            if isinstance(value, float):
                return int(value)
            return 0

        metadata_raw = data.get("metadata", ())
        metadata: tuple[tuple[str, str], ...] = ()
        if isinstance(metadata_raw, list):
            metadata = tuple(
                (str(key), str(value))
                for item in metadata_raw
                if isinstance(item, (list, tuple)) and len(item) == 2
                for key, value in [item]
            )
        wound_ids_raw = data.get("wound_ids", ())
        effect_ids_raw = data.get("effect_ids", ())
        body_location_raw = data.get("body_location")
        body_location_group_raw = data.get("body_location_group")
        hit_quality_raw = data.get("hit_quality")
        armor_layers_raw = data.get("armor_layers", ())
        armor_coverage_outcome_raw = data.get("armor_coverage_outcome")
        armor_coverage_outcome = ArmorCoverageOutcome.from_dict(armor_coverage_outcome_raw) if isinstance(armor_coverage_outcome_raw, dict) else None
        physical_outcome_raw = data.get("physical_outcome")
        physical_outcome = AttackPhysicalOutcome.from_dict(physical_outcome_raw) if isinstance(physical_outcome_raw, dict) else None
        wound_outcome_raw = data.get("wound_outcome")
        wound_outcome = WoundOutcome.from_dict(wound_outcome_raw) if isinstance(wound_outcome_raw, dict) else None
        defense_outcome_raw = data.get("defense_outcome")
        defense_outcome = DefenseOutcome.from_dict(defense_outcome_raw) if isinstance(defense_outcome_raw, dict) else None
        defense_result_raw = data.get("defense_result", DefenseResolution.UNKNOWN_DEFENSE.value)
        defense_result = DefenseResolution(str(defense_result_raw))
        if defense_outcome is not None and defense_outcome.resolution != defense_result:
            defense_result = defense_outcome.resolution
        legacy_body_part_raw = data.get("legacy_body_part")
        legacy_body_part = str(legacy_body_part_raw) if legacy_body_part_raw not in {None, ""} else None
        if legacy_body_part is None and body_location_raw not in {None, ""}:
            try:
                legacy_body_part = legacy_body_part_for_location(BodyLocation(str(body_location_raw)))
            except ValueError:
                legacy_body_part = None
        return cls(
            action_id=str(data.get("action_id", "")),
            actor_id=str(data.get("actor_id", "")),
            target_id=str(data.get("target_id", "")),
            result_type=CombatOutcomeType(str(data.get("result_type", CombatOutcomeType.INVALID.value))),
            hit=_bool_or_none(data.get("hit")),
            defense_result=defense_result,
            defense_outcome=defense_outcome,
            damage=_int_or_zero(data.get("damage", 0)),
            hit_location=str(data["hit_location"]) if data.get("hit_location") not in {None, ""} else None,
            legacy_body_part=legacy_body_part,
            body_location=BodyLocation(str(body_location_raw)) if body_location_raw not in {None, ""} else None,
            body_location_group=BodyLocationGroup(str(body_location_group_raw)) if body_location_group_raw not in {None, ""} else None,
            hit_quality=HitQuality(str(hit_quality_raw)) if hit_quality_raw not in {None, ""} else None,
            armor_layers=tuple(str(value) for value in armor_layers_raw if isinstance(value, str)) if isinstance(armor_layers_raw, list) else (),
            armor_coverage_indicator=_coerce_float(data.get("armor_coverage_indicator", 0.0), 0.0),
            armor_coverage_outcome=armor_coverage_outcome,
            physical_outcome=physical_outcome,
            wound_outcome=wound_outcome,
            wound_ids=tuple(str(value) for value in wound_ids_raw if isinstance(value, str)) if isinstance(wound_ids_raw, list) else (),
            effect_ids=tuple(str(value) for value in effect_ids_raw if isinstance(value, str)) if isinstance(effect_ids_raw, list) else (),
            target_defeated=bool(data.get("target_defeated", False)),
            combat_ended=bool(data.get("combat_ended", False)),
            reason_code=str(data.get("reason_code", "")),
            metadata=metadata,
        )

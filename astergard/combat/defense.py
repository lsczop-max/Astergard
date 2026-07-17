from __future__ import annotations

from dataclasses import dataclass, replace
import warnings
from typing import TYPE_CHECKING, Protocol

from astergard.characters.models import Character
from astergard.combat.actions import (
    DefenseAttempt,
    DefenseOutcome,
    DefenseResolution,
    DefenseType,
)
from astergard.combat.defense_balance import default_defense_probability_policy
from astergard.combat.weapons import (
    ArmorProfile,
    HandRequirement,
    load_default_armor_profile_catalog,
    resolve_armor_profile,
    resolve_shield_profile,
    resolve_weapon_profile,
)
from astergard.combat.tactics import (
    fatigue_defense_penalty,
    formation_defense_modifier,
    morale_score,
    skill_for_weapon,
    wound_defense_penalty,
)
from astergard.rules.combat_specialization import (
    ActiveDefenseStyle,
    defense_specialization_for_style,
    resolve_active_defense_style,
)

if TYPE_CHECKING:
    from astergard.items.models import Item
    from astergard.rules.combat import CombatRules


class RandomSource(Protocol):
    def randint(self, a: int, b: int) -> int: ...


@dataclass(frozen=True, slots=True)
class DefenseContext:
    attacker: Character
    defender: Character
    hit_score: int
    dodge_score: int
    rng: RandomSource
    rules: CombatRules


@dataclass(frozen=True, slots=True)
class DefenseStyleSelectionResult:
    allowed: bool
    reason_code: str
    message: str


@dataclass(frozen=True, slots=True)
class DefenseCandidate:
    defense_type: DefenseType
    learned_skill: int
    equipment_modifier: float
    armor_modifier: float
    situational_modifier: float
    effective_value: float
    available: bool
    reason_code: str
    contested_effective_value: float = 0.0
    base_probability: float = 0.0
    sequence_multiplier: float = 1.0
    final_probability: float = 0.0
    attack_pressure: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "defense_type": self.defense_type.value,
            "learned_skill": self.learned_skill,
            "equipment_modifier": self.equipment_modifier,
            "armor_modifier": self.armor_modifier,
            "situational_modifier": self.situational_modifier,
            "effective_value": self.effective_value,
            "available": self.available,
            "reason_code": self.reason_code,
            "contested_effective_value": self.contested_effective_value,
            "base_probability": self.base_probability,
            "sequence_multiplier": self.sequence_multiplier,
            "final_probability": self.final_probability,
            "attack_pressure": self.attack_pressure,
        }


def can_select_defense_style(defender: Character, style: ActiveDefenseStyle | str | None) -> DefenseStyleSelectionResult:
    resolved = resolve_active_defense_style(style)
    if resolved is None:
        return DefenseStyleSelectionResult(False, "UNKNOWN_DEFENSE_STYLE", "Nie rozpoznajesz takiego sposobu obrony.")
    if not defender.is_alive:
        return DefenseStyleSelectionResult(False, "CHARACTER_DEAD", "Martwa postać nie zmienia już sposobu obrony.")
    current = resolve_active_defense_style(defender.active_defense_style)
    if current == resolved:
        return DefenseStyleSelectionResult(False, "DEFENSE_STYLE_ALREADY_ACTIVE", "Już bronisz się w ten sposób.")

    specialization_id = defense_specialization_for_style(resolved)
    if specialization_id is None:
        return DefenseStyleSelectionResult(False, "UNKNOWN_DEFENSE_STYLE", "Nie rozpoznajesz takiego sposobu obrony.")
    if not _defense_specialization_known(defender, specialization_id):
        if resolved == ActiveDefenseStyle.DODGE:
            return DefenseStyleSelectionResult(False, "DEFENSE_SPECIALIZATION_NOT_LEARNED", "Nie znasz jeszcze sposobu walki pozwalającego skutecznie unikać ciosów.")
        if resolved == ActiveDefenseStyle.PARRY:
            return DefenseStyleSelectionResult(False, "DEFENSE_SPECIALIZATION_NOT_LEARNED", "Nie znasz jeszcze sposobu walki pozwalającego skutecznie parować.")
        return DefenseStyleSelectionResult(False, "DEFENSE_SPECIALIZATION_NOT_LEARNED", "Nie znasz jeszcze sposobu walki pozwalającego skutecznie osłaniać się tarczą.")

    if resolved == ActiveDefenseStyle.DODGE:
        return DefenseStyleSelectionResult(True, "OK", "Rozluźniasz postawę, gotów zejść z linii każdego nadchodzącego ciosu.")

    if resolved == ActiveDefenseStyle.PARRY:
        weapon = defender.weapon()
        if weapon is None or weapon.durability <= 0:
            return DefenseStyleSelectionResult(False, "NO_ACTIVE_WEAPON", "Nie masz broni, którą mógłbyś parować.")
        weapon_profile = resolve_weapon_profile(weapon)
        if weapon_profile is not None and not weapon_profile.legacy and not weapon_profile.supports_parry:
            return DefenseStyleSelectionResult(False, "WEAPON_NOT_PARRY_CAPABLE", "Ta broń nie nadaje się do parowania.")
        return DefenseStyleSelectionResult(True, "OK", "Unosisz broń i przyjmujesz postawę pozwalającą zbijać nadchodzące uderzenia.")

    shield = defender.shield()
    if shield is None or shield.durability <= 0:
        return DefenseStyleSelectionResult(False, "NO_ACTIVE_SHIELD", "Nie masz tarczy, którą mógłbyś się osłonić.")
    weapon = defender.weapon()
    if weapon is not None and weapon.durability > 0:
        weapon_profile = resolve_weapon_profile(weapon)
        if weapon_profile is not None and not weapon_profile.legacy and weapon_profile.hand_requirement == HandRequirement.TWO_HANDED:
            return DefenseStyleSelectionResult(False, "INCOMPATIBLE_TWO_HANDED_WEAPON", "Nie możesz jednocześnie używać tarczy i broni wymagającej obu rąk.")
    return DefenseStyleSelectionResult(True, "OK", "Wysuwasz tarczę przed siebie, przygotowując się do przyjmowania ciosów na jej powierzchni.")


def select_defense_style(defender: Character, style: ActiveDefenseStyle | str | None) -> DefenseStyleSelectionResult:
    result = can_select_defense_style(defender, style)
    if not result.allowed:
        return result
    resolved = resolve_active_defense_style(style)
    defender.active_defense_style = resolved.value if resolved is not None else None
    return result


def _defense_specialization_known(defender: Character, specialization_id: str) -> bool:
    normalized = specialization_id.strip().casefold()
    return any(str(value).strip().casefold() == normalized for value in defender.combat_specializations.defense_specializations)


def resolve_defense(context: DefenseContext) -> DefenseOutcome:
    candidates = build_defense_candidates(context)
    if not candidates:
        return DefenseOutcome(
            resolution=DefenseResolution.NONE,
            successful_defense=False,
            attempts=(),
            selected_defense=None,
            reason_code="NONE",
        )

    attempts: list[DefenseAttempt] = []
    for candidate in candidates:
        attempt = _resolve_candidate(context, candidate)
        attempts.append(attempt)
        if attempt.success:
            resolution = _resolution_for(candidate.defense_type)
            return DefenseOutcome(
                resolution=resolution,
                successful_defense=True,
                attempts=tuple(attempts),
                selected_defense=candidate.defense_type,
                reason_code=resolution.value,
            )

    if not any(candidate.available for candidate in candidates):
        return DefenseOutcome(
            resolution=DefenseResolution.UNAVAILABLE,
            successful_defense=False,
            attempts=tuple(attempts),
            selected_defense=None,
            reason_code="UNAVAILABLE",
        )

    selected = candidates[0].defense_type
    return DefenseOutcome(
        resolution=DefenseResolution.NONE,
        successful_defense=False,
        attempts=tuple(attempts),
        selected_defense=selected,
        reason_code="FAILED",
    )


def build_defense_candidates(context: DefenseContext) -> tuple[DefenseCandidate, ...]:
    if not context.defender.is_alive:
        return ()
    policy = default_defense_probability_policy()
    attack_pressure = _attack_pressure(context)
    candidates: list[DefenseCandidate] = []
    armor_profile = _primary_armor_profile(context.defender)
    dodge_skill = context.defender.skills.level("uniki")
    dodge_situational = _situational_modifier(context, DefenseType.DODGE)
    dodge_available = dodge_skill > 0 and armor_profile.dodge_modifier > 0
    candidates.append(
        DefenseCandidate(
            defense_type=DefenseType.DODGE,
            learned_skill=dodge_skill,
            equipment_modifier=1.0,
            armor_modifier=armor_profile.dodge_modifier,
            situational_modifier=dodge_situational,
            effective_value=_effective_defense_value(dodge_skill, 1.0, armor_profile.dodge_modifier, dodge_situational),
            available=dodge_available,
            reason_code="OK" if dodge_available else "UNAVAILABLE",
        )
    )

    shield = context.defender.shield()
    if shield is not None and shield.durability > 0:
        shield_profile = resolve_shield_profile(shield)
        shield_skill = context.defender.skills.level("tarcze")
        shield_situational = _situational_modifier(context, DefenseType.SHIELD_BLOCK)
        if shield_profile is not None and not shield_profile.legacy:
            shield_equipment = shield_profile.block_modifier
        else:
            shield_equipment = max(1.0, float(getattr(shield, "shield_block", 1.0)))
        shield_compatible = _shield_is_compatible(context.defender)
        shield_available = shield_skill > 0 and shield_equipment > 0 and armor_profile.block_modifier > 0 and shield_compatible
        candidates.append(
            DefenseCandidate(
                defense_type=DefenseType.SHIELD_BLOCK,
                learned_skill=shield_skill,
                equipment_modifier=shield_equipment,
                armor_modifier=armor_profile.block_modifier,
                situational_modifier=shield_situational,
                effective_value=_effective_defense_value(shield_skill, shield_equipment, armor_profile.block_modifier, shield_situational),
                available=shield_available,
                reason_code="OK" if shield_available else ("INCOMPATIBLE_WEAPON_STATE" if not shield_compatible else "UNAVAILABLE"),
            )
        )

    weapon = context.defender.weapon()
    if weapon is not None and weapon.durability > 0:
        weapon_profile = resolve_weapon_profile(weapon)
        parry_skill = context.defender.skills.level("parowanie")
        parry_situational = _situational_modifier(context, DefenseType.PARRY)
        if weapon_profile is None:
            parry_equipment = max(1.0, float(getattr(weapon, "parry_bonus", 1.0)))
            parry_available = parry_skill > 0
        elif weapon_profile.legacy:
            parry_equipment = max(1.0, float(getattr(weapon, "parry_bonus", 1.0)))
            parry_available = parry_skill > 0
        else:
            parry_equipment = weapon_profile.parry_modifier
            parry_available = parry_skill > 0 and weapon_profile.enabled and parry_equipment > 0
        candidates.append(
            DefenseCandidate(
                defense_type=DefenseType.PARRY,
                learned_skill=parry_skill,
                equipment_modifier=parry_equipment,
                armor_modifier=armor_profile.parry_modifier,
                situational_modifier=parry_situational,
                effective_value=_effective_defense_value(parry_skill, parry_equipment, armor_profile.parry_modifier, parry_situational),
                available=parry_available,
                reason_code="OK" if parry_available else "UNAVAILABLE",
            )
        )

    ordered = sorted(candidates, key=lambda candidate: (-candidate.effective_value, policy.tie_break_rank(candidate.defense_type)))
    annotated: list[DefenseCandidate] = []
    for index, candidate in enumerate(ordered):
        contested, base_probability, sequence_multiplier, final_probability = policy.defense_probability(candidate.effective_value, attack_pressure, index)
        annotated.append(
            replace(
                candidate,
                contested_effective_value=contested,
                base_probability=base_probability,
                sequence_multiplier=sequence_multiplier,
                final_probability=final_probability,
                attack_pressure=attack_pressure,
            )
        )
    return tuple(annotated)


def _effective_defense_value(learned_skill: int, equipment_modifier: float, armor_modifier: float, situational_modifier: float) -> float:
    return float(learned_skill) * float(equipment_modifier) * float(armor_modifier) * float(situational_modifier)


def _attack_pressure(context: DefenseContext) -> float:
    weapon_skill = skill_for_weapon(context.attacker.weapon())
    skill_level = context.attacker.skills.level(weapon_skill)
    return max(0.0, float(skill_level) + float(context.hit_score) * 0.02)


def _primary_armor_profile(defender: Character) -> ArmorProfile:
    armor_items = [item for item in defender.armor_items() if item is not None and item.item_type == "armor" and item.durability > 0]
    if not armor_items:
        return load_default_armor_profile_catalog().legacy_profile
    armor_item = max(armor_items, key=lambda item: (max(0, item.protection) + max(0, item.armor_value), item.weight))
    profile = resolve_armor_profile(armor_item)
    return profile or load_default_armor_profile_catalog().legacy_profile


def _shield_is_compatible(defender: Character) -> bool:
    weapon = defender.weapon()
    weapon_profile = resolve_weapon_profile(weapon)
    if weapon is None or weapon.durability <= 0:
        return True
    if weapon_profile is None or weapon_profile.legacy:
        return True
    if weapon_profile.hand_requirement == HandRequirement.TWO_HANDED:
        warnings.warn(
            f"Postać {defender.username} ma broń dwuręczną i tarczę. Tarcza nie bierze udziału w obronie.",
            stacklevel=2,
        )
        return False
    return True


def _situational_modifier(context: DefenseContext, defense_type: DefenseType) -> float:
    modifier = 1.0
    modifier += (morale_score(context.defender) - 10) / 40.0
    modifier -= min(0.35, formation_defense_modifier(context.defender, context.attacker) * 0.05)
    modifier -= min(0.35, wound_defense_penalty(context.defender) * 0.03)
    modifier -= min(0.20, fatigue_defense_penalty(context.defender) * 0.10)
    if defense_type == DefenseType.DODGE:
        modifier -= min(0.40, context.defender.armor_burden_penalty() / 100.0)
    return max(0.0, modifier)


def _resolution_for(defense_type: DefenseType) -> DefenseResolution:
    if defense_type == DefenseType.DODGE:
        return DefenseResolution.DODGED
    if defense_type == DefenseType.SHIELD_BLOCK:
        return DefenseResolution.BLOCKED
    return DefenseResolution.PARRIED


def _resolve_candidate(context: DefenseContext, candidate: DefenseCandidate) -> DefenseAttempt:
    if not candidate.available:
        return DefenseAttempt(
            defense_type=candidate.defense_type,
            available=False,
            attempted=False,
            success=False,
            reason_code=candidate.reason_code,
            attack_pressure=candidate.attack_pressure,
            contested_effective_value=candidate.contested_effective_value,
            base_probability=candidate.base_probability,
            sequence_multiplier=candidate.sequence_multiplier,
            final_probability=candidate.final_probability,
        )
    if candidate.defense_type == DefenseType.DODGE:
        roll = context.rng.randint(1, 1000)
        chance = max(0, min(1000, int(round(candidate.final_probability * 1000))))
        success = roll <= chance
        return DefenseAttempt(
            defense_type=DefenseType.DODGE,
            available=True,
            attempted=True,
            success=success,
            chance=chance,
            roll=roll,
            reason_code="DODGED" if success else "FAILED",
            attack_pressure=candidate.attack_pressure,
            contested_effective_value=candidate.contested_effective_value,
            base_probability=candidate.base_probability,
            sequence_multiplier=candidate.sequence_multiplier,
            final_probability=candidate.final_probability,
        )
    if candidate.defense_type == DefenseType.SHIELD_BLOCK:
        shield = context.defender.shield()
        if shield is None or shield.durability <= 0:
            return DefenseAttempt(
                defense_type=DefenseType.SHIELD_BLOCK,
                available=False,
                attempted=False,
                success=False,
                reason_code="UNAVAILABLE",
                attack_pressure=candidate.attack_pressure,
                contested_effective_value=candidate.contested_effective_value,
                base_probability=candidate.base_probability,
                sequence_multiplier=candidate.sequence_multiplier,
                final_probability=candidate.final_probability,
            )
        roll = context.rng.randint(1, 1000)
        chance = max(0, min(1000, int(round(candidate.final_probability * 1000))))
        success = roll <= chance
        return DefenseAttempt(
            defense_type=DefenseType.SHIELD_BLOCK,
            available=True,
            attempted=True,
            success=success,
            chance=chance,
            roll=roll,
            reason_code="BLOCKED" if success else "FAILED",
            attack_pressure=candidate.attack_pressure,
            contested_effective_value=candidate.contested_effective_value,
            base_probability=candidate.base_probability,
            sequence_multiplier=candidate.sequence_multiplier,
            final_probability=candidate.final_probability,
        )
    weapon = context.defender.weapon()
    if weapon is None or weapon.durability <= 0:
        return DefenseAttempt(
            defense_type=DefenseType.PARRY,
            available=False,
            attempted=False,
            success=False,
            reason_code="UNAVAILABLE",
            attack_pressure=candidate.attack_pressure,
            contested_effective_value=candidate.contested_effective_value,
            base_probability=candidate.base_probability,
            sequence_multiplier=candidate.sequence_multiplier,
            final_probability=candidate.final_probability,
        )
    roll = context.rng.randint(1, 1000)
    chance = max(0, min(1000, int(round(candidate.final_probability * 1000))))
    success = roll <= chance
    return DefenseAttempt(
        defense_type=DefenseType.PARRY,
        available=True,
        attempted=True,
        success=success,
        chance=chance,
        roll=roll,
        reason_code="PARRIED" if success else "FAILED",
        attack_pressure=candidate.attack_pressure,
        contested_effective_value=candidate.contested_effective_value,
        base_probability=candidate.base_probability,
        sequence_multiplier=candidate.sequence_multiplier,
        final_probability=candidate.final_probability,
    )


def _resolve_active_style_defense(context: DefenseContext, active_style: ActiveDefenseStyle) -> DefenseOutcome:
    attempts: list[DefenseAttempt] = []
    if active_style == ActiveDefenseStyle.DODGE:
        dodge_attempt = DefenseAttempt(
            defense_type=DefenseType.DODGE,
            available=context.defender.is_alive,
            attempted=context.defender.is_alive,
            success=context.defender.is_alive and context.hit_score <= context.dodge_score,
            reason_code="DODGED" if context.defender.is_alive and context.hit_score <= context.dodge_score else ("UNAVAILABLE" if not context.defender.is_alive else "FAILED"),
        )
        attempts.append(dodge_attempt)
        if dodge_attempt.success:
            return DefenseOutcome(
                resolution=DefenseResolution.DODGED,
                successful_defense=True,
                attempts=tuple(attempts),
                selected_defense=DefenseType.DODGE,
                reason_code="DODGED",
            )
        if not dodge_attempt.available:
            return DefenseOutcome(
                resolution=DefenseResolution.UNAVAILABLE,
                successful_defense=False,
                attempts=tuple(attempts),
                selected_defense=DefenseType.DODGE,
                reason_code="UNAVAILABLE",
            )
        return DefenseOutcome(
            resolution=DefenseResolution.NONE,
            successful_defense=False,
            attempts=tuple(attempts),
            selected_defense=DefenseType.DODGE,
            reason_code="FAILED",
        )

    if active_style == ActiveDefenseStyle.SHIELD:
        shield = context.defender.shield()
        defender_weapon = context.defender.weapon()
        defender_weapon_profile = resolve_weapon_profile(defender_weapon)
        shield_available = shield is not None and shield.durability > 0
        if shield_available and defender_weapon_profile is not None and not defender_weapon_profile.legacy and defender_weapon_profile.hand_requirement == HandRequirement.TWO_HANDED:
            shield_available = False
        shield_attempt = DefenseAttempt(
            defense_type=DefenseType.SHIELD_BLOCK,
            available=shield_available,
            attempted=shield_available,
            success=False,
            reason_code="UNAVAILABLE" if not shield_available else "FAILED",
        )
        if shield_available and shield is not None:
            block_score = _shield_block_score(context.defender, context.attacker, shield, context.rules, context.rng)
            shield_attempt = DefenseAttempt(
                defense_type=DefenseType.SHIELD_BLOCK,
                available=True,
                attempted=True,
                success=block_score >= context.hit_score + context.rules.shield_block_margin,
                reason_code="BLOCKED" if block_score >= context.hit_score + context.rules.shield_block_margin else "FAILED",
            )
        attempts.append(shield_attempt)
        if shield_attempt.success:
            return DefenseOutcome(
                resolution=DefenseResolution.BLOCKED,
                successful_defense=True,
                attempts=tuple(attempts),
                selected_defense=DefenseType.SHIELD_BLOCK,
                reason_code="BLOCKED",
            )
        if not shield_attempt.available:
            return DefenseOutcome(
                resolution=DefenseResolution.UNAVAILABLE,
                successful_defense=False,
                attempts=tuple(attempts),
                selected_defense=DefenseType.SHIELD_BLOCK,
                reason_code=shield_attempt.reason_code,
            )
        return DefenseOutcome(
            resolution=DefenseResolution.NONE,
            successful_defense=False,
            attempts=tuple(attempts),
            selected_defense=DefenseType.SHIELD_BLOCK,
            reason_code="FAILED",
        )

    weapon = context.defender.weapon()
    defender_weapon_profile = resolve_weapon_profile(weapon)
    if weapon is not None and weapon.durability > 0:
        if defender_weapon_profile is None:
            parry_available = False
        elif defender_weapon_profile.legacy:
            parry_available = True
        else:
            parry_available = defender_weapon_profile.enabled and defender_weapon_profile.supports_parry
        parry_score = _parry_score(context.defender, context.attacker, weapon, context.rules, context.rng)
        parry_attempt = DefenseAttempt(
            defense_type=DefenseType.PARRY,
            available=parry_available,
            attempted=parry_available,
            success=parry_available and parry_score >= context.hit_score + context.rules.parry_margin,
            reason_code="PARRIED" if parry_available and parry_score >= context.hit_score + context.rules.parry_margin else ("UNAVAILABLE" if not parry_available else "FAILED"),
        )
    else:
        parry_attempt = DefenseAttempt(
            defense_type=DefenseType.PARRY,
            available=False,
            attempted=False,
            success=False,
            reason_code="UNAVAILABLE",
        )
    attempts.append(parry_attempt)
    if parry_attempt.success:
        return DefenseOutcome(
            resolution=DefenseResolution.PARRIED,
            successful_defense=True,
            attempts=tuple(attempts),
            selected_defense=DefenseType.PARRY,
            reason_code="PARRIED",
        )
    if not parry_attempt.available:
        return DefenseOutcome(
            resolution=DefenseResolution.UNAVAILABLE,
            successful_defense=False,
            attempts=tuple(attempts),
            selected_defense=DefenseType.PARRY,
            reason_code="UNAVAILABLE",
        )
    return DefenseOutcome(
        resolution=DefenseResolution.NONE,
        successful_defense=False,
        attempts=tuple(attempts),
        selected_defense=DefenseType.PARRY,
        reason_code="FAILED",
    )


def _resolve_legacy_defense(context: DefenseContext) -> DefenseOutcome:
    attempts: list[DefenseAttempt] = []

    dodge_attempt = DefenseAttempt(
        defense_type=DefenseType.DODGE,
        available=context.defender.is_alive,
        attempted=context.defender.is_alive,
        success=context.defender.is_alive and context.hit_score <= context.dodge_score,
        reason_code="DODGED" if context.defender.is_alive and context.hit_score <= context.dodge_score else "FAILED",
    )
    attempts.append(dodge_attempt)
    if dodge_attempt.success:
        return DefenseOutcome(
            resolution=DefenseResolution.DODGED,
            successful_defense=True,
            attempts=tuple(attempts),
            selected_defense=DefenseType.DODGE,
            reason_code="DODGED",
        )

    shield = context.defender.shield()
    defender_weapon = context.defender.weapon()
    defender_weapon_profile = resolve_weapon_profile(defender_weapon)
    shield_reason = "UNAVAILABLE"
    if shield is not None and shield.durability > 0:
        if defender_weapon_profile is not None and not defender_weapon_profile.legacy and defender_weapon_profile.hand_requirement == HandRequirement.TWO_HANDED:
            warnings.warn(
                f"Postać {context.defender.username} ma broń dwuręczną i tarczę. Tarcza nie bierze udziału w obronie.",
                stacklevel=2,
            )
            shield = None
            shield_reason = "INCOMPATIBLE_WEAPON_STATE"
        else:
            shield_reason = "FAILED"
    if shield is not None and shield.durability > 0:
        block_score = _shield_block_score(context.defender, context.attacker, shield, context.rules, context.rng)
        shield_attempt = DefenseAttempt(
            defense_type=DefenseType.SHIELD_BLOCK,
            available=True,
            attempted=True,
            success=block_score >= context.hit_score + context.rules.shield_block_margin,
            reason_code="BLOCKED" if block_score >= context.hit_score + context.rules.shield_block_margin else "FAILED",
        )
    else:
        shield_attempt = DefenseAttempt(
            defense_type=DefenseType.SHIELD_BLOCK,
            available=False if shield_reason != "FAILED" else True,
            attempted=False if shield_reason != "FAILED" else True,
            success=False,
            reason_code=shield_reason,
        )
    attempts.append(shield_attempt)
    if shield_attempt.success:
        return DefenseOutcome(
            resolution=DefenseResolution.BLOCKED,
            successful_defense=True,
            attempts=tuple(attempts),
            selected_defense=DefenseType.SHIELD_BLOCK,
            reason_code="BLOCKED",
        )

    weapon = defender_weapon
    if weapon is not None and weapon.durability > 0:
        if defender_weapon_profile is None:
            parry_available = False
        elif defender_weapon_profile.legacy:
            parry_available = True
        else:
            parry_available = defender_weapon_profile.enabled and defender_weapon_profile.supports_parry
        parry_score = _parry_score(context.defender, context.attacker, weapon, context.rules, context.rng)
        parry_attempt = DefenseAttempt(
            defense_type=DefenseType.PARRY,
            available=parry_available,
            attempted=parry_available,
            success=parry_available and parry_score >= context.hit_score + context.rules.parry_margin,
            reason_code="PARRIED" if parry_available and parry_score >= context.hit_score + context.rules.parry_margin else ("UNAVAILABLE" if not parry_available else "FAILED"),
        )
    else:
        parry_attempt = DefenseAttempt(
            defense_type=DefenseType.PARRY,
            available=False,
            attempted=False,
            success=False,
            reason_code="UNAVAILABLE",
        )
    attempts.append(parry_attempt)
    if parry_attempt.success:
        return DefenseOutcome(
            resolution=DefenseResolution.PARRIED,
            successful_defense=True,
            attempts=tuple(attempts),
            selected_defense=DefenseType.PARRY,
            reason_code="PARRIED",
        )

    return DefenseOutcome(
        resolution=DefenseResolution.NONE,
        successful_defense=False,
        attempts=tuple(attempts),
        selected_defense=None,
        reason_code="NONE",
    )


def _shield_block_score(defender: Character, attacker: Character, shield: Item, rules: CombatRules, rng: RandomSource) -> int:
    style = rules.style(defender.combat_style)
    return (
        defender.stats.zrecznosc
        + style.defense_modifier
        + shield.shield_block
        + defender.skills.level("tarcze")
        + morale_score(defender) // 5
        + formation_defense_modifier(defender, attacker)
        + rng.randint(1, rules.active_defense_roll_sides)
    )


def _parry_score(defender: Character, attacker: Character, weapon: Item, rules: CombatRules, rng: RandomSource) -> int:
    style = rules.style(defender.combat_style)
    return (
        defender.stats.zrecznosc
        + style.defense_modifier
        + defender.skills.level("parowanie")
        + weapon.parry_bonus
        + morale_score(defender) // 5
        + formation_defense_modifier(defender, attacker)
        + rng.randint(1, rules.active_defense_roll_sides)
    )

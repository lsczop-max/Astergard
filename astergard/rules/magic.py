from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MagicRules:
    strength_spell_stamina_cost: int = 30
    strength_spell_bonus: int = 4
    strength_spell_duration_ticks: int = 20
    magic_bolt_stamina_cost: int = 25
    magic_bolt_roll_sides: int = 20
    magic_bolt_wound_increase: int = 2
    backlash_chance: float = 0.15
    backlash_willpower_penalty: int = -2
    backlash_duration_ticks: int = 10
    max_wound_level: int = 4


def default_magic_rules() -> MagicRules:
    return MagicRules()

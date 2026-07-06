from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MovementRules:
    base_move_stamina_cost: int = 3
    severe_leg_wound_level: int = 3
    critical_wound_level: int = 4
    severe_leg_cost_multiplier: int = 3

    def movement_blocked(self, right_leg_wound: int, left_leg_wound: int) -> bool:
        return right_leg_wound >= self.critical_wound_level and left_leg_wound >= self.critical_wound_level

    def move_cost(self, right_leg_wound: int, left_leg_wound: int) -> int:
        if max(right_leg_wound, left_leg_wound) >= self.severe_leg_wound_level:
            return self.base_move_stamina_cost * self.severe_leg_cost_multiplier
        return self.base_move_stamina_cost


@dataclass(frozen=True, slots=True)
class SearchRules:
    stamina_cost: int = 15
    perception_roll_sides: int = 10
    skill_divisor: int = 10

    def score(self, roll: int, perception: int, skill_level: int) -> int:
        return roll + perception + skill_level // self.skill_divisor


def default_movement_rules() -> MovementRules:
    return MovementRules()


def default_search_rules() -> SearchRules:
    return SearchRules()

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SkillRules:
    minimum_level: int = 1
    maximum_level: int = 100
    progress_multiplier: int = 10

    def threshold(self, level: int) -> int:
        return max(self.minimum_level, level) * self.progress_multiplier

    def can_train(self, level: int) -> bool:
        return level < self.maximum_level


def default_skill_rules() -> SkillRules:
    return SkillRules()

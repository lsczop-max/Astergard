from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReputationRules:
    minimum_reputation: int = -2000
    maximum_reputation: int = 2000
    meekhan_gain_for_rebel_kill: int = 50
    meekhan_loss_for_meekhan_kill: int = -500
    guard_hostility_threshold: int = -500

    def clamp(self, value: int) -> int:
        return max(self.minimum_reputation, min(self.maximum_reputation, value))

    def guards_are_hostile(self, meekhan_reputation: int) -> bool:
        return meekhan_reputation < self.guard_hostility_threshold


def default_reputation_rules() -> ReputationRules:
    return ReputationRules()

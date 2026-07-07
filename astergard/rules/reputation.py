from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ReputationRules:
    minimum_reputation: int = -2000
    maximum_reputation: int = 2000
    meekhan_gain_for_rebel_kill: int = 50
    meekhan_loss_for_meekhan_kill: int = -500
    guard_hostility_threshold: int = -500
    guard_wanted_threshold: int = 2
    merchant_friend_threshold: int = 120
    merchant_hostile_threshold: int = -120
    quest_offer_threshold: int = -150
    fame_title_thresholds: tuple[tuple[int, str], ...] = (
        (600, "Legenda"),
        (300, "Sławny"),
        (150, "Znany"),
        (50, "Rozpoznawalny"),
        (0, "Wędrowiec"),
    )
    crime_wanted_weights: dict[str, int] = field(
        default_factory=lambda: {"kradzież": 1, "kradziez": 1, "napaść": 2, "napasc": 2, "zabójstwo": 3, "zabojstwo": 3}
    )

    def clamp(self, value: int) -> int:
        return max(self.minimum_reputation, min(self.maximum_reputation, value))

    def guards_are_hostile(self, meekhan_reputation: int, wanted_level: int = 0) -> bool:
        return meekhan_reputation < self.guard_hostility_threshold or wanted_level >= self.guard_wanted_threshold

    def merchants_are_hostile(self, reputation: int, wanted_level: int = 0) -> bool:
        return reputation < self.merchant_hostile_threshold or wanted_level >= self.guard_wanted_threshold

    def merchants_are_friendly(self, reputation: int) -> bool:
        return reputation >= self.merchant_friend_threshold

    def quests_are_blocked(self, global_reputation: int, wanted_level: int = 0) -> bool:
        return global_reputation <= self.quest_offer_threshold or wanted_level >= self.guard_wanted_threshold

    def title_for(self, renown: int, wanted_level: int) -> str:
        if wanted_level >= self.guard_wanted_threshold:
            return "Poszukiwany"
        for threshold, title in self.fame_title_thresholds:
            if renown >= threshold:
                return title
        return "Wędrowiec"

    def wanted_level_for(self, crimes: dict[str, int]) -> int:
        wanted = 0
        for crime, count in crimes.items():
            wanted += self.crime_wanted_weights.get(crime, 0) * max(0, count)
        return min(3, wanted)


def default_reputation_rules() -> ReputationRules:
    return ReputationRules()

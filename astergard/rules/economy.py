from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EconomyRules:
    minimum_price: int = 1
    maximum_reputation_discount_percent: int = 20
    reputation_points_per_discount_percent: int = 100
    sell_price_multiplier: float = 0.50
    minimum_sell_price_multiplier: float = 0.10

    def buy_price(self, base_value: int, reputation: int = 0) -> int:
        discount_percent = min(
            self.maximum_reputation_discount_percent,
            max(0, reputation // self.reputation_points_per_discount_percent),
        )
        return max(self.minimum_price, int(base_value * (1.0 - discount_percent / 100)))

    def sell_price(self, base_value: int) -> int:
        return max(
            self.minimum_price,
            int(base_value * self.sell_price_multiplier),
            int(base_value * self.minimum_sell_price_multiplier),
        )


def default_economy_rules() -> EconomyRules:
    return EconomyRules()

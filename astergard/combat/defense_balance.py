from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from astergard.combat.actions import DefenseType


class DefenseBalanceConfigurationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class DefenseProbabilityPolicy:
    soft_cap: float = 70.0
    maximum_probability: float = 0.85
    attack_pressure_weight: float = 0.35
    sequence_multipliers: tuple[float, ...] = (1.0, 0.5, 0.25)
    minimum_probability: float = 0.0
    tie_break_order: tuple[DefenseType, ...] = (
        DefenseType.SHIELD_BLOCK,
        DefenseType.PARRY,
        DefenseType.DODGE,
    )

    def __post_init__(self) -> None:
        if self.soft_cap <= 0:
            raise DefenseBalanceConfigurationError("soft_cap musi być dodatnie.")
        if not 0 < self.maximum_probability <= 1:
            raise DefenseBalanceConfigurationError("maximum_probability musi być w zakresie 0-1.")
        if self.attack_pressure_weight < 0:
            raise DefenseBalanceConfigurationError("attack_pressure_weight nie może być ujemne.")
        if self.minimum_probability < 0 or self.minimum_probability > self.maximum_probability:
            raise DefenseBalanceConfigurationError("minimum_probability musi być w zakresie 0-maximum_probability.")
        if not self.sequence_multipliers:
            raise DefenseBalanceConfigurationError("sequence_multipliers nie może być puste.")
        previous = None
        for multiplier in self.sequence_multipliers:
            if multiplier <= 0 or multiplier > 1:
                raise DefenseBalanceConfigurationError("sequence_multipliers muszą być w zakresie 0-1.")
            if previous is not None and multiplier > previous:
                raise DefenseBalanceConfigurationError("sequence_multipliers muszą być malejące.")
            previous = multiplier
        if not self.tie_break_order:
            raise DefenseBalanceConfigurationError("tie_break_order nie może być puste.")
        normalized = []
        seen: set[DefenseType] = set()
        for item in self.tie_break_order:
            if not isinstance(item, DefenseType):
                item = DefenseType(str(item))
            if item in seen:
                raise DefenseBalanceConfigurationError("tie_break_order nie może zawierać duplikatów.")
            seen.add(item)
            normalized.append(item)
        object.__setattr__(self, "tie_break_order", tuple(normalized))

    def sequence_multiplier(self, index: int) -> float:
        if index < len(self.sequence_multipliers):
            return self.sequence_multipliers[index]
        return self.sequence_multipliers[-1]

    def tie_break_rank(self, defense_type: DefenseType) -> int:
        try:
            return self.tie_break_order.index(defense_type)
        except ValueError:
            return len(self.tie_break_order)

    def defense_probability(self, effective_value: float, attack_pressure: float, sequence_index: int) -> tuple[float, float, float, float]:
        contested = max(0.0, float(effective_value) - float(attack_pressure) * self.attack_pressure_weight)
        if contested <= 0:
            base_probability = 0.0
        else:
            raw_probability = contested / (contested + self.soft_cap)
            base_probability = raw_probability * self.maximum_probability
        sequence_multiplier = self.sequence_multiplier(sequence_index)
        final_probability = max(0.0, min(self.maximum_probability, base_probability * sequence_multiplier))
        if contested > 0:
            final_probability = max(self.minimum_probability, final_probability)
        return contested, base_probability, sequence_multiplier, final_probability


def defense_balance_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "defense_balance.json"


def _coerce_defense_type(value: object) -> DefenseType:
    text = str(value).strip().upper()
    try:
        return DefenseType(text)
    except ValueError as exc:
        raise DefenseBalanceConfigurationError(f"Nieznany typ obrony: {value}") from exc


def _as_float(value: object, field: str) -> float:
    if isinstance(value, bool):
        raise DefenseBalanceConfigurationError(f"{field} musi być liczbą.")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise DefenseBalanceConfigurationError(f"{field} nie może być puste.")
        try:
            return float(text)
        except ValueError as exc:
            raise DefenseBalanceConfigurationError(f"{field} musi być liczbą.") from exc
    raise DefenseBalanceConfigurationError(f"{field} musi być liczbą.")


def _load_policy_from_mapping(data: Mapping[str, object]) -> DefenseProbabilityPolicy:
    sequence_raw = data.get("sequence_multipliers", [1.0, 0.5, 0.25])
    tie_break_raw = data.get("tie_break_order", [DefenseType.SHIELD_BLOCK.value, DefenseType.PARRY.value, DefenseType.DODGE.value])
    if not isinstance(sequence_raw, list):
        raise DefenseBalanceConfigurationError("sequence_multipliers musi być listą.")
    if not isinstance(tie_break_raw, list):
        raise DefenseBalanceConfigurationError("tie_break_order musi być listą.")
    return DefenseProbabilityPolicy(
        soft_cap=_as_float(data.get("soft_cap", 70.0), "soft_cap"),
        maximum_probability=_as_float(data.get("maximum_probability", 0.85), "maximum_probability"),
        attack_pressure_weight=_as_float(data.get("attack_pressure_weight", 0.35), "attack_pressure_weight"),
        sequence_multipliers=tuple(_as_float(value, "sequence_multipliers") for value in sequence_raw),
        minimum_probability=_as_float(data.get("minimum_probability", 0.0), "minimum_probability"),
        tie_break_order=tuple(_coerce_defense_type(value) for value in tie_break_raw),
    )


def load_defense_probability_policy(path: str | Path | None = None) -> DefenseProbabilityPolicy:
    policy_path = Path(path) if path is not None else defense_balance_path()
    try:
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DefenseBalanceConfigurationError(f"Nie znaleziono pliku balansu obrony: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise DefenseBalanceConfigurationError(f"Niepoprawny JSON balansu obrony: {policy_path}") from exc
    if not isinstance(raw, Mapping):
        raise DefenseBalanceConfigurationError("Plik balansu obrony musi zawierać obiekt JSON.")
    return _load_policy_from_mapping(raw)


@lru_cache(maxsize=1)
def load_default_defense_probability_policy() -> DefenseProbabilityPolicy:
    return load_defense_probability_policy(defense_balance_path())


def default_defense_probability_policy() -> DefenseProbabilityPolicy:
    return load_default_defense_probability_policy()

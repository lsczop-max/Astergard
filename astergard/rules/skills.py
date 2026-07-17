from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).casefold().strip()


@dataclass(frozen=True, slots=True)
class SkillDefinition:
    key: str
    label: str
    category: str
    description: str
    aliases: tuple[str, ...] = ()
    base_threshold: int = 8
    threshold_step: int = 4


@dataclass(frozen=True, slots=True)
class SkillRules:
    minimum_level: int = 1
    maximum_level: int = 20
    progress_per_use: int = 1

    def threshold(self, definition: SkillDefinition, level: int) -> int:
        return definition.base_threshold + max(0, level - self.minimum_level) * definition.threshold_step

    def can_train(self, level: int) -> bool:
        return level < self.maximum_level


def _skill(
    key: str,
    label: str,
    category: str,
    description: str,
    *,
    aliases: tuple[str, ...] = (),
    base_threshold: int | None = None,
    threshold_step: int | None = None,
) -> SkillDefinition:
    if category == "combat":
        default_base = 8
        default_step = 4
    elif category == "social":
        default_base = 10
        default_step = 5
    else:
        default_base = 12
        default_step = 6
    return SkillDefinition(
        key=key,
        label=label,
        category=category,
        description=description,
        aliases=aliases,
        base_threshold=base_threshold if base_threshold is not None else default_base,
        threshold_step=threshold_step if threshold_step is not None else default_step,
    )


SKILL_DEFINITIONS: tuple[SkillDefinition, ...] = (
    _skill("bron_jednoraczna", "broń jednoręczna", "combat", "Walka bronią jednoręczną.", aliases=("bron_cieta",)),
    _skill("bron_dwureczna", "broń dwuręczna", "combat", "Mocne prowadzenie cięższej broni.", aliases=("bron_obuchowa",)),
    _skill("wlocznie", "włócznie", "combat", "Utrzymywanie dystansu i kontroli z włócznią."),
    _skill("tarcze", "tarcze", "combat", "Używanie tarczy do obrony i przepychania linii."),
    _skill("uniki", "uniki", "combat", "Unikanie ciosów i ustawianie się poza zasięgiem."),
    _skill("parowanie", "parowanie", "combat", "Blokowanie ciosów bronią lub odpowiednim ruchem."),
    _skill("dowodzenie", "dowodzenie", "social", "Wydawanie jasnych rozkazów i trzymanie ludzi w ryzach."),
    _skill("morale", "morale", "social", "Utrzymywanie ducha grupy i odporności psychicznej.", aliases=("wiara",)),
    _skill("obserwacja", "obserwacja", "social", "Wyłapywanie detali, zagrożeń i ruchu wokół.", aliases=("spostrzegawczosc",)),
    _skill("perswazja", "perswazja", "social", "Przekonywanie, targowanie i społeczne naciskanie.", aliases=("przekonywanie", "muzyka")),
    _skill("pierwsza_pomoc", "pierwsza pomoc", "utility", "Opatrunki, stabilizacja i szybka pomoc w terenie.", aliases=("cyrulictwo",)),
    _skill("kowalstwo", "kowalstwo", "utility", "Praca z metalem, naprawy i proste wyroby."),
    _skill("oprawianie", "oprawianie", "utility", "Zdejmowanie skór i obróbka zwierzyny po łowach."),
    _skill("gotowanie", "gotowanie / prowiant", "utility", "Przygotowanie jedzenia i racji na drogę."),
    _skill("handel", "handel", "utility", "Ocena wartości, wymiana i szybkie transakcje."),
)

REMOVED_SKILL_KEYS: frozenset[str] = frozenset({"luki", "kusze", "luczarstwo"})


_SKILL_BY_KEY: dict[str, SkillDefinition] = {definition.key: definition for definition in SKILL_DEFINITIONS}
_SKILL_BY_FOLD: dict[str, SkillDefinition] = {}
for definition in SKILL_DEFINITIONS:
    _SKILL_BY_FOLD[_fold(definition.key)] = definition
    _SKILL_BY_FOLD[_fold(definition.label)] = definition
    for alias in definition.aliases:
        _SKILL_BY_FOLD[_fold(alias)] = definition


def all_skill_definitions() -> list[SkillDefinition]:
    return list(SKILL_DEFINITIONS)


def resolve_skill(value: str) -> SkillDefinition:
    normalized = _fold(value)
    if not normalized:
        raise ValueError("Umiejętność nie może być pusta.")
    definition = _SKILL_BY_FOLD.get(normalized)
    if definition is None:
        raise ValueError(f"Nieznana umiejętność: {value}")
    return definition


def normalize_skill_key(value: str) -> str:
    return resolve_skill(value).key


def skill_label(value: str) -> str:
    try:
        return resolve_skill(value).label
    except ValueError:
        return value


def skill_category(value: str) -> str:
    return resolve_skill(value).category


def skill_definition(value: str) -> SkillDefinition:
    return resolve_skill(value)


def default_skill_state() -> dict[str, int]:
    return {"level": 1, "progress": 0}


def default_skill_values() -> dict[str, dict[str, int]]:
    return {definition.key: default_skill_state() for definition in SKILL_DEFINITIONS}


def canonicalize_skill_values(values: Mapping[str, Mapping[str, int]] | None) -> dict[str, dict[str, int]]:
    canonical = default_skill_values()
    unknown: dict[str, dict[str, int]] = {}
    if values:
        for raw_name, raw_state in values.items():
            raw_key = _fold(str(raw_name))
            if raw_key in REMOVED_SKILL_KEYS:
                continue
            try:
                definition = resolve_skill(raw_name)
            except ValueError:
                state = default_skill_state()
                state["level"] = int(raw_state.get("level", 1) or 1)
                state["progress"] = int(raw_state.get("progress", 0) or 0)
                unknown[str(raw_name)] = state
                continue
            state = canonical.setdefault(definition.key, default_skill_state())
            state["level"] = max(state["level"], int(raw_state.get("level", 1) or 1))
            state["progress"] = max(0, int(raw_state.get("progress", 0) or 0))
    for definition in SKILL_DEFINITIONS:
        state = canonical[definition.key]
        for alias in definition.aliases:
            canonical[alias] = state
    for removed_key in REMOVED_SKILL_KEYS:
        canonical.pop(removed_key, None)
    canonical.update(unknown)
    return canonical


def export_skill_values(values: Mapping[str, Mapping[str, int]] | None) -> dict[str, dict[str, int]]:
    normalized = canonicalize_skill_values(values)
    exported: dict[str, dict[str, int]] = {
        definition.key: dict(normalized[definition.key])
        for definition in SKILL_DEFINITIONS
    }
    canonical_keys = {definition.key for definition in SKILL_DEFINITIONS}
    alias_keys = {_fold(alias) for definition in SKILL_DEFINITIONS for alias in definition.aliases}
    for key, state in normalized.items():
        if key in canonical_keys:
            continue
        if _fold(key) in alias_keys:
            continue
        exported[key] = dict(state)
    return exported


def skill_threshold(name: str, level: int, rules: SkillRules | None = None) -> int:
    definition = resolve_skill(name)
    active_rules = rules or default_skill_rules()
    return active_rules.threshold(definition, level)


def apply_skill_use(
    values: dict[str, dict[str, int]],
    name: str,
    amount: int,
    *,
    rules: SkillRules | None = None,
) -> bool:
    if amount <= 0:
        return False
    active_rules = rules or default_skill_rules()
    definition = resolve_skill(name)
    state = values.setdefault(definition.key, default_skill_state())
    leveled = False
    state["progress"] += amount * active_rules.progress_per_use
    while active_rules.can_train(state["level"]):
        threshold = active_rules.threshold(definition, state["level"])
        if state["progress"] < threshold:
            break
        state["progress"] -= threshold
        state["level"] += 1
        leveled = True
    if not active_rules.can_train(state["level"]):
        state["progress"] = 0
    for alias in definition.aliases:
        values[alias] = state
    return leveled


def apply_starting_skill_bonus(
    values: dict[str, dict[str, int]],
    name: str,
    bonus: int,
    *,
    cap: int = 3,
) -> None:
    if bonus <= 0:
        return
    definition = resolve_skill(name)
    state = values.setdefault(definition.key, default_skill_state())
    state["level"] = min(cap, state["level"] + bonus)
    state["progress"] = 0
    for alias in definition.aliases:
        values[alias] = state


def skill_menu_text() -> str:
    lines = ["Dostępne umiejętności:"]
    for idx, definition in enumerate(SKILL_DEFINITIONS, start=1):
        lines.append(f"{idx}. {definition.label} - {definition.description}")
    return "\n".join(lines)


def default_skill_rules() -> SkillRules:
    return SkillRules()

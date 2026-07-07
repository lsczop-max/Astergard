from __future__ import annotations

import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field

from astergard.items.models import (
    Item,
    battle_axe,
    bowyer_tools,
    command_whistle,
    cyrulik_kit,
    dueling_blade,
    hunting_bow,
    light_crossbow,
    lute,
    prayer_book,
    smith_tools,
    starter_items,
    training_spear,
)


class ProfessionError(ValueError):
    pass


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).casefold().strip()


@dataclass(frozen=True, slots=True)
class ProfessionDefinition:
    key: str
    label: str
    kind: str
    description: str
    skill_bonuses: dict[str, int] = field(default_factory=dict)
    inventory_factory: Callable[[], list[Item]] = field(default_factory=lambda: starter_items)
    equipment_factory: Callable[[], dict[str, Item]] = field(default_factory=lambda: (lambda: {}))
    combat_style: str | None = None

    def inventory_items(self) -> list[Item]:
        return self.inventory_factory()

    def equipment_items(self) -> dict[str, Item]:
        return self.equipment_factory()


@dataclass(frozen=True, slots=True)
class ProfessionSelection:
    main_profession: str
    secondary_profession: str = ""

    def add_secondary(self, profession: str) -> "ProfessionSelection":
        if self.secondary_profession:
            raise ProfessionError("Możesz wybrać tylko jedną profesję dodatkową.")
        resolved = resolve_profession(profession, kind="secondary")
        if resolved.key == self.main_profession:
            raise ProfessionError("Profesja dodatkowa musi być inna niż główna.")
        return ProfessionSelection(self.main_profession, resolved.key)

    def to_dict(self) -> dict[str, str]:
        return {
            "main_profession": self.main_profession,
            "secondary_profession": self.secondary_profession,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ProfessionSelection":
        main = str(data.get("main_profession", "")).strip()
        secondary = str(data.get("secondary_profession", "")).strip()
        if not main:
            return cls("", "")
        return build_selection(main, secondary or None)

    def main_definition(self) -> ProfessionDefinition:
        return resolve_profession(self.main_profession, kind="main")

    def secondary_definition(self) -> ProfessionDefinition | None:
        if not self.secondary_profession:
            return None
        return resolve_profession(self.secondary_profession, kind="secondary")

    def summary(self) -> str:
        main = self.main_definition().label if self.main_profession else "brak"
        secondary_definition = self.secondary_definition()
        secondary = secondary_definition.label if secondary_definition is not None else "brak"
        return f"{main}" + (f" / {secondary}" if self.secondary_profession else "")


def _main_definition(
    key: str,
    label: str,
    description: str,
    *,
    skill_bonuses: dict[str, int] | None = None,
    equipment_factory: Callable[[], dict[str, Item]] | None = None,
    inventory_factory: Callable[[], list[Item]] | None = None,
    combat_style: str | None = None,
) -> ProfessionDefinition:
    return ProfessionDefinition(
        key=key,
        label=label,
        kind="main",
        description=description,
        skill_bonuses=skill_bonuses or {},
        equipment_factory=equipment_factory or (lambda: {}),
        inventory_factory=inventory_factory or (lambda: []),
        combat_style=combat_style,
    )


def _additional_definition(
    key: str,
    label: str,
    description: str,
    *,
    skill_bonuses: dict[str, int] | None = None,
    inventory_factory: Callable[[], list[Item]] | None = None,
) -> ProfessionDefinition:
    return ProfessionDefinition(
        key=key,
        label=label,
        kind="additional",
        description=description,
        skill_bonuses=skill_bonuses or {},
        inventory_factory=inventory_factory or (lambda: []),
        equipment_factory=lambda: {},
    )


MAIN_PROFESSIONS: dict[str, ProfessionDefinition] = {
    "wojownik": _main_definition(
        "wojownik",
        "wojownik",
        "Równy, uniwersalny start w walce wręcz.",
        skill_bonuses={"bron_jednoraczna": 2, "parowanie": 1},
        equipment_factory=lambda: {"prawa_reka": starter_items()[0]},
        combat_style="zrownowazony",
    ),
    "tarczownik": _main_definition(
        "tarczownik",
        "tarczownik",
        "Skupia się na obronie, tarczy i utrzymaniu pozycji.",
        skill_bonuses={"tarcze": 2, "parowanie": 1},
        equipment_factory=lambda: {"lewa_reka": starter_items()[1]},
        combat_style="defensywny",
    ),
    "wlocznik": _main_definition(
        "wlocznik",
        "włócznik",
        "Kontroluje dystans i utrzymuje przeciwnika na końcu broni.",
        skill_bonuses={"wlocznie": 2, "obserwacja": 1},
        equipment_factory=lambda: {"prawa_reka": training_spear()},
        combat_style="ostrozny",
    ),
    "szermierz": _main_definition(
        "szermierz",
        "szermierz",
        "Lekki, techniczny styl z naciskiem na tempo i parowanie.",
        skill_bonuses={"bron_jednoraczna": 2, "parowanie": 1, "uniki": 1},
        equipment_factory=lambda: {"prawa_reka": dueling_blade()},
        combat_style="ofensywny",
    ),
    "berserker": _main_definition(
        "berserker",
        "berserker",
        "Nastawiony na mocny cios i krótką, brutalną presję.",
        skill_bonuses={"bron_dwureczna": 2, "morale": 1},
        equipment_factory=lambda: {"prawa_reka": battle_axe()},
        combat_style="brutalny",
    ),
    "lucznik": _main_definition(
        "lucznik",
        "łucznik",
        "Szybki start na dystans i na obserwacji pola walki.",
        skill_bonuses={"luki": 2, "obserwacja": 1},
        equipment_factory=lambda: {"prawa_reka": hunting_bow()},
        combat_style="ofensywny",
    ),
    "kusznik": _main_definition(
        "kusznik",
        "kusznik",
        "Wolniejszy, ale stabilny styl z naciskiem na precyzję.",
        skill_bonuses={"kusze": 2, "obserwacja": 1},
        equipment_factory=lambda: {"prawa_reka": light_crossbow()},
        combat_style="defensywny",
    ),
}


ADDITIONAL_PROFESSIONS: dict[str, ProfessionDefinition] = {
    "dowodca": _additional_definition(
        "dowodca",
        "dowódca",
        "Porządkuje ludzi, wydaje polecenia i czyta sytuację.",
        skill_bonuses={"dowodzenie": 2, "morale": 1},
        inventory_factory=lambda: [command_whistle()],
    ),
    "kaplan": _additional_definition(
        "kaplan",
        "kapłan",
        "Działa społecznie i moralnie, nie jako użytkowy caster.",
        skill_bonuses={"morale": 2, "perswazja": 1},
        inventory_factory=lambda: [prayer_book()],
    ),
    "kowal": _additional_definition(
        "kowal",
        "kowal",
        "Zna warsztat, metal i cięższą pracę rękami.",
        skill_bonuses={"kowalstwo": 2, "handel": 1},
        inventory_factory=lambda: [smith_tools()],
    ),
    "cyrulik": _additional_definition(
        "cyrulik",
        "cyrulik",
        "Zajmuje się opatrunkami, pielęgnacją i prostą pomocą medyczną.",
        skill_bonuses={"pierwsza_pomoc": 2, "obserwacja": 1},
        inventory_factory=lambda: [cyrulik_kit()],
    ),
    "bard": _additional_definition(
        "bard",
        "bard",
        "Wzmacnia wpływ społeczny przez opowieść, rytm i pamięć.",
        skill_bonuses={"perswazja": 2, "dowodzenie": 1},
        inventory_factory=lambda: [lute()],
    ),
    "luczarz": _additional_definition(
        "luczarz",
        "łuczarz",
        "Dba o łuki, cięciwy i drobne naprawy sprzętu dystansowego.",
        skill_bonuses={"luczarstwo": 2, "obserwacja": 1},
        inventory_factory=lambda: [bowyer_tools()],
    ),
}


def all_profession_definitions() -> list[ProfessionDefinition]:
    return [*MAIN_PROFESSIONS.values(), *ADDITIONAL_PROFESSIONS.values()]


def resolve_profession(value: str, *, kind: str | None = None) -> ProfessionDefinition:
    normalized = _fold(value)
    if not normalized:
        raise ProfessionError("Profesja nie może być pusta.")
    if normalized.isdigit():
        index = int(normalized) - 1
        pool = list(MAIN_PROFESSIONS.values()) if kind in {None, "main"} else list(ADDITIONAL_PROFESSIONS.values())
        if 0 <= index < len(pool):
            return pool[index]
    pool = all_profession_definitions() if kind is None else (list(MAIN_PROFESSIONS.values()) if kind == "main" else list(ADDITIONAL_PROFESSIONS.values()))
    for definition in pool:
        if normalized in {_fold(definition.key), _fold(definition.label)}:
            return definition
    raise ProfessionError("Nieznana profesja.")


def build_selection(main: str, secondary: str | None = None) -> ProfessionSelection:
    main_definition = resolve_profession(main, kind="main")
    if secondary is None or not _fold(secondary) or _fold(secondary) in {"brak", "none", "0"}:
        return ProfessionSelection(main_definition.key)
    secondary_definition = resolve_profession(secondary, kind="secondary")
    if secondary_definition.key == main_definition.key:
        raise ProfessionError("Profesja dodatkowa musi być inna niż główna.")
    return ProfessionSelection(main_definition.key, secondary_definition.key)


def profession_menu_text() -> str:
    lines = ["Profesje główne:"]
    for index, definition in enumerate(MAIN_PROFESSIONS.values(), start=1):
        lines.append(f"{index}. {definition.label} - {definition.description}")
    lines.append("")
    lines.append("Profesje dodatkowe:")
    for index, definition in enumerate(ADDITIONAL_PROFESSIONS.values(), start=1):
        lines.append(f"{index}. {definition.label} - {definition.description}")
    lines.append("")
    lines.append("Profesja dodatkowa jest opcjonalna. Wpisz 0, brak albo pozostaw pusty wpis.")
    return "\n".join(lines)


def profession_label(value: str) -> str:
    try:
        return resolve_profession(value).label
    except ProfessionError:
        return value or "brak"

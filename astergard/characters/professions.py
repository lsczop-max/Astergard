from __future__ import annotations

import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field

from astergard.items.models import (
    Item,
    battle_axe,
    command_whistle,
    cyrulik_kit,
    dueling_blade,
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


LEGACY_MAIN_PROFESSION_MAP: dict[str, str] = {
    "lucznik": "wojownik",
    "kusznik": "wojownik",
}
LEGACY_ADDITIONAL_PROFESSION_KEYS: frozenset[str] = frozenset({"luczarz"})


MAIN_PROFESSIONS: dict[str, ProfessionDefinition] = {
    "wojownik": _main_definition(
        "wojownik",
        "wojownik",
        "Żyje prostym rytmem treningu, marszu i pierwszego ciosu, który ma ważyć więcej niż strach.",
        skill_bonuses={"bron_jednoraczna": 2, "parowanie": 1},
        equipment_factory=lambda: {"prawa_reka": starter_items()[0]},
        combat_style="zrownowazony",
    ),
    "tarczownik": _main_definition(
        "tarczownik",
        "tarczownik",
        "Trzyma linię tam, gdzie inni zaczynają się cofać, i uczy się cierpliwości w żelazie i drewnie.",
        skill_bonuses={"tarcze": 2, "parowanie": 1},
        equipment_factory=lambda: {"lewa_reka": starter_items()[1]},
        combat_style="defensywny",
    ),
    "wlocznik": _main_definition(
        "wlocznik",
        "włócznik",
        "Pilnuje dystansu, czyta ruch przeciwnika i korzysta z przestrzeni jak z własnej przewagi.",
        skill_bonuses={"wlocznie": 2, "obserwacja": 1},
        equipment_factory=lambda: {"prawa_reka": training_spear()},
        combat_style="ostrozny",
    ),
    "szermierz": _main_definition(
        "szermierz",
        "szermierz",
        "Wybiera tempo, balans i precyzję, a nie siłę; walczy jak ktoś, kto ufa ręce bardziej niż pancerzowi.",
        skill_bonuses={"bron_jednoraczna": 2, "parowanie": 1, "uniki": 1},
        equipment_factory=lambda: {"prawa_reka": dueling_blade()},
        combat_style="ofensywny",
    ),
    "berserker": _main_definition(
        "berserker",
        "berserker",
        "Rzuca ciężar ciała w walkę i liczy na to, że przeciwnik pęknie pierwszy.",
        skill_bonuses={"bron_dwureczna": 1, "morale": 1},
        equipment_factory=lambda: {"prawa_reka": battle_axe()},
        combat_style="brutalny",
    ),
}


ADDITIONAL_PROFESSIONS: dict[str, ProfessionDefinition] = {
    "dowodca": _additional_definition(
        "dowodca",
        "dowódca",
        "Umie ustawić ludzi tak, by z pojedynczego zamieszania zrobić plan.",
        skill_bonuses={"dowodzenie": 2, "morale": 1},
        inventory_factory=lambda: [command_whistle()],
    ),
    "kaplan": _additional_definition(
        "kaplan",
        "kapłan",
        "Łączy wiarę z obecnością, a jego siłą są słowa, rytuał i umiejętność uspokojenia tłumu.",
        skill_bonuses={"morale": 2, "perswazja": 1},
        inventory_factory=lambda: [prayer_book()],
    ),
    "kowal": _additional_definition(
        "kowal",
        "kowal",
        "Rozumie metal, ogień i ciężar pracy, którą widać w każdej niedoskonałej krawędzi.",
        skill_bonuses={"kowalstwo": 2, "handel": 1},
        inventory_factory=lambda: [smith_tools()],
    ),
    "cyrulik": _additional_definition(
        "cyrulik",
        "cyrulik",
        "Widzi ciało tak, jak inni widzą narzędzie: trzeba je opatrzyć, oczyścić i przywrócić do pracy.",
        skill_bonuses={"pierwsza_pomoc": 2, "obserwacja": 1},
        inventory_factory=lambda: [cyrulik_kit()],
    ),
    "bard": _additional_definition(
        "bard",
        "bard",
        "Zostawia po sobie piosenki, plotki i wspomnienia, które żyją dłużej niż jeden wieczór.",
        skill_bonuses={"perswazja": 2, "dowodzenie": 1},
        inventory_factory=lambda: [lute()],
    ),
}


def all_profession_definitions() -> list[ProfessionDefinition]:
    return [*MAIN_PROFESSIONS.values(), *ADDITIONAL_PROFESSIONS.values()]


def migrate_legacy_profession_value(value: str, *, kind: str | None = None) -> str:
    normalized = _fold(value)
    if not normalized:
        return ""
    if kind == "main":
        return LEGACY_MAIN_PROFESSION_MAP.get(normalized, normalized)
    if kind == "secondary":
        if normalized in LEGACY_MAIN_PROFESSION_MAP or normalized in LEGACY_ADDITIONAL_PROFESSION_KEYS:
            return ""
    return normalized


def migrate_legacy_profession_selection(main: str, secondary: str | None = None) -> tuple[str, str | None]:
    migrated_main = migrate_legacy_profession_value(main, kind="main")
    migrated_secondary = migrate_legacy_profession_value(secondary or "", kind="secondary") if secondary is not None else None
    if migrated_secondary == "":
        migrated_secondary = None
    return migrated_main, migrated_secondary


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
    lines.append("Wpisz numer albo nazwę. Profesja dodatkowa jest opcjonalna: użyj 0, brak albo zostaw puste pole.")
    return "\n".join(lines)


def profession_label(value: str) -> str:
    try:
        return resolve_profession(value).label
    except ProfessionError:
        return value or "brak"

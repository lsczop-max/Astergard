from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class LexicalEntry:
    lemma: str
    part_of_speech: str
    gender: str = ""
    animacy: str = ""
    declension_data: str = ""
    semantic_tags: tuple[str, ...] = ()
    register: str = "neutralny"
    region_tags: tuple[str, ...] = ()
    incompatibility_tags: tuple[str, ...] = ()
    forms: dict[str, str] = field(default_factory=dict)


class MorphologyProvider(Protocol):
    def inflect(self, lemma: str, case: str, number: str = "sg", gender: str = "") -> str:
        ...

    def agree_adjective(self, adjective: str, gender: str, number: str = "sg", case: str = "nom") -> str:
        ...


class DeterministicMorphologyProvider:
    def __init__(self, lexicon: dict[str, LexicalEntry] | None = None) -> None:
        self.lexicon = lexicon or default_lexicon()

    def inflect(self, lemma: str, case: str, number: str = "sg", gender: str = "") -> str:
        entry = self.lexicon.get(lemma)
        if entry is not None:
            form = entry.forms.get(f"{case}:{number}:{gender}") or entry.forms.get(f"{case}:{number}") or entry.forms.get(case)
            if form:
                return form
        return _fallback_inflect(lemma, case, number, gender)

    def agree_adjective(self, adjective: str, gender: str, number: str = "sg", case: str = "nom") -> str:
        entry = self.lexicon.get(adjective)
        if entry is not None:
            form = entry.forms.get(f"{case}:{number}:{gender}") or entry.forms.get(f"{gender}:{number}") or entry.forms.get(gender)
            if form:
                return form
        if number != "sg":
            return adjective
        if gender == "f":
            if adjective.endswith("y"):
                return adjective[:-1] + "a"
            if adjective.endswith("i"):
                return adjective[:-1] + "ia"
            return adjective + "a"
        if gender == "n":
            if adjective.endswith("y"):
                return adjective[:-1] + "e"
            return adjective + "e"
        return adjective


def _fallback_inflect(lemma: str, case: str, number: str, gender: str) -> str:
    base = lemma
    if case == "nom":
        return base
    if case == "gen":
        return base + "a" if gender == "m" else base
    if case == "loc":
        return base + "ie"
    if case == "acc":
        return base
    if case == "dat":
        return base + "owi"
    return base


def default_lexicon() -> dict[str, LexicalEntry]:
    entries = [
        LexicalEntry("brama", "noun", "f", forms={"nom": "brama", "loc": "bramie", "gen": "bramy"}),
        LexicalEntry("plac", "noun", "m", animacy="inanimate", forms={"nom": "plac", "loc": "placu", "gen": "placu"}),
        LexicalEntry("trakt", "noun", "m", animacy="inanimate", forms={"nom": "trakt", "loc": "trakcie", "gen": "traktu"}),
        LexicalEntry("studnia", "noun", "f", forms={"nom": "studnia", "loc": "studni", "gen": "studni"}),
        LexicalEntry("mur", "noun", "m", animacy="inanimate", forms={"nom": "mur", "loc": "murze", "gen": "muru"}),
        LexicalEntry("karczma", "noun", "f", forms={"nom": "karczma", "loc": "karczmie", "gen": "karczmy"}),
        LexicalEntry("kamienny", "adjective", forms={"m": "kamienny", "f": "kamienna", "n": "kamienne"}),
        LexicalEntry("mokry", "adjective", forms={"m": "mokry", "f": "mokra", "n": "mokre"}),
    ]
    return {entry.lemma: entry for entry in entries}

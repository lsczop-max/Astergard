from __future__ import annotations

from dataclasses import dataclass

from astergard.commands.polish import STOPWORDS, normalize_phrase


@dataclass(frozen=True)
class ParsedCommand:
    command: str
    argument: str | None
    index: int


class CommandParser:
    ORDINALS: dict[str, int] = {
        "pierwszy": 1, "pierwsza": 1, "pierwsze": 1, "1": 1,
        "drugi": 2, "druga": 2, "drugie": 2, "drugiego": 2, "2": 2,
        "trzeci": 3, "trzecia": 3, "trzecie": 3, "trzeciego": 3, "3": 3,
        "czwarty": 4, "czwarta": 4, "czwarte": 4, "czwartego": 4, "4": 4,
        "piaty": 5, "piata": 5, "piate": 5, "piatego": 5, "5": 5,
    }
    RELATION_COMMANDS = {"wloz", "włóż", "wkladaj", "wklad", "daj", "oddaj", "przekaz", "wez", "weź", "podnies", "podnieś", "podn", "wyjmij", "wyciagnij", "wyciągnij", "spojrz", "spójrz", "ob", "obejrzyj", "patrz", "popatrz", "zobacz", "przeloz", "przełóż", "przenies", "przenieś"}
    DIRECTIONS: dict[str, str] = {
        "n": "polnoc", "pn": "polnoc", "polnoc": "polnoc",
        "s": "poludnie", "pd": "poludnie", "poludnie": "poludnie",
        "e": "wschod", "wsch": "wschod", "wschod": "wschod",
        "w": "zachod", "z": "zachod", "zach": "zachod", "zachod": "zachod",
        "ne": "polnocny-wschod", "pnw": "polnocny-wschod",
        "nw": "polnocny-zachod", "pnz": "polnocny-zachod",
        "se": "poludniowy-wschod", "pdw": "poludniowy-wschod",
        "sw": "poludniowy-zachod", "pdz": "poludniowy-zachod",
        "g": "gora", "gora": "gora", "wejdz": "gora",
        "d": "dol", "dol": "dol", "zejdz": "dol",
    }
    MULTIWORD_COMMANDS: dict[tuple[str, str], str] = {
        ("do", "srodka"): "do srodka",
        ("na", "zewnatrz"): "na zewnatrz",
        ("na", "polnoc"): "polnoc",
        ("na", "poludnie"): "poludnie",
        ("na", "wschod"): "wschod",
        ("na", "zachod"): "zachod",
        ("na", "gore"): "gora",
        ("na", "dol"): "dol",
        ("w", "gore"): "gora",
        ("w", "dol"): "dol",
    }

    @staticmethod
    def tokenize(raw_input: str) -> list[str]:
        return normalize_phrase(raw_input).split()

    @classmethod
    def parse(cls, raw_input: str) -> ParsedCommand:
        tokens = cls.tokenize(raw_input)
        if not tokens:
            return ParsedCommand("", None, 1)
        if len(tokens) >= 2:
            multiword = cls.MULTIWORD_COMMANDS.get((tokens[0], tokens[1]))
            if multiword is not None:
                tokens = [multiword, *tokens[2:]]
        command = cls.DIRECTIONS.get(tokens[0], tokens[0])
        rest = tokens[1:]
        index = 1
        if rest and rest[0] in cls.ORDINALS:
            index = cls.ORDINALS[rest[0]]
            rest = rest[1:]
        preserve_relation = command in cls.RELATION_COMMANDS
        if command in {"spojrz", "ob", "obejrzyj", "patrz", "popatrz", "zobacz"}:
            preserve_relation = any(token in {"w", "we"} for token in rest)
        if not preserve_relation:
            rest = [token for token in rest if token not in STOPWORDS]
        argument = " ".join(rest) if rest else None
        return ParsedCommand(command, argument, index)

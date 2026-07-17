from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Literal

from astergard.combat.actions import CombatOutcome, DefenseResolution
from astergard.combat.events import CombatEvent, body_part_label, weapon_family_label

Perspective = Literal["attacker", "defender", "observer"]


@dataclass(slots=True)
class NarrationMemory:
    recent_sentences: dict[str, deque[str]]
    recent_keys: dict[str, deque[str]]

    def __init__(self, window: int = 4) -> None:
        self.recent_sentences = defaultdict(lambda: deque(maxlen=window))
        self.recent_keys = defaultdict(lambda: deque(maxlen=window))

    def remember(self, perspective: str, key: str, sentence: str) -> None:
        self.recent_keys[perspective].append(key)
        self.recent_sentences[perspective].append(sentence)

    def seen(self, perspective: str, key: str) -> bool:
        return key in self.recent_keys[perspective]


class CombatNarrator:
    def __init__(self, memory: NarrationMemory | None = None) -> None:
        self.memory = memory or NarrationMemory()

    def render_outcome(self, outcome: CombatOutcome, event: CombatEvent, perspective: Perspective) -> str:
        if outcome.result_type.value == "INVALID" and outcome.reason_code:
            sentence = self.render(event, perspective)
            return sentence if sentence else "Akcja nie może zostać wykonana."
        if outcome.defense_outcome is not None and outcome.defense_outcome.successful_defense:
            if outcome.defense_outcome.resolution == DefenseResolution.DODGED:
                return self._dodge(event, perspective)
            if outcome.defense_outcome.resolution == DefenseResolution.BLOCKED:
                return self._block(event, perspective)
            if outcome.defense_outcome.resolution == DefenseResolution.PARRIED:
                return self._parry(event, perspective)
        if outcome.result_type.value == "MISS":
            return self._miss(event, perspective)
        sentence = self.render(event, perspective)
        return sentence

    def render(self, event: CombatEvent, perspective: Perspective) -> str:
        key = self._key(event, perspective)
        sentence = self._render(event, perspective)
        reaction_intro = self._reaction_intro(event, perspective)
        if reaction_intro:
            sentence = f"{reaction_intro} {sentence}"
        if self.memory.seen(perspective, key):
            alternate = self._alternate(event, perspective, key)
            if alternate:
                sentence = alternate
                key = key + ":alt"
        self.memory.remember(perspective, key, sentence)
        return sentence

    def _key(self, event: CombatEvent, perspective: Perspective) -> str:
        return ":".join(
            [
                event.action_type,
                event.result,
                event.defense,
                event.reaction_type or "none",
                event.weapon_family,
                event.body_location or event.hit_location or "none",
                perspective,
            ]
        )

    def _reaction_intro(self, event: CombatEvent, perspective: Perspective) -> str:
        if event.action_type != "REACTION":
            return ""
        if (event.reaction_type or "").casefold() != "riposte":
            return ""
        if perspective == "attacker":
            return "Po zbiciu ciosu natychmiast wyprowadzasz ripostę."
        if perspective == "defender":
            return "Po zbiciu twojego ciosu natychmiast wyprowadza ripostę."
        return f"Po zbiciu ciosu {event.attacker_name} natychmiast wyprowadza ripostę."

    def _render(self, event: CombatEvent, perspective: Perspective) -> str:
        if event.result == "miss":
            return self._miss(event, perspective)
        if event.result == "dodge":
            return self._dodge(event, perspective)
        if event.result == "block":
            return self._block(event, perspective)
        if event.result == "parry":
            return self._parry(event, perspective)
        if event.result == "armor":
            return self._armor(event, perspective)
        if event.result in {"glancing", "hit", "critical"}:
            return self._hit(event, perspective)
        if event.result == "defeated":
            return self._defeated(event, perspective)
        return self._generic(event, perspective)

    def _alternate(self, event: CombatEvent, perspective: Perspective, key: str) -> str | None:
        if event.result in {"hit", "critical"}:
            body = body_part_label(event.body_location or event.hit_location)
            return {
                "attacker": f"{event.attacker_name} prowadzi {event.technique} i zostawia {event.defender_name} z {body} odkrytą.",
                "defender": f"{event.attacker_name} trafia w twoją {body}, wykorzystując krótkie odsłonięcie.",
                "observer": f"{event.attacker_name} wykorzystuje odsłonięcie i dosięga {event.defender_name} w {body}.",
            }.get(perspective)
        return None

    def _style_phrase(self, event: CombatEvent) -> str:
        style = event.narrative_tags[0] if event.narrative_tags else ""
        return {
            "ofensywny": "ofensywnym natarciem",
            "defensywny": "defensywną postawą",
            "ostrozny": "ostrożnym ruchem",
            "brutalny": "brutalnym zamachem",
            "zrownowazony": "zrównoważonym ruchem",
        }.get(style, "")

    def _actor(self, perspective: Perspective, event: CombatEvent) -> tuple[str, str, str]:
        if perspective == "attacker":
            return "Wyprowadzasz", "cięcie", "przeciwnika"
        if perspective == "defender":
            return f"{event.attacker_name} wyprowadza", "atak", "w twoją stronę"
        return f"{event.attacker_name} wyprowadza", "atak", f"na {event.defender_name}"

    def _subject(self, perspective: Perspective, event: CombatEvent) -> str:
        if perspective == "attacker":
            return event.defender_name
        if perspective == "defender":
            return "ty"
        return event.defender_name

    def _miss(self, event: CombatEvent, perspective: Perspective) -> str:
        if perspective == "attacker":
            return f"Wyprowadzasz {event.technique}, lecz {event.defender_name} wymyka się z zasięgu."
        if perspective == "defender":
            return f"{event.attacker_name} wyprowadza {event.technique}, lecz w ostatniej chwili zrywasz rytm jego ruchu."
        return f"{event.attacker_name} wyprowadza {event.technique}, lecz {event.defender_name} pozostaje poza zasięgiem."

    def _dodge(self, event: CombatEvent, perspective: Perspective) -> str:
        if perspective == "attacker":
            return f"Wyprowadzasz {event.technique}, ale {event.defender_name} odskakuje i gubi twój rytm."
        if perspective == "defender":
            return f"{event.attacker_name} wyprowadza {event.technique}, a ty odskakujesz w ostatnim ułamku chwili."
        return f"{event.attacker_name} naciera {event.technique}, lecz {event.defender_name} odskakuje z linii ataku."

    def _block(self, event: CombatEvent, perspective: Perspective) -> str:
        shield = "tarczą" if event.defense == "block" else "osłoną"
        if perspective == "attacker":
            return f"Wyprowadzasz {event.technique}, lecz {event.defender_name} tłumi impet {shield}."
        if perspective == "defender":
            return f"{event.attacker_name} wyprowadza {event.technique}, a ty zasłaniasz się {shield} i łamiesz impet ciosu."
        return f"{event.attacker_name} wyprowadza {event.technique}, lecz {event.defender_name} tłumi impet {shield}."

    def _parry(self, event: CombatEvent, perspective: Perspective) -> str:
        if perspective == "attacker":
            return f"Wyprowadzasz {event.technique}, lecz {event.defender_name} paruje i zbija atak własnym orężem."
        if perspective == "defender":
            return f"{event.attacker_name} wyprowadza {event.technique}, a ty parujesz i zbijasz cios własnym orężem."
        return f"{event.attacker_name} wyprowadza {event.technique}, ale {event.defender_name} paruje i zbija go własnym orężem."

    def _armor(self, event: CombatEvent, perspective: Perspective) -> str:
        family = weapon_family_label(event.weapon_family)
        body = body_part_label(event.body_location or event.hit_location)
        armor = event.armor_name or "pancerz"
        if perspective == "attacker":
            return f"Wyprowadzasz {event.technique}, lecz {armor} na {event.defender_name} przyjmuje {family} i łagodzi cios w {body}."
        if perspective == "defender":
            return f"{event.attacker_name} wyprowadza {event.technique}, lecz {event.armor_name or 'pancerz'} przyjmuje impet w {body}."
        return f"{event.attacker_name} wyprowadza {event.technique}, lecz {armor} przyjmuje impet i odpycha go od {event.defender_name}."

    def _hit(self, event: CombatEvent, perspective: Perspective) -> str:
        body = body_part_label(event.body_location or event.hit_location)
        family = weapon_family_label(event.weapon_family)
        family_phrase = {
            "miecz": "mieczem",
            "sztylet": "sztyletem",
            "topór": "toporem",
            "maczuga": "maczugą",
            "młot": "młotem",
            "włócznia": "włócznią",
            "broń drzewcowa": "drzewcem",
            "łuk": "łukiem",
            "kusza": "kuszą",
            "broń improwizowana": "improwizowaną bronią",
            "walka bez broni": "gołą ręką",
        }.get(family, "orężem")
        if perspective == "attacker":
            style_phrase = self._style_phrase(event)
            prefix = f"{style_phrase} " if style_phrase else ""
            return f"Wyprowadzasz {prefix}{event.technique} {family_phrase} i dosięgasz {event.defender_name} w {body}."
        if perspective == "defender":
            style_phrase = self._style_phrase(event)
            prefix = f"{style_phrase} " if style_phrase else ""
            return f"{event.attacker_name} dosięga cię {prefix}{event.technique} {family_phrase} w {body}."
        style_phrase = self._style_phrase(event)
        prefix = f"{style_phrase} " if style_phrase else ""
        return f"{event.attacker_name} dosięga {event.defender_name} {prefix}{event.technique} {family_phrase} w {body}."

    def _defeated(self, event: CombatEvent, perspective: Perspective) -> str:
        if perspective == "attacker":
            return f"{event.defender_name} chwieje się po ostatnim trafieniu i pada bez sił."
        if perspective == "defender":
            return "Ostatni cios odbiera ci siły i wszystko nagle blednie."
        return f"{event.defender_name} osuwa się po ostatnim trafieniu i przestaje walczyć."

    def _generic(self, event: CombatEvent, perspective: Perspective) -> str:
        if perspective == "attacker":
            return f"Wyprowadzasz {event.technique}, a starcie toczy się dalej."
        if perspective == "defender":
            return f"{event.attacker_name} naciera, a ty trwasz jeszcze na nogach."
        return f"{event.attacker_name} i {event.defender_name} dalej mierzą się w walce."

from __future__ import annotations

from dataclasses import dataclass

from astergard.location_narrative.critic import CritiqueResult
from astergard.location_narrative.models import PermanentLocationFacts


@dataclass(slots=True)
class DescriptionReviser:
    def revise(self, draft: str, critique: CritiqueResult, facts: PermanentLocationFacts) -> tuple[str, tuple[str, ...]]:
        text = draft
        changes: list[str] = []
        banned_replacements = {
            "wydaje się": "",
            "jakby": "",
            "mroczna atmosfera": "",
            "czas odcisnął swoje piętno": "",
            "świadek minionych wydarzeń": "",
            "można odnieść wrażenie": "",
        }
        for needle, replacement in banned_replacements.items():
            if needle in text.lower():
                text = self._replace_case_insensitive(text, needle, replacement)
                changes.append(f"removed:{needle}")
        if text.count(".") < 2:
            text = text.rstrip(".") + ". " + self._add_closure(facts)
            changes.append("added_sentence")
        if len(text.split()) > 130:
            words = text.split()
            text = " ".join(words[:130]).rstrip(".") + "."
            changes.append("trimmed_length")
        if any(token in text.lower() for token in (" ty ", " ci ", " ciebie ", " tobie ")):
            text = text.replace(" ty ", " ").replace(" ci ", " ").replace(" ciebie ", " ").replace(" tobie ", " ")
            changes.append("removed_second_person")
        return text.strip(), tuple(changes)

    def _replace_case_insensitive(self, text: str, needle: str, replacement: str) -> str:
        lowered = text.lower()
        index = lowered.find(needle)
        if index < 0:
            return text
        return text[:index] + replacement + text[index + len(needle) :]

    def _add_closure(self, facts: PermanentLocationFacts) -> str:
        if facts.actual_exits:
            return f"Stąd można ruszyć {facts.actual_exits[0]}."
        return "Przestrzeń pozostaje spójna z widocznym układem."

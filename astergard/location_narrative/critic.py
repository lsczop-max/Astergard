from __future__ import annotations

from dataclasses import dataclass

from astergard.location_narrative.models import PermanentLocationFacts, ValidationReport
from astergard.location_narrative.validator import DescriptionValidator


@dataclass(slots=True)
class CritiqueResult:
    report: ValidationReport
    issues: tuple[str, ...]
    score: int


@dataclass(slots=True)
class DescriptionCritic:
    validator: DescriptionValidator

    def critique(self, text: str, facts: PermanentLocationFacts, existing_texts: tuple[str, ...] = ()) -> CritiqueResult:
        report = self.validator.validate(text, facts, existing_texts)
        issues = list(report.critical_errors)
        issues.extend(report.warnings)
        score = report.final_score
        if report.critical_errors:
            score = 0
        return CritiqueResult(report=report, issues=tuple(dict.fromkeys(issues)), score=score)

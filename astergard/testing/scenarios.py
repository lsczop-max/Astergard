from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from astergard.characters.models import Character
from astergard.testing.harness import CommandTranscript, TestGameHarness

AssertionFunc = Callable[[CommandTranscript], None]


@dataclass(frozen=True, slots=True)
class ScenarioStep:
    command: str
    expect_contains: tuple[str, ...] = ()
    assert_func: AssertionFunc | None = None


@dataclass(slots=True)
class ScenarioResult:
    name: str
    transcripts: list[CommandTranscript] = field(default_factory=list)

    @property
    def output_text(self) -> str:
        return "\n".join(t.output for t in self.transcripts)


class ScenarioRunner:
    """Runs command regression scenarios through the real dispatcher."""

    def __init__(self, harness: TestGameHarness) -> None:
        self.harness = harness

    async def run(self, name: str, character: Character, steps: list[ScenarioStep]) -> ScenarioResult:
        result = ScenarioResult(name=name)
        for step in steps:
            transcript = await self.harness.execute(character, step.command)
            for expected in step.expect_contains:
                if expected not in transcript.output:
                    raise AssertionError(
                        f"Scenario {name!r}, command {step.command!r}: expected {expected!r} in {transcript.output!r}"
                    )
            if step.assert_func is not None:
                step.assert_func(transcript)
            result.transcripts.append(transcript)
        return result

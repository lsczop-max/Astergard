#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astergard.testing import ScenarioRunner, ScenarioStep, TestGameHarness


async def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        with TestGameHarness(str(Path(tmp) / "regression.db")) as harness:
            character = harness.create_character("regression")
            runner = ScenarioRunner(harness)
            result = await runner.run(
                "basic_gameplay",
                character,
                [
                    ScenarioStep("spojrz", ("Widoczne wyjścia",)),
                    ScenarioStep("cechy", ("Kondycja",)),
                    ScenarioStep("ekwipunek", ("Wyposażenie",)),
                    ScenarioStep("pomoc", ("Dostępne komendy",)),
                ],
            )
            print(f"Scenario: {result.name}")
            for transcript in result.transcripts:
                print(f"> {transcript.command}")
                print(transcript.output.splitlines()[0] if transcript.output else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

from __future__ import annotations

import asyncio
import unittest

from astergard.testing import FakeReader, FakeWriter, ScenarioRunner, ScenarioStep, TestGameHarness


class TestingEngineTests(unittest.TestCase):
    def test_fake_writer_captures_text_and_close_state(self) -> None:
        async def run() -> None:
            writer = FakeWriter()
            writer.write(b"abc")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            self.assertEqual(writer.text(), "abc")
            self.assertEqual(writer.drains, 1)
            self.assertTrue(writer.closed)

        asyncio.run(run())

    def test_fake_reader_returns_lines_and_eof(self) -> None:
        async def run() -> None:
            reader = FakeReader.from_text_lines(["pierwsza", "druga"])
            self.assertFalse(reader.at_eof())
            self.assertEqual(await reader.readline(), b"pierwsza\n")
            self.assertEqual(await reader.readline(), b"druga\n")
            self.assertTrue(reader.at_eof())

        asyncio.run(run())

    def test_harness_executes_real_dispatcher_command(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                character = harness.create_character("tester")
                transcript = await harness.execute(character, "spojrz")
                self.assertEqual(transcript.command, "spojrz")
                self.assertIn("Widoczne wyjścia", transcript.output)

        asyncio.run(run())

    def test_scenario_runner_validates_expected_output(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                character = harness.create_character("scenario")
                result = await ScenarioRunner(harness).run(
                    "sanity",
                    character,
                    [
                        ScenarioStep("cechy", ("Kondycja",)),
                        ScenarioStep("pomoc", ("Dostępne komendy",)),
                    ],
                )
                self.assertEqual(len(result.transcripts), 2)
                self.assertIn("Dostępne komendy", result.output_text)

        asyncio.run(run())

    def test_harness_save_reload_roundtrip(self) -> None:
        with TestGameHarness() as harness:
            character = harness.create_character("persisted")
            character.gold = 123
            reloaded = harness.save_and_reload_character(character)
            self.assertEqual(reloaded.username, "persisted")
            self.assertEqual(reloaded.gold, 123)


if __name__ == "__main__":
    unittest.main()

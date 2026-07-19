from __future__ import annotations

import asyncio
import json
import re
import unittest
from pathlib import Path
from typing import TypedDict, cast

from astergard.testing.harness import TestGameHarness
from astergard.world.manager import WorldManager


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "docs" / "audits" / "D58_2_CENTRUM_PILOT_DATA.json"
EXPECTED_IDS = [14, 15, 2, 13, 4, 12, 47, 37, 55, 59]
RAW_ALIAS_PATTERN = re.compile(r"\b[a-z]+_[a-z0-9_]+\b")
OLD_TEMPLATE_MARKERS = (
    "prowadzi dalej",
    "ciągnie się dalej",
    "niknie w ciemności",
    "można odnieść wrażenie",
    "zdaje się",
    "to miejsce",
    "miasto zaczyna się",
    "teren sam wybiera",
    "nie potrzebuje",
)
NON_DETERMINISTIC_PREFIXES = (
    "Karczmarz",
    "Strażnik",
    "Kowal",
    "Podróżny",
    "Pies",
    "Gdzieś",
    "Ktoś",
)

EXPECTED_INSPECTABLES = {
    14: {"lada karczmarz", "kominek ogien", "lawy stol"},
    15: {"ludzie przechodnie mieszkancy mieszkańcy", "beczki skrzynie", "stol kufle"},
    2: {"studnia fontanna", "ogloszenia tablica słup", "straz żołnierze ludzie"},
    13: {"slady ślady tropy", "sciana ściana mur", "beczki"},
    4: {"okna okiennice", "drzwi prog próg", "fasady podcienia"},
    12: {"kowadlo młot", "ogien palenisko", "narzedzia szczypce"},
    47: {"kramy stragany", "wagi odważniki", "handel kupcy"},
    37: {"oltarz ołtarz", "swiece wosk", "kaplani modlitwa"},
    55: {"drogi koleiny", "kamień graniczny", "słup drogowy"},
    59: {"wstążki monety", "nisza", "próg bruku"},
}

EXPECTED_EXITS = {
    14: {"polnoc": 5, "poludnie": 15, "zachod": 13},
    15: {"polnoc": 14, "wschod": 16},
    2: {"zachod": 1, "wschod": 3, "poludnie": 10},
    13: {"zachod": 12, "wschod": 14, "polnocny-wschod": 4},
    4: {"zachod": 3, "poludniowy-wschod": 5, "poludniowy-zachod": 13},
    12: {"zachod": 11, "wschod": 13, "poludniowy-zachod": 22},
    47: {"polnoc": 46, "zachod": 48, "poludniowy-wschod": 52},
    37: {"polnoc": 36, "zachod": 38},
    55: {"polnoc": 54, "zachod": 56, "poludniowy-wschod": 59, "wschod": 95},
    59: {"zachod": 58, "polnocny-zachod": 55, "poludniowy-wschod": 135},
}


class AuditCard(TypedDict):
    location_id: int
    spojrz_after: str


class AuditData(TypedDict):
    selected_location_ids: list[int]
    cards: list[AuditCard]


def _load_data() -> AuditData:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return cast(AuditData, raw)


def _render_pilot() -> dict[int, str]:
    async def run() -> dict[int, str]:
        with TestGameHarness() as harness:
            character = harness.create_character("pilot", room_id=EXPECTED_IDS[0])
            rendered: dict[int, str] = {}
            for room_id in EXPECTED_IDS:
                character.room_id = room_id
                transcript = await harness.execute(character, "spojrz")
                rendered[room_id] = transcript.output
            return rendered

    return asyncio.run(run())


def _stable_render(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith(NON_DETERMINISTIC_PREFIXES):
            continue
        lines.append(line)
    return "\n".join(lines)


class D582CentrumPilotTests(unittest.TestCase):
    def test_artifact_records_exact_ten_locations(self) -> None:
        data = _load_data()
        self.assertEqual(data["selected_location_ids"], EXPECTED_IDS)
        self.assertEqual(len(data["cards"]), 10)

    def test_pilot_renders_match_the_saved_audit(self) -> None:
        data = _load_data()
        expected_render = {card["location_id"]: _stable_render(card["spojrz_after"]) for card in data["cards"]}

        first = _render_pilot()
        second = _render_pilot()

        self.assertEqual({rid: _stable_render(text) for rid, text in first.items()}, {rid: _stable_render(text) for rid, text in second.items()})
        self.assertEqual({rid: _stable_render(text) for rid, text in first.items()}, expected_render)

    def test_pilot_rooms_keep_their_landmarks_and_inspectables(self) -> None:
        world = WorldManager()
        world.generate_world()
        self.assertEqual(len(world.locations), 500)

        for room_id in EXPECTED_IDS:
            location = world.locations[room_id]
            expected = EXPECTED_INSPECTABLES[room_id]
            self.assertTrue(expected.issubset(location.inspectables.keys()), (room_id, location.inspectables.keys()))
            self.assertGreaterEqual(len(location.inspectables), 3)
            expected_exits = EXPECTED_EXITS[room_id]
            self.assertEqual(
                {direction: exit_.target_room for direction, exit_ in location.exits.items()},
                expected_exits,
                room_id,
            )

    def test_pilot_renders_do_not_reintroduce_old_templates_or_raw_aliases(self) -> None:
        rendered = _render_pilot()
        for text in rendered.values():
            lowered = text.lower()
            self.assertFalse(any(marker in lowered for marker in OLD_TEMPLATE_MARKERS), text)
            self.assertIsNone(RAW_ALIAS_PATTERN.search(text), text)

    def test_pilot_does_not_bring_back_ranged_weapon_tokens(self) -> None:
        world = WorldManager()
        world.generate_world()
        selected_blob = " ".join(
            " ".join([location.name, location.description, *location.inspectables.keys()])
            for room_id, location in world.locations.items()
            if room_id in EXPECTED_IDS
        ).lower()
        for token in ("łuk", "luk", "kusza", "kusz", "archer", "łucznik", "crossbow", "bow"):
            self.assertNotIn(token, selected_blob)


if __name__ == "__main__":
    unittest.main()

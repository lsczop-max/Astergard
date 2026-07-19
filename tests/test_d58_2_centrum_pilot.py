from __future__ import annotations

import asyncio
import json
import hashlib
import random
import re
import unittest
from pathlib import Path
from typing import TypedDict, cast

from astergard.testing.harness import TestGameHarness
from astergard.world.content import make_content_pack
from astergard.world.manager import WorldManager


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "docs" / "audits" / "D58_2_CENTRUM_PILOT_DATA.json"
BASELINE_SIGNATURES_PATH = ROOT / "tests" / "fixtures" / "d58_2_develop_content_signatures.json"
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
        state = random.getstate()
        random.seed(0)
        try:
            with TestGameHarness() as harness:
                character = harness.create_character("pilot", room_id=EXPECTED_IDS[0])
                rendered: dict[int, str] = {}
                for room_id in EXPECTED_IDS:
                    character.room_id = room_id
                    transcript = await harness.execute(character, "spojrz")
                    rendered[room_id] = transcript.output
                return rendered
        finally:
            random.setstate(state)

    return asyncio.run(run())


def _content_signature(content) -> tuple[object, ...]:
    return (
        content.room_id,
        content.name,
        content.description,
        tuple(sorted(content.inspectables.items())),
        tuple(sorted(getattr(content, "forms", {}).items())),
        tuple(sorted((direction, tuple(sorted(forms.items()))) for direction, forms in getattr(content, "exit_forms", {}).items())),
        tuple(sorted(getattr(content, "exit_kinds", {}).items())),
        getattr(content, "scene_profile", ""),
        tuple(item.name for item in content.items),
        tuple((item.name, amount) for item, amount in content.hidden_items),
    )


def _normalize_signature(value):
    if isinstance(value, dict):
        return {key: _normalize_signature(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_normalize_signature(item) for item in value]
    if isinstance(value, list):
        return [_normalize_signature(item) for item in value]
    return value


def _signature_hash(content) -> str:
    signature = _normalize_signature(_content_signature(content))
    payload = json.dumps(signature, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


EXPECTED_EXIT_KINDS = {
    14: {"polnoc": "drzwi", "poludnie": "drzwi", "zachod": "drzwi"},
    15: {"polnoc": "drzwi", "wschod": "drzwi"},
    2: {"zachod": "ulica", "wschod": "ulica", "poludnie": "drzwi"},
    13: {"zachod": "drzwi", "wschod": "drzwi", "polnocny-wschod": "przejście"},
    4: {"zachod": "przejście", "poludniowy-wschod": "przejście", "poludniowy-zachod": "przejście"},
    12: {"zachod": "drzwi", "wschod": "ulica", "poludniowy-zachod": "przejście"},
    47: {"polnoc": "przejście", "zachod": "przejście", "poludniowy-wschod": "przejście"},
    37: {"polnoc": "drzwi", "zachod": "przejście"},
    55: {"polnoc": "ulica", "zachod": "trakt", "poludniowy-wschod": "trakt", "wschod": "furta"},
    59: {"zachod": "trakt", "polnocny-zachod": "trakt", "poludniowy-wschod": "trakt"},
}

EXPECTED_EXIT_FORMS = {
    14: {
        "polnoc": {"prep": "w stronę", "genitive": "Zaułka za Karczmą"},
        "poludnie": {"prep": "do", "genitive": "Tyłów Karczmy"},
        "zachod": {"prep": "ku", "locative": "Szerokiej Brukowanej"},
    },
    15: {
        "polnoc": {"prep": "do", "genitive": "Karczmy pod Żurawiem"},
        "wschod": {"prep": "ku", "locative": "Małej Stajni"},
    },
    2: {
        "zachod": {"prep": "ku", "locative": "Placu Przed Wartownią"},
        "wschod": {"prep": "ku", "locative": "Bocznym Uliczkom Placu"},
        "poludnie": {"prep": "do", "genitive": "Domu Snycerza"},
    },
    13: {
        "zachod": {"prep": "do", "genitive": "Kuźni przy Murze"},
        "wschod": {"prep": "do", "genitive": "Karczmy pod Żurawiem"},
        "polnocny-wschod": {"prep": "ku", "locative": "Podcieniom Kupieckim"},
    },
    4: {
        "zachod": {"prep": "ku", "locative": "Bocznym Uliczkom Placu"},
        "poludniowy-wschod": {"prep": "w stronę", "genitive": "Zaułka za Karczmą"},
        "poludniowy-zachod": {"prep": "ku", "locative": "Szerokiej Brukowanej"},
    },
    12: {
        "zachod": {"prep": "do", "genitive": "Starego Spichlerza"},
        "wschod": {"prep": "ku", "locative": "Szerokiej Brukowanej"},
        "poludniowy-zachod": {"prep": "do", "genitive": "Jatek Rzeźników"},
    },
    47: {
        "polnoc": {"prep": "do", "genitive": "Kramu Świecarza"},
        "zachod": {"prep": "do", "genitive": "Warsztatu Cieśli"},
        "poludniowy-wschod": {"prep": "do", "genitive": "Składu Drewna"},
    },
    37: {
        "polnoc": {"prep": "do", "genitive": "Przedsionka Świątyni"},
        "zachod": {"prep": "ku", "locative": "Portowi Rzecznemu"},
    },
    55: {
        "polnoc": {"prep": "do", "genitive": "Zaułka Czeladników"},
        "zachod": {"prep": "do", "genitive": "Opuszczonej Chaty"},
        "poludniowy-wschod": {"prep": "do", "genitive": "Kapliczki Przydrożnej"},
        "wschod": {"prep": "do", "genitive": "Wschodniej Furty Łowców"},
    },
    59: {
        "zachod": {"prep": "do", "genitive": "Pastwisk"},
        "polnocny-zachod": {"prep": "do", "genitive": "Rozstajów Traktów"},
        "poludniowy-wschod": {"prep": "ku", "locative": "Kapliczce Podróżnych za Murem"},
    },
}


def _load_baseline_signatures() -> dict[int, str]:
    raw = json.loads(BASELINE_SIGNATURES_PATH.read_text(encoding="utf-8"))
    room_signatures = raw["room_signatures"]
    return {int(room_id): signature for room_id, signature in room_signatures.items()}


class D582CentrumPilotTests(unittest.TestCase):
    def test_artifact_records_exact_ten_locations(self) -> None:
        data = _load_data()
        self.assertEqual(data["selected_location_ids"], EXPECTED_IDS)
        self.assertEqual(len(data["cards"]), 10)

    def test_pilot_renders_match_the_saved_audit(self) -> None:
        data = _load_data()
        expected_render = {card["location_id"]: card["spojrz_after"] for card in data["cards"]}

        first = _render_pilot()
        second = _render_pilot()

        self.assertEqual(first, second)
        self.assertEqual(first, expected_render)

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
            self.assertEqual({direction: exit_.kind for direction, exit_ in location.exits.items()}, EXPECTED_EXIT_KINDS[room_id], room_id)
            self.assertEqual(location.exit_forms, EXPECTED_EXIT_FORMS[room_id], room_id)

    def test_pilot_renders_do_not_reintroduce_old_templates_or_raw_aliases(self) -> None:
        rendered = _render_pilot()
        for text in rendered.values():
            lowered = text.lower()
            self.assertFalse(any(marker in lowered for marker in OLD_TEMPLATE_MARKERS), text)
            self.assertIsNone(RAW_ALIAS_PATTERN.search(text), text)
            self.assertNotIn("Świt rozprasza ciemność.", text)
            self.assertNotIn("Lato trzyma ciepło.", text)
            self.assertNotIn("Gdzieś dalej trzaśnie gałąź", text)

    def test_production_changes_exactly_ten_locations_against_develop(self) -> None:
        current = {content.room_id: _signature_hash(content) for content in make_content_pack()}
        develop = _load_baseline_signatures()

        self.assertEqual(set(current), set(develop))
        changed_ids = {room_id for room_id in current if current[room_id] != develop[room_id]}

        self.assertEqual(changed_ids, set(EXPECTED_IDS))
        self.assertEqual(len(changed_ids), 10)
        self.assertEqual(current[56], develop[56])

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

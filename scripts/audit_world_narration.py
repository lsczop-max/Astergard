from __future__ import annotations

import argparse
import re
import tempfile
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astergard.application.bootstrap import GameBootstrapper  # noqa: E402
from astergard.narrative import build_world_scene, render_world_scene  # noqa: E402


BAD_PATTERNS: tuple[str, ...] = (
    r"Drogi stąd",
    r"Na ziemi spoczyw",
    r"W pobliżu są",
    r"prowadzi droga",
    r"Świt zmywa",
    r"Świat trwa tu",
    r"wydaje się",
    r"sprawia wrażenie",
    r"jest miejscem",
    r"to miejsce",
    r"nie ma tu nic przypadkowego",
    r"człowiek jest tu",
    r"miasto zaczyna się",
    r"droga jest bardziej",
    r"należy do",
    r"leży w strefie",
)


def _normalize_sentence(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower().rstrip(".")


def _render_samples() -> tuple[list[tuple[int, str, str]], list[str]]:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    services = GameBootstrapper(tmp.name).build()
    world = services.world
    npcs = services.npcs
    weather = services.weather

    scenarios = [
        ("day", 12, None, None, weather.world_state),
        ("night", 22, None, None, weather.world_state),
        ("rain", 12, "deszcz", "wiosna", weather.world_state),
        ("fog", 12, "mgla", "jesien", weather.world_state),
        ("winter", 12, "sniezyca", "zima", weather.world_state),
        ("summer", 12, "slonecznie", "lato", weather.world_state),
    ]

    rendered: list[tuple[int, str, str]] = []
    all_texts: list[str] = []
    original_hour = weather.hour
    original_season = weather.season
    original_weather = dict(weather.weather_by_zone)
    for loc in world.locations.values():
        room_npcs = list(npcs.by_room(loc.id))
        target_names = {
            direction: world.locations[exit_.target_room].name.lower()
            for direction, exit_ in loc.exits.items()
            if exit_.target_room in world.locations
        }
        for label, hour, weather_state, season, world_state in scenarios:
            weather.hour = hour
            weather.season = season or original_season
            if weather_state is not None:
                weather.weather_by_zone[loc.zone] = weather_state
            else:
                weather.weather_by_zone.pop(loc.zone, None)
            scene = build_world_scene(
                title=loc.name,
                description=loc.description,
                zone=loc.zone,
                time_of_day=weather.hour,
                season=weather.season,
                weather=weather.weather_by_zone.get(loc.zone),
                world_state=world_state,
                perspective=label,
                exits=loc.exits,
                items=list(loc.items),
                npcs=room_npcs,
                target_names=target_names,
            )
            text = render_world_scene(scene)
            rendered.append((loc.id, label, text))
            all_texts.append(text)
    weather.hour = original_hour
    weather.season = original_season
    weather.weather_by_zone = original_weather
    return rendered, all_texts


def _build_report() -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    services = GameBootstrapper(tmp.name).build()
    world = services.world
    npcs = services.npcs

    rendered, all_texts = _render_samples()
    sentences = Counter(_normalize_sentence(text.splitlines()[1]) for _, _, text in rendered if len(text.splitlines()) > 1)
    repeated = {sentence: count for sentence, count in sentences.items() if sentence and count > 10}
    bad_hits: Counter[str] = Counter()
    for text in all_texts:
        for pattern in BAD_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                bad_hits[pattern] += 1

    exit_kind_missing = sum(1 for loc in world.locations.values() for exit_ in loc.exits.values() if not getattr(exit_, "kind", ""))
    missing_item_categories = sum(1 for loc in world.locations.values() for item in loc.items if not getattr(item, "presentation_category", None))
    missing_npc_scene = sum(1 for npc in npcs.npcs.values() if not npc.short_desc.strip() or not npc.long_desc.strip())
    raw_id_hits: Counter[str] = Counter()
    for text in all_texts:
        for token in re.findall(r"\b[a-z]+_[a-z0-9_]+\b", text):
            raw_id_hits[token] += 1

    lines = [
        "# WORLD_NARRATION_REPORT_D52",
        "",
        f"- Liczba lokacji: {len(world.locations)}",
        f"- Liczba renderów próbnych: {len(rendered)}",
        f"- Liczba powtórzeń zdań: {sum(count - 1 for count in sentences.values() if count > 1)}",
        f"- Brakujące typy wyjść: {exit_kind_missing}",
        f"- Przedmioty bez kategorii prezentacji: {missing_item_categories}",
        f"- NPC bez pełnego opisu scenicznego: {missing_npc_scene}",
        f"- Surowe identyfikatory w renderach: {sum(raw_id_hits.values())}",
        "",
        "## Powtarzające się frazy",
    ]
    if repeated:
        for sentence, count in sorted(repeated.items(), key=lambda item: (-item[1], item[0]))[:20]:
            lines.append(f"- `{sentence}`: {count}")
    else:
        lines.append("- brak istotnych powtórzeń")

    lines.extend([
        "",
        "## Podejrzane konstrukcje",
    ])
    if bad_hits:
        for pattern, count in bad_hits.items():
            lines.append(f"- `{pattern}`: {count}")
    else:
        lines.append("- brak wykrytych konstrukcji z listy kontrolnej")

    lines.extend([
        "",
        "## Surowe identyfikatory",
    ])
    if raw_id_hits:
        for token, count in raw_id_hits.most_common(20):
            lines.append(f"- `{token}`: {count}")
    else:
        lines.append("- brak")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit world narration quality.")
    parser.add_argument("--output", type=Path, default=Path("WORLD_NARRATION_REPORT_D52.md"))
    args = parser.parse_args()
    report = _build_report()
    args.output.write_text(report, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

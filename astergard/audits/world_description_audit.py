from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, cast

from astergard.application.services.exploration_scene import ExplorationSceneRenderer
from astergard.application.use_case_contexts import ExplorationContext
from astergard.characters.models import Character
from astergard.commands.polish import normalize_phrase
from astergard.engine.events import EventBus
from astergard.location_narrative.validator import DescriptionValidator
from astergard.location_narrative.world_adapter import WorldNarrativeAdapter
from astergard.npcs.manager import NPCManager
from astergard.npcs.models import NPC
from astergard.weather.time_weather import TimeAndWeatherManager
from astergard.world.manager import REGION_RANGES, WorldManager


_GENERATED_AT = "2026-07-17T00:00:00Z"
_FIXED_SEASON = "lato"
_FIXED_HOUR = 6
_FIXED_WORLD_STATE = "spokojnie"

_ABSTRACT_PHRASES = (
    "wydaje się",
    "sprawia wrażenie",
    "można odnieść wrażenie",
    "to teren",
    "to miejsce",
    "nie potrzebuje",
    "sam wybiera",
    "tu liczy się",
    "nie jest to miejsce",
    "miejsce emanuje",
    "jakby",
    "świat trwa",
    "natura odzyskuje swoje prawa",
    "nie potrzebuje murów",
    "nie potrzebuje straży",
)

_GRAMMAR_PATTERNS = (
    r"\bknieii\b",
    r"\bmoze\b",
    r"\bspoczyw[a-z]*\s+w\s+szczelinach\b",
    r"\bnie\s+da\s+się\b",
)

_LANDMARK_TOKENS = {
    "brama",
    "furta",
    "mur",
    "mury",
    "studnia",
    "most",
    "plac",
    "rynek",
    "karczma",
    "kuźnia",
    "kaplica",
    "kapliczka",
    "świątynia",
    "zaułek",
    "ulica",
    "trakt",
    "droga",
    "ścieżka",
    "przesmyk",
    "przełęcz",
    "wieża",
    "skała",
    "urwisko",
    "stok",
    "korytarz",
    "szyb",
    "chodnik",
    "ruina",
    "ruiny",
    "bagno",
    "bagna",
    "torf",
    "trzcina",
    "kładka",
    "palisada",
    "dziedziniec",
    "dziedziniec",
    "dziedziniec",
    "mostek",
    "podgrodzie",
    "forteca",
    "strażnica",
}

_SPATIAL_TOKENS = {
    "przy",
    "między",
    "miedzy",
    "obok",
    "wzdłuż",
    "wzdluz",
    "nad",
    "pod",
    "za",
    "przed",
    "na skraju",
    "na obrzeżu",
    "na obrzezu",
    "w głębi",
    "w glebi",
    "u wylotu",
    "na końcu",
    "na koncu",
    "po bokach",
    "pośrodku",
    "posrodku",
    "na dole",
    "na górze",
    "na gorze",
    "na zboczu",
    "na stoku",
    "na przełęczy",
    "na przeleczy",
    "w przejściu",
    "w przejsciu",
    "w tunelu",
    "w korytarzu",
    "w bramie",
    "na rynku",
    "na drodze",
    "na ścieżce",
    "na sciezce",
}

_SENSORY_CLICHES = {
    "zapach",
    "pachnie",
    "czujesz",
    "słychać",
    "slychac",
    "widać",
    "widac",
    "cisza",
    "mrok",
    "mgła",
    "mgla",
}

_RAW_ALIAS_GROUPS = (
    {"torf", "bloto", "błoto", "mul", "muł", "młyn"},
    {"łuk", "luk", "luki", "kusza", "kusze", "strzała", "strzala", "strzały", "strzaly", "bełt", "bełty", "belt", "belty"},
)

_COMMON_VERBS = {
    "jest",
    "sa",
    "stoi",
    "lezy",
    "leza",
    "prowadzi",
    "ciągnie",
    "ciagnie",
    "niknie",
    "wiedzie",
    "otwiera",
    "trzyma",
    "widac",
    "slychac",
    "pachnie",
    "odzywaja",
    "rozprasza",
    "wciska",
    "miesza",
    "odbiija",
    "odbija",
    "wisi",
    "podpiera",
    "osiada",
    "wychodzi",
    "schodzi",
    "wchodzi",
    "odchodzi",
}

_COMMON_ADJECTIVES = {
    "ciemny",
    "ciemna",
    "ciemne",
    "stary",
    "stara",
    "stare",
    "mokry",
    "mokra",
    "mokre",
    "surowy",
    "surowa",
    "surowe",
    "wąski",
    "waska",
    "wąska",
    "szeroki",
    "szeroka",
    "szerokie",
    "niski",
    "niska",
    "niskie",
    "wysoki",
    "wysoka",
    "wysokie",
    "chłodny",
    "chlodny",
    "chłodna",
    "chlodna",
    "chłodne",
    "chlodne",
    "szary",
    "szara",
    "szare",
    "głęboki",
    "gleboki",
    "głęboka",
    "gleboka",
    "głębokie",
    "glebokie",
    "brudny",
    "brudna",
    "brudne",
    "pęknięty",
    "peknięty",
    "pekniety",
    "pęknięta",
    "peknięta",
    "peknieta",
}


@dataclass(frozen=True, slots=True)
class ExitRecord:
    direction: str
    target_id: int
    target_name: str
    kind: str


@dataclass(frozen=True, slots=True)
class LocationAuditRecord:
    location_id: int
    name: str
    region: str
    terrain: str
    source_description: str
    rendered_look: str
    exits: tuple[ExitRecord, ...]
    neighbour_names: tuple[str, ...]
    inspectables: tuple[str, ...]
    items: tuple[str, ...]
    npcs: tuple[str, ...]
    issues: tuple[str, ...]
    class_name: str
    score: int
    line_count: int
    sentence_count: int
    token_count: int
    lexical_diversity: float
    max_same_region_similarity: float
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["issues"] = sorted(self.issues)
        data["exits"] = [asdict(exit_) for exit_ in sorted(self.exits, key=lambda item: (item.direction, item.target_id, item.target_name))]
        data["neighbour_names"] = sorted(self.neighbour_names)
        data["inspectables"] = sorted(self.inspectables)
        data["items"] = sorted(self.items)
        data["npcs"] = sorted(self.npcs)
        data["notes"] = sorted(self.notes)
        return data


@dataclass(frozen=True, slots=True)
class RegionAuditSummary:
    region: str
    location_count: int
    p0_count: int
    p1_count: int
    p2_count: int
    p3_count: int
    accept_count: int
    average_score: float
    median_score: float
    average_same_region_similarity: float
    worst_score: int
    best_score: int
    issue_counts: tuple[tuple[str, int], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "location_count": self.location_count,
            "p0_count": self.p0_count,
            "p1_count": self.p1_count,
            "p2_count": self.p2_count,
            "p3_count": self.p3_count,
            "accept_count": self.accept_count,
            "average_score": self.average_score,
            "median_score": self.median_score,
            "average_same_region_similarity": self.average_same_region_similarity,
            "worst_score": self.worst_score,
            "best_score": self.best_score,
            "issue_counts": list(self.issue_counts),
        }


@dataclass(frozen=True, slots=True)
class WorldDescriptionAudit:
    generated_at: str
    world_size: int
    records: tuple[LocationAuditRecord, ...]
    class_counts: tuple[tuple[str, int], ...]
    issue_counts: tuple[tuple[str, int], ...]
    repeated_sentences: tuple[tuple[str, int], ...]
    repeated_openings: tuple[tuple[str, int], ...]
    repeated_endings: tuple[tuple[str, int], ...]
    identical_sentence_instances: int
    identical_sentence_forms: int
    template_openers: int
    template_endings: int
    abstract_narrator_count: int
    generic_location_count: int
    no_landmark_count: int
    no_spatial_layout_count: int
    language_error_count: int
    spatial_inconsistency_count: int
    raw_alias_count: int
    non_interactive_detail_count: int
    overloaded_render_count: int
    duplicate_identity_count: int
    region_summaries: tuple[RegionAuditSummary, ...]
    rewrite_order: tuple[str, ...]
    manual_samples: dict[str, tuple[int, ...]]
    worst_locations: tuple[int, ...]
    best_locations: tuple[int, ...]
    region_similarity: tuple[tuple[str, float], ...]
    cross_region_similarity: tuple[tuple[str, float], ...]
    report_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "world_size": self.world_size,
            "records": [record.to_dict() for record in self.records],
            "class_counts": list(self.class_counts),
            "issue_counts": list(self.issue_counts),
            "repeated_sentences": [list(item) for item in self.repeated_sentences],
            "repeated_openings": [list(item) for item in self.repeated_openings],
            "repeated_endings": [list(item) for item in self.repeated_endings],
            "identical_sentence_instances": self.identical_sentence_instances,
            "identical_sentence_forms": self.identical_sentence_forms,
            "template_openers": self.template_openers,
            "template_endings": self.template_endings,
            "abstract_narrator_count": self.abstract_narrator_count,
            "generic_location_count": self.generic_location_count,
            "no_landmark_count": self.no_landmark_count,
            "no_spatial_layout_count": self.no_spatial_layout_count,
            "language_error_count": self.language_error_count,
            "spatial_inconsistency_count": self.spatial_inconsistency_count,
            "raw_alias_count": self.raw_alias_count,
            "non_interactive_detail_count": self.non_interactive_detail_count,
            "overloaded_render_count": self.overloaded_render_count,
            "duplicate_identity_count": self.duplicate_identity_count,
            "region_summaries": [summary.to_dict() for summary in self.region_summaries],
            "rewrite_order": list(self.rewrite_order),
            "manual_samples": {key: list(self.manual_samples[key]) for key in sorted(self.manual_samples)},
            "worst_locations": list(self.worst_locations),
            "best_locations": list(self.best_locations),
            "region_similarity": list(self.region_similarity),
            "cross_region_similarity": list(self.cross_region_similarity),
            "report_digest": self.report_digest,
        }


def _normalize_sentence(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return normalize_phrase(cleaned.strip().rstrip(".!?"))


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.!?]", text) if part.strip()]


def _content_lines(rendered: str) -> list[str]:
    return [line.strip() for line in rendered.splitlines() if line.strip()]


def _body_text(rendered: str) -> str:
    lines = _content_lines(rendered)
    if len(lines) <= 1:
        return ""
    return " ".join(lines[1:])


def _tokenize(text: str) -> list[str]:
    return [token for token in normalize_phrase(text, drop_stopwords=True).split() if token]


def detect_raw_alias_leak(text: str) -> bool:
    tokens = set(_tokenize(text))
    return any(len(tokens & group) >= 3 for group in _RAW_ALIAS_GROUPS)


def detect_obvious_language_error(text: str) -> bool:
    normalized = normalize_phrase(text)
    return any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in _GRAMMAR_PATTERNS)


def detect_identical_endings(texts: Iterable[str]) -> Counter[str]:
    endings: Counter[str] = Counter()
    for text in texts:
        lines = _content_lines(text)
        body = " ".join(lines[1:]) if len(lines) > 1 else text
        sentences = [_normalize_sentence(sentence) for sentence in _split_sentences(body)]
        if sentences:
            endings[sentences[-1]] += 1
    return Counter({ending: count for ending, count in endings.items() if count > 1})


def _classification_from_scores(score: int, issues: set[str], notes: tuple[str, ...]) -> str:
    if issues & {"GRAMMAR_ERROR", "NEIGHBOUR_CONTRADICTION", "EXIT_NOT_REFLECTED", "FALSE_CONTINUITY", "RAW_ALIAS_LEAK"}:
        return "P0"
    if score >= 85 and not issues:
        return "ACCEPT"
    if score >= 75 and not (issues & {"TEMPLATE_OPENER", "TEMPLATE_ENDING", "ABSTRACT_NARRATOR", "GENERIC_LOCATION", "NO_LANDMARK", "NO_SPATIAL_LAYOUT", "LIST_LIKE_DESCRIPTION", "NON_INTERACTIVE_DETAIL", "OVERLOADED_RENDER", "UNNATURAL_POLISH"}):
        return "P3"
    if score >= 60:
        return "P2"
    return "P1"


def classify_quality_band(score: int, issues: Iterable[str] = ()) -> str:
    issue_set = set(issues)
    return _classification_from_scores(score, issue_set, ())


def _spawn_deterministic_world() -> tuple[WorldManager, NPCManager, TimeAndWeatherManager]:
    world = WorldManager()
    world.generate_world()
    npcs = NPCManager(world)
    npcs.populate()
    _stabilize_npc_ids(world, npcs)
    weather = TimeAndWeatherManager()
    weather.hour = _FIXED_HOUR
    weather.season = _FIXED_SEASON
    weather.world_state = _FIXED_WORLD_STATE
    weather.weather_by_zone.clear()
    weather.ambient_event = lambda zone: None  # type: ignore[assignment]
    return world, npcs, weather


def _stabilize_npc_ids(world: WorldManager, npcs: NPCManager) -> None:
    ordered_npcs = sorted(npcs.npcs.values(), key=lambda npc: (npc.home_room_id, npc.vnum, npc.name))
    stabilized: dict[str, NPC] = {}
    for index, npc in enumerate(ordered_npcs):
        old_id = npc.id
        new_id = f"audit_{index:04d}_{npc.vnum}"
        npc.id = new_id
        npc.character.combat_identity = new_id
        stabilized[new_id] = npc
        location = world.get_location(npc.home_room_id)
        if location is not None:
            location.npc_ids = [new_id if npc_id == old_id else npc_id for npc_id in location.npc_ids]
    npcs.npcs = stabilized


def _render_location(world: WorldManager, npcs: NPCManager, weather: TimeAndWeatherManager, location_id: int) -> str:
    renderer = ExplorationSceneRenderer()
    character = Character("world-audit", room_id=location_id)
    location = world.locations[location_id]
    ctx = ExplorationContext(
        character=character,
        event_bus=EventBus(),
        world=world,
        weather=weather,
        npcs=npcs,
        players_in_room=lambda room_id: [],
    )
    return renderer.render(ctx, location, False)


def _extract_text_facts(rendered: str, name: str) -> dict[str, Any]:
    lines = _content_lines(rendered)
    body = _body_text(rendered)
    sentences = [_normalize_sentence(sentence) for sentence in _split_sentences(body)]
    first_sentence = sentences[0] if sentences else ""
    last_sentence = sentences[-1] if sentences else ""
    tokens = _tokenize(body)
    lexical_diversity = round(len(set(tokens)) / len(tokens), 3) if tokens else 0.0
    return {
        "lines": lines,
        "body": body,
        "sentences": sentences,
        "first_sentence": first_sentence,
        "last_sentence": last_sentence,
        "token_count": len(tokens),
        "lexical_diversity": lexical_diversity,
        "title_like_opening": first_sentence == normalize_phrase(name),
    }


def _common_sentence_statistics(texts: dict[int, str]) -> tuple[Counter[str], Counter[str], Counter[str]]:
    sentence_counter: Counter[str] = Counter()
    opening_counter: Counter[str] = Counter()
    ending_counter: Counter[str] = Counter()
    for rendered in texts.values():
        lines = _content_lines(rendered)
        body = " ".join(lines[1:]) if len(lines) > 1 else ""
        sentences = [_normalize_sentence(sentence) for sentence in _split_sentences(body)]
        sentence_counter.update(sentence for sentence in sentences if sentence)
        if sentences:
            opening_counter[sentences[0]] += 1
            ending_counter[sentences[-1]] += 1
    return sentence_counter, opening_counter, ending_counter


def _region_for_location(location_id: int) -> str:
    for start, end, region, _label in REGION_RANGES:
        if start <= location_id <= end:
            return region
    raise KeyError(location_id)


def _region_label(region: str) -> str:
    for _start, _end, zone, label in REGION_RANGES:
        if zone == region:
            return label
    return region


def _region_order(region_summaries: dict[str, RegionAuditSummary]) -> tuple[str, ...]:
    priority = {
        "Centrum_Twierdza": 0,
        "Podgrodzie": 1,
        "Trakty": 2,
        "Boczne_Drogi": 3,
        "Forteca_Dungrim": 4,
        "Straznica_Przeleczy": 5,
        "Haldun": 6,
        "Osada_Mysliwych": 7,
        "Puszcza_Ciszy": 8,
        "Knieja_Cichych_Sciezek": 9,
        "Gory_Mekhara": 10,
        "Kopalnia_Zelaza": 11,
        "Ruiny_Karshold": 12,
        "Jaskinie_Wilkow": 13,
        "Bagna_Hookri": 14,
    }
    return tuple(
        summary.region
        for summary in sorted(
            region_summaries.values(),
            key=lambda item: (
                priority.get(item.region, 99),
                -(item.p0_count + item.p1_count),
                -item.location_count,
                item.region,
            ),
        )
    )


def _manual_sample_ids(records: list[LocationAuditRecord]) -> dict[str, tuple[int, ...]]:
    by_category: dict[str, list[LocationAuditRecord]] = defaultdict(list)
    for record in records:
        region = record.region
        if region in {"Centrum_Twierdza", "Podgrodzie", "Haldun", "Osada_Mysliwych", "Forteca_Dungrim", "Straznica_Przeleczy"}:
            by_category["city"].append(record)
        elif region in {"Trakty", "Boczne_Drogi"}:
            by_category["roads"].append(record)
        elif region in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            by_category["forest"].append(record)
        elif region == "Bagna_Hookri":
            by_category["swamp"].append(record)
        elif region == "Gory_Mekhara":
            by_category["mountain"].append(record)
        elif region in {"Kopalnia_Zelaza", "Ruiny_Karshold", "Jaskinie_Wilkow"}:
            by_category["ruins_mines"].append(record)
    samples: dict[str, tuple[int, ...]] = {}
    for category, pool in by_category.items():
        pool = sorted(pool, key=lambda record: (record.score, record.location_id))
        if len(pool) <= 10:
            samples[category] = tuple(record.location_id for record in pool)
            continue
        indices = [round(i * (len(pool) - 1) / 9) for i in range(10)]
        samples[category] = tuple(pool[index].location_id for index in indices)
    return samples


def _score_record(
    *,
    location_id: int,
    rendered: str,
    facts: dict[str, Any],
    text_stats: dict[str, Any],
    validator: DescriptionValidator,
    world: WorldManager,
    same_region_max_similarity: float,
    location_facts: Any,
) -> tuple[list[str], list[str], int]:
    location = world.locations[location_id]
    validation_report = validator.validate(rendered, location_facts)
    issues = list(validation_report.critical_errors)
    notes = list(validation_report.warnings)
    body = facts["body"]
    lines = facts["lines"]
    first_sentence = facts["first_sentence"]
    last_sentence = facts["last_sentence"]
    title = normalize_phrase(location.name)
    tokens = text_stats["tokens"]
    unique_tokens = set(tokens)

    if facts["title_like_opening"] and len(first_sentence.split()) <= 8:
        issues.append("TEMPLATE_OPENER")
    if text_stats["opening_frequency"] >= 2 and len(first_sentence.split()) <= 12 and (
        first_sentence == title or same_region_max_similarity >= 0.78 or location.name.lower() in first_sentence
    ):
        issues.append("TEMPLATE_OPENER")
    if text_stats["ending_frequency"] >= 2 and len(last_sentence.split()) <= 14:
        issues.append("TEMPLATE_ENDING")

    if any(phrase in normalize_phrase(body) for phrase in _ABSTRACT_PHRASES):
        issues.append("ABSTRACT_NARRATOR")
    if len(unique_tokens) < 18 or facts["lexical_diversity"] < 0.46:
        issues.append("GENERIC_LOCATION")
    if not any(token in unique_tokens for token in _LANDMARK_TOKENS):
        issues.append("NO_LANDMARK")
    if not any(phrase in normalize_phrase(body) for phrase in _SPATIAL_TOKENS):
        issues.append("NO_SPATIAL_LAYOUT")
    if detect_obvious_language_error(rendered):
        issues.append("GRAMMAR_ERROR")
    if detect_raw_alias_leak(rendered):
        issues.append("RAW_ALIAS_LEAK")
    if len(lines) >= 7 or len(rendered) > 900:
        issues.append("OVERLOADED_RENDER")
    if sum(line.count(",") for line in lines) >= 6:
        issues.append("LIST_LIKE_DESCRIPTION")
    if any(phrase in normalize_phrase(body) for phrase in _SENSORY_CLICHES) and text_stats["sentence_count"] <= 4:
        issues.append("SENSORY_CLICHE")
    if any(token in normalize_phrase(body) for token in ("tobie", "ciebie", "twoj", "twoja", "twoje", "ty ")):
        issues.append("PLAYER_EMOTION")
    if location.items and not any(any(normalize_phrase(item.name.split()[0]) in normalize_phrase(alias) for alias in location.inspectables) for item in location.items):
        issues.append("NON_INTERACTIVE_DETAIL")
    if same_region_max_similarity >= 0.86:
        issues.append("DUPLICATE_IDENTITY")
    if text_stats["opening_frequency"] >= 3:
        issues.append("TEMPLATE_OPENER")
    if text_stats["ending_frequency"] >= 3:
        issues.append("TEMPLATE_ENDING")

    if any(pattern in normalize_phrase(body) for pattern in ("brak", "pusto", "pustka")) and len(location.inspectables) == 0:
        issues.append("EMPTY_GRANDEUR")

    if any(token in normalize_phrase(body) for token in ("jakby", "wydaje się", "sprawia wrażenie")):
        issues.append("ABSTRACT_NARRATOR")

    if not issues and validation_report.warnings:
        notes.extend(validation_report.warnings)
    if "catalogue_style" in validation_report.warnings or "predictable_opening" in validation_report.warnings:
        issues.append("UNNATURAL_POLISH")

    score = max(
        1,
        100
        - len(set(issues)) * 8
        - len(validation_report.warnings) * 2
        - max(0, 20 - len(unique_tokens))
        - max(0, 0 if same_region_max_similarity < 0.7 else int((same_region_max_similarity - 0.7) * 100)),
    )
    if "OVERLOADED_RENDER" in issues:
        score -= 8
    if "NON_INTERACTIVE_DETAIL" in issues:
        score -= 4
    if "GENERIC_LOCATION" in issues:
        score -= 4
    if "NO_LANDMARK" in issues:
        score -= 4
    if "NO_SPATIAL_LAYOUT" in issues:
        score -= 4
    if "ABSTRACT_NARRATOR" in issues:
        score -= 4
    if "TEMPLATE_OPENER" in issues or "TEMPLATE_ENDING" in issues:
        score -= 3
    if "DUPLICATE_IDENTITY" in issues:
        score -= 5
    score = max(1, min(100, score))
    return issues, notes, score


def _score_to_class(score: int, issues: Iterable[str]) -> str:
    return _classification_from_scores(score, set(issues), ())


def analyze_rendered_location(
    *,
    location_id: int,
    world: WorldManager,
    npcs: NPCManager | None = None,
    rendered: str,
    same_region_max_similarity: float,
    sentence_frequency: Counter[str],
    opener_frequency: Counter[str],
    ending_frequency: Counter[str],
) -> tuple[LocationAuditRecord, dict[str, Any]]:
    location = world.locations[location_id]
    lines = _content_lines(rendered)
    body = _body_text(rendered)
    sentences = [_normalize_sentence(sentence) for sentence in _split_sentences(body)]
    tokens = _tokenize(body)
    text_stats = {
        "tokens": tokens,
        "sentence_count": len(sentences),
        "opening_frequency": opener_frequency[sentences[0]] if sentences else 0,
        "ending_frequency": ending_frequency[sentences[-1]] if sentences else 0,
    }
    facts = {
        "lines": lines,
        "body": body,
        "sentences": sentences,
        "first_sentence": sentences[0] if sentences else "",
        "last_sentence": sentences[-1] if sentences else "",
        "token_count": len(tokens),
        "lexical_diversity": round(len(set(tokens)) / len(tokens), 3) if tokens else 0.0,
        "title_like_opening": sentences[:1] == [normalize_phrase(location.name)],
    }
    adapter = WorldNarrativeAdapter(world)
    location_facts = adapter.facts_for_location(location_id)
    validator = DescriptionValidator()
    issues, notes, score = _score_record(
        location_id=location_id,
        rendered=rendered,
        facts=facts,
        text_stats=text_stats,
        validator=validator,
        world=world,
        same_region_max_similarity=same_region_max_similarity,
        location_facts=location_facts,
    )
    region = location.zone
    neighbour_names = tuple(
        world.locations[exit_.target_room].name
        for exit_ in location.exits.values()
        if exit_.target_room in world.locations
    )
    exits = tuple(
        ExitRecord(
            direction=direction,
            target_id=exit_.target_room,
            target_name=world.locations[exit_.target_room].name if exit_.target_room in world.locations else "",
            kind=getattr(exit_, "kind", ""),
        )
        for direction, exit_ in location.exits.items()
    )
    class_name = _score_to_class(score, issues)
    record = LocationAuditRecord(
        location_id=location_id,
        name=location.name,
        region=region,
        terrain=location_facts.terrain,
        source_description=location.description,
        rendered_look=rendered,
        exits=exits,
        neighbour_names=neighbour_names,
        inspectables=tuple(location.inspectables.keys()),
        items=tuple(item.name for item in location.items),
        npcs=_collect_npc_names(world, npcs or NPCManager(world), location_id) if npcs is not None else tuple(),
        issues=tuple(sorted(dict.fromkeys(issues))),
        class_name=class_name,
        score=score,
        line_count=len(lines),
        sentence_count=len(sentences),
        token_count=len(tokens),
        lexical_diversity=cast(float, facts["lexical_diversity"]),
        max_same_region_similarity=round(same_region_max_similarity, 3),
        notes=tuple(sorted(dict.fromkeys(notes))),
    )
    return record, facts


def _collect_npc_names(world: WorldManager, npcs: NPCManager, location_id: int) -> tuple[str, ...]:
    return tuple(npc.name for npc in npcs.by_room(location_id))


def _build_region_summaries(records: list[LocationAuditRecord]) -> tuple[RegionAuditSummary, ...]:
    grouped: dict[str, list[LocationAuditRecord]] = defaultdict(list)
    for record in records:
        grouped[record.region].append(record)
    summaries: list[RegionAuditSummary] = []
    for region, items in sorted(grouped.items(), key=lambda item: (_region_for_location(item[1][0].location_id), item[0]) if item[1] else (item[0], item[0])):
        scores = [item.score for item in items]
        issue_counts = Counter(issue for item in items for issue in item.issues)
        summaries.append(
            RegionAuditSummary(
                region=region,
                location_count=len(items),
                p0_count=sum(1 for item in items if item.class_name == "P0"),
                p1_count=sum(1 for item in items if item.class_name == "P1"),
                p2_count=sum(1 for item in items if item.class_name == "P2"),
                p3_count=sum(1 for item in items if item.class_name == "P3"),
                accept_count=sum(1 for item in items if item.class_name == "ACCEPT"),
                average_score=round(mean(scores), 2) if scores else 0.0,
                median_score=round(sorted(scores)[len(scores) // 2], 2) if scores else 0.0,
                average_same_region_similarity=round(mean(item.max_same_region_similarity for item in items), 3) if items else 0.0,
                worst_score=min(scores) if scores else 0,
                best_score=max(scores) if scores else 0,
                issue_counts=tuple(sorted(issue_counts.items(), key=lambda pair: (-pair[1], pair[0]))),
            )
        )
    return tuple(sorted(summaries, key=lambda item: item.region))


def _pair_similarity(left: str, right: str) -> float:
    left_tokens = set(_tokenize(_body_text(left)))
    right_tokens = set(_tokenize(_body_text(right)))
    if not left_tokens and not right_tokens:
        return 1.0
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def _compute_similarity_maps(world: WorldManager, rendered_by_id: dict[int, str]) -> tuple[dict[int, float], list[tuple[str, float]], list[tuple[str, float]]]:
    by_region: dict[str, list[int]] = defaultdict(list)
    for location_id in sorted(rendered_by_id):
        by_region[world.locations[location_id].zone].append(location_id)
    max_same_region: dict[int, float] = {location_id: 0.0 for location_id in rendered_by_id}
    region_scores: dict[str, list[float]] = defaultdict(list)
    region_signature: dict[str, str] = {}
    for region, ids in by_region.items():
        for index, left_id in enumerate(ids):
            for right_id in ids[index + 1 :]:
                similarity = _pair_similarity(rendered_by_id[left_id], rendered_by_id[right_id])
                max_same_region[left_id] = max(max_same_region[left_id], similarity)
                max_same_region[right_id] = max(max_same_region[right_id], similarity)
                region_scores[region].append(similarity)
        region_text = " ".join(
            _normalize_sentence(line)
            for location_id in ids[: min(len(ids), 8)]
            for line in _split_sentences(_body_text(rendered_by_id[location_id]))[:2]
        )
        region_signature[region] = region_text

    region_similarity: list[tuple[str, float]] = []
    for region, scores in sorted(region_scores.items()):
        region_similarity.append((region, round(mean(scores), 3) if scores else 0.0))

    cross_region_similarity: list[tuple[str, float]] = []
    regions = sorted(region_signature)
    for index, left in enumerate(regions):
        left_signature = region_signature[left]
        best = 0.0
        for right in regions[index + 1 :]:
            score = _pair_similarity(left_signature, region_signature[right])
            best = max(best, score)
        cross_region_similarity.append((left, round(best, 3)))
    return max_same_region, region_similarity, cross_region_similarity


def _render_manual_excerpt(rendered: str, max_lines: int = 4) -> str:
    lines = _content_lines(rendered)
    return "\n".join(lines[:max_lines]).strip()


def _select_manual_samples(result: WorldDescriptionAudit) -> dict[str, list[dict[str, Any]]]:
    records_by_id = {record.location_id: record for record in result.records}
    samples: dict[str, list[dict[str, Any]]] = {}
    for category, ids in result.manual_samples.items():
        selected: list[dict[str, Any]] = []
        for location_id in ids:
            record = records_by_id[location_id]
            selected.append(
                {
                    "location_id": record.location_id,
                    "name": record.name,
                    "region": record.region,
                    "terrain": record.terrain,
                    "score": record.score,
                    "class_name": record.class_name,
                    "issues": list(record.issues),
                    "render_excerpt": _render_manual_excerpt(record.rendered_look),
                    "recommendation": {
                        "P0": "Pilna przebudowa zanim trafi do etapu produkcyjnego.",
                        "P1": "Zmiana struktury i tożsamości, nie tylko kosmetyka.",
                        "P2": "Należy doprecyzować orientację i punkt ciężkości.",
                        "P3": "Wystarczy dopracowanie frazy i detali.",
                        "ACCEPT": "Może służyć jako wzorzec wewnętrzny.",
                    }[record.class_name],
                }
            )
        samples[category] = selected
    return samples


@lru_cache(maxsize=1)
def build_world_description_audit() -> WorldDescriptionAudit:
    world, npcs, weather = _spawn_deterministic_world()
    adapter = WorldNarrativeAdapter(world)
    facts_by_id = {location_id: adapter.facts_for_location(location_id) for location_id in sorted(world.locations)}
    rendered_by_id = {
        location_id: _render_location(world, npcs, weather, location_id)
        for location_id in sorted(world.locations)
    }
    records: list[LocationAuditRecord] = []
    sentence_counter, opening_counter, ending_counter = _common_sentence_statistics(rendered_by_id)
    max_same_region_similarity, region_similarity, cross_region_similarity = _compute_similarity_maps(world, rendered_by_id)
    validator = DescriptionValidator()
    for location_id in sorted(world.locations):
        rendered = rendered_by_id[location_id]
        rendered_by_id[location_id] = rendered
        location = world.locations[location_id]
        facts = _extract_text_facts(rendered, location.name)
        location_facts = facts_by_id[location_id]
        same_region_max = max_same_region_similarity.get(location_id, 0.0)
        issues, notes, score = _score_record(
            location_id=location_id,
            rendered=rendered,
            facts=facts,
            text_stats={
                "tokens": _tokenize(facts["body"]),
                "sentence_count": len(facts["sentences"]),
                "opening_frequency": opening_counter[facts["first_sentence"]] if facts["first_sentence"] else 0,
                "ending_frequency": ending_counter[facts["last_sentence"]] if facts["last_sentence"] else 0,
            },
            validator=validator,
            world=world,
            same_region_max_similarity=same_region_max,
            location_facts=location_facts,
        )
        record = LocationAuditRecord(
            location_id=location_id,
            name=location.name,
            region=location.zone,
            terrain=location_facts.terrain,
            source_description=location.description,
            rendered_look=rendered,
            exits=tuple(
                ExitRecord(
                    direction=direction,
                    target_id=exit_.target_room,
                    target_name=world.locations[exit_.target_room].name if exit_.target_room in world.locations else "",
                    kind=getattr(exit_, "kind", ""),
                )
                for direction, exit_ in location.exits.items()
            ),
            neighbour_names=tuple(
                world.locations[exit_.target_room].name
                for exit_ in location.exits.values()
                if exit_.target_room in world.locations
            ),
            inspectables=tuple(location.inspectables.keys()),
            items=tuple(item.name for item in location.items),
            npcs=_collect_npc_names(world, npcs, location_id),
            issues=tuple(sorted(dict.fromkeys(issues))),
            class_name=_score_to_class(score, issues),
            score=score,
            line_count=len(facts["lines"]),
            sentence_count=len(facts["sentences"]),
            token_count=facts["token_count"],
            lexical_diversity=facts["lexical_diversity"],
            max_same_region_similarity=round(same_region_max, 3),
            notes=tuple(sorted(dict.fromkeys(notes))),
        )
        records.append(record)

    class_counts = Counter(record.class_name for record in records)
    issue_counts = Counter(issue for record in records for issue in record.issues)
    repeated_sentences = tuple(
        sorted(
            ((sentence, count) for sentence, count in sentence_counter.items() if count > 1),
            key=lambda item: (-item[1], item[0]),
        )
    )
    repeated_openings = tuple(
        sorted(
            ((sentence, count) for sentence, count in opening_counter.items() if count > 1),
            key=lambda item: (-item[1], item[0]),
        )
    )
    repeated_endings = tuple(
        sorted(
            ((sentence, count) for sentence, count in ending_counter.items() if count > 1),
            key=lambda item: (-item[1], item[0]),
        )
    )
    region_summaries = _build_region_summaries(records)
    rewrite_order = _region_order({summary.region: summary for summary in region_summaries})
    manual_samples = _manual_sample_ids(records)
    worst_locations = tuple(record.location_id for record in sorted(records, key=lambda item: (item.score, -item.max_same_region_similarity, item.location_id))[:20])
    best_locations = tuple(record.location_id for record in sorted(records, key=lambda item: (-item.score, item.max_same_region_similarity, item.location_id))[:20])
    duplicate_identity_count = sum(1 for record in records if record.max_same_region_similarity >= 0.86)
    template_openers = sum(1 for record in records if "TEMPLATE_OPENER" in record.issues)
    template_endings = sum(1 for record in records if "TEMPLATE_ENDING" in record.issues)
    abstract_narrator_count = sum(1 for record in records if "ABSTRACT_NARRATOR" in record.issues)
    generic_location_count = sum(1 for record in records if "GENERIC_LOCATION" in record.issues)
    no_landmark_count = sum(1 for record in records if "NO_LANDMARK" in record.issues)
    no_spatial_layout_count = sum(1 for record in records if "NO_SPATIAL_LAYOUT" in record.issues)
    language_error_count = sum(1 for record in records if "GRAMMAR_ERROR" in record.issues or "UNNATURAL_POLISH" in record.issues)
    spatial_inconsistency_count = sum(
        1
        for record in records
        if {"NEIGHBOUR_CONTRADICTION", "EXIT_NOT_REFLECTED", "FALSE_CONTINUITY"} & set(record.issues)
    )
    raw_alias_count = sum(1 for record in records if "RAW_ALIAS_LEAK" in record.issues)
    non_interactive_detail_count = sum(1 for record in records if "NON_INTERACTIVE_DETAIL" in record.issues)
    overloaded_render_count = sum(1 for record in records if "OVERLOADED_RENDER" in record.issues)
    report = WorldDescriptionAudit(
        generated_at=_GENERATED_AT,
        world_size=len(world.locations),
        records=tuple(records),
        class_counts=tuple(sorted(class_counts.items(), key=lambda item: item[0])),
        issue_counts=tuple(sorted(issue_counts.items(), key=lambda item: (-item[1], item[0]))),
        repeated_sentences=repeated_sentences,
        repeated_openings=repeated_openings,
        repeated_endings=repeated_endings,
        identical_sentence_instances=sum(count - 1 for _sentence, count in repeated_sentences),
        identical_sentence_forms=len(repeated_sentences),
        template_openers=template_openers,
        template_endings=template_endings,
        abstract_narrator_count=abstract_narrator_count,
        generic_location_count=generic_location_count,
        no_landmark_count=no_landmark_count,
        no_spatial_layout_count=no_spatial_layout_count,
        language_error_count=language_error_count,
        spatial_inconsistency_count=spatial_inconsistency_count,
        raw_alias_count=raw_alias_count,
        non_interactive_detail_count=non_interactive_detail_count,
        overloaded_render_count=overloaded_render_count,
        duplicate_identity_count=duplicate_identity_count,
        region_summaries=region_summaries,
        rewrite_order=rewrite_order,
        manual_samples=manual_samples,
        worst_locations=worst_locations,
        best_locations=best_locations,
        region_similarity=tuple(region_similarity),
        cross_region_similarity=tuple(cross_region_similarity),
        report_digest="",
    )
    digest = hashlib.sha256(json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return WorldDescriptionAudit(
        generated_at=report.generated_at,
        world_size=report.world_size,
        records=report.records,
        class_counts=report.class_counts,
        issue_counts=report.issue_counts,
        repeated_sentences=report.repeated_sentences,
        repeated_openings=report.repeated_openings,
        repeated_endings=report.repeated_endings,
        identical_sentence_instances=report.identical_sentence_instances,
        identical_sentence_forms=report.identical_sentence_forms,
        template_openers=report.template_openers,
        template_endings=report.template_endings,
        abstract_narrator_count=report.abstract_narrator_count,
        generic_location_count=report.generic_location_count,
        no_landmark_count=report.no_landmark_count,
        no_spatial_layout_count=report.no_spatial_layout_count,
        language_error_count=report.language_error_count,
        spatial_inconsistency_count=report.spatial_inconsistency_count,
        raw_alias_count=report.raw_alias_count,
        non_interactive_detail_count=report.non_interactive_detail_count,
        overloaded_render_count=report.overloaded_render_count,
        duplicate_identity_count=report.duplicate_identity_count,
        region_summaries=report.region_summaries,
        rewrite_order=report.rewrite_order,
        manual_samples=report.manual_samples,
        worst_locations=report.worst_locations,
        best_locations=report.best_locations,
        region_similarity=report.region_similarity,
        cross_region_similarity=report.cross_region_similarity,
        report_digest=digest,
    )


def _format_issue_summary(items: Iterable[tuple[str, int]], *, limit: int = 12) -> str:
    lines = []
    for issue, count in list(items)[:limit]:
        lines.append(f"- `{issue}`: {count}")
    return "\n".join(lines) if lines else "- brak"


def _format_list(items: Iterable[Any], *, limit: int | None = None) -> str:
    values = list(items)
    if limit is not None:
        values = values[:limit]
    return "\n".join(f"- {item}" for item in values) if values else "- brak"


def render_audit_markdown(audit: WorldDescriptionAudit) -> str:
    records = list(audit.records)
    class_counts = dict(audit.class_counts)
    manual_samples = _select_manual_samples(audit)
    lines: list[str] = [
        "# D58.1 World Description Audit",
        "",
        "## Verdict",
        "WORLD_DESCRIPTION_AUDIT_READY" if audit.world_size == len(records) == 500 else "INCOMPLETE",
        "",
        "## Summary",
        f"- World size: {audit.world_size}",
        f"- Identical sentence instances: {audit.identical_sentence_instances}",
        f"- Repeated sentence forms: {audit.identical_sentence_forms}",
        f"- Template openers: {audit.template_openers}",
        f"- Template endings: {audit.template_endings}",
        f"- Abstract narrator hits: {audit.abstract_narrator_count}",
        f"- Generic location hits: {audit.generic_location_count}",
        f"- No landmark hits: {audit.no_landmark_count}",
        f"- No spatial layout hits: {audit.no_spatial_layout_count}",
        f"- Language errors: {audit.language_error_count}",
        f"- Spatial inconsistencies: {audit.spatial_inconsistency_count}",
        f"- Raw alias leaks: {audit.raw_alias_count}",
        f"- Non-interactive detail hits: {audit.non_interactive_detail_count}",
        f"- Overloaded renders: {audit.overloaded_render_count}",
        f"- Duplicate identity hits: {audit.duplicate_identity_count}",
        "",
        "## Class Counts",
        f"- P0: {class_counts.get('P0', 0)}",
        f"- P1: {class_counts.get('P1', 0)}",
        f"- P2: {class_counts.get('P2', 0)}",
        f"- P3: {class_counts.get('P3', 0)}",
        f"- ACCEPT: {class_counts.get('ACCEPT', 0)}",
        "",
        "## Frequent Problems",
        _format_issue_summary(audit.issue_counts),
        "",
        "## Repeated Sentences",
        _format_issue_summary(audit.repeated_sentences[:20], limit=20),
        "",
        "## Repeated Openings",
        _format_issue_summary(audit.repeated_openings[:20], limit=20),
        "",
        "## Repeated Endings",
        _format_issue_summary(audit.repeated_endings[:20], limit=20),
        "",
        "## Region Order",
    ]
    for index, region in enumerate(audit.rewrite_order, start=1):
        lines.append(f"{index}. {region}")

    lines.extend(["", "## Region Summary"])
    for summary in audit.region_summaries:
        lines.append(
            f"- {summary.region}: {summary.location_count} lokacji, P0={summary.p0_count}, P1={summary.p1_count}, "
            f"P2={summary.p2_count}, P3={summary.p3_count}, ACCEPT={summary.accept_count}, "
            f"średnia={summary.average_score}, similarity={summary.average_same_region_similarity}"
        )

    lines.extend(["", "## 20 Worst Locations"])
    for record in sorted(records, key=lambda item: (item.score, -item.max_same_region_similarity, item.location_id))[:20]:
        lines.append(
            f"- #{record.location_id} {record.name} [{record.region}] score={record.score} class={record.class_name} issues={', '.join(record.issues)}"
        )

    lines.extend(["", "## 20 Best Locations"])
    for record in sorted(records, key=lambda item: (-item.score, item.max_same_region_similarity, item.location_id))[:20]:
        lines.append(
            f"- #{record.location_id} {record.name} [{record.region}] score={record.score} class={record.class_name}"
        )

    lines.extend(["", "## Manual Samples"])
    for category, sample_records in manual_samples.items():
        lines.append(f"### {category}")
        for sample in sample_records:
            excerpt = sample["render_excerpt"].replace("`", "'")
            lines.extend(
                [
                    f"- #{sample['location_id']} {sample['name']} [{sample['region']}] score={sample['score']} class={sample['class_name']}",
                    f"  - excerpt: `{excerpt}`",
                    f"  - issues: {', '.join(sample['issues']) if sample['issues'] else 'brak'}",
                    f"  - recommendation: {sample['recommendation']}",
                ]
            )

    lines.extend(["", "## Notes", f"- Digest: `{audit.report_digest}`"])
    return "\n".join(lines).strip() + "\n"


def render_rewrite_order_markdown(audit: WorldDescriptionAudit) -> str:
    lines = [
        "# D58.1 Rewrite Order",
        "",
        "Kolejność przebudowy regionów wyznaczona przez:",
        "1. znaczenie dla pierwszych godzin gry",
        "2. natężenie ruchu graczy",
        "3. liczbę problemów P0/P1",
        "4. zależności przestrzenne",
        "5. możliwość przetestowania pełnej trasy",
        "",
        "## Proponowana kolejność",
    ]
    for index, region in enumerate(audit.rewrite_order, start=1):
        summary = next(summary for summary in audit.region_summaries if summary.region == region)
        lines.append(
            f"{index}. {region} - P0={summary.p0_count}, P1={summary.p1_count}, średnia={summary.average_score}, "
            f"coverage={summary.location_count}"
        )
    lines.extend(
        [
            "",
            "## Zależności",
            "- Najpierw centrum i podgrodzie: tam gracz uczy się rytmu ruchu i orientacji.",
            "- Potem trakty oraz strefy przejściowe: pozwalają przetestować spójność przejść na dłuższej trasie.",
            "- Następnie regiony wysokiej i niskiej dostępności, gdzie testy są wciąż proste do przejścia.",
            "- Na końcu obszary odcięte, długie lub ciężkie w testowaniu regresji.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_world_description_audit_outputs(
    audit: WorldDescriptionAudit | None = None,
    markdown_path: Path | str = Path("docs/audits/D58_1_WORLD_DESCRIPTION_AUDIT.md"),
    json_path: Path | str = Path("docs/audits/D58_1_WORLD_DESCRIPTION_DATA.json"),
    rewrite_order_path: Path | str = Path("docs/audits/D58_1_REWRITE_ORDER.md"),
) -> WorldDescriptionAudit:
    audit = audit or build_world_description_audit()
    markdown_path = Path(markdown_path)
    json_path = Path(json_path)
    rewrite_order_path = Path(rewrite_order_path)
    markdown_path.write_text(render_audit_markdown(audit), encoding="utf-8")
    json_path.write_text(json.dumps(audit.to_dict(), ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    rewrite_order_path.write_text(render_rewrite_order_markdown(audit), encoding="utf-8")
    return audit

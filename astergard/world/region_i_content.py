from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from astergard.world.content import LocationContent
from astergard.world.models import Location
from astergard.world.region_i_loader import RegionIData, load_region_i_data

REPO_ROOT = Path(__file__).resolve().parents[2]
REGION_I_CARDS_PATH = REPO_ROOT / "docs" / "maps" / "region_i_import" / "mapa_karty_lokacji.json"
REGION_I_PILOT_CONTENT_PATH = Path(__file__).resolve().parent / "data" / "region_i_pilot_content.json"

CANONICAL_REGION_IDS = {
    "centrum",
    "trakt",
    "trakt-gorniczy",
    "trakt-nadrzeczny",
    "polnocny-las",
    "nadrzeczne-mokradla",
}


class RegionIContentError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RegionIContinuity:
    direction: str
    room_id: int
    room_name: str


@dataclass(frozen=True, slots=True)
class RegionICard:
    id: int
    name: str
    region_id: str
    function: str
    terrain: str
    spatial_layout: str
    materials: str
    landmark_and_objects: str
    sound_and_smell: str
    light: str
    weather_and_climate: str
    traces_of_use: str
    possible_interactions: tuple[str, ...]
    inhabitants_and_users: tuple[str, ...]
    local_history: str
    continuity: tuple[RegionIContinuity, ...]


@dataclass(frozen=True, slots=True)
class RegionIPilotContent:
    id: int
    name: str
    description: str
    inspectables: dict[str, str]
    dynamic_hooks: tuple[str, ...]


def _require_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegionIContentError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _require_int(value: Any, field_name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool):
        raise RegionIContentError(f"{field_name} must be an integer.")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        try:
            result = int(value.strip())
        except ValueError as exc:
            raise RegionIContentError(f"{field_name} must be an integer.") from exc
    else:
        raise RegionIContentError(f"{field_name} must be an integer.")
    if minimum is not None and result < minimum:
        raise RegionIContentError(f"{field_name} must be >= {minimum}.")
    return result


def _require_str_list(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise RegionIContentError(f"{field_name} must be a list of strings.")
    items: list[str] = []
    for index, item in enumerate(value):
        items.append(_require_str(item, f"{field_name}[{index}]"))
    return tuple(items)


def _region_i_cards_path(path: Path | None = None) -> Path:
    return path or REGION_I_CARDS_PATH


def _region_i_pilot_path(path: Path | None = None) -> Path:
    return path or REGION_I_PILOT_CONTENT_PATH


@lru_cache(maxsize=1)
def load_region_i_cards(path: Path | None = None) -> tuple[RegionICard, ...]:
    asset_path = _region_i_cards_path(path)
    raw = json.loads(asset_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RegionIContentError("Region I cards asset must be a JSON object.")
    cards_raw = raw.get("cards")
    if not isinstance(cards_raw, list):
        raise RegionIContentError("Region I cards asset field 'cards' must be a list.")
    cards: list[RegionICard] = []
    seen_ids: set[int] = set()
    for index, card in enumerate(cards_raw):
        if not isinstance(card, dict):
            raise RegionIContentError(f"Region I cards asset field 'cards[{index}]' must be an object.")
        card_id = _require_int(card.get("id"), f"cards[{index}].id", minimum=0)
        if card_id in seen_ids:
            raise RegionIContentError(f"Duplicate Region I card id detected: {card_id}.")
        seen_ids.add(card_id)
        continuity_raw = card.get("continuity", [])
        if not isinstance(continuity_raw, list):
            raise RegionIContentError(f"cards[{index}].continuity must be a list.")
        continuity: list[RegionIContinuity] = []
        for c_index, item in enumerate(continuity_raw):
            if not isinstance(item, dict):
                raise RegionIContentError(f"cards[{index}].continuity[{c_index}] must be an object.")
            continuity.append(
                RegionIContinuity(
                    direction=_require_str(item.get("direction"), f"cards[{index}].continuity[{c_index}].direction"),
                    room_id=_require_int(item.get("roomId"), f"cards[{index}].continuity[{c_index}].roomId", minimum=0),
                    room_name=_require_str(item.get("roomName"), f"cards[{index}].continuity[{c_index}].roomName"),
                )
            )
        card_region_id = _require_str(card.get("regionId"), f"cards[{index}].regionId")
        if card_region_id not in CANONICAL_REGION_IDS:
            raise RegionIContentError(f"cards[{index}].regionId contains an unknown region id: {card_region_id}.")
        cards.append(
            RegionICard(
                id=card_id,
                name=_require_str(card.get("name"), f"cards[{index}].name"),
                region_id=card_region_id,
                function=_require_str(card.get("function"), f"cards[{index}].function"),
                terrain=_require_str(card.get("terrain"), f"cards[{index}].terrain"),
                spatial_layout=_require_str(card.get("spatialLayout"), f"cards[{index}].spatialLayout"),
                materials=_require_str(card.get("materials"), f"cards[{index}].materials"),
                landmark_and_objects=_require_str(card.get("landmarkAndObjects"), f"cards[{index}].landmarkAndObjects"),
                sound_and_smell=_require_str(card.get("soundAndSmell"), f"cards[{index}].soundAndSmell"),
                light=_require_str(card.get("light"), f"cards[{index}].light"),
                weather_and_climate=_require_str(card.get("weatherAndClimate"), f"cards[{index}].weatherAndClimate"),
                traces_of_use=_require_str(card.get("tracesOfUse"), f"cards[{index}].tracesOfUse"),
                possible_interactions=_require_str_list(card.get("possibleInteractions"), f"cards[{index}].possibleInteractions"),
                inhabitants_and_users=_require_str_list(card.get("inhabitantsAndUsers"), f"cards[{index}].inhabitantsAndUsers"),
                local_history=_require_str(card.get("localHistory"), f"cards[{index}].localHistory"),
                continuity=tuple(continuity),
            )
        )
    if len(cards) != 170:
        raise RegionIContentError(f"Region I cards asset must contain exactly 170 cards, found {len(cards)}.")
    return tuple(cards)


@lru_cache(maxsize=1)
def load_region_i_pilot_content(path: Path | None = None) -> tuple[RegionIPilotContent, ...]:
    asset_path = _region_i_pilot_path(path)
    raw = json.loads(asset_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RegionIContentError("Region I pilot asset must be a JSON object.")
    descriptions = raw.get("descriptions")
    if not isinstance(descriptions, list):
        raise RegionIContentError("Region I pilot asset field 'descriptions' must be a list.")
    pilots: list[RegionIPilotContent] = []
    seen_ids: set[int] = set()
    for index, item in enumerate(descriptions):
        if not isinstance(item, dict):
            raise RegionIContentError(f"Region I pilot asset field 'descriptions[{index}]' must be an object.")
        pilot_id = _require_int(item.get("id"), f"descriptions[{index}].id", minimum=0)
        if pilot_id in seen_ids:
            raise RegionIContentError(f"Duplicate pilot room id detected: {pilot_id}.")
        seen_ids.add(pilot_id)
        inspectables_raw = item.get("inspectables", {})
        if not isinstance(inspectables_raw, dict):
            raise RegionIContentError(f"descriptions[{index}].inspectables must be an object.")
        inspectables: dict[str, str] = {}
        for key, value in inspectables_raw.items():
            inspectables[_require_str(key, f"descriptions[{index}].inspectables key")] = _require_str(value, f"descriptions[{index}].inspectables[{key}]")
        hooks_raw = item.get("dynamicHooks", [])
        if not isinstance(hooks_raw, list):
            raise RegionIContentError(f"descriptions[{index}].dynamicHooks must be a list.")
        hooks = _require_str_list(hooks_raw, f"descriptions[{index}].dynamicHooks")
        pilots.append(
            RegionIPilotContent(
                id=pilot_id,
                name=_require_str(item.get("name"), f"descriptions[{index}].name"),
                description=_require_str(item.get("description"), f"descriptions[{index}].description"),
                inspectables=inspectables,
                dynamic_hooks=hooks,
            )
        )
    if len(pilots) != 15:
        raise RegionIContentError(f"Region I pilot asset must contain exactly 15 descriptions, found {len(pilots)}.")
    return tuple(pilots)


def _technical_description(card: RegionICard) -> str:
    continuity = "; ".join(f"{entry.direction}->{entry.room_id}" for entry in card.continuity) or "brak jawnej ciągłości"
    interactions = ", ".join(card.possible_interactions) or "brak jawnych interakcji"
    inhabitants = ", ".join(card.inhabitants_and_users) or "brak jawnych użytkowników"
    return (
        "[TECHNICZNY FALBACK DANYCH KARTY] "
        f"Nazwa: {card.name}. Funkcja: {card.function}. Teren: {card.terrain}. "
        f"Układ: {card.spatial_layout}. Materiały: {card.materials}. "
        f"Punkt orientacyjny: {card.landmark_and_objects}. Dźwięk i zapach: {card.sound_and_smell}. "
        f"Światło: {card.light}. Pogoda i klimat: {card.weather_and_climate}. "
        f"Ślady użycia: {card.traces_of_use}. Interakcje: {interactions}. Użytkownicy: {inhabitants}. "
        f"Historia lokalna: {card.local_history}. Ciągłość: {continuity}."
    )


def _technical_inspectables(card: RegionICard) -> dict[str, str]:
    inspectables = {
        "funkcja": f"Funkcja karty: {card.function}.",
        "układ": f"Układ przestrzenny: {card.spatial_layout}.",
        "materiały": f"Materiały: {card.materials}.",
        "orientacja": f"Punkt orientacyjny: {card.landmark_and_objects}.",
        "ślad użycia": f"Ślady użycia: {card.traces_of_use}.",
        "ciągłość": " | ".join(f"{entry.direction}:{entry.room_id}" for entry in card.continuity) or "Brak jawnej ciągłości.",
    }
    return inspectables


def build_region_i_content_pack(
    region_i_data: RegionIData | None = None,
    *,
    cards_path: Path | None = None,
    pilot_path: Path | None = None,
) -> tuple[LocationContent, ...]:
    region_i_data = region_i_data or load_region_i_data()
    cards = load_region_i_cards(cards_path)
    pilots = load_region_i_pilot_content(pilot_path)
    card_by_id = {card.id: card for card in cards}
    room_ids = region_i_data.room_ids
    if set(card_by_id) != set(room_ids):
        missing = sorted(room_ids - set(card_by_id))
        extra = sorted(set(card_by_id) - room_ids)
        raise RegionIContentError(f"Region I cards do not match topology ids. missing={missing}, extra={extra}")
    pilot_by_id = {pilot.id: pilot for pilot in pilots}
    if len(pilot_by_id) != len(pilots):
        raise RegionIContentError("Duplicate pilot room ids are not allowed.")
    missing_pilot_ids = sorted(set(pilot_by_id) - room_ids)
    if missing_pilot_ids:
        raise RegionIContentError(f"Region I pilot content references missing rooms: {missing_pilot_ids}")
    content: list[LocationContent] = []
    for room in region_i_data.rooms:
        card = card_by_id[room.id]
        pilot = pilot_by_id.get(room.id)
        description = _technical_description(card)
        inspectables = _technical_inspectables(card)
        dynamic_hooks: tuple[str, ...] = ()
        name = card.name
        if pilot is not None:
            if pilot.name != card.name:
                raise RegionIContentError(
                    f"Pilot room {pilot.id} name does not match card name: {pilot.name!r} != {card.name!r}."
                )
            description = pilot.description
            inspectables = {**inspectables, **pilot.inspectables}
            dynamic_hooks = pilot.dynamic_hooks
        content.append(
            LocationContent(
                room_id=room.id,
                name=name,
                description=description,
                inspectables=inspectables,
                scene_profile=card.function,
                dynamic_hooks=dynamic_hooks,
            )
        )
    return tuple(content)


def apply_region_i_content(
    locations: dict[int, Location],
    region_i_data: RegionIData | None = None,
) -> None:
    from astergard.world.content import apply_content_pack

    apply_content_pack(locations, build_region_i_content_pack(region_i_data))

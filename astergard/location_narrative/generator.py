from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Protocol

from astergard.commands.polish import normalize_phrase
from astergard.location_narrative.critic import DescriptionCritic
from astergard.location_narrative.critic import CritiqueResult
from astergard.location_narrative.lexicon import DeterministicMorphologyProvider
from astergard.location_narrative.models import (
    DescriptionPlan,
    DynamicLocationState,
    FingerprintReviewEntry,
    FingerprintReviewStatus,
    FingerprintTechnicalRecommendation,
    LocationFingerprint,
    LocationNarrativeResult,
    PermanentLocationFacts,
    RevisionRecord,
)
from astergard.location_narrative.planner import DescriptionPlanner
from astergard.location_narrative.realizer import SurfaceRealizer
from astergard.location_narrative.reviser import DescriptionReviser
from astergard.location_narrative.similarity import DeterministicSimilarityProvider
from astergard.location_narrative.validator import DescriptionValidator
from astergard.location_narrative.world_adapter import WorldNarrativeAdapter
from astergard.world.manager import WorldManager

GENERATOR_VERSION = "0.1.0"

_GENERIC_SUBJECT_MARKERS = {
    "krawedz przejscia",
    "nawierzchnia traktu",
    "mur lub strop",
    "stanowisko pracy",
    "próg mur albo posadzka",
    "prog mur albo posadzka",
    "grunt",
    "wiejski",
    "swiece wosk",
    "kamien przy podstawie kapliczki",
    "krawedz stoku",
    "chodnik skalny",
    "lokalny slad",
}
_GENERIC_POSITION_MARKERS = {
    "na dolnej krawedzi terenu",
    "na osi przejazdu",
    "przy rdzeniu ruiny",
    "przy blacie piecu albo wjezdzie",
    "przy blacie piecu albo wjezdzie",
    "przy wejsciu lub w osi przejscia",
    "at the passage axis",
    "at the altar or niche",
    "w punkcie przejscia",
    "powyzej lub ponizej glównego dojscia",
    "powyżej lub poniżej głównego dojścia",
}
_GENERIC_STATE_MARKERS = {
    "podmokla i czesciowo rozmyta",
    "podmokła i częściowo rozmyta",
    "material change visible at the passage",
    "częściowo zawalony lub wypalony",
    "pokryte pyllem, zuzellem albo odpadkami",
    "pokryte pyłem, żużlem albo odpadkami",
    "localised change in level or cover",
    "localized change in level or cover",
    "starta od ruchu i napraw",
}
_GENERIC_CAUSE_MARKERS = {
    "splyw wody i osiadanie torfu",
    "spływ wody i osiadanie torfu",
    "ruch i runoff",
    "movement and runoff",
    "ogień podmycie albo wtórny rozbiór",
    "ogień, podmycie albo wtórny rozbiór",
    "obróbka transport lub czyszczenie",
    "obróbka, transport lub czyszczenie",
    "wielokrotne dotykanie i pozostawianie sladow",
    "wielokrotne dotykanie i pozostawiane ślady",
}
_DIRECTION_LABELS = {
    "polnoc": "północnej",
    "poludnie": "południowej",
    "wschod": "wschodniej",
    "zachod": "zachodniej",
    "polnocny-wschod": "północno-wschodniej",
    "polnocny-zachod": "północno-zachodniej",
    "poludniowy-wschod": "południowo-wschodniej",
    "poludniowy-zachod": "południowo-zachodniej",
    "gora": "górnej",
    "dol": "dolnej",
}


class DraftSource(Protocol):
    def generate(
        self,
        facts: PermanentLocationFacts,
        plan: DescriptionPlan,
        state: DynamicLocationState,
        variant: int = 0,
    ) -> str:
        ...


@dataclass(slots=True)
class DeterministicDraftSource:
    realizer: SurfaceRealizer

    def generate(self, facts: PermanentLocationFacts, plan, state: DynamicLocationState, variant: int = 0) -> str:
        return self.realizer.realize_long(facts, plan, state, variant=variant)


def _state_variant_offset(state: DynamicLocationState) -> int:
    signature = normalize_phrase(
        " ".join(
            (
                state.time_of_day,
                state.weather,
                state.season,
                state.lighting,
                state.current_event,
                " ".join(state.recent_traces),
                state.temporary_threat,
                state.visibility_modifier,
            )
        ),
        drop_stopwords=False,
    )
    return sum(ord(char) for char in signature) % 8


def _fingerprint_subtype_from_payload(category: str, payload: dict[str, Any]) -> str:
    source_facts = payload.get("old_data") if isinstance(payload.get("old_data"), dict) else {}
    if not isinstance(source_facts, dict):
        source_facts = {}
    subject = str(payload.get("subject", "")).lower()
    physical_state = str(payload.get("physical_state", "")).lower()
    spatial_position = str(payload.get("spatial_position", "")).lower()
    cause = str(payload.get("cause", "")).lower()
    name = " ".join((subject, physical_state, spatial_position, cause, str(source_facts.get("name", "")).lower(), str(source_facts.get("function", "")).lower(), str(source_facts.get("terrain", "")).lower()))
    family = str(source_facts.get("family", "")).lower()
    raw_materials = source_facts.get("materials")
    materials = " ".join(str(item).lower() for item in raw_materials if isinstance(item, str)) if isinstance(raw_materials, (list, tuple)) else ""
    raw_traces = source_facts.get("traces")
    traces = raw_traces if isinstance(raw_traces, dict) else {}
    traces_text = " ".join(str(value).lower() for value in traces.values() if isinstance(value, str))
    raw_geometry = source_facts.get("geometry")
    geometry = raw_geometry if isinstance(raw_geometry, dict) else {}
    geometry_text = " ".join(str(value).lower() for value in geometry.values() if isinstance(value, (str, list, tuple)))
    name_blob = " ".join((name, materials, traces_text, geometry_text))
    if category == "drainage_damage":
        if "kład" in name_blob or "próg" in name_blob:
            return "sunk_edge"
        if "rów" in name_blob or "odpływ" in name_blob or "muł" in name_blob:
            return "silted_drain"
        if "bag" in family or "torf" in name_blob or "woda" in name_blob:
            return "saturated_bank"
        return "washed_bank"
    if category == "road_surface_change":
        if "bruk" in name_blob:
            return "broken_paving"
        if "nasyp" in name_blob or "skarpa" in name_blob:
            return "slope_erosion"
        if "kolein" in name_blob:
            return "rut_deepening"
        if "piasek" in name_blob or "żwir" in name_blob:
            return "loose_gravel"
        if "podmy" in name_blob or "rów" in name_blob:
            return "washed_edge"
        return "washed_edge"
    if category == "structural_collapse":
        if "schod" in name_blob:
            return "broken_stair"
        if "łuk" in name_blob:
            return "failed_arch"
        if "dach" in name_blob or "strop" in name_blob:
            return "missing_roof"
        if "fundament" in name_blob:
            return "exposed_foundation"
        if "korzeń" in name_blob:
            return "root_displacement"
        if "rozb" in name_blob:
            return "material_salvage"
        if "wypal" in traces_text or "ogień" in cause:
            return "fire_weakened_beam"
        return "fallen_wall"
    if category == "vertical_exposure":
        if "szyb" in name_blob:
            return "shaft_drop"
        if "schod" in name_blob:
            return "stair_drop"
        if "urw" in name_blob:
            return "cliff_edge"
        if "wiatr" in cause or "wiatr" in name_blob:
            return "wind_gap"
        return "ledged_slope"
    if category == "maintenance_pressure":
        if "brama" in name_blob or "furta" in name_blob:
            return "threshold_wear"
        if "mur" in name_blob:
            return "wall_wear"
        if "posadz" in name_blob or "bruk" in name_blob:
            return "floor_wear"
        if "kaplic" in name_blob or "ołtarz" in name_blob:
            return "ritual_wear"
        return "traffic_wear"
    if category == "vegetation_narrowing":
        if "korz" in name_blob:
            return "root_encroachment"
        if "pni" in name_blob or "drzew" in name_blob:
            return "canopy_close"
        if "ścież" in name_blob or "przej" in name_blob:
            return "path_squeeze"
        if "sitow" in name_blob or "trzcin" in name_blob:
            return "reed_closure"
        return "branch_close"
    if category == "cave_contour":
        if "szyb" in name_blob:
            return "shaft_contour"
        if "korytarz" in name_blob or "chodnik" in name_blob:
            return "tight_passage"
        if "kamień" in materials or "skała" in name_blob:
            return "rock_rib"
        return "rock_rib"
    if category == "work_residue":
        if "piec" in name_blob or "kuź" in name_blob:
            return "furnace_residue"
        if "stół" in name_blob or "warsztat" in name_blob:
            return "bench_dust"
        if "magaz" in name_blob or "skład" in name_blob:
            return "stockpile_trace"
        if "transport" in cause or "woz" in traces_text:
            return "transfer_residue"
        return "handling_residue"
    return "local_trace"


def _descriptor_token(source_facts: dict[str, Any]) -> str:
    candidates = (
        str(source_facts.get("dominant_landmark", "")),
        str(source_facts.get("name", "")),
        str(source_facts.get("function", "")),
        str(source_facts.get("terrain", "")),
    )
    for candidate in candidates:
        tokens = [token for token in normalize_phrase(candidate).split() if token and token not in {"i", "oraz", "lub", "na", "w", "z"}]
        if tokens:
            return tokens[0]
    return ""


def _normalize_text(text: str) -> str:
    return normalize_phrase(text, drop_stopwords=False)


def _compact_name(name: str) -> str:
    tokens = [token for token in _normalize_text(name).split() if token]
    if not tokens:
        return ""
    if len(tokens) <= 4:
        return name.strip()
    return " ".join(name.strip().split()[:4])


def _field_is_generic(value: str, markers: set[str]) -> bool:
    normalized = _normalize_text(value)
    return not normalized or any(marker in normalized for marker in markers)


def _localized_subject(source_facts: dict[str, Any], raw: dict[str, Any], category: str) -> str:
    for key in ("name", "dominant_landmark"):
        value = str(source_facts.get(key, "")).strip()
        if value:
            compact = _compact_name(value)
            if compact:
                return compact
    subject = str(raw.get("subject", "")).strip()
    if subject:
        return subject
    if category:
        return category.replace("_", " ")
    return "lokalny element"


def _localized_position(source_facts: dict[str, Any], raw: dict[str, Any], category: str, subject: str) -> str:
    raw_position = str(raw.get("spatial_position", "")).strip()
    if raw_position and not _field_is_generic(raw_position, _GENERIC_POSITION_MARKERS):
        return raw_position
    geometry = source_facts.get("geometry") if isinstance(source_facts.get("geometry"), dict) else {}
    visible = geometry.get("visible_directions") if isinstance(geometry, dict) else ()
    enclosure = str(geometry.get("enclosure", "")).strip() if isinstance(geometry, dict) else ""
    elevation = str(geometry.get("elevation", "")).strip() if isinstance(geometry, dict) else ""
    materials = source_facts.get("materials")
    material_text = " ".join(str(item).lower() for item in materials if isinstance(item, str)) if isinstance(materials, (list, tuple)) else ""
    name = _normalize_text(str(source_facts.get("name", "")))
    if category == "drainage_damage" and name:
        if "próg" in name or "rozlew" in name or "grzęz" in name:
            return "przy dolnej krawędzi przejścia"
        if "stara grobla" in name or "grobla" in name:
            return "na krawędzi grobli"
    if category == "road_surface_change" and visible:
        direction = str(visible[0]).replace("_", " ")
        return f"przy wlocie traktu od {_DIRECTION_LABELS.get(direction, direction)} strony"
    if category == "structural_collapse":
        if "ościeżnic" in name or "wrota" in name or "bram" in name:
            return "w osi wejścia"
        if "strop" in name or "dach" in name:
            return "pod osiadłym stropem"
    if category == "maintenance_pressure":
        if "kaplic" in name or "ołtarz" in name:
            return "przy podstawie kapliczki"
        if "bram" in name or "furta" in name:
            return "przy progu"
    if category == "work_residue":
        if "piec" in name or "kuź" in name:
            return "przy piecu albo stole roboczym"
        if "kopal" in name or "wrota" in name:
            return "przy wjeździe do chodnika"
    if category == "vegetation_narrowing":
        if "ścież" in name or "przej" in name:
            return "na wąskim przesmyku"
        if "sitow" in material_text or "trzcin" in material_text:
            return "przy kępie sitowia"
    if category == "vertical_exposure":
        if elevation:
            elevation_norm = _normalize_text(elevation)
            if "wysok" in elevation_norm:
                return "na górnej krawędzi"
            if "nis" in elevation_norm or "dol" in elevation_norm:
                return "u podstawy"
            return f"przy {elevation}"
        if enclosure == "zamknięta":
            return "przy zamkniętym przejściu"
    if visible:
        direction = str(visible[0]).replace("_", " ")
        return f"przy {_DIRECTION_LABELS.get(direction, direction)} krawędzi"
    return raw_position or "przy lokalnym przejściu"


def _localized_state(source_facts: dict[str, Any], raw: dict[str, Any], category: str, subject: str) -> str:
    raw_state = str(raw.get("physical_state", "")).strip()
    if raw_state and not _field_is_generic(raw_state, _GENERIC_STATE_MARKERS):
        return raw_state
    name = _normalize_text(str(source_facts.get("name", "")))
    traces_raw = source_facts.get("traces")
    traces: dict[str, Any] = traces_raw if isinstance(traces_raw, dict) else {}
    history = str(traces.get("historical_layer", "")).strip()
    damage = str(traces.get("damage", "")).strip()
    materials = source_facts.get("materials")
    material_text = " ".join(str(item).lower() for item in materials if isinstance(item, str)) if isinstance(materials, (list, tuple)) else ""
    if category == "drainage_damage":
        if "sucha" in name:
            return "sucha i wyniesiona nad wodę"
        if "rozlew" in name or "topiel" in name:
            return "podmokła i rozlana"
        if "trzcin" in name or "grzęz" in name:
            return "rozmiękła i miękka pod stopą"
        return "wilgotna i częściowo rozmyta"
    if category == "road_surface_change":
        if "błot" in name:
            return "miękka i rozjechana przez koła"
        if "bruk" in material_text:
            return "nierówna i popękana między kamieniami"
        if "piask" in name:
            return "sypka i płytka"
        return "rozjechana i pofalowana"
    if category == "structural_collapse":
        if "zarośnięta" in name:
            return "częściowo zawalona i zarastająca"
        if "powalon" in name:
            return "przywalona i przewrócona"
        if "wrota" in name or "oścież" in name:
            return "wyłamana i odarta z mocowań"
        return "zawalona i rozszczelniona"
    if category == "vertical_exposure":
        if "szyb" in name:
            return "ciemna i stroma"
        if "urw" in name or "skarp" in name:
            return "stroma i osypująca się"
        return "stroma i chłodna"
    if category == "maintenance_pressure":
        if "kaplic" in name:
            return "wygładzona od dotykania"
        if "bram" in name or "furta" in name:
            return "starta od przejść i otarć"
        return "starta i przytarta"
    if category == "vegetation_narrowing":
        if "sitow" in name or "trzcin" in name:
            return "zwężona przez sitowie"
        if "korz" in name:
            return "rozchylona przez korzenie"
        return "zwężona przez roślinność"
    if category == "cave_contour":
        if "szyb" in name:
            return "wąska i ciemna"
        return "ciasna i kamienista"
    if category == "work_residue":
        if "piec" in name or "kuź" in name:
            return "pokryta pyłem i żużlem"
        if "kopal" in name:
            return "spowita pyłem i wilgocią"
        return "pokryta pyłem i odpadkami"
    if category == "ritual_wear":
        return "wygładzona od dotykania"
    if history:
        return history
    if damage:
        return damage
    return raw_state or "konkretna i miejscowa"


def _localized_cause(source_facts: dict[str, Any], raw: dict[str, Any], category: str, subject: str) -> str:
    raw_cause = str(raw.get("cause", "")).strip()
    if raw_cause and not _field_is_generic(raw_cause, _GENERIC_CAUSE_MARKERS):
        return raw_cause
    traces_raw = source_facts.get("traces")
    traces: dict[str, Any] = traces_raw if isinstance(traces_raw, dict) else {}
    historical = str(traces.get("historical_layer", "")).strip()
    activity = str(traces.get("persistent_activity", "")).strip()
    economy = str(traces.get("economic_activity", "")).strip()
    if category == "drainage_damage":
        return "spływ wody i osiadanie podłoża"
    if category == "road_surface_change":
        return "ruch wozów i spływ z krawędzi"
    if category == "structural_collapse":
        if "ogie" in historical.lower():
            return "ogień i osłabienie kamienia"
        return "podmycie, ogień albo wtórny rozbiór"
    if category == "vertical_exposure":
        return "nachylenie i osypywanie materiału"
    if category == "maintenance_pressure":
        return activity or economy or "ciągłe przejścia i dotyk"
    if category == "vegetation_narrowing":
        return "zarastanie i rozrastanie korzeni"
    if category == "work_residue":
        return economy or activity or "obróbka i czyszczenie stanowiska"
    if category == "ritual_wear":
        return "wielokrotne dotykanie i ofiary"
    return raw_cause or "lokalne użytkowanie"


def _polish_fingerprint_fields(category: str, source_facts: dict[str, Any], raw: dict[str, Any]) -> tuple[str, str, str, str]:
    family = str(source_facts.get("family", "")).lower()
    landmark = str(source_facts.get("dominant_landmark", "")).lower()
    function = str(source_facts.get("function", "")).lower()
    terrain = str(source_facts.get("terrain", "")).lower()
    if category == "drainage_damage":
        subject = "krawędź przejścia"
        if "kład" in landmark or "próg" in landmark:
            subject = "krawędź przejścia"
        elif "rów" in landmark:
            subject = "rów przy przejściu"
        physical_state = "podmokła i częściowo rozmyta"
        spatial_position = "na dolnej krawędzi terenu"
        cause = "spływ wody i osiadanie torfu"
        if "bag" in family or "torf" in terrain:
            physical_state = "podmokła i rozmiękła"
        return subject, physical_state, spatial_position, cause
    if category == "road_surface_change":
        subject = "nawierzchnia traktu"
        if "bram" in landmark or "przej" in function:
            subject = "krawędź przejazdu"
        physical_state = "koleiny, żwir lub bruk o różnej głębokości"
        spatial_position = "na osi przejazdu"
        cause = "ruch wozów i spływ z krawędzi"
        return subject, physical_state, spatial_position, cause
    if category == "structural_collapse":
        subject = "mur lub strop"
        if "schod" in landmark:
            subject = "urwany bieg schodów"
        elif "łuk" in landmark:
            subject = "urwany łuk"
        physical_state = "częściowo zawalony lub wypalony"
        spatial_position = "przy rdzeniu ruiny"
        cause = "ogień, podmycie albo wtórny rozbiór"
        return subject, physical_state, spatial_position, cause
    if category == "vertical_exposure":
        subject = "krawędź stoku"
        if "szyb" in landmark:
            subject = "krawędź szybu"
        physical_state = "osypująca się lub przecięta przejściem"
        spatial_position = "powyżej lub poniżej głównego dojścia"
        cause = "nachylenie i wiatr"
        return subject, physical_state, spatial_position, cause
    if category == "maintenance_pressure":
        if "kaplic" in landmark or "ołtarz" in landmark or family == "sacred":
            return "kamień przy podstawie kapliczki", "wygładzony od dotykania", "przy podstawie kapliczki", "wielokrotne dotykanie i pozostawiane ślady"
        if "bram" in landmark or "furta" in landmark or function == "kontrola przejazdu":
            return "próg i okucia", "starty od ruchu", "przy wejściu", "ciągły ruch pieszy i kołowy"
        return "próg, mur albo posadzka", "starta od ruchu i napraw", "przy wejściu lub w osi przejścia", "warta, handel lub ciągły ruch"
    if category == "vegetation_narrowing":
        if "sitow" in terrain or "bag" in terrain:
            return "prześwit między kępami", "zwężony przez sitowie", "na granicy dojścia", "zarastanie i wilgoć"
        return "prześwit między pniami", "zwężony przez korzenie i gałęzie", "na granicy dojścia", "zarastanie i łamanie roślin przez ruch"
    if category == "cave_contour":
        if "szyb" in landmark:
            return "chodnik przy szybie", "ciasny i chropawy", "przy ścianie lub w osi przejścia", "naturalny przebieg skały"
        return "chodnik skalny", "ciasny i chropawy", "przy ścianie lub w osi przejścia", "naturalny przebieg skały"
    if category == "work_residue":
        if "piec" in landmark or "kuź" in landmark or "kuź" in function:
            return "stanowisko przy piecu", "pokryte pyłem i żużlem", "przy blacie albo piecu", "obróbka i czyszczenie stanowiska"
        return "stanowisko pracy", "pokryte pyłem, żużlem albo odpadkami", "przy blacie, piecu albo wjeździe", "obróbka, transport lub czyszczenie"
    return "lokalny ślad", "konkretny i miejscowy", "w punkcie przejścia", "lokalne użytkowanie"


def _normalize_review_category(raw_category: str, source_facts: dict[str, Any]) -> str:
    category = raw_category.strip()
    family = str(source_facts.get("family", "")).lower()
    terrain = str(source_facts.get("terrain", "")).lower()
    function = str(source_facts.get("function", "")).lower()
    landmark = str(source_facts.get("dominant_landmark", "")).lower()
    materials = " ".join(str(item).lower() for item in source_facts.get("materials", []) if isinstance(item, str))
    if category in {"terrain_transition", "transition_surface"}:
        if family in {"road", "border"} or "droga" in terrain or "przej" in function or "bram" in landmark:
            return "road_surface_change"
        if family in {"natural", "landscape"} or "traw" in terrain or "korz" in materials or "sitow" in materials:
            return "vegetation_narrowing"
        if family in {"vertical"} or "gór" in terrain or "skał" in materials:
            return "vertical_exposure"
        return "maintenance_pressure"
    if category == "ritual_wear":
        return "maintenance_pressure"
    return category


def _fingerprint_from_payload(payload: dict[str, Any]) -> LocationFingerprint | None:
    raw = payload.get("proposed_fingerprint") or payload.get("fingerprint")
    if not isinstance(raw, dict):
        return None
    source_facts = payload.get("old_data") if isinstance(payload.get("old_data"), dict) else {}
    if not isinstance(source_facts, dict):
        source_facts = {}
    category = _normalize_review_category(str(raw.get("category", "")).strip(), source_facts)
    subject = _localized_subject(source_facts, raw, category)
    physical_state = _localized_state(source_facts, raw, category, subject)
    spatial_position = _localized_position(source_facts, raw, category, subject)
    cause = _localized_cause(source_facts, raw, category, subject)
    visibility = str(raw.get("visibility", "plain")).strip() or "plain"
    persistence = str(raw.get("persistence", "permanent")).strip() or "permanent"
    examinable = bool(raw.get("examinable", False))
    regional_compatibility = str(raw.get("regional_compatibility", "high")).strip() or "high"
    neighbouring_constraints = tuple(str(item) for item in raw.get("neighbouring_constraints", ()) if str(item).strip())
    polished_subject, polished_state, polished_position, polished_cause = _polish_fingerprint_fields(category, source_facts, raw)
    if _field_is_generic(subject, _GENERIC_SUBJECT_MARKERS):
        subject = polished_subject or subject
    if _field_is_generic(physical_state, _GENERIC_STATE_MARKERS):
        physical_state = polished_state or physical_state
    if _field_is_generic(spatial_position, _GENERIC_POSITION_MARKERS):
        spatial_position = polished_position or spatial_position
    if _field_is_generic(cause, _GENERIC_CAUSE_MARKERS):
        cause = polished_cause or cause
    subtype = str(raw.get("subtype", "")).strip() or _fingerprint_subtype_from_payload(category, payload)
    token = _descriptor_token(source_facts)
    if token and token not in subtype:
        subtype = f"{subtype}_{token}" if subtype else token
    if not category or not subject or not physical_state or not spatial_position or not cause:
        return None
    return LocationFingerprint(
        category=category,
        subject=subject,
        physical_state=physical_state,
        spatial_position=spatial_position,
        cause=cause,
        visibility=visibility,
        persistence=persistence,
        examinable=examinable,
        regional_compatibility=regional_compatibility,
        neighbouring_constraints=neighbouring_constraints,
        subtype=subtype,
    )


def _technical_recommendation(payload: dict[str, Any], fingerprint: LocationFingerprint | None) -> FingerprintTechnicalRecommendation:
    old_data = payload.get("old_data")
    source_facts_raw = old_data
    source_facts: dict[str, Any] = source_facts_raw if isinstance(source_facts_raw, dict) else {}
    raw = payload.get("proposed_fingerprint") or payload.get("fingerprint")
    if not isinstance(raw, dict):
        return FingerprintTechnicalRecommendation.REJECT_CANDIDATE
    subject = str(raw.get("subject", "")).strip().lower()
    state = str(raw.get("physical_state", "")).strip().lower()
    position = str(raw.get("spatial_position", "")).strip().lower()
    cause = str(raw.get("cause", "")).strip().lower()
    name = str(source_facts.get("name", "")).strip().lower()
    geometry_raw = source_facts.get("geometry")
    geometry: dict[str, Any] = geometry_raw if isinstance(geometry_raw, dict) else {}
    relations_raw = source_facts.get("relations")
    relations: dict[str, Any] = relations_raw if isinstance(relations_raw, dict) else {}
    neighbour_terrains_raw = relations.get("neighbor_terrains")
    neighbour_terrains = neighbour_terrains_raw if isinstance(neighbour_terrains_raw, (list, tuple)) else ()
    shared_with_neighbors_raw = relations.get("shared_with_neighbors")
    shared_with_neighbors = shared_with_neighbors_raw if isinstance(shared_with_neighbors_raw, (list, tuple)) else ()
    examinables_raw = source_facts.get("examinables")
    examinables: tuple[Any, ...] = tuple(examinables_raw) if isinstance(examinables_raw, (list, tuple)) else ()
    name_tokens = [token for token in normalize_phrase(name, drop_stopwords=True).split() if token]
    generic_nouns = {
        "droga",
        "brama",
        "wrota",
        "kamien",
        "kamień",
        "las",
        "woda",
        "polana",
        "grobla",
        "rów",
        "prog",
        "próg",
        "wyspa",
        "kapliczka",
        "kamień",
        "stok",
        "ścieżka",
        "sciezka",
    }
    descriptive_names = {
        "stara",
        "czarna",
        "sucha",
        "martwy",
        "mglista",
        "błotna",
        "blotna",
        "zarośnięta",
        "zarosnieta",
        "powalone",
        "krzyżowy",
        "krzyzowy",
    }
    if not subject or not state or not position:
        return FingerprintTechnicalRecommendation.REJECT_CANDIDATE

    raw_specificity = sum(
        1
        for value, markers in (
            (subject, _GENERIC_SUBJECT_MARKERS),
            (state, _GENERIC_STATE_MARKERS),
            (position, _GENERIC_POSITION_MARKERS),
            (cause, _GENERIC_CAUSE_MARKERS),
        )
        if value and not _field_is_generic(value, markers)
    )
    if raw_specificity >= 3 and not _field_is_generic(subject, _GENERIC_SUBJECT_MARKERS):
        return FingerprintTechnicalRecommendation.ACCEPT_CANDIDATE

    rare_name_tokens = [
        token
        for token in name_tokens
        if token not in generic_nouns and token not in descriptive_names and len(token) > 2
    ]
    name_score = len(rare_name_tokens)
    if len(tuple(item for item in examinables if isinstance(item, str) and item.strip())) >= 2:
        name_score += 1
    if geometry and isinstance(geometry.get("visible_directions"), (list, tuple)) and geometry.get("visible_directions"):
        name_score += 1
    if neighbour_terrains and len(set(str(item) for item in neighbour_terrains if str(item).strip())) >= 2:
        name_score += 1

    if name_score >= 2 and raw_specificity >= 1:
        return FingerprintTechnicalRecommendation.EDIT_REQUIRED

    if len(name_tokens) <= 2 and all(token in generic_nouns | descriptive_names for token in name_tokens):
        return FingerprintTechnicalRecommendation.REJECT_CANDIDATE
    if len(shared_with_neighbors) >= 7 and raw_specificity <= 1:
        return FingerprintTechnicalRecommendation.EDIT_REQUIRED
    return FingerprintTechnicalRecommendation.EDIT_REQUIRED


def load_fingerprint_review(path: str | Path) -> list[FingerprintReviewEntry]:
    payload = load_review(path)
    entries: list[FingerprintReviewEntry] = []
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        fingerprint = _fingerprint_from_payload(raw)
        recommendation = _technical_recommendation(raw, fingerprint)
        review_status = {
            FingerprintTechnicalRecommendation.ACCEPT_CANDIDATE: FingerprintReviewStatus.accept,
            FingerprintTechnicalRecommendation.EDIT_REQUIRED: FingerprintReviewStatus.edit,
            FingerprintTechnicalRecommendation.REJECT_CANDIDATE: FingerprintReviewStatus.reject,
        }[recommendation]
        decision = str(raw.get("decision", "pending")).strip().lower()
        source_facts_raw = raw.get("old_data")
        source_facts: dict[str, Any] = source_facts_raw if isinstance(source_facts_raw, dict) else {}
        source_facts_dict: dict[str, Any] = source_facts
        neighbouring_constraints = fingerprint.neighbouring_constraints if fingerprint else ()
        entries.append(
            FingerprintReviewEntry(
                location_id=int(raw.get("location_id", -1)),
                source_facts={str(key): str(value) for key, value in source_facts_dict.items()},
                proposed_fingerprint=fingerprint,
                confidence=0.95 if recommendation == FingerprintTechnicalRecommendation.ACCEPT_CANDIDATE else 0.7,
                hallucination_risk="low" if recommendation == FingerprintTechnicalRecommendation.ACCEPT_CANDIDATE else "medium",
                neighbouring_constraints=neighbouring_constraints,
                review_status=review_status,
                reviewer_note=f"{str(raw.get('source', 'review import'))}; raw_decision={decision or 'pending'}",
                technical_recommendation=recommendation,
            )
        )
    return entries


def fingerprint_overlay_from_review(entries: list[FingerprintReviewEntry]) -> dict[int, FingerprintReviewEntry]:
    return {entry.location_id: entry for entry in entries if entry.review_status in {FingerprintReviewStatus.accept, FingerprintReviewStatus.edit}}


@dataclass(slots=True)
class LocationNarrativeGenerator:
    planner: DescriptionPlanner
    validator: DescriptionValidator
    critic: DescriptionCritic
    reviser: DescriptionReviser
    world_adapter: WorldNarrativeAdapter
    draft_source: DraftSource
    similarity_provider: DeterministicSimilarityProvider
    realizer: SurfaceRealizer

    @classmethod
    def default(
        cls,
        world: WorldManager,
        *,
        fingerprint_overlay: dict[int, FingerprintReviewEntry] | None = None,
    ) -> "LocationNarrativeGenerator":
        morphology = DeterministicMorphologyProvider()
        validator = DescriptionValidator()
        critic = DescriptionCritic(validator)
        realizer = SurfaceRealizer(morphology)
        return cls(
            planner=DescriptionPlanner(),
            validator=validator,
            critic=critic,
            reviser=DescriptionReviser(),
            world_adapter=WorldNarrativeAdapter(world, fingerprint_overlay=fingerprint_overlay),
            draft_source=DeterministicDraftSource(realizer),
            similarity_provider=DeterministicSimilarityProvider(),
            realizer=realizer,
        )

    def generate(
        self,
        location_id: int,
        *,
        manual_description: str | None = None,
        existing_texts: tuple[str, ...] = (),
        use_local_fingerprint: bool = True,
    ) -> LocationNarrativeResult:
        facts = self.world_adapter.facts_for_location(location_id)
        if not use_local_fingerprint:
            facts = replace(facts, local_fingerprint=None)
        state = self.world_adapter.state_for_location(location_id)
        plan = self.planner.build_plan(facts, state)
        trace: list[RevisionRecord] = []
        if manual_description is not None:
            draft = manual_description
            critique = self.critic.critique(draft, facts, existing_texts)
            score = critique.score
            final_text = draft
        else:
            final_text, critique = self._generate_draft(facts, plan, state, existing_texts)
            score = critique.score
            if not critique.report.is_accepted and not self._needs_reroll(critique, final_text, existing_texts):
                draft = final_text
                for _ in range(3):
                    final_text, changes = self.reviser.revise(final_text, critique, facts)
                    new_critique = self.critic.critique(final_text, facts, existing_texts)
                    trace.append(
                        RevisionRecord(
                            draft=draft,
                            detected_issues=critique.issues,
                            applied_changes=changes,
                            final_text=final_text,
                            score_delta=new_critique.score - score,
                        )
                    )
                    critique = new_critique
                    score = new_critique.score
                    if critique.report.is_accepted or self._needs_reroll(critique, final_text, existing_texts):
                        break
        long_description = final_text
        short_description = self.realizer.realize_short(facts, plan)
        if manual_description is not None:
            short_description = short_description or facts.dominant_landmark
        return LocationNarrativeResult(
            location_id=location_id,
            short_description=short_description,
            long_description=long_description,
            examinable_details=self.realizer.realize_examinable_details(facts, plan),
            optional_sensory_variants=self.realizer.realize_sensory_variants(facts, state),
            validation_report=critique.report,
            quality_score=score,
            generation_seed=facts.narrative_seed,
            generator_version=GENERATOR_VERSION,
            draft_trace=tuple(trace),
            manual_override=manual_description is not None,
        )

    def generate_from_facts(
        self,
        facts: PermanentLocationFacts,
        *,
        state: DynamicLocationState | None = None,
        existing_texts: tuple[str, ...] = (),
        use_local_fingerprint: bool = True,
        manual_description: str | None = None,
    ) -> LocationNarrativeResult:
        effective_facts = facts if use_local_fingerprint else replace(facts, local_fingerprint=None)
        state = state or self.world_adapter.state_for_location(effective_facts.location_id)
        plan = self.planner.build_plan(effective_facts, state)
        trace: list[RevisionRecord] = []
        if manual_description is not None:
            draft = manual_description
            critique = self.critic.critique(draft, effective_facts, existing_texts)
            score = critique.score
            final_text = draft
        else:
            final_text, critique = self._generate_draft(effective_facts, plan, state, existing_texts)
            score = critique.score
            if not critique.report.is_accepted and not self._needs_reroll(critique, final_text, existing_texts):
                draft = final_text
                for _ in range(3):
                    final_text, changes = self.reviser.revise(final_text, critique, effective_facts)
                    new_critique = self.critic.critique(final_text, effective_facts, existing_texts)
                    trace.append(
                        RevisionRecord(
                            draft=draft,
                            detected_issues=critique.issues,
                            applied_changes=changes,
                            final_text=final_text,
                            score_delta=new_critique.score - score,
                        )
                    )
                    critique = new_critique
                    score = new_critique.score
                    if critique.report.is_accepted or self._needs_reroll(critique, final_text, existing_texts):
                        break
        long_description = final_text
        short_description = self.realizer.realize_short(effective_facts, plan)
        if manual_description is not None:
            short_description = short_description or effective_facts.dominant_landmark
        return LocationNarrativeResult(
            location_id=effective_facts.location_id,
            short_description=short_description,
            long_description=long_description,
            examinable_details=self.realizer.realize_examinable_details(effective_facts, plan),
            optional_sensory_variants=self.realizer.realize_sensory_variants(effective_facts, state),
            validation_report=critique.report,
            quality_score=score,
            generation_seed=effective_facts.narrative_seed,
            generator_version=GENERATOR_VERSION,
            draft_trace=tuple(trace),
            manual_override=manual_description is not None,
        )

    def _generate_draft(
        self,
        facts: PermanentLocationFacts,
        plan: DescriptionPlan,
        state: DynamicLocationState,
        existing_texts: tuple[str, ...],
    ) -> tuple[str, CritiqueResult]:
        candidate = ""
        critique = self.critic.critique("", facts, existing_texts)
        variant_offset = _state_variant_offset(state)
        for variant in range(8):
            candidate = self.draft_source.generate(facts, plan, state, variant=variant + variant_offset)
            critique = self.critic.critique(candidate, facts, existing_texts)
            if not self._needs_reroll(critique, candidate, existing_texts):
                return candidate, critique
        return candidate, critique

    def _needs_reroll(self, critique: CritiqueResult, text: str, existing_texts: tuple[str, ...]) -> bool:
        if any(issue in critique.report.critical_errors for issue in {"ai_like", "regular_rhythm", "template_opening", "template_closure", "repetitive_opening", "repetitive_closure", "cliche_phrase"}):
            return True
        if any(issue in critique.report.warnings for issue in {"catalogue_style", "predictable_opening", "syntactic_monotony", "short_text"}):
            return True
        for other in existing_texts:
            if self.similarity_provider.similarity(text, other) >= self.validator.similarity_threshold:
                return True
        return False


def compare_location_results(left: LocationNarrativeResult, right: LocationNarrativeResult) -> dict[str, float]:
    similarity = DeterministicSimilarityProvider().similarity(left.long_description, right.long_description)
    return {
        "similarity": similarity,
        "short_overlap": 1.0 if left.short_description == right.short_description else 0.0,
        "score_gap": abs(left.quality_score - right.quality_score),
    }


def build_pilot_review(
    world: WorldManager,
    location_ids: tuple[int, ...],
    *,
    fingerprint_overlay: dict[int, FingerprintReviewEntry] | None = None,
    use_local_fingerprint: bool = True,
) -> list[LocationNarrativeResult]:
    generator = LocationNarrativeGenerator.default(world, fingerprint_overlay=fingerprint_overlay)
    return [generator.generate(location_id, use_local_fingerprint=use_local_fingerprint) for location_id in location_ids]


def export_review(results: list[LocationNarrativeResult], path: str | Path) -> Path:
    path = Path(path)
    payload = [asdict(result) for result in results]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_review(path: str | Path) -> list[dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

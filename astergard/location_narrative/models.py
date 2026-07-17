from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SensoryMode(StrEnum):
    light = "light"
    smell = "smell"
    sound = "sound"
    touch = "touch"


class DataCompleteness(StrEnum):
    COMPLETE = "COMPLETE"
    SUFFICIENT = "SUFFICIENT"
    SPARSE = "SPARSE"
    EMPTY = "EMPTY"


class LocalDistinctiveness(StrEnum):
    UNIQUE = "UNIQUE"
    DISTINCT = "DISTINCT"
    GENERIC = "GENERIC"
    INDISTINGUISHABLE = "INDISTINGUISHABLE"


class FingerprintReviewStatus(StrEnum):
    accept = "accept"
    edit = "edit"
    reject = "reject"
    pending = "pending"


class FingerprintTechnicalRecommendation(StrEnum):
    ACCEPT_CANDIDATE = "ACCEPT_CANDIDATE"
    EDIT_REQUIRED = "EDIT_REQUIRED"
    REJECT_CANDIDATE = "REJECT_CANDIDATE"


@dataclass(slots=True)
class NeighbouringLocationFact:
    location_id: int
    direction: str
    summary: str
    terrain: str = ""
    landmarks: tuple[str, ...] = ()


@dataclass(slots=True)
class LocationFingerprint:
    category: str
    subject: str
    physical_state: str
    spatial_position: str
    cause: str
    visibility: str
    persistence: str
    examinable: bool
    regional_compatibility: str
    neighbouring_constraints: tuple[str, ...] = ()
    subtype: str = ""


@dataclass(slots=True)
class FingerprintMicroScene:
    anchor_object: str
    local_position: str
    visible_state: str
    physical_cause: str
    relation_to_movement: str
    relation_to_neighbour: str
    optional_examinable: str = ""
    facts_that_must_not_be_added: tuple[str, ...] = ()


@dataclass(slots=True)
class FingerprintReviewEntry:
    location_id: int
    source_facts: dict[str, str]
    proposed_fingerprint: LocationFingerprint | None
    confidence: float
    hallucination_risk: str
    neighbouring_constraints: tuple[str, ...]
    review_status: FingerprintReviewStatus
    reviewer_note: str
    technical_recommendation: FingerprintTechnicalRecommendation = FingerprintTechnicalRecommendation.EDIT_REQUIRED


@dataclass(slots=True)
class StyleProfile:
    region_id: str
    dominant_materials: tuple[str, ...] = ()
    building_styles: tuple[str, ...] = ()
    road_types: tuple[str, ...] = ()
    vegetation: tuple[str, ...] = ()
    occupations: tuple[str, ...] = ()
    smell_sources: tuple[str, ...] = ()
    sound_sources: tuple[str, ...] = ()
    wear_signs: tuple[str, ...] = ()
    technical_vocabulary: tuple[str, ...] = ()
    register: str = "neutralny"
    max_metaphor_level: int = 2
    material_history: str = ""
    forbidden_cliches: tuple[str, ...] = ()
    forbidden_cultural_elements: tuple[str, ...] = ()


@dataclass(slots=True)
class RegionalKnowledgeEntry:
    lemma: str
    semantic_category: str
    regions: tuple[str, ...]
    location_types: tuple[str, ...]
    required_conditions: tuple[str, ...]
    excluding_conditions: tuple[str, ...]
    register: str = "neutralny"
    frequency: int = 50
    declension_data: str = ""
    semantic_tags: tuple[str, ...] = ()
    forms: dict[str, str] = field(default_factory=dict)
    natural_collocations: tuple[str, ...] = ()
    forbidden_collocations: tuple[str, ...] = ()
    sensory_sources: tuple[str, ...] = ()
    cause_trace: str = ""
    characteristicness: int = 50
    examinable: bool = False


@dataclass(slots=True)
class RegionalKnowledgeBank:
    region_id: str
    material_entries: tuple[RegionalKnowledgeEntry, ...] = ()
    construction_entries: tuple[RegionalKnowledgeEntry, ...] = ()
    trace_entries: tuple[RegionalKnowledgeEntry, ...] = ()
    natural_entries: tuple[RegionalKnowledgeEntry, ...] = ()
    economy_culture_entries: tuple[RegionalKnowledgeEntry, ...] = ()
    style_notes: tuple[str, ...] = ()

    def all_entries(self) -> tuple[RegionalKnowledgeEntry, ...]:
        return (
            *self.material_entries,
            *self.construction_entries,
            *self.trace_entries,
            *self.natural_entries,
            *self.economy_culture_entries,
        )


@dataclass(slots=True)
class PermanentLocationFacts:
    location_id: int
    region_id: str
    area_id: str
    location_type: str
    terrain: str
    biome: str
    settlement_type: str
    function: str
    scale: str
    enclosure: str
    elevation: str
    ground: str
    dominant_materials: tuple[str, ...]
    architecture: str
    vegetation: tuple[str, ...]
    water: str
    light_sources: tuple[str, ...]
    smell_sources: tuple[str, ...]
    sound_sources: tuple[str, ...]
    temperature: str
    humidity: str
    cleanliness: str
    maintenance: str
    age: str
    damage: str
    social_status: str
    economic_activity: str
    cultural_influences: tuple[str, ...]
    historical_layer: str
    danger_level: str
    dominant_landmark: str
    secondary_details: tuple[str, ...]
    persistent_activity: str
    visible_directions: tuple[str, ...]
    actual_exits: tuple[str, ...]
    examinable_features: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    neighbouring_location_facts: tuple[NeighbouringLocationFact, ...]
    regional_style_profile: StyleProfile
    narrative_seed: int
    regional_knowledge_bank: RegionalKnowledgeBank | None = None
    local_fingerprint: LocationFingerprint | None = None
    dominant_sensory_mode: SensoryMode = SensoryMode.sound
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DynamicLocationState:
    time_of_day: str
    weather: str
    season: str
    lighting: str
    current_event: str = ""
    recent_traces: tuple[str, ...] = ()
    temporary_threat: str = ""
    visibility_modifier: str = ""


@dataclass(slots=True)
class DescriptionPlan:
    opening_focus: str
    spatial_relation: str
    material_details: tuple[str, ...]
    use_trace: str
    sensory_anchor: str
    historical_trace: str
    examinable_hooks: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    style_register: str
    max_metaphor_level: int
    local_fingerprint: LocationFingerprint | None = None
    fingerprint_micro_scene: FingerprintMicroScene | None = None


@dataclass(slots=True)
class ValidationReport:
    factual_consistency: int
    spatial_consistency: int
    regional_consistency: int
    linguistic_correctness: int
    concreteness: int
    sensory_grounding: int
    distinctiveness: int
    readability: int
    stylistic_naturalness: int
    interaction_support: int
    repetition_risk: int
    cliché_risk: int
    critical_errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_accepted(self) -> bool:
        return not self.critical_errors and self.final_score >= 82

    @property
    def final_score(self) -> int:
        if self.critical_errors:
            return 0
        weighted = (
            self.factual_consistency * 0.20
            + self.spatial_consistency * 0.12
            + self.regional_consistency * 0.10
            + self.linguistic_correctness * 0.12
            + self.concreteness * 0.10
            + self.sensory_grounding * 0.07
            + self.distinctiveness * 0.10
            + self.readability * 0.09
            + self.stylistic_naturalness * 0.10
            + self.interaction_support * 0.03
            + (100 - self.repetition_risk) * 0.04
            + (100 - self.cliché_risk) * 0.03
        )
        return max(0, min(100, round(weighted)))


@dataclass(slots=True)
class RevisionRecord:
    draft: str
    detected_issues: tuple[str, ...]
    applied_changes: tuple[str, ...]
    final_text: str
    score_delta: int


@dataclass(slots=True)
class LocationNarrativeResult:
    location_id: int
    short_description: str
    long_description: str
    examinable_details: dict[str, str]
    optional_sensory_variants: dict[str, str]
    validation_report: ValidationReport
    quality_score: int
    generation_seed: int
    generator_version: str
    draft_trace: tuple[RevisionRecord, ...] = ()
    manual_override: bool = False

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from astergard.location_narrative.models import (
    DescriptionPlan,
    DynamicLocationState,
    FingerprintMicroScene,
    PermanentLocationFacts,
)
from astergard.location_narrative.regional_knowledge import bank_for_region, pick_examinable_hooks, pick_sensory_phrases, pick_surface_phrases, pick_trace_phrase


_DIRECTION_PHRASES = {
    "polnoc": "północy",
    "poludnie": "południu",
    "wschod": "wschodowi",
    "zachod": "zachodowi",
    "polnocny-wschod": "północnemu wschodowi",
    "polnocny-zachod": "północnemu zachodowi",
    "poludniowy-wschod": "południowemu wschodowi",
    "poludniowy-zachod": "południowemu zachodowi",
    "gora": "górze",
    "dol": "dołowi",
}

_DIRECTION_DESCRIPTORS = {
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

@dataclass(slots=True)
class DescriptionPlanner:
    def build_plan(self, facts: PermanentLocationFacts, state: DynamicLocationState | None = None) -> DescriptionPlan:
        state = state or DynamicLocationState(
            time_of_day="dzień",
            weather="bezchmurnie",
            season="nieznana",
            lighting="pełne światło",
        )
        bank = facts.regional_knowledge_bank or bank_for_region(facts.region_id)
        rng = Random(facts.narrative_seed)
        fingerprint = facts.local_fingerprint
        material_details = list(
            pick_surface_phrases(
                bank,
                location_type=facts.location_type,
                terrain=facts.terrain,
                state=state,
                rng=rng,
                count=3,
            )
        )
        if fingerprint:
            fingerprint_details = [
                item
                for item in (
                    fingerprint.subject,
                    fingerprint.physical_state,
                    fingerprint.spatial_position,
                )
                if item
            ]
            for detail in fingerprint_details:
                if detail not in material_details:
                    material_details.insert(0, detail)
        material_details = material_details[:3]
        opening_pool = [
            facts.dominant_landmark,
            material_details[0] if material_details else "",
            facts.function,
            facts.secondary_details[0] if facts.secondary_details else "",
            facts.secondary_details[-1] if facts.secondary_details else "",
        ]
        if fingerprint:
            opening_pool.extend([fingerprint.subject, fingerprint.physical_state, fingerprint.spatial_position])
        opening_candidates = tuple(candidate for candidate in opening_pool if candidate)
        opening_focus = rng.choice(opening_candidates) if opening_candidates else facts.function or facts.location_type
        sensory_candidates = pick_sensory_phrases(bank, location_type=facts.location_type, terrain=facts.terrain, state=state, rng=rng)
        sensory_anchor = sensory_candidates[0] if sensory_candidates else self._pick_sensory_anchor(facts, state, rng)
        spatial_relation = fingerprint.spatial_position if fingerprint and fingerprint.spatial_position else self._spatial_relation(facts)
        trace_phrase, trace_cause = pick_trace_phrase(bank, location_type=facts.location_type, terrain=facts.terrain, state=state, rng=rng)
        historical_trace = (
            fingerprint.cause
            if fingerprint and fingerprint.cause
            else facts.historical_layer
            or trace_cause
            or facts.age
            or facts.damage
            or bank.style_notes[0]
        )
        examinable_hooks = pick_examinable_hooks(bank, location_type=facts.location_type, terrain=facts.terrain, state=state, rng=rng)
        if not examinable_hooks:
            examinable_hooks = tuple(facts.examinable_features[:3])
        elif fingerprint and fingerprint.examinable and fingerprint.subject and fingerprint.subject not in examinable_hooks:
            examinable_hooks = (fingerprint.subject, *examinable_hooks[:2])
        fingerprint_micro_scene = self._build_fingerprint_micro_scene(facts, fingerprint, spatial_relation, trace_phrase, examinable_hooks)
        forbidden_claims = tuple(
            dict.fromkeys(
                (
                    *facts.forbidden_claims,
                    facts.location_type,
                    facts.terrain,
                    facts.biome,
                    *(phrase for entry in bank.all_entries() for phrase in entry.forbidden_collocations),
                )
            )
        )
        return DescriptionPlan(
            opening_focus=opening_focus,
            spatial_relation=spatial_relation,
            material_details=tuple(material_details),
            use_trace=trace_phrase or facts.persistent_activity or facts.economic_activity or facts.social_status,
            sensory_anchor=sensory_anchor,
            historical_trace=historical_trace,
            examinable_hooks=examinable_hooks,
            forbidden_claims=forbidden_claims,
            style_register=facts.regional_style_profile.register,
            max_metaphor_level=facts.regional_style_profile.max_metaphor_level,
            local_fingerprint=fingerprint,
            fingerprint_micro_scene=fingerprint_micro_scene,
        )

    def _pick_material_details(self, facts: PermanentLocationFacts, rng: Random) -> tuple[str, ...]:
        pool = list(facts.dominant_materials)
        if not pool:
            pool = list(facts.secondary_details)
        if not pool:
            return ()
        rng.shuffle(pool)
        return tuple(pool[:3])

    def _pick_sensory_anchor(self, facts: PermanentLocationFacts, state: DynamicLocationState, rng: Random) -> str:
        candidates = [*facts.smell_sources, *facts.sound_sources, *facts.light_sources]
        if state.current_event:
            candidates.insert(0, state.current_event)
        if not candidates:
            return state.lighting
        return rng.choice(candidates[: min(4, len(candidates))])

    def _spatial_relation(self, facts: PermanentLocationFacts) -> str:
        if facts.visible_directions:
            directions = [_DIRECTION_DESCRIPTORS.get(direction, direction) for direction in facts.visible_directions[:3]]
            if len(directions) == 1:
                return f"{directions[0]} stronie"
            if len(directions) == 2:
                return f"{directions[0]} i {directions[1]} stronie"
            return f"{directions[0]}, {directions[1]} i {directions[2]} stronie"
        return "jedynym czytelnym przejściu"

    def _build_fingerprint_micro_scene(
        self,
        facts: PermanentLocationFacts,
        fingerprint,
        spatial_relation: str,
        trace_phrase: str,
        examinable_hooks: tuple[str, ...],
    ) -> FingerprintMicroScene | None:
        if fingerprint is None:
            return None
        relation_to_movement = self._movement_relation(facts, fingerprint)
        relation_to_neighbour = self._neighbour_relation(facts, fingerprint)
        optional_examinable = examinable_hooks[0] if examinable_hooks and fingerprint.examinable else ""
        return FingerprintMicroScene(
            anchor_object=fingerprint.subject,
            local_position=fingerprint.spatial_position or spatial_relation,
            visible_state=fingerprint.physical_state,
            physical_cause=fingerprint.cause or trace_phrase,
            relation_to_movement=relation_to_movement,
            relation_to_neighbour=relation_to_neighbour,
            optional_examinable=optional_examinable,
            facts_that_must_not_be_added=facts.forbidden_claims,
        )

    def _movement_relation(self, facts: PermanentLocationFacts, fingerprint) -> str:
        if not fingerprint:
            return ""
        function = facts.function
        category = fingerprint.category
        if category in {"road_surface_change", "drainage_damage"} or function == "przejście":
            return "zwęża przejście i rozlewa wodę na bok"
        if category in {"structural_collapse", "vertical_exposure"}:
            return "osłabia przejście i osypuje kamień niżej"
        if category in {"maintenance_pressure", "work_residue"}:
            return "zostawia pył i ślady przy progu albo stanowisku"
        if category == "vegetation_narrowing":
            return "wciska roślinność w przejście"
        if category == "cave_contour":
            return "prowadzi przez ciasny, skalny ciąg"
        return ""

    def _neighbour_relation(self, facts: PermanentLocationFacts, fingerprint) -> str:
        if not fingerprint:
            return ""
        neighbours = facts.neighbouring_location_facts
        if not neighbours:
            return ""
        first = neighbours[0]
        terrain = first.terrain or ""
        if first.direction and terrain:
            return f"po {first.direction} stronie przechodzi w {terrain} teren"
        if first.direction:
            return f"po {first.direction} stronie widać sąsiednią lokację"
        if terrain:
            return f"przy krawędzi przechodzi w {terrain} teren"
        return "łączy się z sąsiednią lokacją"

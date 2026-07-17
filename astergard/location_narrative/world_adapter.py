from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from typing import Any

from astergard.location_narrative.models import (
    DataCompleteness,
    DynamicLocationState,
    FingerprintReviewEntry,
    FingerprintReviewStatus,
    LocalDistinctiveness,
    NeighbouringLocationFact,
    LocationFingerprint,
    PermanentLocationFacts,
    StyleProfile,
    SensoryMode,
)
from astergard.location_narrative.regional_knowledge import REGIONAL_KNOWLEDGE_BANKS, bank_for_region, region_style_profile
from astergard.world.manager import WorldManager
from astergard.world.models import Location


_ZONE_STYLE: dict[str, StyleProfile] = {region_id: region_style_profile(region_id) for region_id in REGIONAL_KNOWLEDGE_BANKS}

_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "terrain",
    "biome",
    "settlement_type",
    "function",
    "scale",
    "enclosure",
    "elevation",
    "ground",
    "dominant_materials",
    "architecture",
    "vegetation",
    "water",
    "light_sources",
    "smell_sources",
    "sound_sources",
    "temperature",
    "humidity",
    "cleanliness",
    "maintenance",
    "age",
    "damage",
    "social_status",
    "economic_activity",
    "cultural_influences",
    "historical_layer",
    "danger_level",
    "dominant_landmark",
    "secondary_details",
    "persistent_activity",
    "visible_directions",
    "actual_exits",
    "examinable_features",
    "forbidden_claims",
)

@dataclass(slots=True)
class IdentityAuditEntry:
    location_id: int
    name: str
    region_id: str
    area_id: str
    family: str
    data_completeness: DataCompleteness
    local_distinctiveness: LocalDistinctiveness
    local_fact_count: int
    regional_fact_count: int
    material_referents: int
    shared_with_neighbors: tuple[str, ...]
    shared_with_area: tuple[str, ...]
    empty_fields: tuple[str, ...]
    local_fingerprint: LocationFingerprint | None


def _normalize_signature(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, tuple):
        parts = [part.strip().lower() for part in value if isinstance(part, str) and part.strip()]
        return "|".join(sorted(dict.fromkeys(parts)))
    if isinstance(value, list):
        parts = [str(part).strip().lower() for part in value if str(part).strip()]
        return "|".join(sorted(dict.fromkeys(parts)))
    text = str(value).strip().lower()
    return text


def _countable_fields(facts: PermanentLocationFacts) -> dict[str, str]:
    return {
        field: _normalize_signature(getattr(facts, field))
        for field in _COMPLETENESS_FIELDS
    }


def _family_name(facts: PermanentLocationFacts) -> str:
    terrain = facts.terrain
    location_type = facts.location_type
    function = facts.function
    region = facts.region_id.lower()
    landmark = facts.dominant_landmark.lower()
    if terrain in {"ruinowy"} or "ruin" in region:
        return "ruin"
    if terrain in {"podziemny", "jaskiniowy"} or location_type == "podziemie":
        return "vertical" if "kopal" in region or "szyb" in landmark else "industrial"
    if location_type == "droga" or terrain == "drogowy":
        return "road"
    if location_type == "brama" or facts.enclosure == "zamknięta":
        return "border"
    if location_type == "wnętrze" or function in {"gospoda", "zaopatrzenie w wodę"}:
        return "interior"
    if any(token in landmark for token in ("ołtarz", "kaplic", "świąty", "sanktu")):
        return "sacred"
    if terrain in {"leśny", "bagienny"}:
        return "natural" if "bag" in region else "landscape"
    if facts.settlement_type == "miejska":
        return "town"
    return "landscape"


def _shared_field_names(facts: PermanentLocationFacts, peers: tuple[PermanentLocationFacts, ...]) -> tuple[str, ...]:
    shared: list[str] = []
    signatures = _countable_fields(facts)
    for field, signature in signatures.items():
        if not signature:
            continue
        if any(signature == _normalize_signature(getattr(peer, field)) for peer in peers):
            shared.append(field)
    return tuple(dict.fromkeys(shared))


def _material_referent_count(facts: PermanentLocationFacts) -> int:
    tokens = {
        token
        for token in (
            *facts.dominant_materials,
            facts.ground,
            facts.architecture,
            facts.water,
            facts.dominant_landmark,
        )
        if isinstance(token, str) and token.strip()
    }
    return len(tokens)


def _completeness_from_count(count: int) -> DataCompleteness:
    if count >= 18:
        return DataCompleteness.COMPLETE
    if count >= 12:
        return DataCompleteness.SUFFICIENT
    if count >= 6:
        return DataCompleteness.SPARSE
    return DataCompleteness.EMPTY


def _distinctiveness_from_facts(
    facts: PermanentLocationFacts,
    shared_with_neighbors: tuple[str, ...],
    shared_with_area: tuple[str, ...],
) -> LocalDistinctiveness:
    fingerprint = facts.local_fingerprint
    if fingerprint is None:
        if len(shared_with_area) >= 12 and len(shared_with_neighbors) >= 8:
            return LocalDistinctiveness.INDISTINGUISHABLE
        if len(shared_with_area) >= 8 or len(shared_with_neighbors) >= 5:
            return LocalDistinctiveness.GENERIC
        return LocalDistinctiveness.DISTINCT

    signature = {
        _normalize_signature(fingerprint.subject),
        _normalize_signature(fingerprint.physical_state),
        _normalize_signature(fingerprint.spatial_position),
        _normalize_signature(fingerprint.cause),
    }
    signature = {item for item in signature if item}
    if not signature:
        return LocalDistinctiveness.GENERIC
    overlap = len(shared_with_neighbors) + len(shared_with_area)
    if len(signature) >= 3 and overlap <= 4 and fingerprint.persistence == "permanent":
        return LocalDistinctiveness.UNIQUE
    if overlap <= 8 and fingerprint.examinable:
        return LocalDistinctiveness.DISTINCT
    if len(shared_with_area) >= 10:
        return LocalDistinctiveness.GENERIC
    return LocalDistinctiveness.DISTINCT


@dataclass(slots=True)
class WorldNarrativeAdapter:
    world: WorldManager
    fingerprint_overlay: dict[int, FingerprintReviewEntry] | None = None

    def facts_for_location(self, location_id: int) -> PermanentLocationFacts:
        location = self.world.get_location(location_id)
        if location is None:
            raise KeyError(f"Unknown location: {location_id}")
        style = _ZONE_STYLE.get(location.zone, self._default_style(location.zone))
        bank = bank_for_region(location.zone)
        neighbours = self._neighbour_facts(location)
        visible_directions = tuple(sorted(location.exits))
        facts = PermanentLocationFacts(
            location_id=location.id,
            region_id=location.zone,
            area_id=location.zone,
            location_type=self._guess_location_type(location),
            terrain=self._guess_terrain(location),
            biome=self._guess_biome(location),
            settlement_type=self._guess_settlement(location),
            function=self._guess_function(location),
            scale=self._guess_scale(location),
            enclosure=self._guess_enclosure(location),
            elevation=self._guess_elevation(location),
            ground=self._guess_ground(location),
            dominant_materials=self._guess_materials(location),
            architecture=self._guess_architecture(location),
            vegetation=self._guess_vegetation(location),
            water=self._guess_water(location),
            light_sources=self._guess_light(location),
            smell_sources=style.smell_sources,
            sound_sources=style.sound_sources,
            temperature=self._guess_temperature(location),
            humidity=self._guess_humidity(location),
            cleanliness=self._guess_cleanliness(location),
            maintenance=self._guess_maintenance(location),
            age=self._guess_age(location),
            damage=self._guess_damage(location),
            social_status=self._guess_social_status(location),
            economic_activity=self._guess_activity(location),
            cultural_influences=self._guess_culture(location),
            historical_layer=self._guess_history(location),
            danger_level=self._guess_danger(location),
            dominant_landmark=location.name,
            secondary_details=tuple(self._secondary_details(location)),
            persistent_activity=self._guess_persistence(location),
            visible_directions=visible_directions,
            actual_exits=visible_directions,
            examinable_features=tuple(location.inspectables.keys()),
            forbidden_claims=tuple(self._forbidden_claims(location)),
            neighbouring_location_facts=neighbours,
            regional_style_profile=style,
            narrative_seed=location.id,
            regional_knowledge_bank=bank,
            local_fingerprint=self._fingerprint_for_location(location, neighbours),
            dominant_sensory_mode=SensoryMode.sound,
            metadata={
                "zone_label": location.zone,
                "item_count": len(location.items),
                "npc_count": len(location.npc_ids),
                "base_description": location.description,
                "base_name": location.name,
                "inspectables": dict(location.inspectables),
            },
        )
        return self.apply_fingerprint_overlay(facts, location.id)

    def apply_fingerprint_overlay(
        self,
        facts: PermanentLocationFacts,
        location_id: int,
    ) -> PermanentLocationFacts:
        overlay = self.fingerprint_overlay or {}
        entry = overlay.get(location_id)
        if entry is None or entry.review_status not in {FingerprintReviewStatus.accept, FingerprintReviewStatus.edit}:
            return facts
        fingerprint = entry.proposed_fingerprint
        if fingerprint is None:
            return facts
        return replace(facts, local_fingerprint=fingerprint)

    def state_for_location(self, location_id: int) -> DynamicLocationState:
        location = self.world.get_location(location_id)
        if location is None:
            raise KeyError(f"Unknown location: {location_id}")
        return DynamicLocationState(
            time_of_day="dzień",
            weather="bezchmurnie",
            season="lato",
            lighting="pełne światło",
            recent_traces=tuple(),
            temporary_threat="",
        )

    def _neighbour_facts(self, location: Location) -> tuple[NeighbouringLocationFact, ...]:
        facts: list[NeighbouringLocationFact] = []
        for direction, exit_ in location.exits.items():
            neighbour = self.world.get_location(exit_.target_room)
            if neighbour is None:
                continue
            facts.append(
                NeighbouringLocationFact(
                    location_id=neighbour.id,
                    direction=direction,
                    summary=neighbour.description,
                    terrain=self._guess_terrain(neighbour),
                    landmarks=(neighbour.name,),
                )
            )
        return tuple(facts)

    def _default_style(self, zone: str) -> StyleProfile:
        return region_style_profile(zone)

    def audit_identity(self) -> tuple[IdentityAuditEntry, ...]:
        entries: list[IdentityAuditEntry] = []
        facts_by_location = {location_id: self.facts_for_location(location_id) for location_id in self.world.locations}
        for location_id, facts in facts_by_location.items():
            neighbours = tuple(facts_by_location.get(neighbour.location_id) for neighbour in facts.neighbouring_location_facts if neighbour.location_id in facts_by_location)
            same_area = tuple(
                peer
                for peer_id, peer in facts_by_location.items()
                if peer_id != location_id and peer.area_id == facts.area_id
            )
            shared_with_neighbors = _shared_field_names(facts, tuple(peer for peer in neighbours if peer is not None))
            shared_with_area = _shared_field_names(facts, same_area)
            completeness_count = sum(1 for value in _countable_fields(facts).values() if value)
            local_fact_count = max(0, completeness_count - len(shared_with_area))
            regional_fact_count = len(shared_with_area)
            location = self.world.get_location(location_id)
            entries.append(
                IdentityAuditEntry(
                    location_id=location_id,
                    name=location.name if location is not None else "",
                    region_id=facts.region_id,
                    area_id=facts.area_id,
                    family=_family_name(facts),
                    data_completeness=_completeness_from_count(completeness_count),
                    local_distinctiveness=_distinctiveness_from_facts(facts, shared_with_neighbors, shared_with_area),
                    local_fact_count=local_fact_count,
                    regional_fact_count=regional_fact_count,
                    material_referents=_material_referent_count(facts),
                    shared_with_neighbors=shared_with_neighbors,
                    shared_with_area=shared_with_area,
                    empty_fields=tuple(field for field, value in _countable_fields(facts).items() if not value),
                    local_fingerprint=facts.local_fingerprint,
                )
            )
        return tuple(entries)
    def _guess_location_type(self, location: Location) -> str:
        name = location.name.lower()
        if any(token in name for token in ("brama", "furta")):
            return "brama"
        if any(token in name for token in ("karcz", "zajazd")):
            return "wnętrze"
        if any(token in name for token in ("jask", "kopal", "tunel")):
            return "podziemie"
        if any(token in name for token in ("droga", "trakt", "ścieżka", "szlak")):
            return "droga"
        return "lokacja"

    def _guess_terrain(self, location: Location) -> str:
        return {
            "Centrum_Twierdza": "miejski",
            "Podgrodzie": "przedmiejski",
            "Haldun": "wiejski",
            "Osada_Mysliwych": "leśny",
            "Forteca_Dungrim": "forteczny",
            "Straznica_Przeleczy": "górski",
            "Trakty": "drogowy",
            "Boczne_Drogi": "drogowy",
            "Puszcza_Ciszy": "leśny",
            "Knieja_Cichych_Sciezek": "leśny",
            "Gory_Mekhara": "górski",
            "Kopalnia_Zelaza": "podziemny",
            "Ruiny_Karshold": "ruinowy",
            "Jaskinie_Wilkow": "jaskiniowy",
            "Bagna_Hookri": "bagienny",
        }.get(location.zone, "mieszany")

    def _guess_biome(self, location: Location) -> str:
        return self._guess_terrain(location)

    def _guess_settlement(self, location: Location) -> str:
        return "miejska" if location.zone in {"Centrum_Twierdza", "Podgrodzie"} else "pozamiejska"

    def _guess_function(self, location: Location) -> str:
        name = location.name.lower()
        if "karcz" in name:
            return "gospoda"
        if "brama" in name:
            return "kontrola przejazdu"
        if "studnia" in name:
            return "zaopatrzenie w wodę"
        return "przejście"

    def _guess_scale(self, location: Location) -> str:
        return "średnia"

    def _guess_enclosure(self, location: Location) -> str:
        return "otwarta" if location.zone not in {"Kopalnia_Zelaza", "Jaskinie_Wilkow", "Forteca_Dungrim"} else "zamknięta"

    def _guess_elevation(self, location: Location) -> str:
        if location.map_z > 1:
            return "wysoko"
        if location.map_z < 0:
            return "nisko"
        return "na poziomie gruntu"

    def _guess_ground(self, location: Location) -> str:
        return "grunt"

    def _guess_materials(self, location: Location) -> tuple[str, ...]:
        if location.zone in {"Centrum_Twierdza", "Forteca_Dungrim"}:
            return ("kamień", "drewno", "żelazo")
        if location.zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            return ("drewno", "mech", "kora")
        if location.zone == "Bagna_Hookri":
            return ("torf", "trzcina", "drewno")
        return ("kamień", "drewno")

    def _guess_architecture(self, location: Location) -> str:
        return "surowa"

    def _guess_vegetation(self, location: Location) -> tuple[str, ...]:
        if location.zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            return ("buk", "sosna", "paproć")
        if location.zone == "Bagna_Hookri":
            return ("trzcina", "wierzba")
        return ()

    def _guess_water(self, location: Location) -> str:
        if location.zone == "Bagna_Hookri":
            return "stojąca woda"
        if "studnia" in location.name.lower():
            return "studnia"
        return ""

    def _guess_light(self, location: Location) -> tuple[str, ...]:
        return ("pochodnie", "okna") if location.zone in {"Centrum_Twierdza", "Forteca_Dungrim"} else ()

    def _guess_temperature(self, location: Location) -> str:
        return "chłodno"

    def _guess_humidity(self, location: Location) -> str:
        return "umiarkowana"

    def _guess_cleanliness(self, location: Location) -> str:
        return "zmienna"

    def _guess_maintenance(self, location: Location) -> str:
        return "utrzymana"

    def _guess_age(self, location: Location) -> str:
        return "różny"

    def _guess_damage(self, location: Location) -> str:
        return "niewielkie"

    def _guess_social_status(self, location: Location) -> str:
        return "codzienna"

    def _guess_activity(self, location: Location) -> str:
        return {
            "Centrum_Twierdza": "handel i warta",
            "Podgrodzie": "targ i zaplecze",
            "Haldun": "rolnictwo",
            "Osada_Mysliwych": "obróbka trofeów",
            "Forteca_Dungrim": "wojsko i magazyny",
            "Straznica_Przeleczy": "kontrola przejazdu",
            "Trakty": "karawany",
            "Boczne_Drogi": "objazdy i naprawy",
            "Puszcza_Ciszy": "łowy i zbieractwo",
            "Knieja_Cichych_Sciezek": "łowy i patrole",
            "Gory_Mekhara": "przeprawa",
            "Kopalnia_Zelaza": "wydobycie",
            "Ruiny_Karshold": "poszukiwanie przejść",
            "Jaskinie_Wilkow": "ruch zwierząt",
            "Bagna_Hookri": "zbiory i przeprawy",
        }.get(location.zone, "ruch lokalny")

    def _guess_culture(self, location: Location) -> tuple[str, ...]:
        return (location.zone,)

    def _guess_history(self, location: Location) -> str:
        return {
            "Centrum_Twierdza": "warstwy murów i ciągłe naprawy",
            "Podgrodzie": "mokre przedmieście i łatane płoty",
            "Haldun": "praca pól i studni",
            "Osada_Mysliwych": "dym, skóry i tropy",
            "Forteca_Dungrim": "żelazo, warta i zapasy",
            "Straznica_Przeleczy": "kontrola przejazdu i wiatr",
            "Trakty": "ruch karawan i łatanie drogi",
            "Boczne_Drogi": "polne objazdy i rozjazdy",
            "Puszcza_Ciszy": "tropy, popiół i cień",
            "Knieja_Cichych_Sciezek": "gęstszy cień i starsze ścieżki",
            "Gory_Mekhara": "osypiska i wiatr",
            "Kopalnia_Zelaza": "wydobycie i obudowa chodników",
            "Ruiny_Karshold": "pożar i długie opuszczenie",
            "Jaskinie_Wilkow": "pazury i echo",
            "Bagna_Hookri": "torf, trzcina i kładki",
        }.get(location.zone, "warstwa użytkowa")

    def _guess_danger(self, location: Location) -> str:
        return "niski"

    def _secondary_details(self, location: Location) -> list[str]:
        details = list(location.inspectables.keys())
        if location.description:
            details.append(location.description.split(".")[0])
        return details[:4]

    def _guess_persistence(self, location: Location) -> str:
        return "stały ruch"

    def _forbidden_claims(self, location: Location) -> list[str]:
        claims = []
        if location.zone == "Bagna_Hookri":
            claims.append("suchy grunt")
        return claims

    def _fingerprint_subtype(self, location: Location, category: str) -> str:
        name = location.name.lower()
        zone = location.zone
        if category == "drainage_damage":
            if "kład" in name or "próg" in name:
                return "sunk_edge"
            if "rów" in name or "odpływ" in name:
                return "silted_drain"
            return "washed_bank"
        if category == "road_surface_change":
            if "bruk" in name:
                return "broken_paving"
            if "nasyp" in name or "skarpa" in name:
                return "slope_erosion"
            if "kolein" in name:
                return "rut_deepening"
            return "washed_edge"
        if category == "structural_collapse":
            if "schod" in name:
                return "broken_stair"
            if "łuk" in name:
                return "failed_arch"
            if "dach" in name or "strop" in name:
                return "missing_roof"
            if "fundament" in name:
                return "exposed_foundation"
            if "korzeń" in name:
                return "root_displacement"
            if "rozb" in name:
                return "material_salvage"
            return "fallen_wall"
        if category == "vertical_exposure":
            if "szyb" in name or zone == "Kopalnia_Zelaza":
                return "shaft_drop"
            if "schod" in name:
                return "stair_drop"
            if "urw" in name:
                return "cliff_edge"
            return "ledged_slope"
        if category == "maintenance_pressure":
            if "brama" in name or "furta" in name:
                return "threshold_wear"
            if "mur" in name:
                return "wall_wear"
            if "posadz" in name or "bruk" in name:
                return "floor_wear"
            return "traffic_wear"
        if category == "vegetation_narrowing":
            if "korz" in name:
                return "root_encroachment"
            if "pni" in name or "drzew" in name:
                return "canopy_close"
            if "ścież" in name or "przej" in name:
                return "path_squeeze"
            return "branch_close"
        if category == "cave_contour":
            if "szyb" in name:
                return "shaft_contour"
            if "korytarz" in name or "chodnik" in name:
                return "tight_passage"
            return "rock_rib"
        if category == "work_residue":
            if "piec" in name or "kuź" in name:
                return "furnace_residue"
            if "stół" in name or "warsztat" in name:
                return "bench_dust"
            if "magaz" in name or "skład" in name:
                return "stockpile_trace"
            return "handling_residue"
        return "local_trace"

    def _fingerprint_for_location(self, location: Location, neighbours: tuple[NeighbouringLocationFact, ...]) -> LocationFingerprint | None:
        neighbour_constraints = tuple(
            sorted(
                {
                    f"{fact.direction}:{fact.terrain}" if fact.terrain else fact.direction
                    for fact in neighbours[:3]
                }
            )
        )
        if location.zone == "Bagna_Hookri":
            return LocationFingerprint(
                category="drainage_damage",
                subject="krawędź przejścia",
                physical_state="podmokła i częściowo rozmyta",
                spatial_position="na dolnej krawędzi terenu",
                cause="spływ wody i osiadanie torfu",
                visibility="plain",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("wymaga niższej strefy lub miękkiego brzegu",),
                subtype=self._fingerprint_subtype(location, "drainage_damage"),
            )
        if location.zone in {"Trakty", "Boczne_Drogi"}:
            return LocationFingerprint(
                category="road_surface_change",
                subject="nawierzchnia traktu",
                physical_state="koleiny, żwir lub bruk o różnej głębokości",
                spatial_position="na osi przejazdu",
                cause="ruch wozów i spływ z krawędzi",
                visibility="plain",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("powinna łączyć się z sąsiednią drogą albo przejściem",),
                subtype=self._fingerprint_subtype(location, "road_surface_change"),
            )
        if location.zone in {"Ruiny_Karshold"}:
            return LocationFingerprint(
                category="structural_collapse",
                subject="mur lub strop",
                physical_state="częściowo zawalony lub wypalony",
                spatial_position="przy rdzeniu ruiny",
                cause="ogień, podmycie albo wtórny rozbiór",
                visibility="plain",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("powinien mieć ciągłość z sąsiednim fragmentem ruiny",),
                subtype=self._fingerprint_subtype(location, "structural_collapse"),
            )
        if location.zone in {"Gory_Mekhara", "Straznica_Przeleczy"}:
            return LocationFingerprint(
                category="vertical_exposure",
                subject="krawędź stoku",
                physical_state="osypująca się lub przecięta przejściem",
                spatial_position="powyżej lub poniżej głównego dojścia",
                cause="nachylenie i wiatr",
                visibility="plain",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("musi respektować zmianę wysokości",),
                subtype=self._fingerprint_subtype(location, "vertical_exposure"),
            )
        if location.zone in {"Forteca_Dungrim", "Centrum_Twierdza"}:
            return LocationFingerprint(
                category="maintenance_pressure",
                subject="próg, mur albo posadzka",
                physical_state="starta od ruchu i napraw",
                spatial_position="przy wejściu lub w osi przejścia",
                cause="warta, handel lub ciągły ruch",
                visibility="plain",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("powinna łączyć się z miejskim ruchem",),
                subtype=self._fingerprint_subtype(location, "maintenance_pressure"),
            )
        if location.zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            return LocationFingerprint(
                category="vegetation_narrowing",
                subject="prześwit między pniami",
                physical_state="zwężony przez korzenie i gałęzie",
                spatial_position="na granicy dojścia",
                cause="zarastanie i łamanie roślin przez ruch",
                visibility="partial",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("nie powinien przeczyć sąsiedniemu prześwitowi",),
                subtype=self._fingerprint_subtype(location, "vegetation_narrowing"),
            )
        if location.zone == "Jaskinie_Wilkow":
            return LocationFingerprint(
                category="cave_contour",
                subject="chodnik skalny",
                physical_state="ciasny i chropawy",
                spatial_position="przy ścianie lub w osi przejścia",
                cause="naturalny przebieg skały",
                visibility="partial",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("powinien zachować ciągłość korytarza",),
                subtype=self._fingerprint_subtype(location, "cave_contour"),
            )
        if location.zone == "Kopalnia_Zelaza":
            return LocationFingerprint(
                category="work_residue",
                subject="stanowisko pracy",
                physical_state="pokryte pyłem, żużlem albo odpadkami",
                spatial_position="przy blacie, piecu albo wjeździe",
                cause="obróbka, transport lub czyszczenie",
                visibility="plain",
                persistence="permanent",
                examinable=bool(location.inspectables),
                regional_compatibility="high",
                neighbouring_constraints=neighbour_constraints or ("powinien wynikać z faktycznej pracy na miejscu",),
                subtype=self._fingerprint_subtype(location, "work_residue"),
            )
        return None


def select_fingerprint_pilot_locations(world: WorldManager) -> tuple[int, ...]:
    adapter = WorldNarrativeAdapter(world)
    audit = adapter.audit_identity()
    desired = (
        ("natural", 10),
        ("ruin", 10),
        ("road", 10),
        ("border", 10),
        ("vertical", 10),
        ("sacred", 1),
        ("landscape", 9),
    )
    priority = {
        LocalDistinctiveness.INDISTINGUISHABLE: 0,
        LocalDistinctiveness.GENERIC: 1,
        LocalDistinctiveness.DISTINCT: 2,
        LocalDistinctiveness.UNIQUE: 3,
    }
    completeness_priority = {
        DataCompleteness.EMPTY: 0,
        DataCompleteness.SPARSE: 1,
        DataCompleteness.SUFFICIENT: 2,
        DataCompleteness.COMPLETE: 3,
    }
    selected: list[int] = []
    taken: set[int] = set()
    for family, count in desired:
        pool = [entry for entry in audit if entry.family == family and entry.location_id not in taken]
        pool.sort(
            key=lambda entry: (
                priority.get(entry.local_distinctiveness, 99),
                completeness_priority.get(entry.data_completeness, 99),
                entry.local_fact_count,
                entry.location_id,
            )
        )
        chosen = pool[:count]
        selected.extend(entry.location_id for entry in chosen)
        taken.update(entry.location_id for entry in chosen)
    if len(selected) < 60:
        remaining = [entry for entry in audit if entry.location_id not in taken]
        remaining.sort(
            key=lambda entry: (
                priority.get(entry.local_distinctiveness, 99),
                completeness_priority.get(entry.data_completeness, 99),
                entry.local_fact_count,
                entry.location_id,
            )
        )
        for entry in remaining:
            selected.append(entry.location_id)
            if len(selected) >= 60:
                break
    return tuple(selected[:60])

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random
from typing import Iterable

from astergard.commands.polish import normalize_phrase
from astergard.location_narrative.models import (
    DynamicLocationState,
    RegionalKnowledgeBank,
    RegionalKnowledgeEntry,
    StyleProfile,
)


def _ensure_tuple(value: tuple[str, ...] | str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _entry_factory(region_id: str):
    def _entry(
        lemma: str,
        semantic_category: str,
        location_types: tuple[str, ...] | str | Iterable[str],
        required_conditions: tuple[str, ...] | str | Iterable[str] = (),
        excluding_conditions: tuple[str, ...] | str | Iterable[str] = (),
        *,
        register: str = "neutralny",
        frequency: int = 50,
        declension_data: str = "",
        semantic_tags: tuple[str, ...] | str | Iterable[str] = (),
        natural_collocations: tuple[str, ...] | str | Iterable[str] = (),
        forbidden_collocations: tuple[str, ...] | str | Iterable[str] = (),
        sensory_sources: tuple[str, ...] | str | Iterable[str] = (),
        cause_trace: str = "",
        characteristicness: int = 50,
        examinable: bool = False,
        forms: dict[str, str] | None = None,
    ) -> RegionalKnowledgeEntry:
        return RegionalKnowledgeEntry(
            lemma=lemma,
            semantic_category=semantic_category,
            regions=(region_id,),
            location_types=_ensure_tuple(location_types),
            required_conditions=_ensure_tuple(required_conditions),
            excluding_conditions=_ensure_tuple(excluding_conditions),
            register=register,
            frequency=frequency,
            declension_data=declension_data,
            semantic_tags=_ensure_tuple(semantic_tags),
            natural_collocations=_ensure_tuple(natural_collocations),
            forbidden_collocations=_ensure_tuple(forbidden_collocations),
            sensory_sources=_ensure_tuple(sensory_sources),
            cause_trace=cause_trace,
            characteristicness=characteristicness,
            examinable=examinable,
            forms=forms or {},
        )

    return _entry


def _bank(
    region_id: str,
    *,
    style_notes: tuple[str, ...],
    materials: tuple[RegionalKnowledgeEntry, ...],
    constructions: tuple[RegionalKnowledgeEntry, ...],
    traces: tuple[RegionalKnowledgeEntry, ...],
    natural: tuple[RegionalKnowledgeEntry, ...],
    economy_culture: tuple[RegionalKnowledgeEntry, ...],
) -> RegionalKnowledgeBank:
    return RegionalKnowledgeBank(
        region_id=region_id,
        material_entries=materials,
        construction_entries=constructions,
        trace_entries=traces,
        natural_entries=natural,
        economy_culture_entries=economy_culture,
        style_notes=style_notes,
    )


def _surface(entry: RegionalKnowledgeEntry) -> str:
    if entry.natural_collocations:
        return entry.natural_collocations[0]
    return entry.lemma


def _active_conditions(
    bank: RegionalKnowledgeBank,
    location_type: str,
    terrain: str,
    state: DynamicLocationState | None,
) -> set[str]:
    state = state or DynamicLocationState(time_of_day="dzień", weather="", season="", lighting="")
    conditions = {
        bank.region_id,
        location_type,
        terrain,
        state.time_of_day,
        state.weather,
        state.season,
        state.lighting,
        state.current_event,
        state.temporary_threat,
        *bank.style_notes,
    }
    return {normalize_phrase(item) for item in conditions if item}


def _matches(entry: RegionalKnowledgeEntry, active_conditions: set[str], location_type: str) -> bool:
    if entry.location_types and location_type not in entry.location_types and "dowolna" not in entry.location_types:
        return False
    required = {normalize_phrase(item) for item in entry.required_conditions if item}
    excluded = {normalize_phrase(item) for item in entry.excluding_conditions if item}
    if required and not required.issubset(active_conditions):
        return False
    if excluded and excluded & active_conditions:
        return False
    return True


def _select_entries(
    entries: Iterable[RegionalKnowledgeEntry],
    bank: RegionalKnowledgeBank,
    location_type: str,
    terrain: str,
    state: DynamicLocationState | None,
    rng: Random,
    count: int,
) -> tuple[RegionalKnowledgeEntry, ...]:
    active_conditions = _active_conditions(bank, location_type, terrain, state)
    pool = [entry for entry in entries if _matches(entry, active_conditions, location_type)]
    if not pool:
        pool = list(entries)
    pool.sort(key=lambda entry: (entry.characteristicness, entry.frequency, entry.lemma), reverse=True)
    selected = pool[: max(count, min(len(pool), 6))]
    rng.shuffle(selected)
    return tuple(selected[:count])


def surface_for_entry(entry: RegionalKnowledgeEntry) -> str:
    return _surface(entry)


def pick_surface_phrases(
    bank: RegionalKnowledgeBank,
    *,
    location_type: str,
    terrain: str,
    state: DynamicLocationState | None,
    rng: Random,
    count: int = 3,
) -> tuple[str, ...]:
    materials = _select_entries(bank.material_entries, bank, location_type, terrain, state, rng, count)
    constructions = _select_entries(bank.construction_entries, bank, location_type, terrain, state, rng, count)
    combined = [*materials, *constructions]
    if not combined:
        combined = list(bank.all_entries())[:count]
    if not combined:
        return ()
    chosen = []
    for entry in combined:
        value = surface_for_entry(entry)
        if value not in chosen:
            chosen.append(value)
        if len(chosen) >= count:
            break
    return tuple(chosen)


def pick_trace_phrase(
    bank: RegionalKnowledgeBank,
    *,
    location_type: str,
    terrain: str,
    state: DynamicLocationState | None,
    rng: Random,
) -> tuple[str, str]:
    traces = _select_entries(bank.trace_entries, bank, location_type, terrain, state, rng, 2)
    if traces:
        primary = surface_for_entry(traces[0])
        cause = traces[0].cause_trace or primary
        return primary, cause
    culture = _select_entries(bank.economy_culture_entries, bank, location_type, terrain, state, rng, 1)
    if culture:
        primary = surface_for_entry(culture[0])
        return primary, culture[0].cause_trace or primary
    return "", ""


def pick_sensory_phrases(
    bank: RegionalKnowledgeBank,
    *,
    location_type: str,
    terrain: str,
    state: DynamicLocationState | None,
    rng: Random,
) -> tuple[str, ...]:
    entries = _select_entries(
        (*bank.natural_entries, *bank.economy_culture_entries, *bank.trace_entries),
        bank,
        location_type,
        terrain,
        state,
        rng,
        3,
    )
    senses: list[str] = []
    for entry in entries:
        for source in entry.sensory_sources:
            source = source.strip()
            if source and source not in senses:
                senses.append(source)
            if len(senses) >= 3:
                return tuple(senses)
    return tuple(senses)


def pick_examinable_hooks(
    bank: RegionalKnowledgeBank,
    *,
    location_type: str,
    terrain: str,
    state: DynamicLocationState | None,
    rng: Random,
) -> tuple[str, ...]:
    entries = _select_entries(
        [entry for entry in bank.all_entries() if entry.examinable],
        bank,
        location_type,
        terrain,
        state,
        rng,
        3,
    )
    return tuple(surface_for_entry(entry) for entry in entries)


def build_style_profile(bank: RegionalKnowledgeBank) -> StyleProfile:
    materials = tuple(dict.fromkeys(surface_for_entry(entry).split()[0] for entry in bank.material_entries[:4] if entry))
    buildings = tuple(dict.fromkeys(entry.semantic_tags[0] if entry.semantic_tags else entry.lemma for entry in bank.construction_entries[:4]))
    roads = tuple(dict.fromkeys(entry.lemma for entry in bank.construction_entries if "droga" in entry.semantic_tags or "nawierzchnia" in entry.semantic_tags))[:3]
    vegetation = tuple(dict.fromkeys(entry.lemma for entry in bank.natural_entries if "rośl" in " ".join(entry.semantic_tags) or "wilgoć" in entry.semantic_tags))[:4]
    occupations = tuple(dict.fromkeys(entry.lemma for entry in bank.economy_culture_entries[:4]))
    smell_sources = tuple(dict.fromkeys(source for entry in bank.natural_entries + bank.economy_culture_entries for source in entry.sensory_sources))[:4]
    sound_sources = tuple(dict.fromkeys(source for entry in bank.trace_entries + bank.economy_culture_entries for source in entry.sensory_sources))[:4]
    wear_signs = tuple(dict.fromkeys(entry.lemma for entry in bank.trace_entries[:4]))
    technical_vocabulary = tuple(dict.fromkeys(entry.lemma for entry in bank.construction_entries[:4]))
    material_history = bank.style_notes[0] if bank.style_notes else ""
    return StyleProfile(
        region_id=bank.region_id,
        dominant_materials=materials,
        building_styles=buildings,
        road_types=roads,
        vegetation=vegetation,
        occupations=occupations,
        smell_sources=smell_sources,
        sound_sources=sound_sources,
        wear_signs=wear_signs,
        technical_vocabulary=technical_vocabulary,
        register="neutralny",
        max_metaphor_level=1,
        material_history=material_history,
        forbidden_cliches=(),
        forbidden_cultural_elements=(),
    )


def bank_for_region(region_id: str) -> RegionalKnowledgeBank:
    return REGIONAL_KNOWLEDGE_BANKS.get(region_id, _default_bank(region_id))


@dataclass(slots=True)
class RegionalKnowledgeAudit:
    region_id: str
    sample_size: int
    top_nouns: tuple[tuple[str, int], ...]
    top_adjectives: tuple[tuple[str, int], ...]
    top_structures: tuple[tuple[str, int], ...]
    repeated_openings: tuple[tuple[str, int], ...]
    repeated_endings: tuple[tuple[str, int], ...]
    cultural_incompatibilities: tuple[str, ...]
    details_without_cause: tuple[str, ...]
    generic_fantasy_fragments: tuple[str, ...]
    rerun_consistent: bool


@dataclass(slots=True)
class RegionalStyleGuide:
    region_id: str
    material_identity: str
    dominant_contrasts: tuple[str, ...]
    frequent_elements: tuple[str, ...]
    rare_elements: tuple[str, ...]
    forbidden_elements: tuple[str, ...]
    good_concretes: tuple[str, ...]
    bad_abstracts: tuple[str, ...]
    neighbour_guidance: tuple[str, ...]


@dataclass(slots=True)
class RegionalGenerationAudit:
    region_id: str
    sample_size: int
    text_audit: RegionalKnowledgeAudit
    accepted_count: int
    rejected_count: int
    average_score: float



_GENERIC_FORBIDDEN = (
    "mroczna atmosfera",
    "serce lasu",
    "morze zieleni",
    "taniec cieni",
    "niepokojąca cisza",
    "skrywa tajemnice",
    "majestatyczny",
    "prastary",
    "złowieszczy",
)


def audit_region_texts(region_id: str, texts: Iterable[str], bank: RegionalKnowledgeBank) -> RegionalKnowledgeAudit:
    text_list = [normalize_phrase(text) for text in texts]
    noun_counter: Counter[str] = Counter()
    adjective_counter: Counter[str] = Counter()
    structure_counter: Counter[str] = Counter()
    opening_counter: Counter[str] = Counter()
    ending_counter: Counter[str] = Counter()
    details_without_cause: list[str] = []
    generic: list[str] = []

    for text in text_list:
        words = [word for word in text.split() if word]
        if not words:
            continue
        opening_counter[" ".join(words[:4])] += 1
        ending_counter[" ".join(words[-4:])] += 1
        structure_counter[f"{len(words)}:{text.count('.') + text.count('!') + text.count('?')}"] += 1
        for word in words:
            if len(word) > 4 and not word.endswith(("a", "e", "y", "i", "o", "u")):
                noun_counter[word] += 1
            if word.endswith(("y", "a", "e", "ny", "owy", "ski")) and len(word) > 4:
                adjective_counter[word] += 1
        if any(phrase in text for phrase in _GENERIC_FORBIDDEN):
            generic.append(text)
        if "bo" not in text and "ponieważ" not in text and any(token in text for token in ("koleiny", "sadza", "torf", "wilgoć", "rynsztok", "mch", "błot", "ścież", "mur", "bruk")):
            details_without_cause.append(text)

    incompatibilities = [entry.lemma for entry in bank.all_entries() if any(phrase in entry.forbidden_collocations for phrase in _GENERIC_FORBIDDEN)]
    return RegionalKnowledgeAudit(
        region_id=region_id,
        sample_size=len(text_list),
        top_nouns=tuple(noun_counter.most_common(20)),
        top_adjectives=tuple(adjective_counter.most_common(20)),
        top_structures=tuple(structure_counter.most_common(20)),
        repeated_openings=tuple(opening_counter.most_common(10)),
        repeated_endings=tuple(ending_counter.most_common(10)),
        cultural_incompatibilities=tuple(dict.fromkeys(incompatibilities)),
        details_without_cause=tuple(dict.fromkeys(details_without_cause[:20])),
        generic_fantasy_fragments=tuple(dict.fromkeys(generic[:20])),
        rerun_consistent=len(opening_counter) > 0 and len(ending_counter) > 0,
    )


def audit_region_generation(generator, world, region_id: str, sample_size: int = 200) -> RegionalGenerationAudit:
    location_ids = [location.id for location in world.locations.values() if location.zone == region_id]
    if not location_ids:
        raise KeyError(f"Unknown region: {region_id}")
    texts: list[str] = []
    scores: list[int] = []
    accepted = 0
    rejected = 0
    for index in range(sample_size):
        location_id = location_ids[index % len(location_ids)]
        result = generator.generate(location_id)
        texts.append(result.long_description)
        scores.append(result.quality_score)
        if result.validation_report.is_accepted:
            accepted += 1
        else:
            rejected += 1
    bank = bank_for_region(region_id)
    return RegionalGenerationAudit(
        region_id=region_id,
        sample_size=sample_size,
        text_audit=audit_region_texts(region_id, texts, bank),
        accepted_count=accepted,
        rejected_count=rejected,
        average_score=(sum(scores) / len(scores)) if scores else 0.0,
    )


def build_style_guide(region_id: str, bank: RegionalKnowledgeBank, audit: RegionalKnowledgeAudit | None = None) -> RegionalStyleGuide:
    audit = audit or audit_region_texts(region_id, (), bank)
    frequent = tuple(surface_for_entry(entry) for entry in bank.all_entries()[:6])
    rare = tuple(surface_for_entry(entry) for entry in bank.all_entries()[-4:])
    forbidden = tuple(_GENERIC_FORBIDDEN)
    good_concretes = tuple(
        surface_for_entry(entry)
        for entry in bank.all_entries()
        if entry.characteristicness >= 80
    )[:8]
    bad_abstracts = ("mroczna atmosfera", "niepokojąca cisza", "świadek minionych wydarzeń")
    neighbour_guidance = tuple(bank.style_notes[1:4]) if len(bank.style_notes) > 1 else ()
    return RegionalStyleGuide(
        region_id=region_id,
        material_identity=bank.style_notes[0] if bank.style_notes else "",
        dominant_contrasts=tuple(bank.style_notes[1:3]) if len(bank.style_notes) > 2 else (),
        frequent_elements=frequent,
        rare_elements=rare,
        forbidden_elements=forbidden,
        good_concretes=good_concretes,
        bad_abstracts=bad_abstracts,
        neighbour_guidance=neighbour_guidance,
    )


def _default_bank(region_id: str) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=("Miejsce nosi ślady codziennego użycia, napraw i pogody.", "Materiał i ślad są ważniejsze niż ozdobność."),
        materials=(
            e("kamień", "material", ("dowolna",), ("teren",), (), semantic_tags=("materiał", "kamień"), natural_collocations=("kamień łamany",), sensory_sources=("stuk",), cause_trace="budowa i ruch", characteristicness=70),
            e("drewno", "material", ("dowolna",), ("teren",), (), semantic_tags=("materiał", "drewno"), natural_collocations=("drewno konstrukcyjne",), sensory_sources=("skrzypienie",), cause_trace="obróbka i naprawy", characteristicness=68),
        ),
        constructions=(
            e("mur", "construction", ("dowolna",), ("teren",), (), semantic_tags=("obrona", "mur"), natural_collocations=("mur z kamienia",), sensory_sources=("echo",), cause_trace="wznoszenie i łatanie", characteristicness=72, examinable=True, forms={"nom": "mur", "gen": "muru", "loc": "murze"}),
            e("brama", "construction", ("dowolna",), ("teren",), (), semantic_tags=("przejście", "brama"), natural_collocations=("brama z okutym progiem",), sensory_sources=("zawiasy",), cause_trace="kontrola przejazdu", characteristicness=78, examinable=True, forms={"nom": "brama", "gen": "bramy", "loc": "bramie"}),
        ),
        traces=(
            e("koleina", "trace", ("dowolna",), ("teren",), (), semantic_tags=("ruch", "wozy"), natural_collocations=("koleiny po wozach",), sensory_sources=("skrzyp osi",), cause_trace="powtarzalny ruch", characteristicness=76, examinable=True, forms={"nom": "koleina", "gen": "koleiny", "loc": "koleinie"}),
            e("wilgoć", "trace", ("dowolna",), ("mokro",), (), semantic_tags=("woda",), natural_collocations=("wilgotne ślady",), sensory_sources=("kap",), cause_trace="słabe odprowadzenie wody", characteristicness=62, examinable=False),
        ),
        natural=(
            e("mgła", "natural", ("dowolna",), ("noc", "wilgotno"), (), semantic_tags=("widoczność",), natural_collocations=("mgła przy ziemi",), sensory_sources=("stłumione dźwięki",), cause_trace="wilgoć i chłód", characteristicness=64),
            e("mech", "natural", ("dowolna",), ("cień",), (), semantic_tags=("roślinność", "wilgoć"), natural_collocations=("mech od północnej strony",), sensory_sources=("szelest",), cause_trace="długie zacienienie", characteristicness=70),
        ),
        economy_culture=(
            e("handel", "culture", ("dowolna",), ("osada",), (), register="urzędowy", frequency=62, semantic_tags=("handel",), natural_collocations=("handel na wymianę",), sensory_sources=("monety",), cause_trace="przepływ towarów", characteristicness=74),
            e("naprawa", "culture", ("dowolna",), ("teren",), (), register="neutralny", frequency=66, semantic_tags=("praca", "utrzymanie"), natural_collocations=("naprawy po sezonie",), sensory_sources=("młotek",), cause_trace="zużycie materiału", characteristicness=71),
        ),
    )


def _urban_bank(region_id: str, *, history: str, trade: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, trade, *notes),
        materials=(
            e("kamień", "material", ("plac", "ulica", "brama", "mur"), ("miasto",), (), semantic_tags=("kamień", "bruk"), natural_collocations=("kamień ciosany", "starty bruk", "kamień w cokole"), sensory_sources=("stuk kół", "echo kroków"), cause_trace="ruch pieszy i wozów", characteristicness=95, declension_data="noun:m", forms={"nom": "kamień", "gen": "kamienia", "loc": "kamieniu"}),
            e("cegła", "material", ("plac", "ulica", "dziedziniec"), ("miasto",), (), semantic_tags=("cegła", "ściana"), natural_collocations=("cegła z zaprawą", "ceglany cokół"), sensory_sources=("suchy stuk",), cause_trace="miejskie murowanie", characteristicness=88, declension_data="noun:f", forms={"nom": "cegła", "gen": "cegły", "loc": "cegle"}),
        ),
        constructions=(
            e("mur", "construction", ("mur", "brama", "plac"), ("miasto",), (), semantic_tags=("obrona", "mur"), natural_collocations=("mur z ciosanego kamienia", "mur obronny"), sensory_sources=("echo",), cause_trace="obwarowanie", characteristicness=92, examinable=True, forms={"nom": "mur", "gen": "muru", "loc": "murze"}),
            e("rynsztok", "construction", ("ulica", "plac"), ("deszcz", "miasto"), (), semantic_tags=("odwodnienie", "bruk"), natural_collocations=("rynsztok przy krawężniku", "rynsztok z cegły"), sensory_sources=("kap",), cause_trace="odprowadzanie wody z bruku", characteristicness=86, examinable=True, forms={"nom": "rynsztok", "gen": "rynsztoku", "loc": "rynsztoku"}),
        ),
        traces=(
            e("sadza", "trace", ("kuchnia", "ulica", "brama"), ("piec",), (), semantic_tags=("dym", "ogień"), natural_collocations=("sadza na belkach", "sadza przy otworach"), sensory_sources=("dym",), cause_trace="ogniska i paleniska", characteristicness=84, examinable=False),
            e("koleina", "trace", ("ulica", "plac"), ("wozy",), (), semantic_tags=("koło", "transport"), natural_collocations=("koleiny od wozów", "koleiny na mokrym bruku"), sensory_sources=("skrzyp kół",), cause_trace="ciągły przejazd", characteristicness=90, examinable=True),
        ),
        natural=(
            e("wilgoć", "natural", ("ulica", "dziedziniec", "brama"), ("miasto",), (), semantic_tags=("mokro",), natural_collocations=("wilgoć przy murach", "wilgoć w szczelinach"), sensory_sources=("chłód",), cause_trace="cień wysokich ścian", characteristicness=76),
            e("dym", "natural", ("ulica", "plac"), ("piec",), (), semantic_tags=("ogień", "powietrze"), natural_collocations=("dym z palenisk",), sensory_sources=("palenisko",), cause_trace="domowe paleniska", characteristicness=82),
        ),
        economy_culture=(
            e("straż", "culture", ("brama", "plac"), ("warta",), (), register="urzędowy", frequency=74, semantic_tags=("obrona", "władza"), natural_collocations=("straż przy bramie", "straż zmianowa"), sensory_sources=("komendy",), cause_trace="kontrola ruchu", characteristicness=90, examinable=True),
            e("handel", "culture", ("plac", "ulica", "podcień"), ("miasto",), (), register="neutralny", frequency=82, semantic_tags=("kupcy", "towar"), natural_collocations=("handel w podcieniach", "handel przy placu"), sensory_sources=("gwar",), cause_trace="stały przepływ towarów", characteristicness=88),
        ),
    )


def _village_bank(region_id: str, *, history: str, crops: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, crops, *notes),
        materials=(
            e("drewno", "material", ("zagroda", "studnia", "stodoła"), ("wieś",), (), semantic_tags=("drewno",), natural_collocations=("drewno sosnowe", "drewno w płocie"), sensory_sources=("skrzyp",), cause_trace="budowa zagrodowa", characteristicness=92),
            e("glina", "material", ("dom", "piec", "podłoga"), ("wieś",), (), semantic_tags=("glina",), natural_collocations=("glina w zaprawie",), sensory_sources=("chłód",), cause_trace="lepienie ścian i pieców", characteristicness=84),
        ),
        constructions=(
            e("zagroda", "construction", ("zagroda", "obejście"), ("wieś",), (), semantic_tags=("gospodarstwo",), natural_collocations=("zagroda z żerdzi", "zagroda przy polu"), sensory_sources=("zatrzask",), cause_trace="hodowla i obejście", characteristicness=90, examinable=True),
            e("studnia", "construction", ("studnia", "plac"), ("woda",), (), semantic_tags=("woda", "zaopatrzenie"), natural_collocations=("studnia z cembrowiną", "studnia przy obejściu"), sensory_sources=("chlupot",), cause_trace="codzienne pobieranie wody", characteristicness=94, examinable=True, forms={"nom": "studnia", "gen": "studni", "loc": "studni"}),
        ),
        traces=(
            e("wydeptanie", "trace", ("droga", "obejście", "zagroda"), ("ruch pieszy",), (), semantic_tags=("ścieżka", "grunt"), natural_collocations=("wydeptana ziemia",), sensory_sources=("szelest trawy",), cause_trace="codzienny ruch ludzi", characteristicness=86),
            e("łatka", "trace", ("płot", "dom"), ("naprawa",), (), semantic_tags=("naprawa",), natural_collocations=("łatki na płocie", "łatki w dachu"), sensory_sources=("młotek",), cause_trace="drobne naprawy po sezonie", characteristicness=79),
        ),
        natural=(
            e("rosa", "natural", ("pole", "zagroda"), ("rano",), (), semantic_tags=("wilgoć",), natural_collocations=("rosa na trawie",), sensory_sources=("chłód poranka",), cause_trace="nocne wychłodzenie", characteristicness=71),
            e("błoto", "natural", ("droga", "obejście"), ("deszcz",), (), semantic_tags=("grunt",), natural_collocations=("błoto przy koleinach",), sensory_sources=("chlupot",), cause_trace="opady i ruch kół", characteristicness=88),
        ),
        economy_culture=(
            e("rolnictwo", "culture", ("wieś", "zagroda"), ("pole",), (), register="neutralny", frequency=90, semantic_tags=("praca", "pole"), natural_collocations=("praca przy zagonach",), sensory_sources=("kosy",), cause_trace="cykl upraw", characteristicness=94),
            e("targ", "culture", ("plac", "droga"), ("wieś",), (), register="neutralny", frequency=66, semantic_tags=("wymiana",), natural_collocations=("targ przy drodze",), sensory_sources=("gwar",), cause_trace="wymiana płodów", characteristicness=76),
        ),
    )


def _forest_bank(region_id: str, *, history: str, density: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, density, *notes),
        materials=(
            e("drewno", "material", ("ścieżka", "obóz", "przesmyk"), ("las",), (), semantic_tags=("drewno",), natural_collocations=("drewno okorowane", "gałęzie przy ziemi"), sensory_sources=("skrzyp gałęzi",), cause_trace="ścinanie i łamanie", characteristicness=92),
            e("kora", "material", ("drzewo", "obóz"), ("las",), (), semantic_tags=("drzewo",), natural_collocations=("kora na pniach", "kora przy zrębie"), sensory_sources=("szelest",), cause_trace="naturalny wzrost i obłupywanie", characteristicness=82),
        ),
        constructions=(
            e("szałas", "construction", ("obóz", "polana"), ("las",), (), semantic_tags=("nocleg",), natural_collocations=("szałas z gałęzi",), sensory_sources=("trzask",), cause_trace="tymczasowy postój", characteristicness=88, examinable=True),
            e("kładka", "construction", ("strumień", "ścieżka"), ("woda", "las"), (), semantic_tags=("przejście",), natural_collocations=("kładka nad rowem", "kładka z bali"), sensory_sources=("stuk desek",), cause_trace="przejście nad mokrym gruntem", characteristicness=86, examinable=True),
        ),
        traces=(
            e("trop", "trace", ("ścieżka", "polana"), ("las",), (), semantic_tags=("zwierzę", "ruch"), natural_collocations=("tropy przy korzeniach", "świeży trop"), sensory_sources=("szelest ściółki",), cause_trace="ruch ludzi i zwierząt", characteristicness=94, examinable=True),
            e("popiół", "trace", ("obóz", "polana"), ("ogień",), (), semantic_tags=("ogień",), natural_collocations=("popiół po ognisku",), sensory_sources=("sypki pył",), cause_trace="wygaszone palenisko", characteristicness=84),
        ),
        natural=(
            e("żywica", "natural", ("las", "obóz"), ("drzewa iglaste",), (), semantic_tags=("zapach",), natural_collocations=("żywica na pniu",), sensory_sources=("zapach",), cause_trace="uszkodzona kora", characteristicness=88),
            e("mech", "natural", ("las", "korzeń"), ("cień",), (), semantic_tags=("wilgoć",), natural_collocations=("mech od północnej strony",), sensory_sources=("miękkie stłumienie"), cause_trace="stałe zacienienie", characteristicness=90),
        ),
        economy_culture=(
            e("łowiectwo", "culture", ("las", "obóz"), ("myśliwi",), (), register="oszczędny", frequency=78, semantic_tags=("polowanie",), natural_collocations=("łowiectwo sezonowe",), sensory_sources=("gwizd",), cause_trace="polowania i tropienie", characteristicness=92),
            e("zbieractwo", "culture", ("las", "polana"), ("zioła",), (), register="neutralny", frequency=64, semantic_tags=("zbiór",), natural_collocations=("zbieractwo ziół",), sensory_sources=("szelest kosza",), cause_trace="sezon zbioru", characteristicness=74),
        ),
    )


def _fortress_bank(region_id: str, *, history: str, control: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, control, *notes),
        materials=(
            e("kamień", "material", ("mur", "brama", "dziedziniec"), ("forteca",), (), semantic_tags=("kamień",), natural_collocations=("kamień z licem", "kamień w murze"), sensory_sources=("stuk",), cause_trace="umacnianie warstwy", characteristicness=94),
            e("żelazo", "material", ("brama", "warsztat", "zbrojownia"), ("forteca",), (), semantic_tags=("żelazo",), natural_collocations=("żelazne okucia", "żelazny hak"), sensory_sources=("brzęk",), cause_trace="okucia i zbrojenia", characteristicness=90),
        ),
        constructions=(
            e("blanka", "construction", ("mur", "wieża"), ("forteca",), (), semantic_tags=("obrona",), natural_collocations=("blanki na murze",), sensory_sources=("kroki wart",), cause_trace="warty i obrona", characteristicness=84, examinable=True),
            e("bastion", "construction", ("mur", "dziedziniec"), ("forteca",), (), semantic_tags=("obrona", "artyleria"), natural_collocations=("bastion przy bramie",), sensory_sources=("komendy",), cause_trace="ostrzał i kontrola", characteristicness=88, examinable=True),
        ),
        traces=(
            e("naprawa", "trace", ("mur", "brama"), ("wojsko",), (), semantic_tags=("utrzymanie",), natural_collocations=("świeża naprawa muru",), sensory_sources=("młot",), cause_trace="uszkodzenia po wietrze i uderzeniach", characteristicness=86),
            e("warta", "trace", ("brama", "dziedziniec"), ("wojsko",), (), semantic_tags=("straż",), natural_collocations=("ślady warty",), sensory_sources=("metal",), cause_trace="zmiany posterunku", characteristicness=92),
        ),
        natural=(
            e("wiatr", "natural", ("mur", "wieża"), ("wysoko",), (), semantic_tags=("powietrze",), natural_collocations=("wiatr przy blankach",), sensory_sources=("świst",), cause_trace="otwarta ekspozycja", characteristicness=82),
            e("szron", "natural", ("mur", "dziedziniec"), ("zima",), (), semantic_tags=("chłód",), natural_collocations=("szron na kamieniu",), sensory_sources=("zimno",), cause_trace="nocny spadek temperatury", characteristicness=78),
        ),
        economy_culture=(
            e("garnizon", "culture", ("forteca",), ("wojsko",), (), register="urzędowy", frequency=86, semantic_tags=("wojsko",), natural_collocations=("garnizon zmianowy",), sensory_sources=("komenda",), cause_trace="stała obsada", characteristicness=96),
            e("magazyn", "culture", ("dziedziniec", "brama"), ("zapasy",), (), register="neutralny", frequency=72, semantic_tags=("zapasy",), natural_collocations=("magazyn z zapasami",), sensory_sources=("skrzynia",), cause_trace="gromadzenie rezerw", characteristicness=84),
        ),
    )


def _road_bank(region_id: str, *, history: str, ground: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, ground, *notes),
        materials=(
            e("tłuczeń", "material", ("droga", "przepust"), ("szlak",), (), semantic_tags=("drogowy",), natural_collocations=("tłuczeń pod kołami",), sensory_sources=("stuk",), cause_trace="układanie nawierzchni", characteristicness=90),
            e("żwir", "material", ("droga", "skraj"), ("szlak",), (), semantic_tags=("drogowy",), natural_collocations=("żwir na poboczu",), sensory_sources=("szelest",), cause_trace="wietrzenie i rozjazd", characteristicness=82),
        ),
        constructions=(
            e("przepust", "construction", ("droga", "rów"), ("woda",), (), semantic_tags=("odwodnienie",), natural_collocations=("przepust pod drogą",), sensory_sources=("kap",), cause_trace="odprowadzanie wody", characteristicness=86, examinable=True),
            e("znak", "construction", ("droga", "skręt"), ("szlak",), (), semantic_tags=("wskazanie",), natural_collocations=("znak drogowy",), sensory_sources=("deska",), cause_trace="znakowanie kierunku", characteristicness=84, examinable=True),
        ),
        traces=(
            e("koleina", "trace", ("droga", "skręt"), ("wozy",), (), semantic_tags=("ruch",), natural_collocations=("koleiny po wozach",), sensory_sources=("skrzyp osi",), cause_trace="ciągły przejazd", characteristicness=94),
            e("łata", "trace", ("droga", "przepust"), ("naprawa",), (), semantic_tags=("naprawa",), natural_collocations=("łaty na drodze",), sensory_sources=("młotek",), cause_trace="po sezonie deszczu", characteristicness=80),
        ),
        natural=(
            e("kurz", "natural", ("droga",), ("sucho",), (), semantic_tags=("pył",), natural_collocations=("kurz na trakcie",), sensory_sources=("szuranie"), cause_trace="ruch kół i kroków", characteristicness=76),
            e("śnieg", "natural", ("droga",), ("zima",), (), semantic_tags=("pogoda",), natural_collocations=("śnieg na poboczu",), sensory_sources=("cisza",), cause_trace="opad i wiatr", characteristicness=70),
        ),
        economy_culture=(
            e("karawana", "culture", ("droga",), ("handel",), (), register="neutralny", frequency=84, semantic_tags=("transport",), natural_collocations=("karawana ciężkich wozów",), sensory_sources=("dzwonki",), cause_trace="przewóz towaru", characteristicness=94),
            e("poczta", "culture", ("droga",), ("meldunek",), (), register="urzędowy", frequency=60, semantic_tags=("transport", "wieści"), natural_collocations=("poczta między osadami",), sensory_sources=("krzyk",), cause_trace="łączność między punktami", characteristicness=78),
        ),
    )


def _ruins_bank(region_id: str, *, history: str, collapse: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, collapse, *notes),
        materials=(
            e("kamień", "material", ("ruina", "mur", "dziedziniec"), ("ruiny",), (), semantic_tags=("kamień",), natural_collocations=("kamień ze zwietrzałym licem",), sensory_sources=("kruszenie"), cause_trace="czas i mróz", characteristicness=92),
            e("zaprawa", "material", ("mur", "fundament"), ("ruiny",), (), semantic_tags=("spoiwo",), natural_collocations=("zaprawa w spoinach",), sensory_sources=("pył"), cause_trace="rozpad spoin", characteristicness=84),
        ),
        constructions=(
            e("fundament", "construction", ("ruina", "dziedziniec"), ("ruiny",), (), semantic_tags=("podstawa",), natural_collocations=("odsłonięty fundament",), sensory_sources=("gruz"), cause_trace="zawalenie ścian", characteristicness=90, examinable=True),
            e("łuk", "construction", ("ruina", "wejście"), ("ruiny",), (), semantic_tags=("przejście",), natural_collocations=("pęknięty łuk",), sensory_sources=("odłamek"), cause_trace="osłabienie konstrukcji", characteristicness=88, examinable=True),
        ),
        traces=(
            e("pożar", "trace", ("ruina", "dziedziniec"), ("ogień",), (), semantic_tags=("ogień",), natural_collocations=("ślad pożaru",), sensory_sources=("sadza"), cause_trace="spalenie zabudowań", characteristicness=94),
            e("grabież", "trace", ("ruina", "skład"), ("rabunek",), (), semantic_tags=("wyłam",), natural_collocations=("wyłamane ślady grabieży",), sensory_sources=("pustka"), cause_trace="wyniesienie wyposażenia", characteristicness=88),
        ),
        natural=(
            e("mech", "natural", ("ruina", "mur"), ("wilgotno",), (), semantic_tags=("wilgoć",), natural_collocations=("mech na spoinach",), sensory_sources=("miękkość"), cause_trace="cień i wilgoć", characteristicness=84),
            e("woda", "natural", ("ruina", "dziedziniec"), ("deszcz",), (), semantic_tags=("zalanie",), natural_collocations=("woda stojąca w zagłębieniach",), sensory_sources=("chlupot"), cause_trace="zniszczone odwodnienie", characteristicness=86),
        ),
        economy_culture=(
            e("opuszczenie", "culture", ("ruina",), ("pustka",), (), register="neutralny", frequency=78, semantic_tags=("zanik",), natural_collocations=("długie opuszczenie",), sensory_sources=("cisza"), cause_trace="wyjazd i rozpad osady", characteristicness=92),
            e("poszukiwanie", "culture", ("ruina",), ("ruiny",), (), register="neutralny", frequency=54, semantic_tags=("badanie",), natural_collocations=("poszukiwanie przejścia"), sensory_sources=("głos"), cause_trace="ostrożna eksploracja", characteristicness=72),
        ),
    )


def _mine_bank(region_id: str, *, history: str, depth: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, depth, *notes),
        materials=(
            e("drewno", "material", ("szyb", "korytarz"), ("kopalnia",), (), semantic_tags=("obudowa",), natural_collocations=("drewniana obudowa",), sensory_sources=("trzeszczenie",), cause_trace="wzmocnienie chodników", characteristicness=92),
            e("żelazo", "material", ("szyb", "warsztat"), ("kopalnia",), (), semantic_tags=("ruda",), natural_collocations=("żelazne okucia",), sensory_sources=("brzęk"), cause_trace="wydobycie i obróbka", characteristicness=88),
        ),
        constructions=(
            e("szyb", "construction", ("szyb",), ("kopalnia",), (), semantic_tags=("wydobycie",), natural_collocations=("szyb wentylacyjny", "szyb z windą"), sensory_sources=("echo"), cause_trace="głębienie wyrobiska", characteristicness=94, examinable=True),
            e("obudowa", "construction", ("korytarz",), ("kopalnia",), (), semantic_tags=("podpora",), natural_collocations=("obudowa z bali",), sensory_sources=("skrzyp"), cause_trace="podparcie stropu", characteristicness=86),
        ),
        traces=(
            e("sadza", "trace", ("korytarz", "warsztat"), ("ogień",), (), semantic_tags=("dym",), natural_collocations=("sadza na ścianach",), sensory_sources=("pył"), cause_trace="lampy i paleniska", characteristicness=88),
            e("wilgoć", "trace", ("korytarz", "szyb"), ("podziemie",), (), semantic_tags=("woda",), natural_collocations=("wilgoć w spoinach",), sensory_sources=("kap"), cause_trace="przesiąkanie skały", characteristicness=84),
        ),
        natural=(
            e("pył", "natural", ("korytarz",), ("kopalnia",), (), semantic_tags=("ruda",), natural_collocations=("pył rudny",), sensory_sources=("suchy osad"), cause_trace="kruszenie skały", characteristicness=82),
            e("echo", "natural", ("szyb", "korytarz"), ("podziemie",), (), semantic_tags=("dźwięk",), natural_collocations=("echo w szybie",), sensory_sources=("odgłos"), cause_trace="zamknięta przestrzeń", characteristicness=86),
        ),
        economy_culture=(
            e("urobek", "culture", ("kopalnia",), ("praca",), (), register="techniczny", frequency=90, semantic_tags=("wydobycie",), natural_collocations=("urobek wózkami",), sensory_sources=("zgrzyt"), cause_trace="wydobywanie rudy", characteristicness=96),
            e("wózek", "culture", ("szyb", "korytarz"), ("kopalnia",), (), register="neutralny", frequency=68, semantic_tags=("transport",), natural_collocations=("wózek z rudą",), sensory_sources=("koła"), cause_trace="transport rudy", characteristicness=86, examinable=True),
        ),
    )


def _swamp_bank(region_id: str, *, history: str, wetness: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, wetness, *notes),
        materials=(
            e("torf", "material", ("bagno", "kępa", "grobla"), ("mokro",), (), semantic_tags=("mokradło",), natural_collocations=("torf miękki i ciężki",), sensory_sources=("wilgoć"), cause_trace="nagromadzenie roślinnych osadów", characteristicness=94),
            e("trzcina", "material", ("bagno", "kładka"), ("mokro",), (), semantic_tags=("roślina",), natural_collocations=("trzcina przy brzegu",), sensory_sources=("szelest"), cause_trace="wzrost na płytkiej wodzie", characteristicness=88),
        ),
        constructions=(
            e("kładka", "construction", ("bagno", "grobla"), ("mokro",), (), semantic_tags=("przejście",), natural_collocations=("kładka na palach",), sensory_sources=("stuk desek"), cause_trace="przejście nad grzęzawiskiem", characteristicness=90, examinable=True),
            e("palik", "construction", ("bagno", "brzeg"), ("wytyczenie",), (), semantic_tags=("znacznik",), natural_collocations=("palik w szlamie",), sensory_sources=("skrzyp"), cause_trace="oznaczanie bezpiecznej drogi", characteristicness=84, examinable=True),
        ),
        traces=(
            e("zalanie", "trace", ("bagno", "grobla"), ("deszcz",), (), semantic_tags=("woda",), natural_collocations=("zalane ślady",), sensory_sources=("chlupot"), cause_trace="wysoka woda", characteristicness=92),
            e("zbutwienie", "trace", ("bagno", "brzeg"), ("wilgoć",), (), semantic_tags=("rozpad",), natural_collocations=("zbutwiałe gałęzie",), sensory_sources=("miękki trzask"), cause_trace="długie zawilgocenie", characteristicness=86),
        ),
        natural=(
            e("mgła", "natural", ("bagno",), ("wilgotno",), (), semantic_tags=("widoczność",), natural_collocations=("mgła przy ziemi",), sensory_sources=("stłumienie"), cause_trace="chłód i woda", characteristicness=90),
            e("plusk", "natural", ("bagno",), ("woda",), (), semantic_tags=("dźwięk",), natural_collocations=("plusk w trzcinie",), sensory_sources=("woda"), cause_trace="ruch zwierząt i ludzi", characteristicness=82),
        ),
        economy_culture=(
            e("zioła", "culture", ("bagno",), ("zbiór",), (), register="neutralny", frequency=74, semantic_tags=("zbiór",), natural_collocations=("torfowe zioła",), sensory_sources=("ostry zapach"), cause_trace="zbiór na mokradle", characteristicness=94, examinable=True),
            e("przeprawa", "culture", ("bagno", "grobla"), ("transport",), (), register="neutralny", frequency=66, semantic_tags=("transport",), natural_collocations=("przeprawa po kępach",), sensory_sources=("krótki rozkaz"), cause_trace="przejście ludzi i towarów", characteristicness=84),
        ),
    )


def _hunter_bank(region_id: str, *, history: str, hide: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, hide, *notes),
        materials=(
            e("skóra", "material", ("obóz", "suszarni", "pracownia"), ("myśliwi",), (), semantic_tags=("skóra",), natural_collocations=("skóra suszona przy dymie",), sensory_sources=("zapach garbni"), cause_trace="obróbka trofeów", characteristicness=90),
            e("drewno", "material", ("obóz", "suszarni"), ("las",), (), semantic_tags=("drewno",), natural_collocations=("drewno okorowane",), sensory_sources=("skrzyp"), cause_trace="budowa w terenie leśnym", characteristicness=84),
        ),
        constructions=(
            e("wędzarnia", "construction", ("obóz", "pracownia"), ("dym",), (), semantic_tags=("obróbka",), natural_collocations=("wędzarnia przy ścianie",), sensory_sources=("dym"), cause_trace="suszenie mięsa i skór", characteristicness=94, examinable=True),
            e("suszarnia", "construction", ("obóz", "pracownia"), ("myśliwi",), (), semantic_tags=("obróbka",), natural_collocations=("suszarnia skór",), sensory_sources=("suchy trzask"), cause_trace="dosuszanie trofeów", characteristicness=88, examinable=True),
        ),
        traces=(
            e("nacięcie", "trace", ("praca", "obóz"), ("narzędzie",), (), semantic_tags=("obróbka",), natural_collocations=("nacięcia po nożu",), sensory_sources=("skrobanie"), cause_trace="cięcie skóry i drewna", characteristicness=86),
            e("trop", "trace", ("las", "ścieżka"), ("łowy",), (), semantic_tags=("zwierzyna",), natural_collocations=("tropy przy obozie",), sensory_sources=("trzeszczenie ściółki"), cause_trace="kontrola szlaków zwierząt", characteristicness=92),
        ),
        natural=(
            e("dym", "natural", ("obóz", "pracownia"), ("wędzarnia",), (), semantic_tags=("ogień",), natural_collocations=("dym z wędzarni",), sensory_sources=("zapach dymu"), cause_trace="suszenie i obróbka", characteristicness=88),
            e("żywica", "natural", ("las", "obóz"), ("sosna",), (), semantic_tags=("zapach",), natural_collocations=("żywica na korze",), sensory_sources=("ostry zapach"), cause_trace="pęknięta kora", characteristicness=84),
        ),
        economy_culture=(
            e("łup", "culture", ("obóz",), ("polowanie",), (), register="neutralny", frequency=60, semantic_tags=("zdobycz",), natural_collocations=("łup z polowania",), sensory_sources=("krótka rozmowa"), cause_trace="rozliczanie zdobyczy", characteristicness=88),
            e("skóry", "culture", ("pracownia", "obóz"), ("handlowe",), (), register="neutralny", frequency=64, semantic_tags=("handel",), natural_collocations=("skóry na belkach",), sensory_sources=("szelest"), cause_trace="sortowanie i sprzedaż", characteristicness=86),
        ),
    )


def _pass_bank(region_id: str, *, history: str, wind: str, notes: tuple[str, ...]) -> RegionalKnowledgeBank:
    e = _entry_factory(region_id)
    return _bank(
        region_id,
        style_notes=(history, wind, *notes),
        materials=(
            e("kamień", "material", ("przełęcz", "mur", "skarpa"), ("góry",), (), semantic_tags=("kamień",), natural_collocations=("kamień łupany",), sensory_sources=("stuk"), cause_trace="osuwanie i budowa", characteristicness=92),
            e("łupek", "material", ("skarpa", "przejście"), ("góry",), (), semantic_tags=("skała",), natural_collocations=("łupek na zboczu",), sensory_sources=("zgrzyt"), cause_trace="warstwowa skała odsłonięta przez wiatr", characteristicness=88),
        ),
        constructions=(
            e("poręcz", "construction", ("skarpa", "schody"), ("góry",), (), semantic_tags=("bezpieczeństwo",), natural_collocations=("poręcz na krawędzi",), sensory_sources=("metal"), cause_trace="zabezpieczenie przejścia", characteristicness=84, examinable=True),
            e("mur oporowy", "construction", ("skarpa", "droga"), ("góry",), (), semantic_tags=("podpora",), natural_collocations=("mur oporowy przy drodze",), sensory_sources=("kamień"), cause_trace="utrzymanie gruntu", characteristicness=90, examinable=True),
        ),
        traces=(
            e("osypisko", "trace", ("skarpa", "droga"), ("deszcz",), (), semantic_tags=("erozja",), natural_collocations=("osypisko przy zakręcie",), sensory_sources=("gruz"), cause_trace="kruszenie zbocza", characteristicness=94),
            e("pył", "trace", ("przełęcz", "droga"), ("wiatr",), (), semantic_tags=("skała",), natural_collocations=("pył na kamieniu",), sensory_sources=("suchy osad"), cause_trace="wiatr i obcieranie skał", characteristicness=82),
        ),
        natural=(
            e("wiatr", "natural", ("przełęcz", "skarpa"), ("góry",), (), semantic_tags=("powietrze",), natural_collocations=("wiatr w przesmyku",), sensory_sources=("świst"), cause_trace="otwarty grzbiet", characteristicness=92),
            e("mróz", "natural", ("przełęcz", "góra"), ("zima",), (), semantic_tags=("chłód",), natural_collocations=("mróz na kamieniu",), sensory_sources=("szron"), cause_trace="wysoka ekspozycja", characteristicness=84),
        ),
        economy_culture=(
            e("straż", "culture", ("przełęcz",), ("wojsko",), (), register="urzędowy", frequency=84, semantic_tags=("warta",), natural_collocations=("straż przełęczy",), sensory_sources=("komenda"), cause_trace="kontrola przejazdu", characteristicness=96),
            e("karawana", "culture", ("droga", "przełęcz"), ("transport",), (), register="neutralny", frequency=70, semantic_tags=("handel",), natural_collocations=("karawana na grzbiecie",), sensory_sources=("dzwonki"), cause_trace="przejazd towarowy", characteristicness=86),
        ),
    )


def _style_notes(*items: str) -> tuple[str, ...]:
    return tuple(item for item in items if item)


REGIONAL_KNOWLEDGE_BANKS: dict[str, RegionalKnowledgeBank] = {
    "Centrum_Twierdza": _urban_bank(
        "Centrum_Twierdza",
        history="Twierdza opiera się na kamieniu, ciosach murarskich i stałym ruchu służb.",
        trade="Handel w centrum wisi na bramach, składach i krótkich zmianach straży.",
        notes=_style_notes("bruk", "bramy", "rynsztoki", "cysterna", "cech"),
    ),
    "Podgrodzie": _urban_bank(
        "Podgrodzie",
        history="Podgrodzie jest niższe, bardziej mokre i łatane szybciej niż centrum.",
        trade="Tu materiał krąży między targiem, wozem i zapleczem miejskim.",
        notes=_style_notes("błoto", "płoty", "kramy", "warsztaty"),
    ),
    "Haldun": _village_bank(
        "Haldun",
        history="Haldun stoi na pracy pól, cembrowinach i prostych naprawach po sezonie.",
        crops="Wieś oddycha zbożem, sianem i wodą ze studni.",
        notes=_style_notes("zagrody", "zboże", "studnie", "płoty"),
    ),
    "Osada_Mysliwych": _hunter_bank(
        "Osada_Mysliwych",
        history="Osada myśliwych żyje dymem, skórą i rozchodzeniem się tropów w lesie.",
        hide="To miejsce bardziej obrabia zdobycz niż ją wystawia.",
        notes=_style_notes("wędzarnie", "suszarnie", "psy", "tropy"),
    ),
    "Forteca_Dungrim": _fortress_bank(
        "Forteca_Dungrim",
        history="Forteca Dungrim trzyma ciężar żelaza, kamienia i liczonej warty.",
        control="Na pierwszym planie stoją brama, meldunek i zapasy.",
        notes=_style_notes("żelazo", "warta", "skład", "blanki"),
    ),
    "Straznica_Przeleczy": _pass_bank(
        "Straznica_Przeleczy",
        history="Strażnica jest wąska, surowa i zbudowana pod kontrolę przejazdu.",
        wind="Wiatr jest tu stałym współautorem wszystkiego, co widoczne.",
        notes=_style_notes("przełęcz", "skarpa", "meldunek", "liny"),
    ),
    "Trakty": _road_bank(
        "Trakty",
        history="Trakty żyją koleiną, tłuczniem i ruchami karawan między osadami.",
        ground="Droga mówi tu językiem kół, kurzu i łatania po deszczu.",
        notes=_style_notes("koleiny", "miedz", "znaki", "przepusty"),
    ),
    "Boczne_Drogi": _road_bank(
        "Boczne_Drogi",
        history="Boczne drogi zbierają mniej ruchu, ale więcej brudu i doraźnych napraw.",
        ground="Tu trasa jest bardziej rolnicza, rozjeżdżona i mniej oficjalna.",
        notes=_style_notes("błoto", "pobocza", "rozjazdy", "przepusty"),
    ),
    "Puszcza_Ciszy": _forest_bank(
        "Puszcza_Ciszy",
        history="Puszcza Ciszy trzyma mech, korę i ruch tropów pod koronami.",
        density="To las o czytelnym dnie i gęstym cieniu na bokach ścieżek.",
        notes=_style_notes("polany", "tropy", "żywica", "obóz"),
    ),
    "Knieja_Cichych_Sciezek": _forest_bank(
        "Knieja_Cichych_Sciezek",
        history="Knieja jest głębsza, starsza i mniej chętna do oddawania jasnej drogi.",
        density="Cień jest tu cięższy, a ścieżka częściej znika niż prowadzi.",
        notes=_style_notes("knieja", "mech", "gałęzie", "ślady"),
    ),
    "Gory_Mekhara": _pass_bank(
        "Gory_Mekhara",
        history="Góry Mekhara są warstwą łupku, pyłu i twardego przejścia.",
        wind="Wiatr i osypiska robią za główne rzemiosło terenu.",
        notes=_style_notes("zbocza", "osypiska", "liny", "przełęcze"),
    ),
    "Kopalnia_Zelaza": _mine_bank(
        "Kopalnia_Zelaza",
        history="Kopalnia Żelaza opiera się na obudowie, wózkach i powtarzalnym wydobyciu.",
        depth="Im głębiej, tym więcej pyłu, wilgoci i skrzypiących podpór.",
        notes=_style_notes("szyby", "wózki", "pył", "obudowa"),
    ),
    "Ruiny_Karshold": _ruins_bank(
        "Ruiny_Karshold",
        history="Ruiny Karshold są pamięcią po pożarze, rozbiórce i długim opuszczeniu.",
        collapse="Tu głównym faktem jest rozpad, a nie legenda.",
        notes=_style_notes("gruz", "sadza", "mech", "fundament"),
    ),
    "Jaskinie_Wilkow": _mine_bank(
        "Jaskinie_Wilkow",
        history="Jaskinie Wilków są bardziej organiczne niż górnicze i trzymają ślady pazurów.",
        depth="W podziemiu dźwięk wraca szybciej niż światło.",
        notes=_style_notes("kości", "wilgoć", "pazury", "echo"),
    ),
    "Bagna_Hookri": _swamp_bank(
        "Bagna_Hookri",
        history="Bagna Hookri składają się z torfu, trzcin i dróg, które trzeba utrzymywać ręcznie.",
        wetness="Tu woda jest częścią gruntu, a nie tylko przeszkodą.",
        notes=_style_notes("torf", "trzcina", "mgła", "kładki"),
    ),
}


def _default_style_notes(region_id: str) -> tuple[str, ...]:
    return (f"Region {region_id} opiera się na materialnym konkretcie i powtarzalnej pracy.", "Unikaj ogólnych metafor i pustych klisz.")


def _default_style_profile(region_id: str) -> StyleProfile:
    return StyleProfile(
        region_id=region_id,
        dominant_materials=("kamień", "drewno"),
        building_styles=("surowy",),
        road_types=("przejście",),
        vegetation=(),
        occupations=("praca",),
        smell_sources=("wilgoć",),
        sound_sources=("kroki",),
        wear_signs=("zużycie",),
        technical_vocabulary=("mur", "brama"),
        register="neutralny",
        max_metaphor_level=1,
        material_history="Brak wystarczająco szczegółowego profilu regionalnego.",
        forbidden_cliches=_GENERIC_FORBIDDEN,
        forbidden_cultural_elements=(),
    )


def region_style_profile(region_id: str) -> StyleProfile:
    return build_style_profile(bank_for_region(region_id))

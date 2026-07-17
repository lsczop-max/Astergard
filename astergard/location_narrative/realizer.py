from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import TypeVar

from astergard.commands.polish import normalize_phrase
from astergard.location_narrative.lexicon import MorphologyProvider
from astergard.location_narrative.models import DescriptionPlan, DynamicLocationState, PermanentLocationFacts

T = TypeVar("T")


def _clean(text: str) -> str:
    return text.strip().rstrip(".")


def _first(values: tuple[str, ...], fallback: str = "") -> str:
    return values[0] if values else fallback


def _compact_phrase(text: str, limit: int = 4) -> str:
    words: list[str] = []
    seen: set[str] = set()
    for raw in text.replace(",", " ").replace(";", " ").split():
        token = raw.strip()
        if not token:
            continue
        lowered = token.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        words.append(token)
        if len(words) >= limit:
            break
    return " ".join(words) if words else _clean(text)


def _title(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _stable_index(*parts: object, modulo: int) -> int:
    seed = 0
    for part in parts:
        text = normalize_phrase(str(part), drop_stopwords=False)
        for char in text:
            seed = (seed * 33 + ord(char)) % 2**32
    return seed % modulo if modulo else 0


def _sentence_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _pick(rng: Random, options: tuple[T, ...], fallback: T) -> T:
    if not options:
        return fallback
    return options[rng.randrange(len(options))]


def _join_parts(parts: list[str]) -> str:
    return " ".join(_sentence_case(_clean(part)) + "." for part in parts if part).strip()


def _core_phrase(text: str) -> str:
    phrase = _clean(text)
    lowered = phrase.lower()
    for prefix in ("przy ", "na ", "w ", "at the ", "on the ", "in the "):
        if lowered.startswith(prefix):
            return phrase[len(prefix) :].strip()
    return phrase


_DIRECTION_FORMS = {
    "polnoc": "północy",
    "poludnie": "południu",
    "wschod": "wschodzie",
    "zachod": "zachodzie",
    "polnocny-wschod": "północnym wschodzie",
    "polnocny-zachod": "północnym zachodzie",
    "poludniowy-wschod": "południowym wschodzie",
    "poludniowy-zachod": "południowym zachodzie",
    "gora": "górze",
    "dol": "dole",
}


@dataclass(slots=True)
class _NarrativeContext:
    facts: PermanentLocationFacts
    plan: DescriptionPlan
    state: DynamicLocationState
    rng: Random
    variant: int = 0

    @property
    def focus(self) -> str:
        return self.plan.opening_focus or self.facts.dominant_landmark or self.facts.function or self.facts.location_type

    @property
    def fingerprint(self):
        return self.plan.local_fingerprint

    @property
    def material1(self) -> str:
        return _first(self.plan.material_details)

    @property
    def material2(self) -> str:
        return self.plan.material_details[1] if len(self.plan.material_details) > 1 else ""

    @property
    def material3(self) -> str:
        return self.plan.material_details[2] if len(self.plan.material_details) > 2 else ""

    @property
    def trace(self) -> str:
        return self.plan.use_trace or self.facts.maintenance or self.facts.damage

    @property
    def sensory(self) -> str:
        return self.plan.sensory_anchor or self.state.lighting

    @property
    def history(self) -> str:
        return self.plan.historical_trace or self.facts.historical_layer

    @property
    def space(self) -> str:
        return self.plan.spatial_relation.rstrip(".")

    @property
    def space_core(self) -> str:
        text = self.space
        prefixes = (
            "Otwiera się ku ",
            "Otwiera się ",
            "Przestrzeń jest ",
            "Układ otwiera się ku ",
            "Układ otwiera się ",
        )
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix) :]
        return text

    @property
    def activity(self) -> str:
        return self.facts.economic_activity or self.facts.persistent_activity or self.facts.social_status

    @property
    def detail_feature(self) -> str:
        if not self.facts.examinable_features:
            return ""
        phrase = _compact_phrase(_first(self.facts.examinable_features))
        words = phrase.split()
        if len(words) != 1:
            return ""
        return phrase

    @property
    def direction_phrase(self) -> str:
        directions = [_DIRECTION_FORMS.get(direction, direction) for direction in self.facts.visible_directions[:3]]
        if not directions:
            return ""
        if len(directions) == 1:
            return f"Na {directions[0]}"
        if len(directions) == 2:
            return f"Na {directions[0]} i {directions[1]}"
        return f"Na {directions[0]}, {directions[1]} i {directions[2]}"

    @property
    def fingerprint_subject(self) -> str:
        return self.fingerprint.subject if self.fingerprint else ""

    @property
    def fingerprint_state(self) -> str:
        return self.fingerprint.physical_state if self.fingerprint else ""

    @property
    def fingerprint_position(self) -> str:
        return self.fingerprint.spatial_position if self.fingerprint else ""

    @property
    def fingerprint_cause(self) -> str:
        return self.fingerprint.cause if self.fingerprint else ""

    @property
    def fingerprint_subtype(self) -> str:
        return self.fingerprint.subtype if self.fingerprint else ""

    @property
    def scene(self):
        return self.plan.fingerprint_micro_scene


class _BaseFamilyRealizer:
    family_name = "base"
    opener_templates: tuple[str, ...] = ()
    short_templates: tuple[str, ...] = ("{focus}",)

    def __init__(self, morphology: MorphologyProvider) -> None:
        self.morphology = morphology

    def realize_short(self, facts: PermanentLocationFacts, plan: DescriptionPlan, rng: Random) -> str:
        ctx = _NarrativeContext(facts, plan, DynamicLocationState("dzień", "bezchmurnie", "nieznana", "pełne światło"), rng, 0)
        template = _pick(rng, self.short_templates, "{focus}")
        text = template.format(
            focus=ctx.focus,
            material1=ctx.material1 or facts.function,
            material2=ctx.material2 or ctx.material1 or facts.function,
            material3=ctx.material3 or ctx.material2 or ctx.material1 or facts.function,
            material=ctx.material1 or facts.function,
            terrain=facts.terrain,
            function=facts.function,
            landmark=facts.dominant_landmark,
            region=facts.region_id,
            trace=ctx.trace or facts.maintenance,
            space=ctx.space,
            activity=ctx.activity,
            sensory=ctx.sensory,
        ).strip()
        if not text:
            text = ctx.focus
        return text[:1].upper() + text[1:]

    def realize_long(
        self,
        facts: PermanentLocationFacts,
        plan: DescriptionPlan,
        state: DynamicLocationState | None = None,
        *,
        variant: int = 0,
    ) -> str:
        state = state or DynamicLocationState("dzień", "bezchmurnie", "nieznana", "pełne światło")
        rng = Random((facts.narrative_seed * 97) + variant * 997 + len(facts.region_id))
        ctx = _NarrativeContext(facts, plan, state, rng, variant)
        parts = self._compose_long(ctx)
        if not parts:
            parts = [self._opening_sentence(ctx)]
        return _join_parts(self._polish_parts(parts, ctx))

    def realize_sensory_variants(self, facts: PermanentLocationFacts, state: DynamicLocationState) -> dict[str, str]:
        return {
            "light": state.lighting,
            "smell": _first(facts.smell_sources),
            "sound": _first(facts.sound_sources),
        }

    def realize_examinable_details(self, facts: PermanentLocationFacts, plan: DescriptionPlan) -> dict[str, str]:
        raw = facts.metadata.get("inspectables")
        if isinstance(raw, dict) and raw:
            details: dict[str, str] = {}
            normalized_raw: list[tuple[str, str, set[str]]] = []
            for key, value in raw.items():
                if isinstance(key, str) and isinstance(value, str) and value.strip():
                    normalized_raw.append((key, value.strip(), set(normalize_phrase(key, drop_stopwords=True).split())))

            for feature in plan.examinable_hooks:
                feature_tokens = set(normalize_phrase(feature, drop_stopwords=True).split())
                best_match: tuple[str, str] | None = None
                best_score = 0
                for key, value, key_tokens in normalized_raw:
                    score = len(feature_tokens & key_tokens)
                    if score > best_score:
                        best_match = (key, value)
                        best_score = score
                if best_match and best_score > 0:
                    details[feature] = best_match[1]
                elif feature in raw and isinstance(raw[feature], str) and raw[feature].strip():
                    details[feature] = raw[feature].strip()
            if details:
                return details
            for key, value, _ in normalized_raw[:3]:
                details[key] = value
            if details:
                return details
        return {}

    def _segment_map(self, ctx: _NarrativeContext) -> dict[str, str]:
        return {
            "opening": self._opening_sentence(ctx),
            "space": self._space_sentence(ctx),
            "material": self._material_sentence(ctx),
            "trace": self._trace_sentence(ctx),
            "sensory": self._sensory_sentence(ctx),
            "context": self._context_sentence(ctx),
            "detail": self._detail_sentence(ctx),
        }

    def _maybe_trim_clause(self, sentence: str, rng: Random) -> str:
        parts = [part.strip() for part in sentence.split(",") if part.strip()]
        if len(parts) > 2 and rng.random() < 0.45:
            return ", ".join(parts[:2])
        return sentence

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        segments = self._segment_map(ctx)
        orders = (
            ("opening", "trace", "material", "space", "detail", "sensory"),
            ("trace", "opening", "space", "material", "sensory"),
            ("opening", "material", "context", "detail", "space"),
        )
        order = _pick(ctx.rng, orders, orders[0])
        parts: list[str] = []
        for key in order:
            sentence = segments.get(key, "")
            if not sentence:
                continue
            if key != "opening" and ctx.rng.random() > 0.68:
                continue
            sentence = self._maybe_trim_clause(sentence, ctx.rng)
            if sentence and sentence not in parts:
                parts.append(sentence)
        if not parts:
            parts.append(self._opening_sentence(ctx))
        if len(parts) < 3 and segments.get("space") and segments["space"] not in parts:
            parts.append(segments["space"])
        return parts

    def _polish_parts(self, parts: list[str], ctx: _NarrativeContext) -> list[str]:
        return parts

    def _opening_sentence(self, ctx: _NarrativeContext) -> str:
        template = _pick(ctx.rng, self.opener_templates, "Bruk i mur wyznaczają przejście.")
        return template.format(
            focus=ctx.focus,
            material1=ctx.material1 or ctx.focus,
            material2=ctx.material2 or ctx.material1 or ctx.focus,
            material3=ctx.material3 or ctx.material2 or ctx.material1 or ctx.focus,
            space=ctx.space,
            trace=ctx.trace,
            sensory=ctx.sensory,
            history=ctx.history,
            activity=ctx.activity,
            terrain=ctx.facts.terrain,
            region=ctx.facts.region_id,
            function=ctx.facts.function,
            landmark=ctx.facts.dominant_landmark,
            weather=ctx.state.weather,
            lighting=ctx.state.lighting,
        ).strip()

    def _space_sentence(self, ctx: _NarrativeContext) -> str:
        templates = (
            "Bruk i ubita ziemia zwężają przejście przy {ground}.",
            "{ground} kończy się przy kamiennym brzegu.",
            "Kamienny próg oddziela pas przejścia od sąsiedniego terenu.",
            "Przy {ground} zostaje wąski pas przejścia.",
        )
        template = _pick(ctx.rng, tuple(templates), templates[0])
        return template.format(space_core=ctx.space_core.lower(), space_core_title=_title(ctx.space_core.lower()), ground=ctx.facts.ground)

    def _material_sentence(self, ctx: _NarrativeContext) -> str:
        mats = [item for item in (ctx.material1, ctx.material2, ctx.material3) if item]
        if not mats:
            return ""
        if len(mats) == 1:
            templates = (
                "W {material1} zrobiono ściany albo nawierzchnię.",
                "{material1} pokrywa narożniki i brzegi.",
                "Na {material1} widać zużycie przy krawędziach.",
            )
        elif len(mats) == 2:
            templates = (
                "{material1} i {material2} tworzą ścianę przy przejściu.",
                "{material1} oraz {material2} odcinają bok od gruntu.",
                "Na styku {material1} i {material2} widać pęknięte spoiny.",
            )
        else:
            templates = (
                "{material1}, {material2} i {material3} tworzą kilka warstw przy ścianie.",
                "Na granicy {material1}, {material2} i {material3} widać różne naprawy.",
                "{material1}, {material2} i {material3} pojawiają się przy narożniku i progu.",
            )
        return _pick(ctx.rng, templates, templates[0]).format(material1=mats[0], material2=mats[1] if len(mats) > 1 else "", material3=mats[2] if len(mats) > 2 else "")

    def _trace_sentence(self, ctx: _NarrativeContext) -> str:
        trace = ctx.trace
        if not trace:
            return ""
        templates = (
            "Na progu widać {trace}.",
            "W {trace} zbiera się brud i kurz.",
            "{trace} zostawił ruch albo tarcie.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(trace=trace)

    def _sensory_sentence(self, ctx: _NarrativeContext) -> str:
        anchor = ctx.sensory
        if not anchor:
            return ""
        templates = (
            "Najbliżej słychać {anchor}.",
            "Z paleniska ciągnie {anchor}.",
            "Przy {anchor} stoi najostrzejszy zapach.",
            "Wzdłuż ściany niesie się {anchor}.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(anchor=anchor, anchor_title=_title(anchor))

    def _context_sentence(self, ctx: _NarrativeContext) -> str:
        if not ctx.history and not ctx.activity:
            return ""
        templates = (
            "{history}.",
            "{activity} zostawia ślady przy progu i na ścianach.",
            "Przy {activity} widać zużycie na progach i belkach.",
            "{history} miesza się z pyłem, sadzą albo błotem.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(history=ctx.history, activity=ctx.activity)

    def _detail_sentence(self, ctx: _NarrativeContext) -> str:
        if not ctx.detail_feature:
            return ""
        feature = ctx.detail_feature
        templates = (
            "Na {feature} widać ślady użycia.",
            "Przy {feature} zbiera się kurz.",
            "Na {feature} osiadł pył.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(feature=feature)

    def _examining_sentence(self, feature: str) -> str:
        templates = (
            "Na {feature} widać wyraźny ślad.",
            "Przy {feature} zbiera się kurz.",
            "Na {feature} osiadł pył.",
        )
        index = sum(ord(char) for char in feature) % len(templates)
        return templates[index].format(feature=feature)

    def _insert_fingerprint_sentence(self, parts: list[str], ctx: _NarrativeContext, sentence: str) -> list[str]:
        if not sentence:
            return parts
        index = 1 if len(parts) < 2 else min(len(parts), 1 + (ctx.variant % max(1, min(2, len(parts)))))
        if sentence not in parts:
            parts.insert(index, sentence)
        return parts

    def _scene_sentence(self, ctx: _NarrativeContext) -> str:
        scene = ctx.scene
        fp = ctx.fingerprint
        if not scene or not fp:
            return ""
        subject = _core_phrase(scene.anchor_object or fp.subject or ctx.focus)
        position = _core_phrase(scene.local_position or fp.spatial_position or ctx.space_core)
        state = _core_phrase(scene.visible_state or fp.physical_state)
        cause = _core_phrase(scene.physical_cause or fp.cause or ctx.trace)
        movement = _core_phrase(scene.relation_to_movement)
        neighbour = _core_phrase(scene.relation_to_neighbour)
        examinable = _core_phrase(scene.optional_examinable)
        family = self.family_name

        family_templates: dict[str, tuple[str, ...]] = {
            "town": (
                "Przy {position} {subject} jest {state}, a {cause} zostawia ślady ruchu.",
                "Na {subject} widać {state}; {cause} zbiera brud przy progu.",
            ),
            "interior": (
                "Przy {position} {subject} jest {state}, a {cause} osiada przy wejściu.",
                "Na {subject} widać {state}; wąski ruch zatrzymuje się przy progu.",
            ),
            "road": (
                "Przy {position} {subject} jest {state}, a {cause} zmienia przejazd.",
                "Na {subject} widać {state}; ruch musi zwolnić przy {position}.",
                "Przy {position} {subject} jest {state}, więc {movement}.",
            ),
            "border": (
                "Przy {position} {subject} jest {state}, a po drugiej stronie {neighbour}.",
                "Na styku {subject} i sąsiedniego terenu widać {state}.",
            ),
            "vertical": (
                "Przy {position} {subject} jest {state}, a {cause} osypuje kamień niżej.",
                "Na {subject} widać {state}; niższy stopień łapie spadający gruz.",
            ),
            "ruin": (
                "Przy {position} {subject} jest {state}, a {cause} odsłania starszą warstwę.",
                "Na {subject} widać {state}; {examinable} pozwala zobaczyć pusty otwór.",
            ),
            "industrial": (
                "Przy {position} {subject} jest {state}, a {cause} zostawia pył i żużel.",
                "Na {subject} widać {state}; ruch kończy się przy stanowisku.",
            ),
            "sacred": (
                "Przy {position} {subject} jest {state}, a {cause} wygładza kamień.",
                "Na {subject} widać {state}; {examinable} zbiera ślady dłoni przy podstawie.",
            ),
            "natural": (
                "Przy {position} {subject} jest {state}, a {cause} zwęża dojście.",
                "Na {subject} widać {state}; woda i korzenie trzymają przejście w miejscu.",
            ),
            "landscape": (
                "Przy {position} {subject} jest {state}, a {cause} zmienia krawędź terenu.",
                "Na {subject} widać {state}; wiatr i spływ rozcinają zbocze.",
            ),
        }
        templates = list(family_templates.get(family, ()))
        if not examinable:
            templates = [template for template in templates if "{examinable}" not in template]
        if not neighbour:
            templates = [template for template in templates if "{neighbour}" not in template]
        if not movement:
            templates = [template for template in templates if "{movement}" not in template]
        if not templates:
            return ""
        template = _pick(ctx.rng, tuple(templates), templates[0])
        sentence = template.format(
            subject=subject,
            position=position,
            state=state,
            cause=cause,
            movement=movement or "przejście zwęża się przy krawędzi",
            neighbour=neighbour,
            examinable=examinable,
        ).strip()
        return sentence

    def _scene_slot(self, ctx: _NarrativeContext, parts: list[str]) -> int:
        if not parts:
            return 0
        family_bias = {
            "town": 1,
            "interior": 1,
            "road": 0,
            "border": 0,
            "vertical": 0,
            "ruin": 0,
            "industrial": 1,
            "sacred": 1,
            "natural": 1,
            "landscape": 0,
        }.get(self.family_name, 1)
        seed = _stable_index(ctx.facts.location_id, ctx.fingerprint_subtype, ctx.fingerprint_subject, self.family_name, modulo=max(1, len(parts)))
        return min(len(parts) - 1, max(0, family_bias + (seed % max(1, min(2, len(parts))))))

    def _weave_scene(self, parts: list[str], ctx: _NarrativeContext) -> list[str]:
        sentence = self._scene_sentence(ctx)
        if not sentence:
            return parts
        if sentence in parts:
            return parts
        slot = self._scene_slot(ctx, parts)
        if len(parts) >= 3:
            parts[slot] = sentence
        elif len(parts) == 2:
            parts.insert(slot, sentence)
            parts.pop(-1 if slot == 0 else 0)
        else:
            parts.append(sentence)
        return parts


class TownRealizer(_BaseFamilyRealizer):
    family_name = "town"
    opener_templates = (
        "Przy kramach stoją wozy i beczki.",
        "{material1} oblepia podstawy domów i murów.",
        "Bruk zwęża się między progami a podcieniami.",
        "{activity} zostawia ślady na progach i narożnikach.",
    )
    sentence_orders = (
        ("opening", "material", "space", "context", "trace", "sensory", "detail"),
        ("opening", "context", "material", "space", "trace", "sensory"),
        ("space", "opening", "material", "context", "detail", "trace"),
    )
    short_templates = (
        "{focus}",
        "{material1} przy {focus}",
        "{function} {landmark}",
        "{region}: {focus}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Przy {subject} widać wyraźne wytarcie od ruchu.",
            "Na {subject} osiadły kurz i drobny gruz.",
            "Krawędź przy {position} jest jaśniejsza od częstych napraw.",
            "Przy {subject} zostają ślady dłoni i kół.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        trace = (ctx.trace or ctx.history or ctx.activity or "").lower()
        parts: list[str] = []
        modes = (
            (
                "{activity} zostawia ślady na progach i na bruku.",
                "W koleinach zbiera się błoto i kurz.",
                "Podcienia zasłaniają wejścia do kramów.",
                "{material1} obciera się na narożach murów.",
                "Przy ścianach stoją skrzynie i wiadra.",
            ),
            (
                "Wozy skręcają przy bramie i zostawiają koleiny.",
                "Kroki ścierają bruk przy wejściach do domów.",
                "Na parapetach leżą skrzynki i kawałki płótna.",
                "{material1} i {material2} osłaniają fasady od podwórza.",
                "Na ścianie widać odbity znak cechu.",
            ),
            (
                "Przy ławach leżą miary, sznury i drobny towar.",
                "Przechodnie ocierają się o mury i słupy.",
                "Przy narożnikach leży popiół z palenisk.",
                "Nad wejściami wiszą szyldy i lampy.",
            ),
        )
        mode = _pick(ctx.rng, modes, modes[0])
        for template in mode:
            sentence = template.format(
                activity=ctx.activity or ctx.focus,
                trace=trace,
                material1=ctx.material1 or ctx.focus,
                material2=ctx.material2 or ctx.material1 or ctx.focus,
            ).strip()
            if sentence and sentence not in parts:
                parts.append(sentence)
        parts = self._weave_scene(parts, ctx)
        return parts[:5]


class InteriorRealizer(_BaseFamilyRealizer):
    family_name = "interior"
    opener_templates = (
        "Przy ścianie stoi stół, a pod oknem leżą skrzynki.",
        "Wąskie przejście prowadzi między stołem a komorą.",
        "Światło wpada przez szczelinę w okiennicy.",
        "Na progu zostaje błoto i pył.",
    )
    sentence_orders = (
        ("opening", "material", "trace", "detail", "sensory"),
        ("material", "opening", "detail", "context", "sensory"),
        ("opening", "context", "detail", "trace", "sensory"),
    )
    short_templates = (
        "{focus}",
        "{material1} w środku",
        "{function} {region}",
        "{landmark} {terrain}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Przy {position} widać starty kamień i pył.",
            "Na {subject} osiadł kurz po częstym dotykaniu.",
            "Na {subject} zostały ciemne ślady użycia.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _target_room_sentence(self, ctx: _NarrativeContext) -> str:
        return _pick(
            ctx.rng,
            (
                "Stół stoi przy ścianie.",
                "Ławy zajmują środek izby.",
                "Skrzynie stoją pod oknem.",
            ),
            "Stół stoi przy ścianie.",
        ).format(focus=ctx.focus)

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        parts = [
            _pick(
                ctx.rng,
                (
                    "Przy ścianie stoi stół, a pod oknem leżą skrzynki.",
                    "Ławy zajmują środek izby, a lampa wisi nisko nad blatem.",
                    "Wąskie przejście prowadzi między stołem a komorą.",
                    "Na progu zostaje błoto i pył.",
                ),
                "Przy ścianie stoi stół, a pod oknem leżą skrzynki.",
            ).format(focus=ctx.focus, activity=ctx.activity or ctx.focus)
        ]
        if ctx.state.lighting:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "Światło wpada przez szczelinę w okiennicy.",
                        "Lampa dymi nad stołem.",
                        "Przy suficie zbiera się przygaszone światło.",
                    ),
                    "Światło wpada przez szczelinę w okiennicy.",
                )
            )
        if ctx.facts.dominant_materials:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "{material1} pokrywa ścianę przy wejściu.",
                        "{material1} i {material2} wzmacniają narożnik izby.",
                        "Na {material1} widać starte krawędzie.",
                    ),
                    "{material1} pokrywa ścianę przy wejściu.",
                ).format(material1=ctx.material1 or ctx.focus, material2=ctx.material2 or ctx.material1 or ctx.focus)
            )
        if ctx.trace:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "Błoto zbiera się przy progu.",
                        "Na blacie zostały ciemne ślady po naczyniach.",
                        "{trace} osiada przy ścianie i pod stołem.",
                    ),
                    "Błoto zbiera się przy progu.",
                ).format(trace=(ctx.trace or ctx.history or ctx.activity or "").lower())
            )
        if ctx.detail_feature:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "Na {feature} widać ślady rąk.",
                        "Przy {feature} zbiera się kurz.",
                        "Na {feature} osiadły odpryski.",
                    ),
                    "Na {feature} widać ślady rąk.",
                ).format(feature=ctx.detail_feature)
            )
        parts = self._weave_scene(parts, ctx)
        return parts[:4]


class RoadRealizer(_BaseFamilyRealizer):
    family_name = "road"
    opener_templates = (
        "Dwie koleiny skręcają ku zakrętowi.",
        "Przy rowie droga zwęża się do jednego pasa.",
        "Na poboczu stoją ślady po postoju wozów.",
        "Krawędź traktu łamie się przy skarpie.",
    )
    sentence_orders = (
        ("opening", "space", "trace", "material", "sensory"),
        ("trace", "space", "opening", "material"),
        ("space", "opening", "trace", "sensory"),
    )
    short_templates = (
        "{material1}",
        "{focus} {terrain}",
        "{activity} {region}",
        "{material1} i {trace}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = {
            "rut_deepening": (
                "Koleina przy {position} jest wyraźnie głębsza od reszty traktu.",
                "W {subject} zbiera się woda i ciemny muł.",
            ),
            "washed_edge": (
                "Przy {position} krawędź drogi jest podmyta.",
                "Deszcz wyciął w brzegach płytką rynnę.",
            ),
            "broken_paving": (
                "Płaskie kamienie przy {position} siedzą nierówno i rozchodzą się pod kołami.",
                "W {subject} zostały szczeliny po wybitych kamieniach.",
            ),
            "slope_erosion": (
                "Na spadku przy {position} nawierzchnia osuwa się ku dołowi.",
                "Z brzegu traktu sypie się drobny rumosz.",
            ),
            "narrow_causeway": (
                "Przejazd przy {position} zwęża się do jednego pasa.",
                "Kamienie i błoto ściskają tu ruch z obu stron.",
            ),
        }
        chosen = templates.get(fp.subtype or "", (
            "Przy {position} droga nosi ślady ruchu i napraw.",
            "Na {subject} widać koleiny i rozjechany brzeg.",
        ))
        return _pick(ctx.rng, chosen, chosen[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        profile_seed = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.facts.ground,
            ctx.trace,
            ctx.activity,
            ctx.direction_phrase,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=8,
        )
        profile = (profile_seed + ctx.variant) % 8
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Dwie głębokie koleiny skręcają ku bramie.",
                "Przy przydrożnym rowie droga zwęża się do jednego pasa.",
                "Deszcz wypłukuje piasek spomiędzy kamieni i zostawia mokry brzeg.",
            ),
            (
                "Za zakrętem ubita ziemia przechodzi w płaskie kamienie.",
                "Na środku traktu leży rozjechany żwir, a po bokach widać miękki piasek.",
            ),
            (
                "Przy mijance ziemia jest mocniej ubita.",
                "Na poboczu stoją ślady po postoju wozów.",
                "Wiatr niesie pył znad nasypu.",
            ),
            (
                "Krawędź traktu łamie się przy skarpie.",
                "Woda stoi w koleinie przy rowie.",
                "Ubita ziemia pęka przy brzegu, a koleina rozszerza się ku dołowi.",
            ),
            (
                "Żwir miesza się z gliną i zostaje w koleinach.",
                "Wąska ścieżka odbija między zabudowania.",
                "Po deszczu na środku zostaje maź i mokry piasek.",
                "Krawędź traktu jest rozjechana przy skręcie.",
            ),
            (
                "Przy miedzy pozostaje wąski przejazd.",
                "Kamienie wystają z nawierzchni i tłuką koła.",
                "Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.",
            ),
            (
                "Droga jest porzucona i zarasta po bokach.",
                "Korzenie wypychają bruk na jednym łuku.",
                "Na środku leżą rumosz i suche liście.",
            ),
            (
                "Ścieżka używana tylko pieszo schodzi z nasypu.",
                "Nawierzchnia zmienia się z bruku w piasek.",
                "Przy wyjściu z osady zostają świeże ślady butów.",
            ),
        )
        parts = list(profiles[profile])
        return self._weave_scene(parts, ctx)[:5]


class BorderRealizer(_BaseFamilyRealizer):
    family_name = "border"
    opener_templates = (
        "Kamienny mur zwęża przejście.",
        "Palisada stoi przy rowie i bramie.",
        "Łańcuch zwisa między słupami.",
        "Przy słupie leży odgarnięty żwir.",
    )
    sentence_orders = (
        ("opening", "space", "material", "trace", "context"),
        ("space", "opening", "trace", "material", "sensory"),
        ("opening", "context", "space", "material"),
    )
    short_templates = (
        "{focus}",
        "{focus} graniczne",
        "{material1} przy przejściu",
        "{region} {focus}",
    )

    def realize_short(self, facts: PermanentLocationFacts, plan: DescriptionPlan, rng: Random) -> str:
        if facts.dominant_landmark and len(facts.dominant_landmark.split()) <= 5:
            return _title(facts.dominant_landmark)
        return super().realize_short(facts, plan, rng)

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Przy {position} przejście zwęża się wyraźnie.",
            "Na {subject} widać starcie od ciągłego przechodzenia.",
            "Krawędź przy {position} jest jaśniejsza od reszty od częstych otarć.",
            "Po jednej stronie {subject}, po drugiej inny materiał.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        profile_seed = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.facts.settlement_type,
            ctx.facts.enclosure,
            ctx.trace,
            ctx.activity,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=8,
        )
        profile = (profile_seed + ctx.variant) % 8
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Brama ściska przejście między dwiema ścianami.",
                "Na jednej krawędzi widać żelazne okucia, na drugiej kamień z licem.",
                "W koleinach stoi błoto po wozach zawracających przed bramą.",
            ),
            (
                "Rów i palisada zamykają przesmyk.",
                "Po jednej stronie leży bruk, po drugiej ubita ziemia.",
            ),
            (
                "Przy granicy teren przechodzi z bruku w ubity grunt.",
                "Wąski prześwit prowadzi między kamiennym murem a palisadą.",
                "Przy słupie stoi łańcuch i odgarnięty żwir.",
                "Ślady butów kończą się przed suchą częścią drogi.",
            ),
            (
                "Mur urywa się przy brukowanej ulicy i zostawia wąskie wejście.",
                "Po stronie osady stoją kramy, po drugiej suchy pas ziemi.",
                "Na progu leżą okruchy zaprawy i drzazgi z furtki.",
            ),
            (
                "Las dochodzi do drogi bez bramy i bez muru.",
                "Światło gaśnie pod pierwszymi pniami.",
            ),
            (
                "Bagno zaczyna się od miękkiego brzegu i niskiego sitowia.",
                "Ziemia ciemnieje i zapada się przy każdym kroku.",
                "Przy kępach zostaje mokry osad i ślady butów.",
                "Na styku twardej ziemi i wody widać wyraźną krawędź.",
            ),
            (
                "Plac wojskowy odcina się od ulicy palisadą i wykopem.",
                "Po jednej stronie leżą zaprawione kamienie, po drugiej szary żwir.",
                "Przy wejściu widać ślady zawracania i cięższy ruch.",
                "W wykopie zbiera się woda po ostatnim deszczu.",
            ),
            (
                "Zaniedbany pas przy murze przechodzi w pył i rumosz.",
                "Roślinność wciska się pod krawężnik i pod ławę.",
            ),
        )
        parts = list(profiles[profile])
        return self._weave_scene(parts, ctx)[:5]


class VerticalSpaceRealizer(_BaseFamilyRealizer):
    family_name = "vertical"
    opener_templates = (
        "Schody opadają do szybu.",
        "Ściana skalna stoi tuż przy ścieżce.",
        "Strop schodzi nisko nad głową.",
        "Urwisko urywa dojście od wschodu.",
    )
    sentence_orders = (
        ("opening", "space", "material", "trace", "detail"),
        ("trace", "material", "opening", "space"),
        ("space", "opening", "detail", "trace"),
    )
    short_templates = (
        "{focus}",
        "{material1} pionu",
        "{trace} {region}",
        "{function} {material1}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Przy {position} kamień kruszy się pod własnym ciężarem.",
            "Na {subject} widać ślady tarcia i osypywania.",
            "Górna krawędź przy {position} rzuca cień na niższy pas.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        profile_seed = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.facts.terrain,
            ctx.trace,
            ctx.activity,
            ctx.facts.dominant_landmark,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=6,
        )
        profile = (profile_seed + ctx.variant) % 6
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Schody urywają się przy skalnym gzymsie.",
                "Na kamieniach widać wyślizgane stopnie.",
                "Na dnie szybu leży wilgoć i luźny gruz.",
            ),
            (
                "Ściana skalna wznosi się po wschodniej stronie.",
                "Ścieżka opada ku dnu żlebu.",
                "Osypisko zasypuje dolny brzeg przejścia.",
            ),
            (
                "Szyb idzie w górę między mokrymi ścianami.",
                "Drewniane belki podpierają zwisający kamień.",
                "Wyżej zostaje tylko wąski pas światła.",
                "Przy podstawie zalega chłodny przeciąg.",
            ),
            (
                "Skarpa urywa się przy kamiennym progu.",
                "Lina ocierała skałę przy zakręcie.",
            ),
            (
                "Wąski korytarz opada pod niskim stropem.",
                "Na ścianie widać ślady tarcia po ramionach i workach.",
                "Wilgoć zalega przy najniższym stopniu.",
                "Kamień kruszy się na ostrym zakręcie.",
            ),
            (
                "Urwisko urywa dojście od dołu.",
                "Z góry spada pył i drobne kamienie.",
                "Przy krawędzi stoi wygięta lina i pęknięty klin.",
            ),
        )
        parts = list(profiles[profile])
        if ctx.detail_feature:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "Na {feature} osiadł pył z osypiska.",
                        "Przy {feature} widać odpryski kamienia.",
                        "Na {feature} widać ślady tarcia.",
                    ),
                    "Na {feature} osiadł pył z osypiska.",
                ).format(feature=ctx.detail_feature)
            )
        return self._weave_scene(parts, ctx)[:4]


class RuinRealizer(_BaseFamilyRealizer):
    family_name = "ruin"
    opener_templates = (
        "Rumowisko zasypuje dawny dziedziniec.",
        "W dawnej ścianie została wyłamana ościeżnica.",
        "Nad wejściem wisi urwany łuk.",
        "Przy murze leżą połamane belki.",
    )
    sentence_orders = (
        ("opening", "trace", "material", "space", "context"),
        ("trace", "opening", "material", "detail", "sensory"),
        ("opening", "space", "trace", "material"),
    )
    short_templates = (
        "{focus}",
        "{trace} {region}",
        "{material1} ruin",
        "{function} {landmark}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Przy {position} widać pusty ślad po mocowaniu.",
            "Na {subject} zostały nadpalone krawędzie i odpryski zaprawy.",
            "W {subject} brakuje całego odcinka i odsłania się starsza warstwa.",
            "Korzenie rozsunęły {subject} i zostawiły szparę przy fundamencie.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        profile_seed = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.facts.damage,
            ctx.facts.historical_layer,
            ctx.trace,
            ctx.activity,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=6,
        )
        profile = (profile_seed + ctx.variant) % 6
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Dawna ściana stoi tylko do połowy wysokości.",
                "U podstawy ściany widać odsłonięty fundament.",
                "Sadza osiadła nad dawnym paleniskiem.",
            ),
            (
                "Jedna ściana przechodzi w rumowisko.",
                "Za pierwszym rzędem murów leży połamany strop.",
                "Pod murem leży wypalona glina i węgiel.",
            ),
            (
                "W wejściu sterczą dwie wyłamane ościeżnice.",
                "Urwany bieg schodów kończy się w gruzie.",
                "Po ogniu zostały czarne smugi na kamieniu.",
                "Na progu widać wtórnie wmurowany kamień.",
            ),
            (
                "Strop zawalił się do środka i przygniótł izbę.",
                "Po bokach zostały tylko niskie ściany i belki.",
                "W środku leżą dachówki, wapno i kurz.",
            ),
            (
                "Korzenie rozsunęły mur przy narożniku.",
                "Kamienie odsunęły się od fundamentu i zostawiły szparę.",
                "W szczelinie widać wilgoć i drobne odłamy zaprawy.",
                "Na górnej krawędzi rośnie mech.",
            ),
            (
                "Ktoś rozebrał jedną stronę i zabrał kamień do wtórnego użycia.",
                "Została tylko niższa warstwa i wyrównany ślad po belce.",
                "Na wyższym progu widać wyryty znak po dawnym mocowaniu.",
            ),
        )
        parts = list(profiles[profile])
        if ctx.detail_feature:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "Na {feature} widać pęknięcia.",
                        "Przy {feature} osiadła sadza.",
                        "Na {feature} widać nadpalone brzegi.",
                    ),
                    "Na {feature} widać pęknięcia.",
                ).format(feature=ctx.detail_feature)
            )
        return self._weave_scene(parts, ctx)[:4]


class IndustrialRealizer(_BaseFamilyRealizer):
    family_name = "industrial"
    opener_templates = (
        "Piec stoi przy ścianie, a obok leży żużel.",
        "Wózki stoją przy torze i hałasują na zjazdach.",
        "Sadza pokrywa belki nad halą.",
        "Na stole leżą narzędzia i odpadki po obróbce.",
    )
    sentence_orders = (
        ("opening", "material", "trace", "context", "sensory"),
        ("material", "opening", "trace", "detail", "sensory"),
        ("trace", "opening", "material", "context"),
    )
    short_templates = (
        "{focus}",
        "{material1} robocze",
        "{activity} {region}",
        "{trace} i {material1}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Na {subject} widać świeże ślady po pracy i czyszczeniu.",
            "Przy {position} zbiera się pył i żużel.",
            "Na {subject} zostały nacięcia po narzędziu.",
            "Stanowisko przy {position} wygląda na chwilowo nieużywane.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=_core_phrase(fp.subject or ctx.focus),
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        process_anchor = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.activity,
            ctx.trace,
            ctx.sensory,
            ctx.facts.dominant_landmark,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=6,
        )
        profile = (process_anchor + ctx.variant) % 6
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Przy piecu widać świeży żar i grube plamy sadzy.",
                "Na kowadle zostały rysy po uderzeniach.",
                "Tłuszcz i pył zbierają się przy stole roboczym.",
            ),
            (
                "Na stole leżą deski z długimi nacięciami.",
                "Wióry zbierają się pod piłą i przy ścianie.",
                "Na podłodze leżą odpadki po obróbce drewna.",
            ),
            (
                "Wózki stoją przy torze, a koła mają świeże otarcia.",
                "Przy belkach wiszą worki oznaczone kredą.",
                "Kroki i obrót kół zostawiają ciemny pył przy wjeździe.",
            ),
            (
                "Skrzynie ustawiono pod ścianą, jedna na drugiej.",
                "Pył zmiatany w kąt tworzy ciemny klin przy progu.",
                "Stanowisko wygląda na chwilowo nieużywane.",
            ),
            (
                "Z pieca wychodzi dym i żar, a kamienna posadzka jest gorąca przy brzegu.",
                "Przy korycie zbiera się wilgoć po chłodzeniu metalu.",
                "Na blacie zostały ciemne smugi po czyszczeniu narzędzi.",
            ),
            (
                "Na ławie leżą klucze, miara i kilka śrub po naprawie.",
                "Belki noszą ślady po hakach i linach do podnoszenia ciężaru.",
                "Przy wejściu widać miejsce po ostatnim rozładunku.",
            ),
        )
        parts = [part for part in profiles[profile] if part]
        return self._weave_scene(parts, ctx)[:4]


class SacredRealizer(_BaseFamilyRealizer):
    family_name = "sacred"
    opener_templates = (
        "Ołtarz stoi pośrodku kamiennej posadzki.",
        "Świece stoją w niszach przy ścianach.",
        "Kamienna ława zasłania boczną kaplicę.",
        "W progu widać starty kamień od klękania.",
    )
    sentence_orders = (
        ("opening", "space", "material", "context", "sensory"),
        ("opening", "material", "trace", "space"),
        ("space", "opening", "context", "detail"),
    )
    short_templates = (
        "{focus}",
        "{region}: {focus}",
        "{material1} i cisza",
        "{function} {landmark}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Kamień przy {position} jest wygładzony od dotykania.",
            "Na {subject} widać wosk i ciemny pył.",
            "Przy {subject} osiadł kurz w wąskiej bruździe.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=fp.subject or ctx.focus,
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        fragments = {
            "opening": _pick(
                ctx.rng,
                (
                    "Ołtarz stoi pośrodku kamiennej posadzki.",
                    "W niszach palą się świece i stoją misy z wodą.",
                    "Próg jest starty od butów i klękania.",
                ),
                "Ołtarz stoi pośrodku kamiennej posadzki.",
            ),
            "material": _pick(
                ctx.rng,
                (
                    "{material1} pokrywa podłogę i stopnie.",
                    "{material1} wzmacnia łuk nad wejściem.",
                    "Na {material1} widać wosk i dłonie.",
                ),
                "{material1} pokrywa podłogę i stopnie.",
            ).format(material1=ctx.material1 or ctx.focus, material2=ctx.material2 or ctx.material1 or ctx.focus),
            "trace": _pick(
                ctx.rng,
                (
                    "Wzdłuż progu zbiera się wosk i pył.",
                    "Na kamieniu przy ołtarzu widać starte kolana.",
                    "Dym osiada pod stropem i przy belkach.",
                ),
                "Wzdłuż progu zbiera się wosk i pył.",
            ),
            "space": _pick(
                ctx.rng,
                (
                    "Kamienna ława odcina boczną niszę od nawy.",
                    "Wąski korytarz prowadzi do zakrystii.",
                    "Niska balustrada zamyka miejsce przed ołtarzem.",
                ),
                "Kamienna ława odcina boczną niszę od nawy.",
            ),
            "detail": _pick(
                ctx.rng,
                (
                    "Na {feature} widać wosk i odciski dłoni.",
                    "Przy {feature} osiadł pył.",
                    "Na {feature} widać starty kamień.",
                ),
                "Na {feature} widać wosk i odciski dłoni.",
            ).format(feature=ctx.detail_feature)
            if ctx.detail_feature
            else "",
        }
        orders = (
            ("opening", "space", "material", "trace", "detail"),
            ("trace", "opening", "material", "space"),
            ("opening", "material", "trace", "detail"),
        )
        parts: list[str] = []
        for key in _pick(ctx.rng, orders, orders[0]):
            sentence = fragments.get(key, "")
            if sentence and sentence not in parts:
                parts.append(sentence)
        return self._weave_scene(parts, ctx)[:4]


class NaturalRealizer(_BaseFamilyRealizer):
    family_name = "natural"
    opener_templates = (
        "Torf ugina się pod stopą.",
        "Pnie stoją gęsto i zasłaniają drogę.",
        "Łąka przechodzi w niższy pas traw.",
        "Szeroki stok opada ku dolinie.",
    )
    sentence_orders = (
        ("opening", "trace", "space", "material", "sensory"),
        ("trace", "opening", "sensory", "material"),
        ("space", "opening", "trace", "detail"),
    )
    short_templates = (
        "{focus}",
        "{material1} {terrain}",
        "{trace} w {region}",
        "{sensory} i {focus}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Przy {position} korzeń jest podmyty i odsłonięty.",
            "Na {subject} widać rozmiękłą ziemię i mokry osad.",
            "Sitowie wciska się w {position} i zwęża przejście.",
            "Woda zbiera się pod {subject} po jednej stronie kępy.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=fp.subject or ctx.focus,
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        profile_seed = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.facts.terrain,
            ctx.trace,
            ctx.activity,
            ctx.sensory,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=6,
        )
        profile = (profile_seed + ctx.variant) % 6
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Podłoże wypuszcza wodę przy każdym kroku.",
                "Sitowie zasłania niski rów z wodą.",
            ),
            (
                "Brzegi rowu są rozmiękłe i pękają pod butem.",
                "Na kępie ziemia jest jeszcze twarda.",
                "Wśród sitowia słychać plusk i komary.",
            ),
            (
                "Pnie stoją gęsto i zasłaniają drogę.",
                "Światło przeciska się między gałęziami.",
                "Przy korzeniach leży połamana gałąź.",
                "Między pniami widać wąski przesmyk.",
            ),
            (
                "Między drzewami zostaje wąski przesmyk.",
                "Na mchu widać ślady butów.",
            ),
            (
                "Łąka przechodzi w niższy pas traw.",
                "W ścieżce widać świeże koleiny.",
                "Powietrze pachnie mokrą korą.",
                "Przy skraju stoją połamane źdźbła.",
                "Zwierzęce tropy urywają się przy kępie sitowia.",
            ),
            (
                "Na skraju lasu rosną młode olsze.",
                "Z kępy ziemi wystaje korzeń i mokry łupek.",
                "Ścieżka otwiera się między kępami trawy.",
            ),
        )
        parts = list(profiles[profile])
        if ctx.detail_feature:
            detail_sentences = (
                "Na {feature} widać błoto i mech.",
                "Przy {feature} zbiera się wilgoć.",
                "Na {feature} osiadła ziemia.",
            )
            parts.append(_pick(ctx.rng, detail_sentences, detail_sentences[0]).format(feature=ctx.detail_feature))
        return self._weave_scene(parts, ctx)[:4]


class LandscapeRealizer(_BaseFamilyRealizer):
    family_name = "landscape"
    opener_templates = (
        "Szeroki stok opada ku dolinie.",
        "Na grzbiecie stoi samotny głaz.",
        "Sztucznie usypany nasyp przecina widok.",
        "W oddali biegnie linia drzew i płytki jar.",
    )
    sentence_orders = (
        ("opening", "space", "material", "trace", "sensory"),
        ("space", "opening", "material", "detail", "trace"),
        ("opening", "trace", "space", "material"),
    )
    short_templates = (
        "{focus}",
        "{material1} {space}",
        "{region} {material1}",
        "{trace} {terrain}",
    )

    def _fingerprint_sentence(self, ctx: _NarrativeContext) -> str:
        fp = ctx.fingerprint
        if not fp:
            return ""
        templates = (
            "Na {position} leży rumosz i drobny żwir.",
            "Przy {subject} widać zacieki po deszczu.",
            "Wiatr zatrzymuje się na {position} i rozdziela trawę.",
        )
        return _pick(ctx.rng, templates, templates[0]).format(
            subject=fp.subject or ctx.focus,
            position=_core_phrase(fp.spatial_position or ctx.space_core),
        )

    def _compose_long(self, ctx: _NarrativeContext) -> list[str]:
        material1 = ctx.material1 or ctx.focus
        profile_seed = _stable_index(
            ctx.facts.location_id,
            ctx.facts.region_id,
            ctx.facts.terrain,
            ctx.trace,
            ctx.activity,
            ctx.facts.dominant_landmark,
            ctx.fingerprint_subtype,
            ctx.fingerprint_subject,
            modulo=6,
        )
        profile = (profile_seed + ctx.variant) % 6
        profiles: tuple[tuple[str, ...], ...] = (
            (
                "Szeroki stok opada ku dolinie.",
                "W pobliżu rowu widać wydeptany pas ziemi.",
                "Wiatr niesie kurz ze zbocza.",
                "Na krawędzi leży kilka odłamków kamienia.",
            ),
            (
                "Na grzbiecie stoi samotny głaz.",
                "Kamienie przy krawędzi noszą zacieki po deszczu, a niżej leży wąski pas trawy.",
            ),
            (
                "Sztucznie usypany nasyp przecina otwarty teren.",
                "{material1} leży przy niskim murku i skarpie.",
                "Słychać kamyki zsuwające się po zboczu.",
            ),
            (
                "W oddali widać linię drzew i płytki jar.",
                "Na skraju drogi leżą połamane gałęzie.",
                "Światło jest ostre i nierówne na całej długości zbocza.",
            ),
            (
                "Na otwartym zboczu widać wydeptany pas ziemi.",
                "Przy niskim murku stoi odłupany kamień.",
                "Z krawędzi sypie się drobny rumosz, który zatrzymuje się w trawie.",
            ),
            (
                "Grzbiet przechodzi w niższy jar bez wyraźnej krawędzi.",
                "Po obu stronach widać inne nachylenie gruntu.",
                "Powietrze jest suche i ruchliwe od wiatru.",
                "Przy samej krawędzi leży żwir i kilka gałęzi.",
            ),
        )
        parts = [sentence.format(material1=material1) for sentence in profiles[profile]]
        if ctx.detail_feature:
            parts.append(
                _pick(
                    ctx.rng,
                    (
                        "Na {feature} widać zacieki po deszczu.",
                        "Przy {feature} leży żwir.",
                        "Na {feature} osiadł kurz ze zbocza.",
                    ),
                    "Na {feature} widać zacieki po deszczu.",
                ).format(feature=ctx.detail_feature)
            )
        return self._weave_scene(parts, ctx)[:4]


@dataclass(slots=True)
class SurfaceRealizer:
    morphology: MorphologyProvider
    _families: tuple[_BaseFamilyRealizer, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._families: tuple[_BaseFamilyRealizer, ...] = (
            TownRealizer(self.morphology),
            InteriorRealizer(self.morphology),
            RoadRealizer(self.morphology),
            BorderRealizer(self.morphology),
            VerticalSpaceRealizer(self.morphology),
            RuinRealizer(self.morphology),
            IndustrialRealizer(self.morphology),
            SacredRealizer(self.morphology),
            NaturalRealizer(self.morphology),
            LandscapeRealizer(self.morphology),
        )

    def realize_short(self, facts: PermanentLocationFacts, plan: DescriptionPlan, variant: int = 0) -> str:
        family = self._select_family(facts, plan)
        rng = Random((facts.narrative_seed * 31) + variant * 131 + len(facts.region_id))
        return family.realize_short(facts, plan, rng)

    def realize_long(
        self,
        facts: PermanentLocationFacts,
        plan: DescriptionPlan,
        state: DynamicLocationState | None = None,
        *,
        variant: int = 0,
    ) -> str:
        family = self._select_family(facts, plan)
        return family.realize_long(facts, plan, state, variant=variant)

    def realize_sensory_variants(self, facts: PermanentLocationFacts, state: DynamicLocationState) -> dict[str, str]:
        return {
            "light": state.lighting,
            "smell": _first(facts.smell_sources),
            "sound": _first(facts.sound_sources),
        }

    def realize_examinable_details(self, facts: PermanentLocationFacts, plan: DescriptionPlan) -> dict[str, str]:
        return self._select_family(facts, plan).realize_examinable_details(facts, plan)

    def _select_family(self, facts: PermanentLocationFacts, plan: DescriptionPlan) -> _BaseFamilyRealizer:
        region = facts.region_id
        terrain = facts.terrain
        location_type = facts.location_type
        function = facts.function
        landmark = facts.dominant_landmark.lower() if facts.dominant_landmark else ""
        if terrain in {"ruinowy"} or "ruin" in region.lower():
            return self._family(RuinRealizer)
        if terrain in {"podziemny", "jaskiniowy"} or location_type in {"podziemie"}:
            return self._family(VerticalSpaceRealizer if "kopal" in region.lower() or "szyb" in landmark else IndustrialRealizer)
        if location_type in {"droga", "przejście"} or terrain == "drogowy":
            return self._family(RoadRealizer)
        if location_type == "brama" or facts.enclosure == "zamknięta":
            return self._family(BorderRealizer)
        if any(token in landmark for token in ("ołtarz", "kaplic", "świąty", "sanktu")):
            return self._family(SacredRealizer)
        if location_type == "wnętrze" or function in {"gospoda", "zaopatrzenie w wodę"}:
            return self._family(InteriorRealizer)
        if terrain in {"leśny", "bagienny"}:
            return self._family(NaturalRealizer if "bag" in region.lower() else LandscapeRealizer)
        if facts.scale == "średnia" and facts.settlement_type == "miejska":
            return self._family(TownRealizer)
        if any(token in region.lower() for token in ("kopal", "dungrim", "forteca", "straznica")):
            return self._family(IndustrialRealizer)
        return self._family(LandscapeRealizer)

    def _family(self, family_type: type[_BaseFamilyRealizer]) -> _BaseFamilyRealizer:
        for family in self._families:
            if isinstance(family, family_type):
                return family
        return self._families[-1]

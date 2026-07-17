from __future__ import annotations

from dataclasses import dataclass
from collections import Counter

from astergard.commands.polish import normalize_phrase
from astergard.location_narrative.models import PermanentLocationFacts, ValidationReport
from astergard.location_narrative.similarity import DeterministicSimilarityProvider, cosine_token_similarity


_BANNED = (
    "wydaje się",
    "jakby",
    "zdaje się pamiętać",
    "czas odcisnął swoje piętno",
    "świadek minionych wydarzeń",
    "skrywa tajemnice",
    "mroczna atmosfera",
    "prastary",
    "majestatyczny",
    "złowieszczy",
    "niepokojąca cisza",
    "szept wiatru",
    "taniec cieni",
    "serce lasu",
    "morze zieleni",
    "natura odzyskuje swoje prawa",
    "miejsce emanuje",
    "można odnieść wrażenie",
)

_SECOND_PERSON = ("cie", "tobie", "ciebie", "twoj", "twoja", "twoje", "twoim", "twoich", "ty", "toba")
_NON_EXISTENT_FEATURE_TOKENS = {
    "rzeka",
    "jezioro",
    "jeziora",
    "staw",
    "stawu",
}
_TEMPLATE_OPENERS = {
    "tutaj",
    "wokol",
    "wsrod",
    "posrodku",
    "przed",
    "stad",
    "dalej",
    "droga",
    "las",
    "plac",
    "sciezka",
    "ruiny",
    "wnetrze",
    "jaskinia",
    "korytarz",
    "szyb",
    "miasto",
    "wieza",
}
_TEMPLATE_CLOSERS = {
    "stad mozna ruszyc",
    "droga prowadzi",
    "na polnoc",
    "na poludnie",
    "na wschod",
    "na zachod",
    "w gore",
    "w dol",
}
_COMMON_VERBS = {
    "jest",
    "sa",
    "stoi",
    "lezy",
    "leza",
    "prowadzi",
    "otwiera",
    "otwiera sie",
    "trzyma",
    "zostawia",
    "widac",
    "czuc",
    "pachnie",
    "slychac",
    "niesie",
    "domyka",
    "przechodzi",
    "wpada",
    "schodzi",
    "wznosi",
    "robi",
    "nadaje",
    "pilnuje",
}
_STOPWORDS = {
    "na",
    "w",
    "we",
    "do",
    "z",
    "ze",
    "za",
    "pod",
    "nad",
    "przez",
    "przy",
    "u",
    "o",
    "po",
    "od",
    "dla",
    "i",
    "a",
    "oraz",
    "jest",
    "sa",
}


@dataclass(slots=True)
class DescriptionValidator:
    similarity_threshold: float = 0.82

    def validate(self, text: str, facts: PermanentLocationFacts, existing_texts: tuple[str, ...] = ()) -> ValidationReport:
        lowered = normalize_phrase(text)
        analysis_text = self._analysis_text(text)
        analysis_lowered = normalize_phrase(analysis_text)
        tokens = lowered.split()
        critical: list[str] = []
        warnings: list[str] = []
        if any(normalize_phrase(phrase) in lowered for phrase in _BANNED):
            critical.append("cliche_phrase")
        if any(token in tokens for token in _SECOND_PERSON):
            critical.append("second_person")
        if any(claim in analysis_lowered for claim in (normalize_phrase(claim) for claim in facts.forbidden_claims)):
            critical.append("forbidden_claim")
        if self._contains_exit_claim(analysis_lowered) and not self._mentions_allowed_exit(analysis_text, facts):
            actual_roots = {root for exit_name in facts.actual_exits for root in self._direction_roots(exit_name)}
            for sentence in self._exit_claim_sentences(analysis_text):
                mentioned = self._mentioned_direction_roots(normalize_phrase(sentence))
                if mentioned and not mentioned.issubset(actual_roots):
                    critical.append("nonexistent_exit")
                    break
        if self._mentions_nonexistent_features(analysis_text, facts):
            critical.append("invented_feature")
        if facts.local_fingerprint is not None and self._fingerprint_expression_score(analysis_text, facts) == 0:
            critical.append("fingerprint_ignored")
        rhythm_issues, rhythm_warnings = self._rhythm_flags(text)
        critical.extend(rhythm_issues)
        warnings.extend(rhythm_warnings)
        if text.count(".") < 2:
            warnings.append("short_text")

        similarity_provider = DeterministicSimilarityProvider()
        similarity = max([similarity_provider.similarity(text, other) for other in existing_texts], default=0.0)
        if similarity >= self.similarity_threshold:
            critical.append("near_duplicate")

        scores = self._score(text, facts, warnings, critical)
        return ValidationReport(
            factual_consistency=scores["factual_consistency"],
            spatial_consistency=scores["spatial_consistency"],
            regional_consistency=scores["regional_consistency"],
            linguistic_correctness=scores["linguistic_correctness"],
            concreteness=scores["concreteness"],
            sensory_grounding=scores["sensory_grounding"],
            distinctiveness=scores["distinctiveness"],
            readability=scores["readability"],
            stylistic_naturalness=scores["stylistic_naturalness"],
            interaction_support=scores["interaction_support"],
            repetition_risk=scores["repetition_risk"],
            cliché_risk=scores["cliché_risk"],
            critical_errors=tuple(dict.fromkeys(critical)),
            warnings=tuple(dict.fromkeys(warnings)),
        )

    def _mentions_allowed_exit(self, text: str, facts: PermanentLocationFacts) -> bool:
        lowered = normalize_phrase(text)
        mentioned_roots = self._mentioned_direction_roots(lowered)
        actual_roots = {root for exit_name in facts.actual_exits for root in self._direction_roots(exit_name)}
        return mentioned_roots.issubset(actual_roots)

    def _mentions_nonexistent_features(self, text: str, facts: PermanentLocationFacts) -> bool:
        lowered = normalize_phrase(text)
        tokens = set(lowered.split())
        if tokens & _NON_EXISTENT_FEATURE_TOKENS and "water" not in normalize_phrase(facts.water):
            return True
        return False

    def _mentioned_direction_roots(self, lowered: str) -> set[str]:
        roots: set[str] = set()
        for token in lowered.split():
            token = token.strip("-")
            if token.startswith("polnoc"):
                roots.add("polnoc")
            if token.startswith("poludni"):
                roots.add("poludnie")
            if token.startswith("wschod"):
                roots.add("wschod")
            if token.startswith("zachod"):
                roots.add("zachod")
        return roots

    def _analysis_text(self, text: str) -> str:
        _, _, remainder = text.partition(".")
        return remainder if remainder else text

    def _fingerprint_expression_score(self, text: str, facts: PermanentLocationFacts) -> int:
        fingerprint = facts.local_fingerprint
        if fingerprint is None:
            return 0
        lowered = normalize_phrase(text)
        score = 0
        for value in (fingerprint.subject, fingerprint.physical_state, fingerprint.spatial_position, fingerprint.cause):
            if not value:
                continue
            tokens = [token for token in normalize_phrase(value, drop_stopwords=True).split() if token]
            if not tokens:
                continue
            if any(token in lowered for token in tokens):
                score += 1
        return score

    def _sentence_parts(self, text: str) -> tuple[str, ...]:
        return tuple(sentence.strip() for sentence in text.split(".") if sentence.strip())

    def _first_word(self, sentence: str) -> str:
        tokens = normalize_phrase(sentence).split()
        return tokens[0] if tokens else ""

    def _last_word(self, sentence: str) -> str:
        tokens = normalize_phrase(sentence).split()
        return tokens[-1] if tokens else ""

    def _first_verblike(self, sentence: str) -> str:
        tokens = normalize_phrase(sentence).split()
        for token in tokens[:6]:
            if token in _COMMON_VERBS or token.startswith(("prowadz", "otwier", "trzym", "zostaw", "piln", "nadaj", "czuj", "pachn", "slysz", "widz")):
                return token
        return ""

    def _first_content_word(self, sentence: str) -> str:
        tokens = [token for token in normalize_phrase(sentence).split() if token not in _STOPWORDS]
        return tokens[0] if tokens else ""

    def _rhythm_flags(self, text: str) -> tuple[list[str], list[str]]:
        sentences = self._sentence_parts(text)
        critical: list[str] = []
        warnings: list[str] = []
        if not sentences:
            critical.append("ai_like")
            return critical, warnings

        normalized_sentences = [normalize_phrase(sentence) for sentence in sentences]
        lengths = [len(sentence.split()) for sentence in normalized_sentences if sentence]
        first_words = [self._first_word(sentence) for sentence in sentences if sentence]
        last_words = [self._last_word(sentence) for sentence in sentences if sentence]
        first_verbs = [self._first_verblike(sentence) for sentence in sentences if sentence]
        first_nouns = [self._first_content_word(sentence) for sentence in sentences if sentence]

        if len(sentences) < 2:
            warnings.append("short_text")

        if len(lengths) >= 3:
            spread = max(lengths) - min(lengths)
            if spread <= 4 and len(set(lengths)) <= 2:
                critical.append("regular_rhythm")
            if max(lengths) <= 14 and spread <= 2 and len(sentences) >= 4:
                critical.append("regular_rhythm")
            if len(set(lengths)) == 1 and len(sentences) >= 3:
                critical.append("regular_rhythm")

        if first_words:
            start_bigram = " ".join(normalized_sentences[0].split()[:2])
            if first_words[0] in _TEMPLATE_OPENERS or start_bigram in _TEMPLATE_OPENERS:
                critical.append("template_opening")
            if max(Counter(first_words).values()) >= 3:
                critical.append("repetitive_opening")
            if len(first_words) >= 4 and len(set(first_words[:4])) <= 2:
                warnings.append("repetitive_opening")

        if last_words:
            if max(Counter(last_words).values()) >= 3:
                critical.append("repetitive_closure")
            ending_bigram = " ".join(normalized_sentences[-1].split()[-2:])
            if ending_bigram in _TEMPLATE_CLOSERS or any(sentence.endswith(closing) for sentence in normalized_sentences for closing in _TEMPLATE_CLOSERS):
                critical.append("template_closure")

        if first_verbs and len(first_verbs) >= 3 and len(set(first_verbs)) <= 2:
            warnings.append("syntactic_monotony")
        if first_nouns and len(first_nouns) >= 3 and len(set(first_nouns)) <= 2:
            warnings.append("syntactic_monotony")
        if len(sentences) >= 4 and len(set(first_words[:4])) <= 2:
            warnings.append("predictable_opening")
        if len(sentences) >= 4 and sum(sentence.count(",") >= 2 for sentence in sentences) >= 2:
            warnings.append("catalogue_style")

        ai_like_triggers = {
            "regular_rhythm",
            "template_opening",
            "template_closure",
            "repetitive_opening",
            "repetitive_closure",
        }
        if any(flag in critical for flag in ai_like_triggers) or "catalogue_style" in warnings:
            critical.append("ai_like")

        return critical, warnings

    def _contains_exit_claim(self, lowered: str) -> bool:
        return any(marker in lowered for marker in ("stad mozna ruszyc", "otwiera sie", "prowadzi", "wiedzie", "niknie", "wychodzi"))

    def _exit_claim_sentences(self, text: str) -> tuple[str, ...]:
        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        markers = ("stad mozna ruszyc", "otwiera sie", "prowadzi", "wiedzie", "niknie", "wychodzi")
        return tuple(sentence for sentence in sentences if any(marker in normalize_phrase(sentence) for marker in markers))

    def _direction_roots(self, exit_name: str) -> set[str]:
        lowered = normalize_phrase(exit_name)
        roots: set[str] = set()
        if "polnoc" in lowered:
            roots.add("polnoc")
        if "poludni" in lowered:
            roots.add("poludnie")
        if "wschod" in lowered:
            roots.add("wschod")
        if "zachod" in lowered:
            roots.add("zachod")
        if "gora" in lowered:
            roots.add("gora")
        if "dol" in lowered:
            roots.add("dol")
        return roots

    def _score(self, text: str, facts: PermanentLocationFacts, warnings: list[str], critical: list[str]) -> dict[str, int]:
        lowered = normalize_phrase(text)
        words = lowered.split()
        sentence_count = max(1, text.count(".") + text.count("!") + text.count("?"))
        avg_sentence_len = len(words) / sentence_count if words else 0.0
        concrete_hits = sum(1 for token in (facts.dominant_landmark, *facts.secondary_details, *facts.dominant_materials) if normalize_phrase(token) in lowered)
        adjective_hits = sum(1 for token in lowered.split() if token.endswith(("y", "a", "e")) and len(token) > 4)
        return {
            "factual_consistency": 0 if critical else 92,
            "spatial_consistency": 0 if "nonexistent_exit" in critical else 90,
            "regional_consistency": 88 if facts.region_id in lowered or facts.area_id in lowered else 78,
            "linguistic_correctness": max(0, 96 - max(0, int(abs(avg_sentence_len - 16) * 2))),
            "concreteness": min(100, 60 + concrete_hits * 8),
            "sensory_grounding": 70 if any(normalize_phrase(src) in lowered for src in (*facts.smell_sources, *facts.sound_sources)) else 55,
            "distinctiveness": 84 - int(cosine_token_similarity(text, facts.dominant_landmark or facts.function) * 30),
            "readability": max(0, 92 - int(abs(avg_sentence_len - 16) * 3)),
            "stylistic_naturalness": max(0, 92 - len(warnings) * 10 - max(0, adjective_hits - 10) * 3),
            "interaction_support": 85 if facts.examinable_features else 60,
            "repetition_risk": min(100, 20 + max(0, len(words) - len(set(words))) * 5),
            "cliché_risk": min(100, len([phrase for phrase in _BANNED if phrase in lowered]) * 18),
        }

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
from typing import Protocol

from astergard.commands.polish import normalize_phrase


class SemanticSimilarityProvider(Protocol):
    def similarity(self, left: str, right: str) -> float:
        ...


def _ngrams(tokens: list[str], size: int) -> set[tuple[str, ...]]:
    if len(tokens) < size:
        return set()
    return {tuple(tokens[index : index + size]) for index in range(len(tokens) - size + 1)}


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
    "są",
    "to",
    "ten",
    "ta",
    "te",
}

_MATERIAL_HINTS = {
    "kamien",
    "kamień",
    "bruk",
    "ziemia",
    "mur",
    "mury",
    "cegla",
    "cegła",
    "belka",
    "belki",
    "drewno",
    "deska",
    "deski",
    "torf",
    "sitowie",
    "korzen",
    "korzeń",
    "koleina",
    "koleiny",
    "gruz",
    "rumowisko",
    "palenisko",
    "strop",
    "łuk",
    "ościeżnica",
    "próg",
    "słup",
    "palisada",
    "nasyp",
    "skarpa",
    "rów",
    "żwir",
    "glina",
    "sadza",
    "woda",
    "błoto",
    "łańcuch",
    "młot",
    "kowadło",
    "piec",
    "wózek",
    "skrzynia",
    "hala",
    "posadzka",
    "schody",
    "szyb",
    "gzyms",
    "trzcina",
    "mgła",
    "wiatr",
    "dym",
    "żar",
    "pył",
    "żelazo",
    "drzwi",
    "zawiasy",
    "tablica",
    "znak",
    "studnia",
    "kubeł",
    "brama",
    "furtka",
    "ława",
    "sufit",
    "okno",
    "okiennica",
}

_ROLE_KEYWORDS = {
    "industrial": {"młot", "młoty", "piec", "żużel", "pył", "sadza", "wózek", "wózki", "hala", "narzędzia", "stół", "kowadło", "szlif", "cięcie", "odlewanie", "sortowanie", "magazyn"},
    "road": {"droga", "trakt", "ścieżka", "koleiny", "zakręt", "rozwidlenie", "nasyp", "rów", "bruk", "kamienie", "piasek", "mijanka", "podjazd", "spadek"},
    "border": {"brama", "mur", "palisada", "granica", "słup", "łańcuch", "okucia", "przejście", "przesmyk", "zwężenie", "most", "brzeg", "las", "bagno", "miasto", "przedmieście", "pole"},
    "ruin": {"ruina", "ruiny", "rumowisko", "fundament", "ściana", "strop", "łuk", "schody", "wypal", "podmy", "korzeń", "zawal", "zasyp", "zniszc"},
    "vertical": {"schody", "szyb", "urwisko", "stok", "żleb", "wał", "wieża", "pion", "wspin", "schod", "osyp", "góra", "dół", "krawędź"},
    "natural": {"torf", "sitowie", "trzcina", "korzeń", "mch", "błoto", "woda", "wypłuk", "zalew", "osiad", "zarast", "podmy", "gnic", "przemarz", "zwierzę"},
    "town": {"kram", "bruk", "dom", "murar", "podcień", "podwór", "cech", "ława", "wozy", "handel", "studnia", "fontanna", "straż", "plac"},
    "interior": {"stół", "ława", "okno", "komora", "izba", "skrzynia", "lampa", "progi", "blat", "ściana", "sufit", "wejście"},
    "landscape": {"stok", "grzbiet", "dolina", "jar", "nasyp", "skarpa", "głaz", "zbocze", "wiatr", "rozstaj"},
    "sacred": {"ołtarz", "kaplica", "nisza", "świece", "wosk", "balustrada", "nawa", "zakrystia", "posadzka"},
}


def _sentence_tokens(text: str) -> tuple[tuple[str, ...], ...]:
    sentences = [part.strip() for part in text.split(".") if part.strip()]
    return tuple(tuple(normalize_phrase(sentence, drop_stopwords=True).split()) for sentence in sentences if sentence)


def _sentence_set_similarity(left: str, right: str) -> float:
    left_sentences = {sentence for sentence in _sentence_tokens(left) if sentence}
    right_sentences = {sentence for sentence in _sentence_tokens(right) if sentence}
    if not left_sentences and not right_sentences:
        return 1.0
    union = left_sentences | right_sentences
    if not union:
        return 0.0
    return len(left_sentences & right_sentences) / len(union)


def _material_similarity(left: str, right: str) -> float:
    left_tokens = set(normalize_phrase(left, drop_stopwords=True).split())
    right_tokens = set(normalize_phrase(right, drop_stopwords=True).split())
    left_material = left_tokens & _MATERIAL_HINTS
    right_material = right_tokens & _MATERIAL_HINTS
    if not left_material and not right_material:
        return 0.0
    union = left_material | right_material
    return len(left_material & right_material) / len(union) if union else 0.0


def _role_signature(text: str) -> tuple[str, ...]:
    roles: list[str] = []
    for sentence in _sentence_tokens(text):
        token_set = set(sentence)
        best_role = "generic"
        best_score = 0
        for role, keywords in _ROLE_KEYWORDS.items():
            score = len(token_set & keywords)
            if score > best_score:
                best_score = score
                best_role = role
        roles.append(best_role)
    return tuple(sorted(roles))


def _role_similarity(left: str, right: str) -> float:
    left_roles = _role_signature(left)
    right_roles = _role_signature(right)
    if not left_roles and not right_roles:
        return 1.0
    left_counter = Counter(left_roles)
    right_counter = Counter(right_roles)
    union_keys = left_counter.keys() | right_counter.keys()
    overlap = sum(min(left_counter[key], right_counter[key]) for key in union_keys)
    total = sum(max(left_counter[key], right_counter[key]) for key in union_keys)
    return overlap / total if total else 0.0


def _noun_verb_signature(text: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for sentence in _sentence_tokens(text):
        noun = ""
        verb = ""
        for token in sentence:
            if not noun and token not in _STOPWORDS:
                noun = token
            if not verb and (token.endswith(("a", "e", "i", "o", "y", "u")) or token in {"widać", "stoi", "leży", "prowadzi", "przechodzi", "skręca", "opada", "wznosi", "ciągnie", "niesie", "zbiera", "pęka", "osiada", "spaja", "podpiera"}):
                verb = token
            if noun and verb:
                break
        if noun or verb:
            pairs.add((noun, verb))
    return pairs


def _noun_verb_similarity(left: str, right: str) -> float:
    left_pairs = _noun_verb_signature(left)
    right_pairs = _noun_verb_signature(right)
    if not left_pairs and not right_pairs:
        return 1.0
    union = left_pairs | right_pairs
    if not union:
        return 0.0
    return len(left_pairs & right_pairs) / len(union)


def jaccard_ngram_similarity(left: str, right: str, *, size: int = 2) -> float:
    left_tokens = normalize_phrase(left, drop_stopwords=True).split()
    right_tokens = normalize_phrase(right, drop_stopwords=True).split()
    left_ngrams = _ngrams(left_tokens, size)
    right_ngrams = _ngrams(right_tokens, size)
    if not left_ngrams and not right_ngrams:
        return 1.0
    union = left_ngrams | right_ngrams
    if not union:
        return 0.0
    return len(left_ngrams & right_ngrams) / len(union)


def cosine_token_similarity(left: str, right: str) -> float:
    left_tokens = normalize_phrase(left, drop_stopwords=True).split()
    right_tokens = normalize_phrase(right, drop_stopwords=True).split()
    if not left_tokens or not right_tokens:
        return 0.0
    left_counter = Counter(left_tokens)
    right_counter = Counter(right_tokens)
    shared = left_counter.keys() & right_counter.keys()
    dot = sum(left_counter[token] * right_counter[token] for token in shared)
    left_norm = sqrt(sum(value * value for value in left_counter.values()))
    right_norm = sqrt(sum(value * value for value in right_counter.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def sentence_edge_similarity(left: str, right: str) -> float:
    left_sentences = [normalize_phrase(sentence, drop_stopwords=True) for sentence in left.split(".") if sentence.strip()]
    right_sentences = [normalize_phrase(sentence, drop_stopwords=True) for sentence in right.split(".") if sentence.strip()]
    if not left_sentences or not right_sentences:
        return 0.0
    left_first = left_sentences[0]
    left_last = left_sentences[-1]
    right_first = right_sentences[0]
    right_last = right_sentences[-1]
    aligned = (jaccard_ngram_similarity(left_first, right_first, size=2) + jaccard_ngram_similarity(left_last, right_last, size=2)) / 2
    crossed = (jaccard_ngram_similarity(left_first, right_last, size=2) + jaccard_ngram_similarity(left_last, right_first, size=2)) / 2
    return max(aligned, crossed)


@dataclass(slots=True)
class SimilarityReport:
    jaccard: float
    cosine: float
    sentence_edges: float
    sentence_set: float
    role_signature: float
    noun_verb: float
    material: float

    @property
    def overall(self) -> float:
        return (
            (self.jaccard * 0.18)
            + (self.cosine * 0.16)
            + (self.sentence_edges * 0.10)
            + (self.sentence_set * 0.22)
            + (self.role_signature * 0.16)
            + (self.noun_verb * 0.10)
            + (self.material * 0.08)
        )


class DeterministicSimilarityProvider:
    def similarity(self, left: str, right: str) -> float:
        return SimilarityReport(
            jaccard=jaccard_ngram_similarity(left, right),
            cosine=cosine_token_similarity(left, right),
            sentence_edges=sentence_edge_similarity(left, right),
            sentence_set=_sentence_set_similarity(left, right),
            role_signature=_role_similarity(left, right),
            noun_verb=_noun_verb_similarity(left, right),
            material=_material_similarity(left, right),
        ).overall

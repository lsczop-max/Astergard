from __future__ import annotations

import re
import unicodedata

POLISH_TRANSLATION = str.maketrans({
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ż": "z", "ź": "z",
    "Ą": "a", "Ć": "c", "Ę": "e", "Ł": "l", "Ń": "n", "Ó": "o", "Ś": "s", "Ż": "z", "Ź": "z",
})

STOPWORDS = {
    "na", "w", "we", "do", "z", "ze", "za", "pod", "nad", "przez", "przy", "u", "o", "po", "od", "dla",
    "sie", "się", "tego", "ta", "ten", "to", "tej", "tym", "tę", "te", "tych",
}

# Small, explicit lemma table. It is intentionally conservative: it improves MUD usability
# without pretending to be a full Polish morphological analyzer.
LEMMA_OVERRIDES: dict[str, str] = {
    "brame": "brama", "bramy": "brama", "brama": "brama", "bramie": "brama",
    "zolnierza": "zolnierz", "zolnierzem": "zolnierz", "zolnierzowi": "zolnierz", "zolnierzu": "zolnierz",
    "kupca": "kupiec", "kupcem": "kupiec", "kupcowi": "kupiec", "kupcu": "kupiec",
    "klucza": "klucz", "kluczem": "klucz", "kluczowi": "klucz", "kluczu": "klucz",
    "miecza": "miecz", "mieczem": "miecz", "mieczowi": "miecz", "mieczu": "miecz",
    "tarcze": "tarcza", "tarcza": "tarcza", "tarczy": "tarcza", "tarczo": "tarcza",
    "kurtke": "kurtka", "kurtki": "kurtka", "kurtka": "kurtka",
    "chleba": "chleb", "chlebem": "chleb", "chlebie": "chleb",
    "wilka": "wilk", "wilkiem": "wilk", "wilku": "wilk",
    "skore": "skora", "skory": "skora", "skora": "skora",
    "sakwy": "sakwa", "sakwe": "sakwa", "sakiewke": "sakiewka", "sakiewki": "sakiewka",
    "plecaka": "plecak", "plecakiem": "plecak", "plecaku": "plecak",
    "torby": "torba", "torbe": "torba", "torbie": "torba", "torebki": "torba",
    "worka": "worek", "workiem": "worek", "worku": "worek", "worki": "worek",
    "pojemnika": "pojemnik", "pojemnikiem": "pojemnik", "pojemniku": "pojemnik", "pojemniki": "pojemnik",
    "skrzynie": "skrzynia", "skrzyni": "skrzynia", "skrzynia": "skrzynia",
    "skrzynke": "skrzynka", "skrzynki": "skrzynka", "skrzynce": "skrzynka",
    "mape": "mapa", "mapy": "mapa", "mapie": "mapa",
    "kamienia": "kamien", "kamieniu": "kamien", "kamieniem": "kamien",
    "glazu": "glaz", "glazem": "glaz", "glazy": "glaz",
    "korze": "kora", "kora": "kora", "kory": "kora",
    "drzewa": "drzewo", "drzewem": "drzewo", "drzewie": "drzewo",
    "slady": "slad", "slad": "slad", "sledy": "slad",
    "sciezki": "sciezka", "sciezce": "sciezka", "sciezka": "sciezka",
    "drugiej": "drugi", "trzeciej": "trzeci", "czwartej": "czwarty", "piatej": "piaty",
    "polnoc": "polnoc", "poludnie": "poludnie", "wschod": "wschod", "zachod": "zachod",
    "wejdz": "gora", "zejdz": "dol", "wroc": "wroc",
}

PUNCT_RE = re.compile(r"[^a-z0-9\- ]+")
SPACE_RE = re.compile(r"\s+")


def strip_diacritics(text: str) -> str:
    translated = text.translate(POLISH_TRANSLATION)
    normalized = unicodedata.normalize("NFKD", translated)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    lowered = strip_diacritics(text).lower().replace("_", " ")
    cleaned = PUNCT_RE.sub(" ", lowered)
    return SPACE_RE.sub(" ", cleaned).strip()


def normalize_token(token: str) -> str:
    base = normalize_text(token)
    return LEMMA_OVERRIDES.get(base, base)


def normalize_phrase(text: str, *, drop_stopwords: bool = False) -> str:
    tokens = [normalize_token(token) for token in normalize_text(text).split()]
    if drop_stopwords:
        tokens = [token for token in tokens if token not in STOPWORDS]
    return " ".join(tokens)


def tokens_match(needle: str, haystack: str) -> bool:
    needle_tokens = [token for token in normalize_phrase(needle, drop_stopwords=True).split() if token]
    hay_tokens = normalize_phrase(haystack, drop_stopwords=False).split()
    hay_joined = " ".join(hay_tokens)
    return bool(needle_tokens) and all(
        token in hay_tokens or any(part.startswith(token) for part in hay_tokens) or token in hay_joined
        for token in needle_tokens
    )


def any_token_matches(needle: str, haystack: str) -> bool:
    needle_tokens = [token for token in normalize_phrase(needle, drop_stopwords=True).split() if token]
    hay_tokens = normalize_phrase(haystack, drop_stopwords=False).split()
    hay_joined = " ".join(hay_tokens)
    return bool(needle_tokens) and any(
        token in hay_tokens or any(part.startswith(token) for part in hay_tokens) or token in hay_joined
        for token in needle_tokens
    )


def is_all_phrase(text: str | None) -> bool:
    if not text:
        return False
    normalized = normalize_phrase(text, drop_stopwords=True)
    return normalized in {"wszystko", "wszystkie", "all"}

def split_relation(text: str | None, connectors: set[str]) -> tuple[str | None, str | None]:
    """Split Polish object interaction phrase into left/right object names.

    Examples:
    - "miecz do plecaka" -> ("miecz", "plecak")
    - "skore kupcowi" -> ("skora", "kupiec") through lemma normalization.
    """
    if not text:
        return None, None
    tokens = normalize_phrase(text, drop_stopwords=False).split()
    if not tokens:
        return None, None
    for idx, token in enumerate(tokens):
        if token in connectors:
            left = " ".join(tokens[:idx]).strip()
            right = " ".join(tokens[idx + 1:]).strip()
            return (left or None), (right or None)
    # Dative shorthand: "daj skore kupcowi" becomes "skora kupiec" after lemma normalization.
    # If there are at least two tokens, treat the final token as recipient/container candidate.
    if len(tokens) >= 2 and connectors & {"recipient"}:
        return " ".join(tokens[:-1]), tokens[-1]
    return " ".join(tokens), None

from __future__ import annotations

STARTING_ROOM_ID = 14

REGION_I_ZONE_IDS = frozenset(
    {
        "centrum",
        "trakt",
        "trakt-gorniczy",
        "trakt-nadrzeczny",
        "polnocny-las",
        "nadrzeczne-mokradla",
    }
)

OPPOSITE = {
    "polnoc": "poludnie",
    "poludnie": "polnoc",
    "wschod": "zachod",
    "zachod": "wschod",
    "polnocny-wschod": "poludniowy-zachod",
    "poludniowy-zachod": "polnocny-wschod",
    "polnocny-zachod": "poludniowy-wschod",
    "poludniowy-wschod": "polnocny-zachod",
    "gora": "dol",
    "dol": "gora",
}

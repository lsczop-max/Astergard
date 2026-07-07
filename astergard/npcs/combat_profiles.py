from __future__ import annotations

NPC_COMBAT_STYLE_BY_VNUM: dict[str, str] = {
    "meekhan_soldier": "defensywny",
    "merchant": "ostrozny",
    "mountain_troll": "brutalny",
    "wolf": "ofensywny",
    "astergard_guard": "defensywny",
    "innkeeper": "ostrozny",
    "blacksmith": "defensywny",
    "farmer": "zrownowazony",
    "fisherman": "zrownowazony",
    "traveler": "zrownowazony",
    "child": "zrownowazony",
    "beggar": "zrownowazony",
    "carpenter": "zrownowazony",
    "tanner": "zrownowazony",
    "bowyer": "zrownowazony",
    "armorer": "defensywny",
    "dockhand": "zrownowazony",
    "miller": "zrownowazony",
    "priest_aide": "zrownowazony",
    "watch_sergeant": "defensywny",
    "customs_clerk": "zrownowazony",
    "fishmonger": "zrownowazony",
    "woodcutter": "zrownowazony",
    "urchin": "zrownowazony",
    "vagrant": "zrownowazony",
}


def combat_style_for_vnum(vnum: str) -> str:
    return NPC_COMBAT_STYLE_BY_VNUM.get(vnum, "zrownowazony")

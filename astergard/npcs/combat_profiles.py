from __future__ import annotations

NPC_COMBAT_STYLE_BY_VNUM: dict[str, str] = {
    "meekhan_soldier": "defensywny",
    "merchant": "ostrozny",
    "mountain_troll": "brutalny",
    "wolf": "ofensywny",
}


def combat_style_for_vnum(vnum: str) -> str:
    return NPC_COMBAT_STYLE_BY_VNUM.get(vnum, "zrownowazony")

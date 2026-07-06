from __future__ import annotations

def overall_health_desc(wounds: dict[str, int]) -> str:
    total = sum(wounds.values())
    if total == 0: return "jest w pełni sił"
    if total <= 3: return "jest lekko ranny"
    if total <= 7: return "krwawi obficie"
    if total <= 12: return "ledwo trzyma się na nogach"
    return "jest u progu śmierci"

def is_dead(wounds: dict[str, int]) -> bool:
    return wounds.get("glowa", 0) >= 4 or wounds.get("korpus", 0) >= 4

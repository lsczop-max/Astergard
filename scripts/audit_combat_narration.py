#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from astergard.characters.models import Character
    from astergard.combat.manager import CombatManager
    from astergard.items.models import Item

    attacker = Character("atakujacy")
    defender = Character("obronca")
    attacker.stats.zrecznosc = 16
    defender.stats.zrecznosc = 10
    attacker.combat_style = "brutalny"
    attacker.equipment["prawa_reka"] = Item("prosty miecz", "", 1.8, 10, "simple_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1)

    manager = CombatManager()
    result = manager.attack(attacker, defender)
    messages = {
        "attacker": result.message,
        "observer": result.observer_message or "",
        "defender": result.defender_message or "",
    }
    issues: list[str] = []
    for perspective, message in messages.items():
        print(f"[{perspective}] {message}")
        if "None" in message:
            issues.append(f"{perspective}: contains None")
        if any(token in message for token in ("attack_score", "defense_score", "CombatEvent", "CombatResult")):
            issues.append(f"{perspective}: technical marker leaked")
        if any(ch.isdigit() for ch in message):
            issues.append(f"{perspective}: visible digit")
    if issues:
        print("\nAUDIT FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("\nAUDIT OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

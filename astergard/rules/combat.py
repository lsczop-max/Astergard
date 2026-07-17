from __future__ import annotations

from dataclasses import dataclass, field

from astergard.combat.manager import CombatStyle


@dataclass(frozen=True, slots=True)
class CombatRules:
    body_part_weights: tuple[tuple[str, int], ...] = (
        ("glowa", 10),
        ("korpus", 40),
        ("prawa_reka", 12),
        ("lewa_reka", 13),
        ("prawa_noga", 12),
        ("lewa_noga", 13),
    )
    styles: dict[str, CombatStyle] = field(default_factory=lambda: {
        "zrownowazony": CombatStyle("zrownowazony", label="zrównoważonym stylem"),
        "ofensywny": CombatStyle("ofensywny", attack_modifier=2, defense_modifier=-1, stamina_cost_modifier=1, damage_modifier=1, label="ofensywnym natarciem"),
        "defensywny": CombatStyle("defensywny", attack_modifier=-1, defense_modifier=1, initiative_modifier=-1, stamina_cost_modifier=0, label="defensywną postawą"),
        "ostrozny": CombatStyle("ostrozny", attack_modifier=0, defense_modifier=1, initiative_modifier=1, label="ostrożnym krokiem"),
        "brutalny": CombatStyle("brutalny", attack_modifier=3, defense_modifier=-1, initiative_modifier=-1, stamina_cost_modifier=1, damage_modifier=0, label="brutalnym zamachem"),
    })
    low_stamina_divisor: int = 5
    low_stamina_initiative_penalty: int = 4
    initiative_roll_sides: int = 10
    attack_roll_sides: int = 20
    base_unarmed_damage: int = 2
    unarmed_reach: int = 1
    base_attack_stamina_cost: int = 4
    minimum_attack_stamina_cost: int = 1
    exhausted_hit_divisor: int = 2
    weapon_degrade_chance: float = 0.10
    armor_degrade_chance: float = 0.15
    active_defense_roll_sides: int = 20
    shield_block_margin: int = 6
    parry_margin: int = 7
    active_defense_degrade_chance: float = 0.08
    max_wound_level: int = 4
    attack_skill_train_amount: int = 2
    dodge_skill_train_amount: int = 1
    parry_skill_train_amount: int = 2

    def normalize_style(self, name: str | None) -> str:
        raw = (name or "").strip().lower().replace("ż", "z").replace("ó", "o")
        aliases = {
            "balanced": "zrownowazony",
            "rownowazony": "zrownowazony",
            "zrównoważony": "zrownowazony",
            "zrownowazony": "zrownowazony",
            "atak": "ofensywny",
            "agresywny": "ofensywny",
            "ofensywny": "ofensywny",
            "obrona": "defensywny",
            "defensywny": "defensywny",
            "ostrozny": "ostrozny",
            "ostrożny": "ostrozny",
            "brutalny": "brutalny",
        }
        return aliases.get(raw, "zrownowazony")

    def style(self, name: str | None) -> CombatStyle:
        return self.styles[self.normalize_style(name)]

    def attack_stamina_cost(self, weapon_reach: int, style: CombatStyle) -> int:
        return max(self.minimum_attack_stamina_cost, self.base_attack_stamina_cost + max(0, weapon_reach - 1) + style.stamina_cost_modifier)


def default_combat_rules() -> CombatRules:
    return CombatRules()

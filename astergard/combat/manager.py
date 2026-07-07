from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from astergard.characters.models import Character
from astergard.combat.wounds import is_dead
from astergard.combat.tactics import (
    fatigue_attack_penalty,
    fatigue_defense_penalty,
    formation_attack_modifier,
    formation_defense_modifier,
    formation_initiative_modifier,
    morale_score,
    profession_tactical_modifiers,
    skill_for_weapon,
    wound_attack_penalty,
    wound_defense_penalty,
    wound_initiative_penalty,
)

if TYPE_CHECKING:
    from astergard.items.models import Item
    from astergard.rules.combat import CombatRules

BODY_WEIGHTS = [
    ("glowa", 10),
    ("korpus", 40),
    ("prawa_reka", 12),
    ("lewa_reka", 13),
    ("prawa_noga", 12),
    ("lewa_noga", 13),
]


class RandomSource(Protocol):
    def randint(self, a: int, b: int) -> int: ...
    def random(self) -> float: ...


@dataclass(frozen=True, slots=True)
class CombatStyle:
    name: str
    attack_modifier: int = 0
    defense_modifier: int = 0
    initiative_modifier: int = 0
    stamina_cost_modifier: int = 0
    damage_modifier: int = 0
    label: str = "zrównoważonym stylem"


COMBAT_STYLES: dict[str, CombatStyle] = {
    "zrownowazony": CombatStyle("zrownowazony", label="zrównoważonym stylem"),
    "ofensywny": CombatStyle("ofensywny", attack_modifier=2, defense_modifier=-1, stamina_cost_modifier=1, damage_modifier=1, label="ofensywnym natarciem"),
    "defensywny": CombatStyle("defensywny", attack_modifier=-1, defense_modifier=1, initiative_modifier=-1, stamina_cost_modifier=0, label="defensywną postawą"),
    "ostrozny": CombatStyle("ostrozny", attack_modifier=0, defense_modifier=1, initiative_modifier=1, label="ostrożnym krokiem"),
    "brutalny": CombatStyle("brutalny", attack_modifier=3, defense_modifier=-1, initiative_modifier=-1, stamina_cost_modifier=1, damage_modifier=2, label="brutalnym zamachem"),
}

def normalize_combat_style(name: str | None) -> str:
    from astergard.rules.combat import default_combat_rules

    return default_combat_rules().normalize_style(name)


def get_combat_style(name: str | None) -> CombatStyle:
    from astergard.rules.combat import default_combat_rules

    return default_combat_rules().style(name)


@dataclass
class CombatResult:
    hit: bool
    message: str
    defender_dead: bool = False
    defended_by: str | None = None
    body_part: str | None = None
    effective_damage: int = 0
    observer_message: str | None = None
    style_used: str = "zrownowazony"
    attack_score: int = 0
    defense_score: int = 0
    tactical_note: str | None = None


@dataclass
class CombatTurn:
    attacker_id: str
    defender_id: str
    initiative: int


@dataclass
class CombatRoundResult:
    turns: list[CombatTurn] = field(default_factory=list)
    results: list[CombatResult] = field(default_factory=list)

    @property
    def message(self) -> str:
        return "\n".join(result.message for result in self.results)

    @property
    def observer_message(self) -> str:
        return "\n".join(result.observer_message or result.message for result in self.results)


class CombatManager:
    def __init__(self, rng: RandomSource | None = None, rules: CombatRules | None = None) -> None:
        from astergard.rules.combat import default_combat_rules

        self.active_fights: list[tuple[str, str]] = []
        self.rng: RandomSource = rng or random
        self.rules = rules or default_combat_rules()

    def start(self, attacker_id: str, defender_id: str) -> None:
        pair = (attacker_id, defender_id)
        rev = (defender_id, attacker_id)
        if pair not in self.active_fights and rev not in self.active_fights:
            self.active_fights.append(pair)

    def stop_for(self, entity_id: str) -> None:
        self.active_fights = [p for p in self.active_fights if entity_id not in p]

    def choose_body_part(self) -> str:
        total = sum(w for _, w in self.rules.body_part_weights)
        roll = self.rng.randint(1, total)
        acc = 0
        for part, weight in self.rules.body_part_weights:
            acc += weight
            if roll <= acc:
                return part
        return "korpus"

    def initiative_score(self, character: Character) -> int:
        weapon = character.weapon()
        style = self.rules.style(character.combat_style)
        weapon_modifier = weapon.initiative_modifier if weapon and weapon.durability > 0 else 0
        wound_penalty = wound_initiative_penalty(character)
        stamina_penalty = self.rules.low_stamina_initiative_penalty if character.stats.kondycja <= max(1, character.stats.max_kondycja // self.rules.low_stamina_divisor) else 0
        tactical = formation_initiative_modifier(character)
        morale_bonus = (morale_score(character) - 10) // 4
        profession_bonus = profession_tactical_modifiers(character, weapon).initiative
        return character.stats.zrecznosc + weapon_modifier + style.initiative_modifier + tactical + morale_bonus + profession_bonus + self.rng.randint(1, self.rules.initiative_roll_sides) - wound_penalty - stamina_penalty

    def ordered_turns(self, attacker_id: str, attacker: Character, defender_id: str, defender: Character) -> list[CombatTurn]:
        turns = [
            CombatTurn(attacker_id, defender_id, self.initiative_score(attacker)),
            CombatTurn(defender_id, attacker_id, self.initiative_score(defender)),
        ]
        return sorted(turns, key=lambda turn: turn.initiative, reverse=True)

    def process_pair_round(
        self,
        attacker_id: str,
        attacker: Character,
        defender_id: str,
        defender: Character,
    ) -> CombatRoundResult:
        round_result = CombatRoundResult()
        entities = {attacker_id: attacker, defender_id: defender}
        for turn in self.ordered_turns(attacker_id, attacker, defender_id, defender):
            round_result.turns.append(turn)
            current_attacker = entities[turn.attacker_id]
            current_defender = entities[turn.defender_id]
            if not current_attacker.is_alive or not current_defender.is_alive:
                continue
            result = self.attack(current_attacker, current_defender)
            round_result.results.append(result)
            if result.defender_dead:
                self.stop_for(turn.defender_id)
                break
        return round_result

    def process_active_round(self, entities: dict[str, Character]) -> CombatRoundResult:
        aggregate = CombatRoundResult()
        for attacker_id, defender_id in list(self.active_fights):
            attacker = entities.get(attacker_id)
            defender = entities.get(defender_id)
            if attacker is None or defender is None or not attacker.is_alive or not defender.is_alive:
                self.stop_for(attacker_id)
                self.stop_for(defender_id)
                continue
            if attacker.room_id != defender.room_id:
                self.stop_for(attacker_id)
                self.stop_for(defender_id)
                continue
            result = self.process_pair_round(attacker_id, attacker, defender_id, defender)
            aggregate.turns.extend(result.turns)
            aggregate.results.extend(result.results)
        return aggregate

    def attack(self, attacker: Character, defender: Character) -> CombatResult:
        if not attacker.is_alive or not defender.is_alive:
            return CombatResult(False, "Walka już się zakończyła.")
        weapon = attacker.weapon()
        attacker_style = self.rules.style(attacker.combat_style)
        defender_style = self.rules.style(defender.combat_style)
        weapon_damage = weapon.base_damage if weapon and weapon.durability > 0 else self.rules.base_unarmed_damage
        weapon_reach = weapon.reach if weapon and weapon.durability > 0 else self.rules.unarmed_reach
        defender_weapon = defender.weapon()
        weapon_skill = self._weapon_skill_name(weapon)
        atk_skill = attacker.skills.level(weapon_skill)
        dodge = defender.skills.level("uniki")
        attacker_profession = profession_tactical_modifiers(attacker, weapon)
        defender_profession = profession_tactical_modifiers(defender, defender_weapon)
        attacker_morale = morale_score(attacker)
        defender_morale = morale_score(defender)
        stamina_cost = self._attack_stamina_cost(weapon_reach, attacker_style)
        attacker.stats.kondycja = max(0, attacker.stats.kondycja - stamina_cost)
        hit_score = (
            attacker.stats.zrecznosc
            + atk_skill
            + weapon_reach
            + attacker_style.attack_modifier
            + formation_attack_modifier(attacker, defender, weapon)
            + (attacker_morale - 10) // 4
            + attacker_profession.attack
            - wound_attack_penalty(attacker)
            - fatigue_attack_penalty(attacker)
            + self.rng.randint(1, self.rules.attack_roll_sides)
        )
        if attacker.stats.kondycja == 0:
            hit_score //= self.rules.exhausted_hit_divisor
        dodge_score = (
            defender.stats.zrecznosc
            + dodge
            + defender_style.defense_modifier
            + formation_defense_modifier(defender, attacker)
            + (defender_morale - 10) // 4
            + defender_profession.defense
            - wound_defense_penalty(defender)
            - fatigue_defense_penalty(defender)
            + self.rng.randint(1, self.rules.attack_roll_sides)
        )
        if hit_score <= dodge_score:
            defender.skills.train("uniki", self.rules.dodge_skill_train_amount)
            message = f"{attacker.username} naciera {attacker_style.label}, lecz {defender.username} uskakuje."
            return CombatResult(False, message, observer_message=message, style_used=attacker_style.name, attack_score=hit_score, defense_score=dodge_score)

        defense = self._active_defense(defender, hit_score)
        if defense is not None:
            defense.style_used = attacker_style.name
            defense.observer_message = defense.observer_message or defense.message
            defense.attack_score = hit_score
            defense.defense_score = dodge_score
            return defense

        part = self.choose_body_part()
        armor = defender.armor_for(part)
        protection = armor.protection if armor and armor.durability > 0 else 0
        effective = weapon_damage + attacker_style.damage_modifier + attacker_profession.damage - protection
        if weapon and self.rng.random() < self.rules.weapon_degrade_chance:
            weapon.durability = max(0.0, weapon.durability - 0.5)
        if armor and self.rng.random() < self.rules.armor_degrade_chance:
            armor.durability = max(0.0, armor.durability - 0.5)
        if effective <= 0:
            message = f"Cios {attacker.username} wykonany {attacker_style.label} zatrzymuje się na pancerzu {defender.username}."
            return CombatResult(True, message, body_part=part, effective_damage=effective, observer_message=message, style_used=attacker_style.name, attack_score=hit_score, defense_score=dodge_score)
        defender.wounds[part] = min(self.rules.max_wound_level, defender.wounds.get(part, 0) + 1)
        attacker.skills.train(weapon_skill, self.rules.attack_skill_train_amount)
        dead = is_dead(defender.wounds)
        if dead:
            defender.die()
        else:
            defender.sync_state_from_flags()
        msg = self._damage_message(attacker.username, defender.username, part, defender.wounds[part], attacker_style)
        if dead:
            msg += f"\n<red>{defender.username} pada martwy.</red>"
        return CombatResult(True, msg, dead, body_part=part, effective_damage=effective, observer_message=msg, style_used=attacker_style.name, attack_score=hit_score, defense_score=dodge_score)

    def _active_defense(self, defender: Character, hit_score: int) -> CombatResult | None:
        defender_style = self.rules.style(defender.combat_style)
        shield = defender.shield()
        if shield is not None:
            block_score = (
                defender.stats.zrecznosc
                + defender_style.defense_modifier
                + shield.shield_block
                + defender.skills.level("tarcze")
                + morale_score(defender) // 5
                + formation_defense_modifier(defender, defender)
                + self.rng.randint(1, self.rules.active_defense_roll_sides)
            )
            if block_score >= hit_score + self.rules.shield_block_margin:
                defender.skills.train("parowanie", self.rules.dodge_skill_train_amount)
                if self.rng.random() < self.rules.active_defense_degrade_chance:
                    shield.durability = max(0.0, shield.durability - 0.5)
                message = f"{defender.username} zbija cios tarczą, trzymając {defender_style.label}."
                return CombatResult(False, message, defended_by="shield", observer_message=message)
        weapon = defender.weapon()
        if weapon is not None and weapon.durability > 0:
            parry_level = defender.skills.level("parowanie")
            parry_score = (
                defender.stats.zrecznosc
                + defender_style.defense_modifier
                + parry_level
                + weapon.parry_bonus
                + morale_score(defender) // 5
                + formation_defense_modifier(defender, defender)
                + self.rng.randint(1, self.rules.active_defense_roll_sides)
            )
            if parry_score >= hit_score + self.rules.parry_margin:
                defender.skills.train("parowanie", self.rules.parry_skill_train_amount)
                if self.rng.random() < self.rules.active_defense_degrade_chance:
                    weapon.durability = max(0.0, weapon.durability - 0.5)
                message = f"{defender.username} paruje uderzenie bronią, walcząc {defender_style.label}."
                return CombatResult(False, message, defended_by="parry", observer_message=message)
        return None

    def _weapon_skill_name(self, weapon: Item | None) -> str:
        return skill_for_weapon(weapon)

    def _attack_stamina_cost(self, weapon_reach: int, style: CombatStyle) -> int:
        return self.rules.attack_stamina_cost(weapon_reach, style)

    def _damage_message(self, attacker: str, defender: str, part: str, wound_level: int, style: CombatStyle) -> str:
        wound = {
            1: "powodując lekkie zadrapanie",
            2: "rozcinając ciało głębiej",
            3: "zadając poważną ranę",
            4: "miażdżąc ciało krytycznie",
        }.get(wound_level, "pogłębiając ranę")
        return f"<red>{attacker} uderza {style.label} i trafia {defender} w {part}, {wound}.</red>"

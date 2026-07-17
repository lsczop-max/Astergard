from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from astergard.combat.actions import (
    CombatAction,
    CombatActionType,
    CombatOutcome,
    CombatOutcomeType,
    DefenseOutcome,
    DefenseResolution,
)
from astergard.combat.defense import DefenseContext, resolve_defense
from astergard.combat.hit_locations import (
    ArmorCoverageOutcome,
    BodyLocation,
    attack_type_for_weapon,
    legacy_body_part_for_location,
    quality_for_margin,
    resolve_armor_coverage,
    resolve_hit_location,
    load_default_hit_location_catalog,
    load_default_armor_coverage_catalog,
)
from astergard.combat.physical_damage import AttackPhysicalOutcome, WoundOutcome, WoundSeverity, resolve_attack_physical_damage
from astergard.combat.reactions import (
    CombatReactionDiscovery,
    CombatReactionExecutor,
    REACTION_POLICY,
    ReactionExecutionResult,
    ReactionTriggerContext,
    build_reaction_user_profile,
    default_combat_reaction_catalog,
    find_available_reactions,
)
from astergard.characters.models import Character
from astergard.combat.events import CombatEvent, normalize_weapon_family
from astergard.combat.narration import CombatNarrator
from astergard.combat.weapons import resolve_weapon_profile, snapshot_weapon_profile
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
    "brutalny": CombatStyle("brutalny", attack_modifier=3, defense_modifier=-1, initiative_modifier=-1, stamina_cost_modifier=1, damage_modifier=0, label="brutalnym zamachem"),
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
    body_location: str | None = None
    body_location_group: str | None = None
    hit_quality: str | None = None
    effective_damage: int = 0
    observer_message: str | None = None
    style_used: str = "zrownowazony"
    attack_score: int = 0
    defense_score: int = 0
    tactical_note: str | None = None
    combat_event: CombatEvent | None = None
    defender_message: str | None = None
    combat_action: CombatAction | None = None
    combat_outcome: CombatOutcome | None = None
    armor_coverage_outcome: ArmorCoverageOutcome | None = None
    physical_outcome: AttackPhysicalOutcome | None = None
    wound_outcome: WoundOutcome | None = None
    armor_layers: tuple[str, ...] = ()
    reaction_discovery: CombatReactionDiscovery | None = None
    reaction_execution: ReactionExecutionResult | None = None


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
        self.narrator = CombatNarrator()
        self._body_part_weights_override: tuple[tuple[str, int], ...] | None = None
        self.reaction_catalog = default_combat_reaction_catalog()
        self.reaction_executor = CombatReactionExecutor(self.reaction_catalog)
        self.hit_location_catalog = load_default_hit_location_catalog()
        self.armor_coverage_catalog = load_default_armor_coverage_catalog()

    def start(self, attacker_id: str, defender_id: str) -> bool:
        pair = (attacker_id, defender_id)
        rev = (defender_id, attacker_id)
        if pair not in self.active_fights and rev not in self.active_fights:
            self.active_fights.append(pair)
            return True
        return False

    def start_fight(self, attacker: Character, defender: Character) -> bool:
        if not attacker.is_alive or not defender.is_alive:
            self._sync_combat_state(attacker)
            self._sync_combat_state(defender)
            return False
        started = self.start(self._combat_identity(attacker), self._combat_identity(defender))
        self._sync_combat_state(attacker)
        self._sync_combat_state(defender)
        return started

    def stop_for(self, entity_id: str) -> None:
        self.active_fights = [p for p in self.active_fights if entity_id not in p]

    def has_fight(self, first_id: str, second_id: str) -> bool:
        pair = (first_id, second_id)
        rev = (second_id, first_id)
        return pair in self.active_fights or rev in self.active_fights

    def fights_for(self, entity_id: str) -> list[tuple[str, str]]:
        return [pair for pair in self.active_fights if entity_id in pair]

    def end_fight(
        self,
        entity_id: str,
        opponent_id: str | None = None,
        reason: str = "MANUAL",
        entities: dict[str, Character] | None = None,
    ) -> int:
        if opponent_id is None:
            removed = [pair for pair in self.active_fights if entity_id in pair]
            self.active_fights = [pair for pair in self.active_fights if entity_id not in pair]
            affected: set[str] = {entity_id}
        else:
            removed = [
                pair
                for pair in self.active_fights
                if pair == (entity_id, opponent_id) or pair == (opponent_id, entity_id)
            ]
            self.active_fights = [pair for pair in self.active_fights if pair not in removed]
            affected = {entity_id, opponent_id}
        if entities is not None:
            affected.update(participant for pair in removed for participant in pair)
            for participant_id in affected:
                self._sync_combat_state(entities.get(participant_id))
        return len(removed)

    def _sync_combat_state(self, character: Character | None) -> None:
        if character is None:
            return
        if not character.is_alive:
            character.in_combat = False
            character.sync_state_from_flags()
            return
        if self.fights_for(self._combat_identity(character)):
            character.enter_combat()
        else:
            character.leave_combat()

    def _combat_identity(self, character: Character) -> str:
        identity = getattr(character, "combat_identity", None)
        if isinstance(identity, str) and identity.strip():
            return identity.strip()
        return character.username

    def build_basic_attack_action(self, attacker: Character, defender: Character) -> CombatAction:
        weapon = attacker.weapon()
        weapon_skill = self._weapon_skill_name(weapon) if weapon is not None else None
        weapon_snapshot = snapshot_weapon_profile(weapon)
        return CombatAction(
            actor_id=self._combat_identity(attacker),
            target_id=self._combat_identity(defender),
            action_type=CombatActionType.BASIC_ATTACK,
            weapon_id=weapon.id if weapon is not None else None,
            weapon_profile_id=weapon_snapshot.weapon_profile_id,
            weapon_specialization_id=weapon_skill,
            weapon_tags=weapon_snapshot.weapon_tags,
            hand_requirement=weapon_snapshot.hand_requirement,
            technique_id=None,
        )

    def resolve_action(self, action: CombatAction, attacker: Character | None, defender: Character | None) -> CombatOutcome:
        if attacker is None:
            return CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.NO_TARGET,
                hit=None,
                defense_result=DefenseResolution.UNKNOWN_DEFENSE,
                target_defeated=False,
                combat_ended=False,
                reason_code="ACTOR_NOT_FOUND",
            )
        if defender is None:
            return CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.NO_TARGET,
                hit=None,
                defense_result=DefenseResolution.UNKNOWN_DEFENSE,
                target_defeated=False,
                combat_ended=False,
                reason_code="TARGET_NOT_FOUND",
            )
        legacy = self.attack(attacker, defender, action=action)
        if legacy.combat_outcome is not None:
            return legacy.combat_outcome
        return CombatOutcome(
            action_id=action.action_id,
            actor_id=action.actor_id,
            target_id=action.target_id,
            result_type=CombatOutcomeType.INVALID,
            hit=None,
            defense_result=DefenseResolution.UNKNOWN_DEFENSE,
            reason_code="INVALID_STATE",
        )

    def choose_body_part(self) -> str:
        weights = self._body_part_weights_override or self.rules.body_part_weights
        total = sum(w for _, w in weights)
        roll = self.rng.randint(1, total)
        acc = 0
        for part, weight in weights:
            acc += weight
            if roll <= acc:
                return part
        return "korpus"

    def initiative_score(self, character: Character) -> int:
        weapon = character.weapon()
        style = self.rules.style(character.combat_style)
        weapon_modifier = weapon.initiative_modifier if weapon and weapon.durability > 0 else 0
        armor_penalty = character.armor_burden_penalty()
        wound_penalty = wound_initiative_penalty(character)
        stamina_penalty = self.rules.low_stamina_initiative_penalty if character.stats.kondycja <= max(1, character.stats.max_kondycja // self.rules.low_stamina_divisor) else 0
        tactical = formation_initiative_modifier(character)
        morale_bonus = (morale_score(character) - 10) // 4
        profession_bonus = profession_tactical_modifiers(character, weapon).initiative
        return character.stats.zrecznosc + weapon_modifier + style.initiative_modifier + tactical + morale_bonus + profession_bonus + self.rng.randint(1, self.rules.initiative_roll_sides) - wound_penalty - stamina_penalty - armor_penalty

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
        entities: dict[str, Character] | None = None,
    ) -> CombatRoundResult:
        round_result = CombatRoundResult()
        entities = entities or {attacker_id: attacker, defender_id: defender}
        for turn in self.ordered_turns(attacker_id, attacker, defender_id, defender):
            round_result.turns.append(turn)
            current_attacker = entities[turn.attacker_id]
            current_defender = entities[turn.defender_id]
            if not current_attacker.is_alive or not current_defender.is_alive:
                continue
            result = self.attack(current_attacker, current_defender)
            round_result.results.append(result)
            reaction_result = None
            if result.reaction_execution is not None:
                reaction_result = result.reaction_execution.reaction_result
            if result.defender_dead or bool(getattr(reaction_result, "defender_dead", False)):
                self.end_fight(turn.attacker_id, turn.defender_id, reason="DEATH", entities=entities)
                break
        return round_result

    def process_active_round(self, entities: dict[str, Character]) -> CombatRoundResult:
        aggregate = CombatRoundResult()
        seen_pairs: set[tuple[str, str]] = set()
        for attacker_id, defender_id in list(self.active_fights):
            pair_key = (attacker_id, defender_id) if attacker_id <= defender_id else (defender_id, attacker_id)
            if pair_key in seen_pairs:
                self.end_fight(attacker_id, defender_id, reason="INVALID_STATE", entities=entities)
                continue
            seen_pairs.add(pair_key)
            attacker = entities.get(attacker_id)
            defender = entities.get(defender_id)
            if attacker is None or defender is None or not attacker.is_alive or not defender.is_alive:
                self.end_fight(attacker_id, defender_id, reason="INVALID_STATE", entities=entities)
                continue
            if attacker.room_id != defender.room_id:
                self.end_fight(attacker_id, defender_id, reason="SEPARATED", entities=entities)
                continue
            result = self.process_pair_round(attacker_id, attacker, defender_id, defender, entities)
            aggregate.turns.extend(result.turns)
            aggregate.results.extend(result.results)
        return aggregate

    def attack(self, attacker: Character, defender: Character, action: CombatAction | None = None) -> CombatResult:
        action = action or self.build_basic_attack_action(attacker, defender)
        if not attacker.is_alive or not defender.is_alive:
            outcome = CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.INVALID,
                hit=False,
                defense_result=DefenseResolution.UNKNOWN_DEFENSE,
                damage=0,
                target_defeated=not defender.is_alive,
                combat_ended=not attacker.is_alive or not defender.is_alive,
                reason_code="ACTOR_DEAD" if not attacker.is_alive else "TARGET_DEAD",
            )
            event = self._build_event(
                attacker,
                defender,
                action_id=action.action_id,
                result="miss",
                defense="none",
                technique="natarcie",
                action_type=action.action_type.value,
                parent_action_id=action.parent_action_id,
                reaction_id=action.reaction_id,
                reaction_type=action.technique_id,
                reaction_depth=action.reaction_depth,
            )
            message = self.narrator.render(event, "attacker")
            return self._attach_reaction_discovery(
                CombatResult(False, message, combat_event=event, combat_action=action, combat_outcome=outcome),
                action,
                attacker,
                defender,
            )

        weapon = attacker.weapon()
        attacker_style = self.rules.style(attacker.combat_style)
        defender_style = self.rules.style(defender.combat_style)
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
        armor_penalty = defender.armor_burden_penalty()
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
        self._body_part_weights_override = self._contextual_body_part_weights(attacker, defender, weapon)
        dodge_score = (
            defender.stats.zrecznosc
            + dodge
            + defender_style.defense_modifier
            + formation_defense_modifier(defender, attacker)
            + (defender_morale - 10) // 4
            + defender_profession.defense
            - wound_defense_penalty(defender)
            - fatigue_defense_penalty(defender)
            - armor_penalty
            + self.rng.randint(1, self.rules.attack_roll_sides)
        )
        self._body_part_weights_override = None
        defense_outcome = resolve_defense(
            DefenseContext(
                attacker=attacker,
                defender=defender,
                hit_score=hit_score,
                dodge_score=dodge_score,
                rng=self.rng,
                rules=self.rules,
            )
        )
        defense = self._active_defense(attacker, defender, action, hit_score, dodge_score, defense_outcome)
        if defense is not None:
            defense.style_used = attacker_style.name
            defense.observer_message = defense.observer_message or self.narrator.render(
                defense.combat_event or self._build_event(attacker, defender, action_id=action.action_id, result=defense.defended_by or "block"),
                "observer",
            )
            defense.attack_score = hit_score
            defense.defense_score = dodge_score
            outcome = CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.DEFENDED,
                hit=False,
                defense_result=defense_outcome.resolution,
                defense_outcome=defense_outcome,
                damage=0,
                target_defeated=False,
                combat_ended=False,
                reason_code="DEFENDED",
            )
            defense.combat_action = action
            defense.combat_outcome = outcome
            return self._attach_reaction_discovery(defense, action, attacker, defender)

        attack_profile = resolve_weapon_profile(weapon)
        attack_type = attack_type_for_weapon(weapon, attack_profile)
        hit_quality = quality_for_margin(hit_score, dodge_score)
        location_outcome = resolve_hit_location(
            attack_profile,
            action,
            hit_quality,
            attacker,
            defender,
            self.rng,
            attack_type=attack_type,
        )
        body_location = location_outcome.location
        body_location_group = location_outcome.location_group
        part = legacy_body_part_for_location(body_location)
        armor_coverage = resolve_armor_coverage(defender, body_location, self.rng, self.armor_coverage_catalog)
        armor_layers = tuple(layer.item_id for layer in armor_coverage.covering_layers)
        armor_coverage_indicator = armor_coverage.total_coverage_indicator
        physical_outcome, wound_outcome = resolve_attack_physical_damage(
            action_id=action.action_id,
            attacker=attacker,
            defender=defender,
            weapon=weapon,
            weapon_profile=attack_profile,
            attack_type=attack_type,
            hit_quality=hit_quality,
            body_location=body_location,
            body_location_group=body_location_group,
            armor_coverage=armor_coverage,
            style_damage=attacker_style.damage_modifier,
            profession_damage=attacker_profession.damage,
        )
        effective = physical_outcome.final_damage
        first_layer = armor_coverage.covering_layers[0] if armor_coverage.covering_layers else None
        armor_name = first_layer.armor_category.replace("_", " ") if first_layer is not None else None
        armor_layer = first_layer.profile_id if first_layer is not None else None
        if armor_coverage.covering_layers:
            if effective <= 0:
                contact = "absorption"
            elif physical_outcome.penetration_margin > 0:
                contact = "penetration"
            elif physical_outcome.remaining_impact > physical_outcome.remaining_cutting:
                contact = "deflection"
            else:
                contact = "glancing"
        else:
            contact = "none"
        if weapon and self.rng.random() < self.rules.weapon_degrade_chance:
            weapon.durability = max(0.0, weapon.durability - 0.5)
        if effective <= 0:
            armor_result = "armor" if armor_coverage.covering_layers else "glancing"
            armor_reason = "ARMOR" if armor_coverage.covering_layers else "GLANCING"
            event = self._build_event(
                attacker,
                defender,
                action_id=action.action_id,
                weapon=weapon,
                weapon_skill=weapon_skill,
                technique=self._technique_for(attacker_style.name, weapon),
                result=armor_result,
                defense="armor" if armor_coverage.covering_layers else "none",
                hit_location=body_location.value,
                body_location=body_location.value,
                body_location_group=body_location_group.value,
                hit_quality=hit_quality.value,
                armor_name=armor_name,
                armor_layer=armor_layer,
                armor_contact=contact,
                armor_layers=armor_layers,
                armor_coverage_indicator=armor_coverage_indicator,
                raw_force=int(round(physical_outcome.weapon_damage_profile.base_damage)),
                reduced_force=effective,
                attacker_style=attacker_style,
                defender_style=defender_style,
                hit_score=hit_score,
                dodge_score=dodge_score,
                action_type=action.action_type.value,
                parent_action_id=action.parent_action_id,
                reaction_id=action.reaction_id,
                reaction_type=action.technique_id,
                reaction_depth=action.reaction_depth,
            )
            message = self.narrator.render(event, "attacker")
            observer_message = self.narrator.render(event, "observer")
            defender_message = self.narrator.render(event, "defender")
            outcome = CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.HIT,
                hit=True,
                defense_result=defense_outcome.resolution,
                defense_outcome=defense_outcome,
                damage=effective,
                hit_location=body_location.value,
                legacy_body_part=part,
                body_location=body_location,
                body_location_group=body_location_group,
                hit_quality=hit_quality,
                armor_layers=armor_layers,
                armor_coverage_indicator=armor_coverage_indicator,
                armor_coverage_outcome=armor_coverage,
                physical_outcome=physical_outcome,
                wound_outcome=wound_outcome,
                target_defeated=False,
                combat_ended=False,
                reason_code=armor_reason,
            )
            return self._attach_reaction_discovery(
                CombatResult(
                    True,
                    message,
                    body_part=part,
                    body_location=body_location.value,
                    body_location_group=body_location_group.value,
                    hit_quality=hit_quality.value,
                    effective_damage=effective,
                    observer_message=observer_message,
                    style_used=attacker_style.name,
                    attack_score=hit_score,
                    defense_score=dodge_score,
                    tactical_note=event.intent,
                    combat_event=event,
                    defender_message=defender_message,
                    combat_action=action,
                    combat_outcome=outcome,
                    armor_coverage_outcome=armor_coverage,
                    physical_outcome=physical_outcome,
                    wound_outcome=wound_outcome,
                    armor_layers=armor_layers,
                ),
                action,
                attacker,
                defender,
            )

        wound_gain = wound_outcome.wound_level
        if wound_gain > 0:
            defender.wounds[part] = min(self.rules.max_wound_level, defender.wounds.get(part, 0) + wound_gain)
        attacker.skills.train(weapon_skill, self.rules.attack_skill_train_amount)
        dead = is_dead(defender.wounds)
        if dead:
            defender.die()
        else:
            defender.sync_state_from_flags()
        result_kind = "critical" if wound_gain >= 3 or physical_outcome.severity in {WoundSeverity.SEVERE, WoundSeverity.CRITICAL} else "hit"
        event = self._build_event(
            attacker,
            defender,
            action_id=action.action_id,
            weapon=weapon,
            weapon_skill=weapon_skill,
            technique=self._technique_for(attacker_style.name, weapon),
            result="defeated" if dead else result_kind,
            defense="none",
            hit_location=body_location.value,
            body_location=body_location.value,
            body_location_group=body_location_group.value,
            hit_quality=hit_quality.value,
            armor_name=armor_name,
            armor_layer=armor_layer,
            armor_contact=contact,
            armor_layers=armor_layers,
            armor_coverage_indicator=armor_coverage_indicator,
            raw_force=int(round(physical_outcome.weapon_damage_profile.base_damage)),
            reduced_force=effective,
            wound_level=defender.wounds[part],
            attacker_style=attacker_style,
            defender_style=defender_style,
            hit_score=hit_score,
            dodge_score=dodge_score,
            dead=dead,
            action_type=action.action_type.value,
            parent_action_id=action.parent_action_id,
            reaction_id=action.reaction_id,
            reaction_type=action.technique_id,
            reaction_depth=action.reaction_depth,
        )
        msg = self.narrator.render(event, "attacker")
        observer_message = self.narrator.render(event, "observer")
        defender_message = self.narrator.render(event, "defender")
        if dead:
            msg += f"\n<red>{defender.username} osuwa się bez życia.</red>"
        outcome = CombatOutcome(
            action_id=action.action_id,
            actor_id=action.actor_id,
            target_id=action.target_id,
            result_type=CombatOutcomeType.TARGET_DEFEATED if dead else CombatOutcomeType.HIT,
            hit=True,
            defense_result=defense_outcome.resolution,
            defense_outcome=defense_outcome,
            damage=effective,
            hit_location=body_location.value,
            legacy_body_part=part,
            body_location=body_location,
            body_location_group=body_location_group,
            hit_quality=hit_quality,
            armor_layers=armor_layers,
            armor_coverage_indicator=armor_coverage_indicator,
            armor_coverage_outcome=armor_coverage,
            physical_outcome=physical_outcome,
            wound_outcome=wound_outcome,
            target_defeated=dead,
            combat_ended=dead,
            reason_code="TARGET_DEFEATED" if dead else "HIT",
        )
        return self._attach_reaction_discovery(
            CombatResult(
                True,
                msg,
                dead,
                body_part=part,
                body_location=body_location.value,
                body_location_group=body_location_group.value,
                hit_quality=hit_quality.value,
                effective_damage=effective,
                observer_message=observer_message,
                style_used=attacker_style.name,
                attack_score=hit_score,
                defense_score=dodge_score,
                tactical_note=event.intent,
                combat_event=event,
                defender_message=defender_message,
                combat_action=action,
                combat_outcome=outcome,
                armor_coverage_outcome=armor_coverage,
                physical_outcome=physical_outcome,
                wound_outcome=wound_outcome,
                armor_layers=armor_layers,
            ),
            action,
            attacker,
            defender,
        )

    def _active_defense(self, attacker: Character, defender: Character, action: CombatAction, hit_score: int, dodge_score: int, defense_outcome: DefenseOutcome) -> CombatResult | None:
        if not defense_outcome.successful_defense:
            return None
        if defense_outcome.resolution == DefenseResolution.DODGED:
            defender.skills.train("uniki", self.rules.dodge_skill_train_amount)
            event = self._build_event(
                attacker,
                defender,
                action_id=action.action_id,
                weapon=None,
                technique=self._technique_for(attacker.combat_style, attacker.weapon()),
                result="dodge",
                defense="dodge",
                hit_score=hit_score,
                dodge_score=dodge_score,
                attacker_style=self.rules.style(attacker.combat_style),
                defender_style=self.rules.style(defender.combat_style),
                action_type=action.action_type.value,
                parent_action_id=action.parent_action_id,
                reaction_id=action.reaction_id,
                reaction_type=action.technique_id,
                reaction_depth=action.reaction_depth,
            )
            message = self.narrator.render(event, "attacker")
            observer_message = self.narrator.render(event, "observer")
            defender_message = self.narrator.render(event, "defender")
            outcome = CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.DEFENDED,
                hit=False,
                defense_result=DefenseResolution.DODGED,
                defense_outcome=defense_outcome,
                damage=0,
                target_defeated=False,
                combat_ended=False,
                reason_code="DODGED",
            )
            return self._attach_reaction_discovery(
                CombatResult(False, message, defended_by="dodge", observer_message=observer_message, combat_event=event, defender_message=defender_message, combat_action=action, combat_outcome=outcome),
                action,
                attacker,
                defender,
            )

        if defense_outcome.resolution == DefenseResolution.BLOCKED:
            shield = defender.shield()
            if shield is not None and shield.durability > 0 and self.rng.random() < self.rules.active_defense_degrade_chance:
                shield.durability = max(0.0, shield.durability - 0.5)
            defender.skills.train("parowanie", self.rules.dodge_skill_train_amount)
            event = self._build_event(
                attacker,
                defender,
                action_id=action.action_id,
                result="block",
                defense="block",
                weapon=shield,
                technique="zasłona tarczą",
                intent="obrona",
                action_type=action.action_type.value,
                parent_action_id=action.parent_action_id,
                reaction_id=action.reaction_id,
                reaction_type=action.technique_id,
                reaction_depth=action.reaction_depth,
            )
            message = self.narrator.render(event, "attacker")
            observer_message = self.narrator.render(event, "observer")
            defender_message = self.narrator.render(event, "defender")
            outcome = CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.DEFENDED,
                hit=False,
                defense_result=DefenseResolution.BLOCKED,
                defense_outcome=defense_outcome,
                damage=0,
                target_defeated=False,
                combat_ended=False,
                reason_code="DEFENDED",
            )
            return self._attach_reaction_discovery(
                CombatResult(False, message, defended_by="shield", observer_message=observer_message, combat_event=event, defender_message=defender_message, combat_action=action, combat_outcome=outcome),
                action,
                attacker,
                defender,
            )

        if defense_outcome.resolution == DefenseResolution.PARRIED:
            weapon = defender.weapon()
            if weapon is not None and weapon.durability > 0 and self.rng.random() < self.rules.active_defense_degrade_chance:
                weapon.durability = max(0.0, weapon.durability - 0.5)
            defender.skills.train("parowanie", self.rules.parry_skill_train_amount)
            event = self._build_event(
                attacker,
                defender,
                action_id=action.action_id,
                result="parry",
                defense="parry",
                weapon=weapon,
                technique="zbicie ciosu",
                intent="obrona",
                action_type=action.action_type.value,
                parent_action_id=action.parent_action_id,
                reaction_id=action.reaction_id,
                reaction_type=action.technique_id,
                reaction_depth=action.reaction_depth,
            )
            message = self.narrator.render(event, "attacker")
            observer_message = self.narrator.render(event, "observer")
            defender_message = self.narrator.render(event, "defender")
            outcome = CombatOutcome(
                action_id=action.action_id,
                actor_id=action.actor_id,
                target_id=action.target_id,
                result_type=CombatOutcomeType.DEFENDED,
                hit=False,
                defense_result=DefenseResolution.PARRIED,
                defense_outcome=defense_outcome,
                damage=0,
                target_defeated=False,
                combat_ended=False,
                reason_code="DEFENDED",
            )
            return self._attach_reaction_discovery(
                CombatResult(False, message, defended_by="parry", observer_message=observer_message, combat_event=event, defender_message=defender_message, combat_action=action, combat_outcome=outcome),
                action,
                attacker,
                defender,
            )
        return None

    def _attach_reaction_discovery(
        self,
        result: CombatResult,
        action: CombatAction,
        attacker: Character | None,
        defender: Character | None,
    ) -> CombatResult:
        if result.combat_outcome is None or attacker is None or defender is None:
            return result
        if action.reaction_depth >= REACTION_POLICY.max_reaction_depth:
            return result
        reactor_profile = build_reaction_user_profile(defender)
        opponent_profile = build_reaction_user_profile(attacker)
        discovery = find_available_reactions(
            ReactionTriggerContext(
                source_action=action,
                source_outcome=result.combat_outcome,
                reactor_profile=reactor_profile,
                opponent_profile=opponent_profile,
                reaction_depth=action.reaction_depth,
            ),
            self.reaction_catalog,
        )
        result.reaction_discovery = discovery
        if discovery.available_reactions:
            execution = self._execute_automatic_reaction(discovery, action, attacker, defender, result.combat_outcome)
            result.reaction_execution = execution
            if execution.executed and execution.reaction_result is not None:
                self._append_reaction_result(result, execution.reaction_result)
        return result

    def _execute_automatic_reaction(
        self,
        discovery: CombatReactionDiscovery,
        source_action: CombatAction,
        attacker: Character,
        defender: Character,
        source_outcome: CombatOutcome,
    ) -> ReactionExecutionResult:
        def _resolve(reaction_action: CombatAction, reactor_character: Character | None, target_character: Character | None) -> object:
            if reactor_character is None or target_character is None:
                return None
            return self.attack(reactor_character, target_character, action=reaction_action)

        executor = CombatReactionExecutor(self.reaction_catalog)
        return executor.execute_reaction(
            discovery,
            source_action,
            source_outcome,
            defender,
            attacker,
            _resolve,
        )

    def _append_reaction_result(self, primary: CombatResult, reaction_result: CombatResult) -> None:
        if reaction_result.message:
            primary.message = f"{primary.message}\n{reaction_result.message}" if primary.message else reaction_result.message
        if reaction_result.observer_message:
            primary.observer_message = (
                f"{primary.observer_message}\n{reaction_result.observer_message}"
                if primary.observer_message
                else reaction_result.observer_message
            )
        if reaction_result.defender_message:
            primary.defender_message = (
                f"{primary.defender_message}\n{reaction_result.defender_message}"
                if primary.defender_message
                else reaction_result.defender_message
            )

    def _weapon_skill_name(self, weapon: Item | None) -> str:
        return skill_for_weapon(weapon)

    def _attack_stamina_cost(self, weapon_reach: int, style: CombatStyle) -> int:
        return self.rules.attack_stamina_cost(weapon_reach, style)

    def _contextual_body_part_weights(self, attacker: Character, defender: Character, weapon: Item | None) -> tuple[tuple[str, int], ...]:
        weights = dict(self.rules.body_part_weights)
        reach = weapon.reach if weapon is not None and weapon.durability > 0 else 1
        if reach >= 2:
            weights["glowa"] = max(4, weights.get("glowa", 0) - 2)
            weights["prawa_noga"] = weights.get("prawa_noga", 0) + 2
            weights["lewa_noga"] = weights.get("lewa_noga", 0) + 2
        if normalize_weapon_family(weapon) in {"luki", "kusze"}:
            weights["glowa"] += 2
            weights["korpus"] += 1
        if defender.shield() is not None:
            weights["lewa_reka"] = max(4, weights.get("lewa_reka", 0) - 3)
            weights["korpus"] += 2
        if defender.stats.wytrzymalosc >= attacker.stats.wytrzymalosc:
            weights["korpus"] += 1
        return tuple((part, max(1, value)) for part, value in weights.items())

    def _technique_for(self, style_name: str, weapon: Item | None) -> str:
        family = normalize_weapon_family(weapon)
        if family == "luki":
            return "mierzony strzał"
        if family == "kusze":
            return "krótki strzał"
        if family == "wlocznie":
            return "krótki wyrzut włóczni"
        if family == "bron_drzewcowa":
            return "szeroki zamach drzewcem"
        if family == "topory":
            return "ciężki zamach"
        if family == "mloty":
            return "mocny cios z bliska"
        if family == "sztylety":
            return "szybkie pchnięcie"
        if family == "miecze":
            if style_name == "brutalny":
                return "gwałtowne cięcie"
            if style_name == "ofensywny":
                return "szybkie cięcie"
            return "precyzyjne pchnięcie"
        if family == "bez_broni":
            return "cios gołą ręką"
        return "atak"

    def _wound_gain(self, effective: int, weapon: Item | None, style_name: str) -> int:
        family = normalize_weapon_family(weapon)
        base = 1
        if effective >= 16:
            base = 3
        elif effective >= 10:
            base = 2
        elif effective >= 4:
            base = 1
        if family in {"mloty", "bron_drzewcowa"}:
            base = min(self.rules.max_wound_level, base + 1)
        if style_name == "brutalny":
            base = min(self.rules.max_wound_level, base + 1)
        return max(1, min(self.rules.max_wound_level, base))

    def _build_event(
        self,
        attacker: Character,
        defender: Character,
        *,
        action_id: str | None = None,
        weapon: Item | None = None,
        weapon_skill: str | None = None,
        technique: str = "",
        result: str = "miss",
        defense: str = "none",
        hit_location: str | None = None,
        body_location: str | None = None,
        body_location_group: str | None = None,
        hit_quality: str | None = None,
        armor: Item | None = None,
        armor_name: str | None = None,
        armor_layer: str | None = None,
        armor_contact: str | None = None,
        armor_layers: tuple[str, ...] = (),
        armor_coverage_indicator: float = 0.0,
        raw_force: int = 0,
        reduced_force: int = 0,
        wound_level: int = 0,
        attacker_style: CombatStyle | None = None,
        defender_style: CombatStyle | None = None,
        hit_score: int = 0,
        dodge_score: int = 0,
        dead: bool = False,
        intent: str | None = None,
        action_type: str = CombatActionType.BASIC_ATTACK.value,
        parent_action_id: str | None = None,
        reaction_id: str | None = None,
        reaction_type: str | None = None,
        reaction_depth: int = 0,
    ) -> CombatEvent:
        family = normalize_weapon_family(weapon)
        return CombatEvent(
            action_id=action_id,
            action_type=action_type,
            attacker_id=attacker.username,
            attacker_name=attacker.username,
            defender_id=defender.username,
            defender_name=defender.username,
            parent_action_id=parent_action_id,
            reaction_id=reaction_id,
            reaction_type=reaction_type,
            reaction_depth=reaction_depth,
            weapon_name=weapon.display_name() if weapon is not None else None,
            weapon_family=family,
            hand="main" if weapon is not None and attacker.weapon() is weapon else None,
            technique=technique or self._technique_for(attacker.combat_style, weapon),
            intent=intent or ("atak" if result not in {"block", "parry"} else "obrona"),
            result=result,
            defense=defense,
            hit_location=hit_location,
            body_location=body_location,
            body_location_group=body_location_group,
            hit_quality=hit_quality,
            body_side=self._body_side_for(hit_location),
            damage_type=weapon.damage_type if weapon is not None else "obuchowa",
            raw_force=raw_force,
            reduced_force=reduced_force,
            armor_name=armor_name if armor_name is not None else (armor.display_name() if armor is not None else None),
            armor_contact=armor_contact,
            armor_layer=armor_layer if armor_layer is not None else (armor.slot if armor is not None else None),
            armor_layers=armor_layers,
            armor_coverage_indicator=armor_coverage_indicator,
            wound_level=wound_level,
            special_effects=self._special_effects_for(result, wound_level, dead),
            attacker_state=attacker.state,
            defender_state=defender.state,
            environment=(),
            narrative_tags=(attacker_style.name if attacker_style is not None else "", defender_style.name if defender_style is not None else "", weapon_skill or ""),
            outcome_notes=(f"hit:{hit_score}", f"defense:{dodge_score}") if hit_score or dodge_score else (),
        )

    def _special_effects_for(self, result: str, wound_level: int, dead: bool) -> tuple[str, ...]:
        effects: list[str] = []
        if result == "parry":
            effects.append("deflection")
        if result == "block":
            effects.append("shield_stop")
        if result == "armor":
            effects.append("armor_absorption")
        if wound_level >= 3:
            effects.append("stagger")
        if dead:
            effects.append("fatal")
        return tuple(effects)

    def _body_side_for(self, body_part: str | None) -> str | None:
        try:
            location = BodyLocation(str(body_part))
        except ValueError:
            location = None
        if location in {
            BodyLocation.RIGHT_SHOULDER,
            BodyLocation.RIGHT_ARM,
            BodyLocation.RIGHT_HAND,
            BodyLocation.RIGHT_THIGH,
            BodyLocation.RIGHT_LEG,
            BodyLocation.RIGHT_FOOT,
        } or body_part in {"prawa_reka", "prawa_noga"}:
            return "right"
        if location in {
            BodyLocation.LEFT_SHOULDER,
            BodyLocation.LEFT_ARM,
            BodyLocation.LEFT_HAND,
            BodyLocation.LEFT_THIGH,
            BodyLocation.LEFT_LEG,
            BodyLocation.LEFT_FOOT,
        } or body_part in {"lewa_reka", "lewa_noga"}:
            return "left"
        return None

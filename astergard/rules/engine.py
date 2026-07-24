from __future__ import annotations

from dataclasses import dataclass, field

from astergard.rules.combat import CombatRules, default_combat_rules
from astergard.rules.economy import EconomyRules, default_economy_rules
from astergard.rules.movement import MovementRules, SearchRules, default_movement_rules, default_search_rules
from astergard.rules.reputation import ReputationRules, default_reputation_rules
from astergard.rules.respawn import RespawnRules, default_respawn_rules
from astergard.rules.skills import SkillRules, default_skill_rules


@dataclass(slots=True)
class RuleSet:
    combat: CombatRules = field(default_factory=default_combat_rules)
    economy: EconomyRules = field(default_factory=default_economy_rules)
    movement: MovementRules = field(default_factory=default_movement_rules)
    search: SearchRules = field(default_factory=default_search_rules)
    reputation: ReputationRules = field(default_factory=default_reputation_rules)
    respawn: RespawnRules = field(default_factory=default_respawn_rules)
    skills: SkillRules = field(default_factory=default_skill_rules)


def default_ruleset() -> RuleSet:
    return RuleSet()

from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from statistics import mean
from typing import Callable

from astergard.characters.professions import all_profession_definitions, resolve_profession
from astergard.characters.models import Character, CharacterStats
from astergard.combat.manager import COMBAT_STYLES, CombatManager
from astergard.items.models import Item
from astergard.npcs.models import NPCFactory
from astergard.npcs.threat import THREAT_PROFILES

CharacterFactory = Callable[[], Character]


@dataclass(frozen=True, slots=True)
class CombatScenario:
    name: str
    attacker_factory: CharacterFactory
    defender_factory: CharacterFactory
    iterations: int = 1000
    max_rounds: int = 80
    seed: int = 12345


@dataclass(frozen=True, slots=True)
class CombatSimulationSummary:
    scenario: str
    iterations: int
    attacker_win_rate: float
    defender_win_rate: float
    draw_rate: float
    average_rounds: float
    average_attacker_stamina: float
    average_defender_stamina: float

    def to_markdown_row(self) -> str:
        return (
            f"| {self.scenario} | {self.iterations} | "
            f"{self.attacker_win_rate:.1%} | {self.defender_win_rate:.1%} | {self.draw_rate:.1%} | "
            f"{self.average_rounds:.1f} | {self.average_attacker_stamina:.1f} | {self.average_defender_stamina:.1f} |"
        )


@dataclass(frozen=True, slots=True)
class CombatSimulationRun:
    winner: str
    rounds: int
    attacker_stamina: int
    defender_stamina: int


class CombatBalanceSimulator:
    def run(self, scenario: CombatScenario) -> CombatSimulationSummary:
        runs = [self._run_once(scenario, i) for i in range(scenario.iterations)]
        attacker_wins = sum(1 for run in runs if run.winner == "attacker")
        defender_wins = sum(1 for run in runs if run.winner == "defender")
        draws = scenario.iterations - attacker_wins - defender_wins
        return CombatSimulationSummary(
            scenario=scenario.name,
            iterations=scenario.iterations,
            attacker_win_rate=attacker_wins / scenario.iterations,
            defender_win_rate=defender_wins / scenario.iterations,
            draw_rate=draws / scenario.iterations,
            average_rounds=mean(run.rounds for run in runs),
            average_attacker_stamina=mean(run.attacker_stamina for run in runs),
            average_defender_stamina=mean(run.defender_stamina for run in runs),
        )

    def run_many(self, scenarios: list[CombatScenario]) -> list[CombatSimulationSummary]:
        return [self.run(scenario) for scenario in scenarios]

    def _run_once(self, scenario: CombatScenario, index: int) -> CombatSimulationRun:
        attacker = copy.deepcopy(scenario.attacker_factory())
        defender = copy.deepcopy(scenario.defender_factory())
        attacker.is_alive = True
        defender.is_alive = True
        attacker.in_combat = False
        defender.in_combat = False
        attacker.sync_state_from_flags()
        defender.sync_state_from_flags()
        attacker.room_id = 1
        defender.room_id = 1
        rng = random.Random(scenario.seed + index)
        manager = CombatManager(rng)
        rounds = 0
        while attacker.is_alive and defender.is_alive and rounds < scenario.max_rounds:
            rounds += 1
            manager.process_pair_round("attacker", attacker, "defender", defender)
        if attacker.is_alive and not defender.is_alive:
            winner = "attacker"
        elif defender.is_alive and not attacker.is_alive:
            winner = "defender"
        else:
            winner = "draw"
        return CombatSimulationRun(winner, rounds, attacker.stats.kondycja, defender.stats.kondycja)


def make_player_duelist(style: str = "zrownowazony") -> Character:
    c = Character("Gracz")
    c.stats = CharacterStats(sila=11, zrecznosc=11, wytrzymalosc=11, percepcja=10, sila_woli=10, kondycja=110)
    if style == "brutalny":
        c.stats.sila = 9
        c.stats.zrecznosc = 9
        c.stats.wytrzymalosc = 10
    c.combat_style = style
    c.formation = "front"
    c.equipment["prawa_reka"] = Item(
        "prosty miecz", "Miecz testowy.", 1.8, 25, "simple_sword", "weapon", "prawa_reka",
        damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1,
    )
    c.equipment["lewa_reka"] = Item(
        "drewniana tarcza", "Tarcza testowa.", 2.5, 15, "wooden_shield", "shield", "lewa_reka",
        protection=1, shield_block=3,
    )
    c.equipment["korpus"] = Item(
        "skórzana kurtka", "Pancerz testowy.", 3.0, 20, "leather_jacket", "armor", "korpus", protection=1,
    )
    return c


def make_profession_duelist(main_profession: str, secondary_profession: str | None = None, style: str | None = None) -> Character:
    combatant = make_player_duelist(style or "zrownowazony")
    combatant.main_profession = resolve_profession(main_profession, kind="main").key
    combatant.secondary_profession = ""
    if secondary_profession:
        combatant.secondary_profession = resolve_profession(secondary_profession, kind="additional").key
    combatant.name = combatant.main_profession
    profession_keys = [combatant.main_profession, combatant.secondary_profession or ""]
    for key in profession_keys:
        if not key:
            continue
        definition = resolve_profession(key)
        if definition.key == "berserker":
            combatant.stats.sila = max(9, combatant.stats.sila - 1)
            combatant.stats.zrecznosc = max(9, combatant.stats.zrecznosc - 1)
            combatant.stats.wytrzymalosc = max(9, combatant.stats.wytrzymalosc - 1)
        for skill, bonus in definition.skill_bonuses.items():
            combatant.skills.grant_starting_bonus(skill, bonus)
        for item in definition.inventory_items():
            combatant.inventory.append(item)
        for slot, item in definition.equipment_items().items():
            matched = next((candidate for candidate in combatant.inventory if candidate.vnum == item.vnum), None)
            equipped = matched if matched is not None else item
            if matched is not None:
                combatant.inventory.remove(matched)
            combatant.equipment[slot] = equipped
        if definition.combat_style:
            combatant.combat_style = definition.combat_style
    combatant.sync_state_from_flags()
    return combatant


def make_npc_character(vnum: str, style: str | None = None) -> Character:
    npc = NPCFactory().create(vnum, room_id=1)
    c = npc.character
    c.username = npc.name
    c.combat_style = style or c.combat_style
    if vnum == "mountain_troll":
        c.stats.sila = max(9, c.stats.sila - 2)
        c.stats.zrecznosc = max(8, c.stats.zrecznosc - 2)
        c.stats.wytrzymalosc = max(10, c.stats.wytrzymalosc - 1)
    return c



def _make_player_duelist_factory(style: str) -> CharacterFactory:
    def factory() -> Character:
        return make_player_duelist(style)

    return factory


def _make_profession_duelist_factory(main_profession: str, secondary_profession: str | None = None) -> CharacterFactory:
    def factory() -> Character:
        return make_profession_duelist(main_profession, secondary_profession)

    return factory

def default_balance_scenarios(iterations: int = 1000) -> list[CombatScenario]:
    scenarios: list[CombatScenario] = [
        CombatScenario(
            "player_balanced_vs_wolf",
            lambda: make_player_duelist("zrownowazony"),
            lambda: make_npc_character("wolf"),
            iterations=iterations,
            seed=1000,
        ),
        CombatScenario(
            "player_defensive_vs_troll",
            lambda: make_player_duelist("defensywny"),
            lambda: make_npc_character("mountain_troll"),
            iterations=iterations,
            seed=2000,
        ),
        CombatScenario(
            "player_offensive_vs_soldier",
            lambda: make_player_duelist("ofensywny"),
            lambda: make_npc_character("meekhan_soldier"),
            iterations=iterations,
            seed=3000,
        ),
    ]
    for style in COMBAT_STYLES:
        scenarios.append(
            CombatScenario(
                f"style_{style}_vs_balanced",
                _make_player_duelist_factory(style),
                lambda: make_player_duelist("zrownowazony"),
                iterations=iterations,
                seed=4000 + len(scenarios),
            )
        )
    return scenarios


def profession_balance_scenarios(iterations: int = 1000) -> list[CombatScenario]:
    scenarios: list[CombatScenario] = []
    for index, definition in enumerate(all_profession_definitions()):
        if definition.kind != "main":
            continue
        scenarios.append(
            CombatScenario(
                f"profession_{definition.key}_vs_balanced",
                _make_profession_duelist_factory(definition.key),
                lambda: make_player_duelist("zrownowazony"),
                iterations=iterations,
                seed=6000 + index,
            )
        )
    return scenarios


def threat_balance_scenarios(iterations: int = 1000) -> list[CombatScenario]:
    return [
        CombatScenario(
            "threat_trash_wolf_vs_player",
            lambda: make_npc_character("wolf"),
            lambda: make_player_duelist("zrownowazony"),
            iterations=iterations,
            seed=5100,
        ),
        CombatScenario(
            "threat_standard_soldier_vs_player",
            lambda: make_npc_character("meekhan_soldier"),
            lambda: make_player_duelist("zrownowazony"),
            iterations=iterations,
            seed=5200,
        ),
        CombatScenario(
            "threat_elite_troll_vs_player",
            lambda: make_npc_character("mountain_troll"),
            lambda: make_player_duelist("zrownowazony"),
            iterations=iterations,
            seed=5300,
        ),
        CombatScenario(
            "threat_boss_captain_vs_player",
            lambda: make_npc_character("warband_captain"),
            lambda: make_player_duelist("zrownowazony"),
            iterations=iterations,
            seed=5400,
        ),
    ]


def all_balance_scenarios(iterations: int = 1000) -> list[CombatScenario]:
    return default_balance_scenarios(iterations) + threat_balance_scenarios(iterations)


def render_balance_report(summaries: list[CombatSimulationSummary]) -> str:
    lines = [
        "# Combat Balance Report",
        "",
        "| Scenario | Iterations | Attacker win | Defender win | Draw | Avg rounds | Avg attacker stamina | Avg defender stamina |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    lines.extend(summary.to_markdown_row() for summary in summaries)
    lines.append("")
    lines.append("## Threat tiers")
    for key in ["trash", "standard", "elite", "boss"]:
        profile = THREAT_PROFILES[key]
        lines.append(f"- `{profile.tier}`: {profile.label}; stat {profile.stat_bonus:+d}, stamina {profile.stamina_bonus:+d}, damage {profile.damage_bonus:+d}, protection {profile.protection_bonus:+d}.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("- A scenario is suspicious when one side exceeds 85% wins unless it is intentionally asymmetric.")
    lines.append("- Draw rate above 20% means fights are too slow or insufficiently lethal.")
    lines.append("- Average rounds above 25 for ordinary encounters should trigger review.")
    return "\n".join(lines)

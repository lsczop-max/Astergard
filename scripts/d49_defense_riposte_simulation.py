from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astergard.combat.d49_simulation import (  # noqa: E402
    REFERENCE_ATTACKER,
    build_armor_probe_preset,
    build_riposte_toggle_preset,
    build_supported_builds,
    build_unsupported_builds,
    build_weapon_probe_preset,
    render_duel_summary,
    render_single_summary,
    simulate_duels,
    simulate_single_attacks,
    as_jsonable,
)


SINGLE_TRIALS = 1000
DUEL_TRIALS = 100
MAX_ROUNDS = 80
RIPOSTE_COMPARE_KEYS = ("C", "D", "F")


def stable_seed(*parts: str) -> int:
    seed = 0
    for part_index, part in enumerate(parts, start=1):
        for char_index, char in enumerate(part, start=1):
            seed = (seed * 131 + part_index * 17 + char_index * 31 + ord(char)) % 2_147_483_647
    return seed


def fmt_pct(value: float) -> str:
    return f"{value:.1%}"


def fmt_num(value: float) -> str:
    return f"{value:.2f}"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |"]
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def build_simulation_payload(single_trials: int, duel_trials: int, max_rounds: int) -> dict[str, Any]:
    supported = build_supported_builds()
    unsupported = build_unsupported_builds()

    single_results: dict[str, dict[str, Any]] = {}
    duel_results: dict[str, dict[str, dict[str, Any]]] = {}
    riposte_comparisons: dict[str, dict[str, Any]] = {}
    weapon_probes: dict[str, dict[str, Any]] = {}
    armor_probes: dict[str, dict[str, Any]] = {}

    for preset in supported:
        single_results[preset.key] = render_single_summary(preset, simulate_single_attacks(preset, single_trials, attacker_preset=REFERENCE_ATTACKER, seed_offset=0))

    for preset in supported:
        duel_results[preset.key] = {}
        for opponent in supported:
            duel_results[preset.key][opponent.key] = render_duel_summary(
                simulate_duels(
                    preset,
                    opponent,
                    duel_trials,
                    max_rounds=max_rounds,
                    seed_offset=stable_seed("duel", preset.key, opponent.key),
                )
            )

    for key in RIPOSTE_COMPARE_KEYS:
        base = next(preset for preset in supported if preset.key == key)
        with_riposte = simulate_duels(build_riposte_toggle_preset(base, known=True), build_riposte_toggle_preset(base, known=True), duel_trials, max_rounds=max_rounds, seed_offset=stable_seed("riposte", key, "with"))
        without_riposte = simulate_duels(build_riposte_toggle_preset(base, known=False), build_riposte_toggle_preset(base, known=False), duel_trials, max_rounds=max_rounds, seed_offset=stable_seed("riposte", key, "without"))
        riposte_comparisons[key] = {
            "with_riposte": render_duel_summary(with_riposte),
            "without_riposte": render_duel_summary(without_riposte),
        }

    for weapon_profile_id in (
        "garrison_short_sword",
        "court_sabre",
        "duelist_dagger",
        "battle_axe",
        "war_hammer",
        "war_mace",
        "watch_spear",
        "watch_halberd",
        "war_flail",
        "war_staff",
    ):
        probe = build_weapon_probe_preset(weapon_profile_id)
        weapon_probes[weapon_profile_id] = render_single_summary(
            probe,
            simulate_single_attacks(probe, single_trials, attacker_preset=REFERENCE_ATTACKER, seed_offset=stable_seed("weapon", weapon_profile_id)),
        )

    for armor_profile_id in ("unarmored", "light_armor", "medium_armor", "heavy_armor"):
        probe = build_armor_probe_preset(armor_profile_id)
        armor_probes[armor_profile_id] = render_single_summary(
            probe,
            simulate_single_attacks(probe, single_trials, attacker_preset=REFERENCE_ATTACKER, seed_offset=stable_seed("armor", armor_profile_id)),
        )

    return {
        "methodology": {
            "single_trials_per_configuration": single_trials,
            "duel_trials_per_configuration": duel_trials,
            "max_rounds": max_rounds,
            "seeding": "deterministic hash-derived offsets per configuration; each trial uses a dedicated seed",
            "pipeline": [
                "CombatManager",
                "CombatAction",
                "DefenseResolver",
                "CombatReactionExecutor",
                "system obrażeń",
                "system ran",
            ],
            "notes": [
                "No second resolver was introduced.",
                "The simulation uses the production combat pipeline and seeded RNG only.",
            ],
        },
        "supported_builds": [preset.key for preset in supported],
        "unsupported_builds": {preset.key: {"name": preset.name, "notes": preset.notes} for preset in unsupported},
        "single_results": single_results,
        "duel_results": duel_results,
        "riposte_comparisons": riposte_comparisons,
        "weapon_probes": weapon_probes,
        "armor_probes": armor_probes,
    }


def render_report(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# D49 Defense and Riposte Balance Simulation")
    lines.append("")
    lines.append("## Methodology")
    methodology = payload["methodology"]
    lines.append(f"- Single-action trials per configuration: {methodology['single_trials_per_configuration']}")
    lines.append(f"- Duel trials per ordered pair: {methodology['duel_trials_per_configuration']}")
    lines.append(f"- Max rounds per duel: {methodology['max_rounds']}")
    lines.append(f"- Seeding: {methodology['seeding']}")
    lines.append("")
    lines.append("## Configuration Set")
    lines.append("- Supported builds: " + ", ".join(payload["supported_builds"]))
    if payload["unsupported_builds"]:
        lines.append("- Unsupported builds: " + ", ".join(payload["unsupported_builds"].keys()))
    lines.append("")

    single_results = payload["single_results"]
    rows = []
    for key in sorted(single_results):
        summary = single_results[key]
        rows.append([
            key,
            fmt_pct(summary["accepted_rate"]),
            str(summary["defended"]),
            str(summary["misses"]),
            str(summary["hits"]),
            str(summary["riposte_executed"]),
            fmt_pct(summary["riposte_share_damage"]),
        ])
    lines.append("## Single Actions")
    lines.append(markdown_table(["Build", "Accepted", "Defended", "Misses", "Hits", "Ripostes", "Riposte dmg share"], rows))
    lines.append("")

    armor_rows = []
    for key in ("unarmored", "light_armor", "medium_armor", "heavy_armor"):
        summary = payload["armor_probes"][key]
        armor_rows.append([
            key,
            fmt_pct(summary["accepted_rate"]),
            fmt_pct(summary["candidate_effective_value_mean"]["DODGE"] / 100.0),
            fmt_pct(summary["candidate_effective_value_mean"]["SHIELD_BLOCK"] / 100.0),
            fmt_pct(summary["candidate_effective_value_mean"]["PARRY"] / 100.0),
        ])
    lines.append("## Armor Probe")
    lines.append(markdown_table(["Armor", "Accepted", "Dodge mean", "Block mean", "Parry mean"], armor_rows))
    lines.append("")

    weapon_rows = []
    for key in (
        "garrison_short_sword",
        "court_sabre",
        "duelist_dagger",
        "battle_axe",
        "war_hammer",
        "war_mace",
        "watch_spear",
        "watch_halberd",
        "war_flail",
        "war_staff",
    ):
        summary = payload["weapon_probes"][key]
        weapon_rows.append([
            key,
            fmt_pct(summary["accepted_rate"]),
            fmt_pct(summary["candidate_effective_value_mean"]["PARRY"] / 100.0),
            str(summary["riposte_executed"]),
            fmt_pct(summary["riposte_share_damage"]),
        ])
    lines.append("## Weapon Probe")
    lines.append(markdown_table(["Weapon", "Accepted", "Parry mean", "Ripostes", "Riposte dmg share"], weapon_rows))
    lines.append("")

    lines.append("## Duel Matrix")
    build_keys = list(single_results.keys())
    duel_rows = []
    for attacker in build_keys:
        row = [attacker]
        for defender in build_keys:
            summary = payload["duel_results"][attacker][defender]
            row.append(fmt_pct(summary["attacker_win_rate"]))
        duel_rows.append(row)
    lines.append(markdown_table(["Atk \\ Def", *build_keys], duel_rows))
    lines.append("")

    lines.append("## Riposte Comparison")
    for key, comparison in payload["riposte_comparisons"].items():
        with_riposte = comparison["with_riposte"]
        without_riposte = comparison["without_riposte"]
        lines.append(f"### {key}")
        lines.append(
            markdown_table(
                ["Mode", "Atk win", "Def win", "Avg rounds", "Riposte dmg share"],
                [
                    ["with", fmt_pct(with_riposte["attacker_win_rate"]), fmt_pct(with_riposte["defender_win_rate"]), fmt_num(with_riposte["average_rounds"]), fmt_pct(with_riposte["riposte_share_damage"])],
                    ["without", fmt_pct(without_riposte["attacker_win_rate"]), fmt_pct(without_riposte["defender_win_rate"]), fmt_num(without_riposte["average_rounds"]), fmt_pct(without_riposte["riposte_share_damage"])],
                ],
            )
        )
        lines.append("")

    lines.append("## Notes")
    lines.append("- The report is generated from the production combat pipeline only.")
    lines.append("- Unsupported dual-wield remains intentionally out of scope.")
    lines.append("- Any balance flags below are descriptive, not automatic tuning rules.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate D49 defense and riposte balance simulation.")
    parser.add_argument("--single-trials", type=int, default=SINGLE_TRIALS)
    parser.add_argument("--duel-trials", type=int, default=DUEL_TRIALS)
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    parser.add_argument("--markdown", type=Path, default=Path("docs/audits/D49_DEFENSE_RIPOSTE_SIMULATION.md"))
    parser.add_argument("--json", type=Path, default=Path("docs/audits/D49_DEFENSE_RIPOSTE_DATA.json"))
    args = parser.parse_args()

    payload = build_simulation_payload(args.single_trials, args.duel_trials, args.max_rounds)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(as_jsonable(payload), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    args.markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"Wrote {args.markdown}")
    print(f"Wrote {args.json}")


if __name__ == "__main__":
    main()

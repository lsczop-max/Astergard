from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from astergard.combat.d49_simulation import (
    REFERENCE_ATTACKER,
    as_jsonable,
    build_armor_probe_preset,
    build_riposte_toggle_preset,
    build_supported_builds,
    build_unsupported_builds,
    build_weapon_probe_preset,
    render_duel_summary,
    render_single_summary,
    simulate_duels,
    simulate_single_attacks,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_D49_PATH = ROOT / "docs" / "audits" / "D49_DEFENSE_RIPOSTE_DATA.json"

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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_d49_payload(path: Path | None = None) -> dict[str, Any]:
    return _load_json(path or DEFAULT_D49_PATH)


def build_current_payload(single_trials: int, duel_trials: int, max_rounds: int) -> dict[str, Any]:
    supported = build_supported_builds()
    unsupported = build_unsupported_builds()

    single_results: dict[str, dict[str, Any]] = {}
    duel_results: dict[str, dict[str, dict[str, Any]]] = {}
    riposte_comparisons: dict[str, dict[str, Any]] = {}
    weapon_probes: dict[str, dict[str, Any]] = {}
    armor_probes: dict[str, dict[str, Any]] = {}

    for preset in supported:
        single_results[preset.key] = render_single_summary(
            preset,
            simulate_single_attacks(
                preset,
                single_trials,
                attacker_preset=REFERENCE_ATTACKER,
                seed_offset=0,
            ),
        )

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
        with_riposte = simulate_duels(
            build_riposte_toggle_preset(base, known=True),
            build_riposte_toggle_preset(base, known=True),
            duel_trials,
            max_rounds=max_rounds,
            seed_offset=stable_seed("riposte", key, "with"),
        )
        without_riposte = simulate_duels(
            build_riposte_toggle_preset(base, known=False),
            build_riposte_toggle_preset(base, known=False),
            duel_trials,
            max_rounds=max_rounds,
            seed_offset=stable_seed("riposte", key, "without"),
        )
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
            simulate_single_attacks(
                probe,
                single_trials,
                attacker_preset=REFERENCE_ATTACKER,
                seed_offset=stable_seed("weapon", weapon_profile_id),
            ),
        )

    for armor_profile_id in ("unarmored", "light_armor", "medium_armor", "heavy_armor"):
        probe = build_armor_probe_preset(armor_profile_id)
        armor_probes[armor_profile_id] = render_single_summary(
            probe,
            simulate_single_attacks(
                probe,
                single_trials,
                attacker_preset=REFERENCE_ATTACKER,
                seed_offset=stable_seed("armor", armor_profile_id),
            ),
        )

    return {
        "meta": {
            "single_trials": single_trials,
            "duel_trials": duel_trials,
            "max_rounds": max_rounds,
            "single_action_configurations": len(single_results) + len(weapon_probes) + len(armor_probes),
            "single_action_total": single_trials * (len(single_results) + len(weapon_probes) + len(armor_probes)),
            "full_duel_configurations": len(supported) * len(supported) + len(RIPOSTE_COMPARE_KEYS) * 2,
            "full_duel_total": duel_trials * (len(supported) * len(supported) + len(RIPOSTE_COMPARE_KEYS) * 2),
            "supported_builds": [preset.key for preset in supported],
            "unsupported_builds": [preset.key for preset in unsupported],
        },
        "single_results": single_results,
        "duel_results": duel_results,
        "riposte_comparisons": riposte_comparisons,
        "weapon_probes": weapon_probes,
        "armor_probes": armor_probes,
    }


def _delta(current: float, baseline: float) -> float:
    return current - baseline


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _num(value: float) -> str:
    return f"{value:.2f}"


def _rows(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def _comparison_entry(current: dict[str, Any], baseline: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {
        key: {
            "current": current.get(key),
            "baseline": baseline.get(key),
            "delta": _delta(float(current.get(key, 0.0)), float(baseline.get(key, 0.0))),
        }
        for key in keys
    }


def compare_payloads(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    single_delta: dict[str, Any] = {}
    for key, current_summary in current["single_results"].items():
        baseline_summary = baseline["single_results"].get(key, {})
        single_delta[key] = {
            "accepted_rate": _comparison_entry(current_summary, baseline_summary, ("accepted_rate",))["accepted_rate"],
            "defended": _comparison_entry(current_summary, baseline_summary, ("defended",))["defended"],
            "hits": _comparison_entry(current_summary, baseline_summary, ("hits",))["hits"],
            "misses": _comparison_entry(current_summary, baseline_summary, ("misses",))["misses"],
            "riposte_share_damage": _comparison_entry(current_summary, baseline_summary, ("riposte_share_damage",))["riposte_share_damage"],
        }

    duel_delta: dict[str, Any] = {}
    for attacker, defenders in current["duel_results"].items():
        duel_delta[attacker] = {}
        for defender, current_summary in defenders.items():
            baseline_summary = baseline["duel_results"].get(attacker, {}).get(defender, {})
            duel_delta[attacker][defender] = {
                "attacker_win_rate": _comparison_entry(current_summary, baseline_summary, ("attacker_win_rate",))["attacker_win_rate"],
                "defender_win_rate": _comparison_entry(current_summary, baseline_summary, ("defender_win_rate",))["defender_win_rate"],
                "draw_rate": _comparison_entry(current_summary, baseline_summary, ("draw_rate",))["draw_rate"],
                "average_rounds": _comparison_entry(current_summary, baseline_summary, ("average_rounds",))["average_rounds"],
                "limit_exceeded": _comparison_entry(current_summary, baseline_summary, ("limit_exceeded",))["limit_exceeded"],
                "riposte_share_damage": _comparison_entry(current_summary, baseline_summary, ("riposte_share_damage",))["riposte_share_damage"],
            }

    riposte_delta: dict[str, Any] = {}
    for key, current_summary in current["riposte_comparisons"].items():
        baseline_summary = baseline.get("riposte_comparisons", {}).get(key, {})
        riposte_delta[key] = {
            mode: {
                "attacker_win_rate": _comparison_entry(current_summary[mode], baseline_summary.get(mode, {}), ("attacker_win_rate",))["attacker_win_rate"],
                "defender_win_rate": _comparison_entry(current_summary[mode], baseline_summary.get(mode, {}), ("defender_win_rate",))["defender_win_rate"],
                "average_rounds": _comparison_entry(current_summary[mode], baseline_summary.get(mode, {}), ("average_rounds",))["average_rounds"],
                "riposte_share_damage": _comparison_entry(current_summary[mode], baseline_summary.get(mode, {}), ("riposte_share_damage",))["riposte_share_damage"],
            }
            for mode in ("with_riposte", "without_riposte")
        }

    summary = summarize_results(current, baseline)
    return {
        "single_deltas": single_delta,
        "duel_deltas": duel_delta,
        "riposte_deltas": riposte_delta,
        "summary": summary,
    }


def summarize_results(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    supported = list(current["single_results"].keys())
    def _defended_keys(payload: dict[str, Any]) -> list[str]:
        return [key for key, summary in payload["single_results"].items() if summary["defended"] == summary["trials"]]

    self_duel_keys = ("B", "C", "D", "F")
    current_limit_exceeded = sum(1 for attacker in supported for defender in supported if current["duel_results"][attacker][defender]["limit_exceeded"] > 0)
    baseline_limit_exceeded = sum(1 for attacker in supported for defender in supported if baseline["duel_results"][attacker][defender]["limit_exceeded"] > 0)
    current_draw_rate = mean(current["duel_results"][key][key]["draw_rate"] for key in self_duel_keys)
    baseline_draw_rate = mean(baseline["duel_results"][key][key]["draw_rate"] for key in self_duel_keys)
    current_self_duel_rounds = mean(current["duel_results"][key][key]["average_rounds"] for key in self_duel_keys)
    baseline_self_duel_rounds = mean(baseline["duel_results"][key][key]["average_rounds"] for key in self_duel_keys)
    current_riposte_rate = mean(current["riposte_comparisons"][key]["with_riposte"]["riposte_executed"] / max(1, current["riposte_comparisons"][key]["with_riposte"]["trials"]) for key in RIPOSTE_COMPARE_KEYS)
    baseline_riposte_rate = mean(baseline["riposte_comparisons"][key]["with_riposte"]["riposte_executed"] / max(1, baseline["riposte_comparisons"][key]["with_riposte"]["trials"]) for key in RIPOSTE_COMPARE_KEYS)
    return {
        "single_defended_all_builds_current": _defended_keys(current),
        "single_defended_all_builds_baseline": _defended_keys(baseline),
        "self_duel_draw_rate_current": current_draw_rate,
        "self_duel_draw_rate_baseline": baseline_draw_rate,
        "self_duel_average_rounds_current": current_self_duel_rounds,
        "self_duel_average_rounds_baseline": baseline_self_duel_rounds,
        "limit_exceeded_current": current_limit_exceeded,
        "limit_exceeded_baseline": baseline_limit_exceeded,
        "riposte_rate_current": current_riposte_rate,
        "riposte_rate_baseline": baseline_riposte_rate,
        "riposte_share_damage_current": mean(current["duel_results"][key][key]["riposte_share_damage"] for key in RIPOSTE_COMPARE_KEYS),
        "riposte_share_damage_baseline": mean(baseline["duel_results"][key][key]["riposte_share_damage"] for key in RIPOSTE_COMPARE_KEYS),
    }


def classify_problems(current: dict[str, Any], baseline: dict[str, Any]) -> list[dict[str, Any]]:
    problems: list[dict[str, Any]] = []
    for key, summary in current["single_results"].items():
        defended_rate = summary["defended"] / summary["trials"] if summary["trials"] else 0.0
        if defended_rate >= 0.999:
            problems.append({
                "priority": "HIGH",
                "build": key,
                "description": "Build zatrzymuje wszystkie pojedyncze ataki.",
            })
    for key in ("B", "C", "D", "F"):
        summary = current["duel_results"][key][key]
        limit_rate = summary["limit_exceeded"] / summary["trials"] if summary["trials"] else 0.0
        if summary["draw_rate"] >= 0.25 or limit_rate >= 0.10:
            problems.append({
                "priority": "HIGH",
                "build": key,
                "description": "Self-duel pozostaje nierozstrzygnięty lub osiąga limit rund.",
            })
    for key in ("A",):
        summary = current["duel_results"][key]["C"]
        if summary["attacker_win_rate"] <= 0.05:
            problems.append({
                "priority": "HIGH",
                "build": key,
                "description": "Podstawowy build nie przebija wyspecjalizowanej obrony.",
            })
    current_riposte_share = mean(current["duel_results"][key][key]["riposte_share_damage"] for key in RIPOSTE_COMPARE_KEYS)
    if current_riposte_share <= 0.0:
        problems.append({
            "priority": "MEDIUM",
            "build": "riposte",
            "description": "Riposta nadal nie wnosi obrażeń do badanego zestawu scenariuszy.",
        })
    return problems


def render_report(current: dict[str, Any], baseline: dict[str, Any], comparison: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# D50 Defense Probability Rebalance")
    lines.append("")
    lines.append("## Methodology")
    lines.append(f"- Single-action trials per configuration: {current['meta']['single_trials']}")
    lines.append(f"- Duel trials per ordered pair: {current['meta']['duel_trials']}")
    lines.append(f"- Max rounds per duel: {current['meta']['max_rounds']}")
    lines.append("- Seeding: deterministic hash-derived offsets per configuration")
    lines.append(f"- Baseline: {DEFAULT_D49_PATH}")
    lines.append("")
    lines.append("## D49 -> D50 Summary")
    summary = comparison["summary"]
    lines.append(f"- Self-duel draw rate: { _pct(summary['self_duel_draw_rate_baseline']) } -> { _pct(summary['self_duel_draw_rate_current']) }")
    lines.append(f"- Self-duel average rounds: { _num(summary['self_duel_average_rounds_baseline']) } -> { _num(summary['self_duel_average_rounds_current']) }")
    lines.append(f"- Riposte damage share: { _pct(summary['riposte_share_damage_baseline']) } -> { _pct(summary['riposte_share_damage_current']) }")
    lines.append(f"- Riposte execution rate: { _pct(summary['riposte_rate_baseline']) } -> { _pct(summary['riposte_rate_current']) }")
    lines.append(f"- Limit-exceeded duels: {summary['limit_exceeded_baseline']} -> {summary['limit_exceeded_current']}")
    lines.append("")

    rows = []
    for key in sorted(current["single_results"].keys()):
        cur = current["single_results"][key]
        base = baseline["single_results"][key]
        base_defended_rate = base["defended"] / base["trials"] if base["trials"] else 0.0
        cur_defended_rate = cur["defended"] / cur["trials"] if cur["trials"] else 0.0
        base_hit_rate = base["hits"] / base["trials"] if base["trials"] else 0.0
        cur_hit_rate = cur["hits"] / cur["trials"] if cur["trials"] else 0.0
        rows.append([
            key,
            _pct(base_defended_rate),
            _pct(cur_defended_rate),
            _pct(cur_defended_rate - base_defended_rate),
            _pct(base_hit_rate),
            _pct(cur_hit_rate),
            _pct(base["riposte_share_damage"]),
            _pct(cur["riposte_share_damage"]),
        ])
    lines.append("## Single Actions")
    lines.append(_rows(["Build", "D49 def.", "D50 def.", "Delta", "D49 hit.", "D50 hit.", "D49 riposte", "D50 riposte"], rows))
    lines.append("")

    duel_rows = []
    for build in sorted(current["duel_results"].keys()):
        cur = current["duel_results"][build][build]
        base = baseline["duel_results"][build][build]
        duel_rows.append([
            build,
            _pct(base["draw_rate"]),
            _pct(cur["draw_rate"]),
            _num(base["average_rounds"]),
            _num(cur["average_rounds"]),
            _pct(base["riposte_share_damage"]),
            _pct(cur["riposte_share_damage"]),
        ])
    lines.append("## Self Duels")
    lines.append(_rows(["Build", "D49 draw", "D50 draw", "D49 rounds", "D50 rounds", "D49 riposte", "D50 riposte"], duel_rows))
    lines.append("")

    riposte_rows = []
    for key in RIPOSTE_COMPARE_KEYS:
        cur = current["riposte_comparisons"][key]["with_riposte"]
        base = baseline["riposte_comparisons"][key]["with_riposte"]
        riposte_rows.append([
            key,
            _pct(base["attacker_win_rate"]),
            _pct(cur["attacker_win_rate"]),
            _pct(base["riposte_share_damage"]),
            _pct(cur["riposte_share_damage"]),
            _num(base["average_rounds"]),
            _num(cur["average_rounds"]),
        ])
    lines.append("## Riposte Comparison")
    lines.append(_rows(["Build", "D49 atk win", "D50 atk win", "D49 riposte", "D50 riposte", "D49 rounds", "D50 rounds"], riposte_rows))
    lines.append("")

    problem_rows = []
    for problem in comparison["problems"]:
        problem_rows.append([problem["priority"], problem["build"], problem["description"]])
    lines.append("## Problems")
    if problem_rows:
        lines.append(_rows(["Priority", "Build", "Description"], problem_rows))
    else:
        lines.append("No balance blockers detected.")
    lines.append("")

    lines.append("## Verdict")
    lines.append(f"- {comparison['verdict']}")
    return "\n".join(lines)


def build_report_payload(single_trials: int, duel_trials: int, max_rounds: int) -> dict[str, Any]:
    current = build_current_payload(single_trials, duel_trials, max_rounds)
    baseline = load_d49_payload()
    comparison = compare_payloads(current, baseline)
    problems = classify_problems(current, baseline)
    verdict = "DEFENSE_REBALANCE_ACCEPTABLE"
    if any(problem["priority"] == "HIGH" for problem in problems):
        verdict = "DEFENSE_REBALANCE_ITERATION_REQUIRED"
    comparison["problems"] = problems
    comparison["verdict"] = verdict
    return {
        "current": current,
        "baseline": baseline,
        "comparison": comparison,
        "meta": {
            "single_trials": single_trials,
            "duel_trials": duel_trials,
            "max_rounds": max_rounds,
            "verdict": verdict,
        },
    }


def write_outputs(payload: dict[str, Any], markdown_path: Path, json_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_report(payload["current"], payload["baseline"], payload["comparison"]), encoding="utf-8")
    json_path.write_text(json.dumps(as_jsonable(payload), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astergard.combat.balance import CombatBalanceSimulator, all_balance_scenarios, render_balance_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Astergard combat balance report.")
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("COMBAT_BALANCE_REPORT.md"))
    args = parser.parse_args()
    simulator = CombatBalanceSimulator()
    summaries = simulator.run_many(all_balance_scenarios(args.iterations))
    args.output.write_text(render_balance_report(summaries), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

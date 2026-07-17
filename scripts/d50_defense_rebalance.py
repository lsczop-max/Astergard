from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astergard.combat.d50_simulation import build_report_payload, write_outputs  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate D50 defense probability rebalance report.")
    parser.add_argument("--single-trials", type=int, default=1000)
    parser.add_argument("--duel-trials", type=int, default=100)
    parser.add_argument("--max-rounds", type=int, default=80)
    parser.add_argument("--markdown", type=Path, default=Path("docs/audits/D50_DEFENSE_REBALANCE_REPORT.md"))
    parser.add_argument("--json", type=Path, default=Path("docs/audits/D50_DEFENSE_REBALANCE_DATA.json"))
    args = parser.parse_args()

    payload = build_report_payload(args.single_trials, args.duel_trials, args.max_rounds)
    write_outputs(payload, args.markdown, args.json)
    print(f"Wrote {args.markdown}")
    print(f"Wrote {args.json}")
    print(f"Verdict: {payload['meta']['verdict']}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astergard.audits.world_description_audit import build_world_description_audit, write_world_description_audit_outputs  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate D58.1 world description audit.")
    parser.add_argument("--markdown", type=Path, default=Path("docs/audits/D58_1_WORLD_DESCRIPTION_AUDIT.md"))
    parser.add_argument("--json", type=Path, default=Path("docs/audits/D58_1_WORLD_DESCRIPTION_DATA.json"))
    parser.add_argument("--rewrite-order", type=Path, default=Path("docs/audits/D58_1_REWRITE_ORDER.md"))
    args = parser.parse_args()
    audit = build_world_description_audit()
    write_world_description_audit_outputs(audit, args.markdown, args.json, args.rewrite_order)
    print(f"Wrote {args.markdown}")
    print(f"Wrote {args.json}")
    print(f"Wrote {args.rewrite_order}")
    print(f"Verdict: {'WORLD_DESCRIPTION_AUDIT_READY' if audit.world_size == 500 else 'INCOMPLETE'}")


if __name__ == "__main__":
    main()

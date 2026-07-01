"""Run Stage 6 PIRL-Nav method smoke integration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.method import load_stage6_config, run_method_smoke  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "method" / "stage6_pirl_nav.yaml",
    )
    args = parser.parse_args()

    config = load_stage6_config(args.repo_root, args.config)
    summary = run_method_smoke(args.repo_root, config)
    print(f"wrote Stage 6 method smoke summary to {config.smoke_summary_path}")
    print(f"method configs: {summary['method_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

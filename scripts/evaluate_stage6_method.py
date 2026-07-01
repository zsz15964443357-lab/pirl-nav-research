"""Evaluate Stage 6 method skeleton through Stage 4/5 record semantics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.method import load_stage6_config, run_method_evaluation  # noqa: E402


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
    records, summary = run_method_evaluation(args.repo_root, config)
    print(
        f"wrote {len(records)} Stage 6 method records to "
        f"{config.validation_episode_records_path}"
    )
    print(f"wrote Stage 6 method summary to {config.validation_summary_path}")
    print(f"overall episodes: {summary['overall']['episodes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

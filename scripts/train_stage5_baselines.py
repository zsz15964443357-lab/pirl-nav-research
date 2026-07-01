"""Run Stage 5 dependency-light baseline smoke training."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.training import load_training_config, run_training_smoke  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "training" / "stage5_baselines.yaml",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run the dependency-light Stage 5 smoke trainer.",
    )
    args = parser.parse_args()

    if not args.smoke:
        parser.error("Stage 5 currently supports only --smoke; formal PPO training is later work.")

    config = load_training_config(args.repo_root, args.config)
    summary = run_training_smoke(args.repo_root, config)
    print(f"wrote Stage 5 smoke training summary to {config.training_summary_path}")
    print(f"baseline families: {summary['baseline_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

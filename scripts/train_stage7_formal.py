"""Run Stage 7 reduced formal training review run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.training import load_stage7_config, run_stage7_training  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "training" / "stage7_formal_training.yaml",
    )
    parser.add_argument("--reduced-review-run", action="store_true")
    args = parser.parse_args()

    if not args.reduced_review_run:
        parser.error("Stage 7 currently requires --reduced-review-run")
    config = load_stage7_config(args.repo_root, args.config)
    summary = run_stage7_training(
        args.repo_root,
        config,
        reduced_review_run=args.reduced_review_run,
    )
    print(f"wrote Stage 7 training metrics to {config.training_metrics_path}")
    print(f"training groups: {len(summary['groups'])}")
    print(f"training rows: {summary['total_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

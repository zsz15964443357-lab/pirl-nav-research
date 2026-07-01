"""Evaluate Stage 5 smoke baselines through Stage 4 record semantics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.training import load_training_config, run_stage5_evaluation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "training" / "stage5_baselines.yaml",
    )
    args = parser.parse_args()

    config = load_training_config(args.repo_root, args.config)
    records, summary = run_stage5_evaluation(args.repo_root, config)
    print(
        f"wrote {len(records)} Stage 5 validation episode records to "
        f"{config.validation_episode_records_path}"
    )
    print(f"wrote Stage 5 validation summary to {config.validation_summary_path}")
    print(f"overall episodes: {summary['overall']['episodes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

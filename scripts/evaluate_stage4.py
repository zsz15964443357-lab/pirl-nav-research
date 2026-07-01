"""Run Stage 4 random/scripted evaluation and write episode records plus summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.evaluation import load_evaluation_config, run_evaluation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "evaluation" / "stage4_random_scripted.yaml",
    )
    args = parser.parse_args()

    config = load_evaluation_config(args.repo_root, args.config)
    records, summary = run_evaluation(args.repo_root, config)
    print(f"wrote {len(records)} Stage 4 episode records to {config.episode_records_path}")
    print(f"wrote Stage 4 summary to {config.summary_path}")
    print(f"overall episodes: {summary['overall']['episodes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

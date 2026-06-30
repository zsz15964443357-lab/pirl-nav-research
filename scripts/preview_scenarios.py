"""Generate Stage 2 scenario visualization review artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.visualization import render_review_artifacts  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "experiments" / "manifests" / "candidate_stage1_2026-06-29.yaml",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=(
            REPO_ROOT
            / "experiments"
            / "review_artifacts"
            / "stage2"
            / "candidate_stage1_2026-06-29"
        ),
    )
    args = parser.parse_args()

    artifacts = render_review_artifacts(
        repo_root=args.repo_root,
        manifest_path=args.manifest,
        output_dir=args.output_dir,
    )
    print(f"generated {len(artifacts)} scenario review artifact sets in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

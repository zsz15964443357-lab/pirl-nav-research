"""Generate Stage 7 representative rollout visualizations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.training import load_stage7_config  # noqa: E402
from pirl_nav.visualization import (  # noqa: E402
    generate_rollout_visuals,
    generate_training_visuals,
    write_visual_index,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "training" / "stage7_formal_training.yaml",
    )
    args = parser.parse_args()

    config = load_stage7_config(args.repo_root, args.config)
    figures = generate_training_visuals(config) + generate_rollout_visuals(args.repo_root, config)
    write_visual_index(config.visual_index_path, figures)
    print(f"wrote {len(figures)} Stage 7 figures under {config.figures_dir}")
    print(f"wrote Stage 7 visual index to {config.visual_index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

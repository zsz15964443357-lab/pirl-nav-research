"""Run Stage 3 smoke rollouts on reviewed scenarios without training a policy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.sim import IntentRiskEnv  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "experiments" / "manifests" / "reviewed_stage2_2026-06-30.yaml",
    )
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument(
        "--mode",
        choices=("random", "scripted"),
        default="random",
        help="scripted uses a goal-seeking smoke policy; neither mode trains a policy.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )
    args = parser.parse_args()
    output = args.output or (
        args.repo_root
        / "experiments"
        / "review_artifacts"
        / "stage3"
        / f"rollout_{args.mode}_smoke_summary.json"
    )

    env = IntentRiskEnv(repo_root=args.repo_root, manifest_path=args.manifest)
    summaries = []
    for scenario_index, scenario in enumerate(env.scenarios):
        _, info = env.reset(seed=scenario.seed, scenario_index=scenario_index)
        terminated = False
        truncated = False
        for _ in range(args.steps):
            if args.mode == "scripted":
                action = env.scripted_goal_action()
            else:
                action = env.sample_random_action()
            _, _, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                break
        summaries.append(
            {
                "scenario_id": scenario.scenario_id,
                "family": scenario.family,
                "seed": scenario.seed,
                "mode": args.mode,
                "steps_executed": info["step_count"],
                "terminated": terminated,
                "truncated": truncated,
                "collision": info["collision"],
                "near_miss": info["near_miss"],
                "min_clearance": info["min_clearance"],
                "active_intents": info["active_intents"],
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(summaries)} Stage 3 smoke rollout summaries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

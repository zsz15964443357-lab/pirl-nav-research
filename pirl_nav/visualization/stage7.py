"""Stage 7 visualization artifact generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pirl_nav.sim import EnvConfig, IntentRiskEnv
from pirl_nav.training.experiment_tracker import read_jsonl
from pirl_nav.training.formal_trainer import PROFILE_BY_GROUP, _apply_review_shield, _policy_action
from pirl_nav.training.stage7_config import Stage7Config
from pirl_nav.visualization.stage7_svg import write_bar_chart, write_line_chart, write_rollout_svg


def generate_training_visuals(config: Stage7Config) -> list[dict[str, str]]:
    rows = read_jsonl(config.training_metrics_path)
    figures = []
    figures.append(
        _line_from_rows(
            rows,
            path=config.figures_dir / "learning_curves.svg",
            metric="reward",
            title="Stage 7 Reduced Formal Training Reward",
            y_label="reward",
        )
    )
    figures.append(
        _line_from_rows(
            rows,
            path=config.figures_dir / "risk_exposure_curves.svg",
            metric="risk_exposure",
            title="Stage 7 Risk Exposure Curves",
            y_label="risk exposure",
        )
    )
    figures.append(
        _line_from_rows(
            rows,
            path=config.figures_dir / "shield_intervention_curves.svg",
            metric="shield_intervention_rate",
            title="Stage 7 Shield Intervention Curves",
            y_label="shield rate",
        )
    )
    metric_values: dict[str, list[float]] = {}
    for row in rows:
        metric_values.setdefault(str(row["method_or_baseline"]), []).append(float(row["reward"]))
    write_bar_chart(
        config.figures_dir / "aggregate_metric_bars.svg",
        title="Stage 7 Aggregate Reward Bars",
        values={
            key: sum(values) / len(values)
            for key, values in metric_values.items()
        },
        y_label="mean reward",
    )
    figures.append(
        {
            "path": str(config.figures_dir / "aggregate_metric_bars.svg"),
            "what_it_shows": "Mean reduced formal training reward per method/group.",
            "how_to_interpret": "Use for review/debug only; higher is not a final paper claim.",
            "known_limitation": "Reduced deterministic review run, not full PPO training.",
        }
    )
    return figures


def generate_rollout_visuals(repo_root: Path, config: Stage7Config) -> list[dict[str, str]]:
    env = IntentRiskEnv(
        repo_root=repo_root,
        manifest_path=config.validation_manifest,
        config=EnvConfig(max_steps=config.max_steps_per_episode),
    )
    selected_groups = [
        group
        for group in config.training_groups
        if group.group_id in {"vanilla_ppo", "full_pirl_nav_skeleton"}
    ]
    figures = []
    for group in selected_groups:
        for run_mode in ("policy_only", "policy_plus_shield"):
            scenario_index = 0
            scenario = env.scenarios[scenario_index]
            spec = scenario.spec
            observation, _ = env.reset(seed=scenario.seed, scenario_index=scenario_index)
            profile = PROFILE_BY_GROUP[group.group_id]
            path_points = [tuple(spec["ego"]["start"])]
            shield_points: list[tuple[float, float]] = []
            for _ in range(config.max_steps_per_episode):
                action = _policy_action(observation, profile=profile, run_mode=run_mode)
                if run_mode == "policy_plus_shield":
                    action, shielded = _apply_review_shield(action, observation, profile=profile)
                else:
                    shielded = False
                observation, _, terminated, truncated, _ = env.step(action)
                current = (float(observation[0]), float(observation[1]))
                path_points.append(current)
                if shielded:
                    shield_points.append(current)
                if terminated or truncated:
                    break
            figure_path = (
                config.figures_dir
                / f"rollout_{scenario.scenario_id}_{group.group_id}_{run_mode}.svg"
            )
            write_rollout_svg(
                figure_path,
                title=f"{group.group_id} {run_mode} {scenario.scenario_id}",
                scenario=spec,
                ego_path=path_points,
                shield_points=shield_points,
            )
            figures.append(
                {
                    "path": str(figure_path),
                    "what_it_shows": (
                        f"Representative trajectory for {group.group_id} on "
                        f"{scenario.scenario_id} in {run_mode} mode."
                    ),
                    "how_to_interpret": (
                        "Inspect whether the path moves toward the goal and whether shield "
                        "points appear near latent-risk objects."
                    ),
                    "known_limitation": (
                        "Single representative rollout for review, not a full result."
                    ),
                }
            )
    return figures


def write_visual_index(path: Path, figures: list[dict[str, str]]) -> None:
    lines = ["# Stage 7 Visual Review Index", ""]
    for figure in figures:
        lines.extend(
            [
                f"## {Path(figure['path']).name}",
                "",
                f"- Figure path: `{figure['path']}`",
                f"- What it shows: {figure['what_it_shows']}",
                f"- How to interpret it: {figure['how_to_interpret']}",
                f"- Known limitation: {figure['known_limitation']}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _line_from_rows(
    rows: list[dict[str, Any]],
    *,
    path: Path,
    metric: str,
    title: str,
    y_label: str,
) -> dict[str, str]:
    by_group: dict[str, list[tuple[float, float]]] = {}
    for row in rows:
        by_group.setdefault(str(row["method_or_baseline"]), []).append(
            (float(row["timestep"]), float(row[metric]))
        )
    series = {
        key: _mean_by_timestep(points)
        for key, points in by_group.items()
    }
    write_line_chart(path, title=title, series=series, y_label=y_label)
    return {
        "path": str(path),
        "what_it_shows": f"{metric} over reduced formal training timesteps.",
        "how_to_interpret": "Trend inspection only; use to detect obvious instability.",
        "known_limitation": "Reduced deterministic review run, not final training curve.",
    }


def _mean_by_timestep(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    grouped: dict[float, list[float]] = {}
    for timestep, value in points:
        grouped.setdefault(timestep, []).append(value)
    return [
        (timestep, sum(values) / len(values))
        for timestep, values in sorted(grouped.items())
    ]

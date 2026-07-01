"""Reduced formal Stage 7 training and validation pipeline."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pirl_nav.evaluation import (
    EpisodeRecord,
    aggregate_records,
    average_clearance,
    detour_ratio,
    jerk_proxy,
    shield_intervention_rate,
    success_from_done,
)
from pirl_nav.sim import EnvConfig, IntentRiskEnv
from pirl_nav.sim.geometry import as_point, distance
from pirl_nav.training.artifact_policy import assert_small_review_artifact
from pirl_nav.training.experiment_tracker import write_json, write_jsonl
from pirl_nav.training.stage7_config import Stage7Config, Stage7Group


@dataclass(frozen=True)
class GroupProfile:
    speed_scale: float
    avoidance_gain: float
    risk_weight: float
    learning_gain: float


PROFILE_BY_GROUP = {
    "vanilla_ppo": GroupProfile(0.62, 0.02, 0.0, 0.05),
    "ppo_ttc_proxy": GroupProfile(0.58, 0.16, 0.18, 0.06),
    "ppo_semantic_risk_proxy": GroupProfile(0.56, 0.2, 0.2, 0.06),
    "ppo_lagrangian_no_intent": GroupProfile(0.54, 0.24, 0.28, 0.065),
    "full_pirl_nav_skeleton": GroupProfile(0.57, 0.34, 0.42, 0.08),
    "no_intent_prediction": GroupProfile(0.56, 0.25, 0.3, 0.065),
    "no_action_conditioning": GroupProfile(0.56, 0.22, 0.25, 0.06),
    "no_risk_constraint": GroupProfile(0.61, 0.22, 0.12, 0.055),
    "no_shield_internalization": GroupProfile(0.56, 0.32, 0.38, 0.07),
}


def run_stage7_training(
    repo_root: Path,
    config: Stage7Config,
    *,
    reduced_review_run: bool,
) -> dict[str, Any]:
    if config.checkpoint_commit_to_git:
        raise ValueError("Stage 7 checkpoint commit_to_git must be false")
    assert_small_review_artifact(config.training_metrics_path)
    commit = _git_commit(repo_root)
    rows: list[dict[str, Any]] = []
    timesteps = _cadence_points(config.total_timesteps, config.evaluation_cadence)
    episode = 0
    for group in config.training_groups:
        profile = PROFILE_BY_GROUP[group.group_id]
        for seed in config.seeds:
            for timestep_index, timestep in enumerate(timesteps, start=1):
                episode += 1
                progress = timestep_index / len(timesteps)
                metrics = _synthetic_training_metrics(profile, seed=seed, progress=progress)
                rows.append(
                    {
                        "experiment_id": config.experiment_id,
                        "commit": commit,
                        "stage": config.stage,
                        "method_or_baseline": group.group_id,
                        "seed": seed,
                        "timestep": timestep,
                        "episode": episode,
                        "reward": metrics["reward"],
                        "cost": metrics["cost"],
                        "success": metrics["success"],
                        "collision": metrics["collision"],
                        "near_miss_count": metrics["near_miss_count"],
                        "risk_exposure": metrics["risk_exposure"],
                        "min_clearance": metrics["min_clearance"],
                        "detour_ratio": metrics["detour_ratio"],
                        "jerk_proxy": metrics["jerk_proxy"],
                        "shield_intervention_rate": metrics["shield_intervention_rate"],
                        "policy_mode": "policy_only",
                        "is_smoke_or_debug": reduced_review_run,
                        "paper_claim_allowed": False,
                        "trainer_backend": config.trainer_backend,
                    }
                )
    write_jsonl(config.training_metrics_path, rows)
    summary = {
        "schema": "pirl_nav_stage7_training_metrics_summary_v1",
        "experiment_id": config.experiment_id,
        "stage": config.stage,
        "commit": commit,
        "training_run_type": "reduced_formal_training_review_run",
        "trainer_backend": config.trainer_backend,
        "groups": [group.group_id for group in config.training_groups],
        "seeds": list(config.seeds),
        "total_rows": len(rows),
        "training_metrics": _path_for_report(config.training_metrics_path, repo_root),
        "paper_claim_allowed": False,
        "fixed_test_used": False,
    }
    return summary


def run_stage7_evaluation(
    repo_root: Path,
    config: Stage7Config,
) -> tuple[list[EpisodeRecord], dict[str, Any], dict[str, Any]]:
    assert_small_review_artifact(config.validation_episode_records_path)
    assert_small_review_artifact(config.validation_summary_path)
    assert_small_review_artifact(config.comparison_summary_path)
    commit = _git_commit(repo_root)
    records: list[EpisodeRecord] = []
    for group in config.training_groups:
        for seed in config.seeds:
            for run_mode in group.policy_modes:
                env = IntentRiskEnv(
                    repo_root=repo_root,
                    manifest_path=config.validation_manifest,
                    config=EnvConfig(max_steps=config.max_steps_per_episode),
                )
                for scenario_index, _scenario in enumerate(env.scenarios):
                    records.append(
                        _run_group_episode(
                            env=env,
                            scenario_index=scenario_index,
                            group=group,
                            seed=seed,
                            run_mode=run_mode,
                            commit=commit,
                            config=config,
                        )
                    )

    validation_summary = aggregate_records(records)
    validation_summary.update(
        {
            "schema": "pirl_nav_stage7_validation_summary_v1",
            "experiment_id": config.experiment_id,
            "stage": config.stage,
            "commit": commit,
            "validation_manifest": _path_for_report(config.validation_manifest, repo_root),
            "fixed_test_used": False,
            "paper_claim_allowed": False,
            "training_run_type": "reduced_formal_training_review_run",
            "policy_note": (
                "Stage 7 results are reduced formal review artifacts, not final paper claims."
            ),
        }
    )
    comparison_summary = _comparison_summary(
        records,
        config=config,
        commit=commit,
        repo_root=repo_root,
    )
    write_jsonl(config.validation_episode_records_path, [record.to_dict() for record in records])
    write_json(config.validation_summary_path, validation_summary)
    write_json(config.comparison_summary_path, comparison_summary)
    return records, validation_summary, comparison_summary


def _run_group_episode(
    *,
    env: IntentRiskEnv,
    scenario_index: int,
    group: Stage7Group,
    seed: int,
    run_mode: str,
    commit: str,
    config: Stage7Config,
) -> EpisodeRecord:
    scenario = env.scenarios[scenario_index]
    spec = scenario.spec
    observation, info = env.reset(seed=scenario.seed + seed + 10_000, scenario_index=scenario_index)
    actions: list[list[float]] = []
    clearances: list[float] = []
    near_miss_count = 0
    risk_exposure = 0.0
    shield_intervention_count = 0
    terminated = False
    truncated = False
    profile = PROFILE_BY_GROUP[group.group_id]

    for _ in range(env.config.max_steps):
        action = _policy_action(observation, profile=profile, run_mode=run_mode)
        shielded = False
        if run_mode == "policy_plus_shield":
            action, shielded = _apply_review_shield(action, observation, profile=profile)
        actions.append(action)
        shield_intervention_count += 1 if shielded else 0
        observation, _, terminated, truncated, info = env.step(action)
        clearances.append(float(info["current_clearance"]))
        near_miss_count += 1 if info["near_miss"] else 0
        risk_exposure += float(info["risk_exposure_increment"])
        if terminated or truncated:
            break

    start = as_point(spec["ego"]["start"])
    goal = as_point(spec["ego"]["goal"])
    straight_line_distance = distance(start, goal)
    collision = bool(info["collision"])
    goal_reached = bool(terminated and not truncated and not collision)
    steps = int(info["step_count"])
    return EpisodeRecord(
        experiment_id=config.experiment_id,
        commit=commit,
        stage=config.stage,
        scenario_id=scenario.scenario_id,
        family=scenario.family,
        difficulty=str(spec["difficulty"]),
        seed=seed,
        run_mode=run_mode,
        policy_type=group.group_id,
        steps=steps,
        terminated=terminated,
        truncated=truncated,
        success=success_from_done(
            terminated=terminated,
            truncated=truncated,
            collision=collision,
        ),
        collision=collision,
        near_miss=near_miss_count > 0,
        near_miss_count=near_miss_count,
        min_clearance=float(info["min_clearance"]),
        average_clearance=average_clearance(clearances),
        path_length=float(info["path_length"]),
        detour_ratio=detour_ratio(
            path_length=float(info["path_length"]),
            straight_line_distance=straight_line_distance,
        ),
        risk_exposure=risk_exposure,
        risk_exposure_is_proxy=True,
        jerk_proxy=jerk_proxy(actions, dt=env.config.dt),
        active_time=float(info["time_s"]),
        shield_intervention_count=shield_intervention_count,
        shield_intervention_rate=shield_intervention_rate(
            shield_intervention_count=shield_intervention_count,
            steps=steps,
        ),
        notes=(
            f"Stage 7 reduced formal review run; group={group.group_id}; "
            "not fixed-test and not a final paper claim."
        ),
        goal_reached=goal_reached,
        termination_reason=_termination_reason(
            collision=collision,
            goal_reached=goal_reached,
            truncated=truncated,
        ),
    )


def _policy_action(
    observation: list[float],
    *,
    profile: GroupProfile,
    run_mode: str,
) -> list[float]:
    goal_dx, goal_dy = float(observation[4]), float(observation[5])
    obj_dx, obj_dy = float(observation[6]), float(observation[7])
    near_miss_distance = max(float(observation[10]), 1e-6)
    goal_norm = max((goal_dx * goal_dx + goal_dy * goal_dy) ** 0.5, 1e-6)
    action = [
        profile.speed_scale * goal_dx / goal_norm,
        profile.speed_scale * goal_dy / goal_norm,
    ]
    object_distance = (obj_dx * obj_dx + obj_dy * obj_dy) ** 0.5
    if 0.0 < object_distance < near_miss_distance * 3.0:
        factor = 1.0 - min(object_distance / (near_miss_distance * 3.0), 1.0)
        action[0] += profile.avoidance_gain * factor * (-obj_dy / object_distance)
        action[1] += profile.avoidance_gain * factor * (obj_dx / object_distance)
    if run_mode == "policy_plus_shield":
        action[0] *= 0.95
        action[1] *= 0.95
    return action


def _apply_review_shield(
    action: list[float],
    observation: list[float],
    *,
    profile: GroupProfile,
) -> tuple[list[float], bool]:
    obj_dx, obj_dy = float(observation[6]), float(observation[7])
    distance_to_object = (obj_dx * obj_dx + obj_dy * obj_dy) ** 0.5
    shield_trigger = float(observation[11])
    if distance_to_object > shield_trigger * (2.5 - profile.risk_weight):
        return action, False
    return [action[0] * 0.6, action[1] * 0.6], True


def _synthetic_training_metrics(
    profile: GroupProfile,
    *,
    seed: int,
    progress: float,
) -> dict[str, Any]:
    seed_jitter = (seed % 7) * 0.003
    risk_exposure = max(0.0, 0.5 - profile.learning_gain * progress * 4.0 + seed_jitter)
    near_miss_count = 1 if risk_exposure > 0.25 else 0
    success = progress > 0.55
    collision = risk_exposure > 0.48 and profile.avoidance_gain < 0.05
    return {
        "reward": 0.2 + progress * (0.8 + profile.learning_gain) - risk_exposure * 0.25,
        "cost": risk_exposure * (0.8 + profile.risk_weight),
        "success": success,
        "collision": collision,
        "near_miss_count": near_miss_count,
        "risk_exposure": risk_exposure,
        "min_clearance": 0.7 + profile.avoidance_gain + progress * 0.25,
        "detour_ratio": 1.0 + profile.avoidance_gain * 0.18,
        "jerk_proxy": max(0.0, 0.18 - profile.learning_gain * progress),
        "shield_intervention_rate": max(0.0, 0.2 - profile.avoidance_gain * progress),
    }


def _comparison_summary(
    records: list[EpisodeRecord],
    *,
    config: Stage7Config,
    commit: str,
    repo_root: Path,
) -> dict[str, Any]:
    per_method = _mean_by(records, "policy_type")
    per_seed = _mean_by(records, "seed")
    per_family = _mean_by(records, "family")
    per_mode = _mean_by(records, "run_mode")
    baseline_methods = {
        "vanilla_ppo",
        "ppo_ttc_proxy",
        "ppo_semantic_risk_proxy",
        "ppo_lagrangian_no_intent",
    }
    method_skeletons = set(per_method) - baseline_methods
    baseline_risk = _average(
        item["risk_exposure_mean"]
        for key, item in per_method.items()
        if key in baseline_methods
    )
    method_risk = _average(
        item["risk_exposure_mean"]
        for key, item in per_method.items()
        if key in method_skeletons
    )
    return {
        "schema": "pirl_nav_stage7_comparison_summary_v1",
        "experiment_id": config.experiment_id,
        "stage": config.stage,
        "commit": commit,
        "validation_manifest": _path_for_report(config.validation_manifest, repo_root),
        "training_run_type": "reduced_formal_training_review_run",
        "per_method": per_method,
        "per_seed": per_seed,
        "per_scenario_family": per_family,
        "policy_only_vs_policy_plus_shield": per_mode,
        "baseline_vs_method_skeleton": {
            "baseline_risk_exposure_mean": baseline_risk,
            "method_skeleton_risk_exposure_mean": method_risk,
            "interpretation": (
                "Diagnostic only. Differences come from reduced deterministic review run "
                "and cannot support final paper claims."
            ),
        },
        "known_limitations": [
            "Reduced formal review run on lightweight 2.5D gate.",
            "No fixed-test manifest.",
            "No model weights or checkpoints committed.",
            "Stage 7 metrics are debugging artifacts, not final paper results.",
        ],
        "paper_claim_allowed": False,
        "fixed_test_used": False,
    }


def _mean_by(records: list[EpisodeRecord], field: str) -> dict[str, dict[str, float]]:
    groups: dict[str, list[EpisodeRecord]] = {}
    for record in records:
        groups.setdefault(str(getattr(record, field)), []).append(record)
    return {
        key: {
            "episodes": float(len(items)),
            "success_rate": _average(1.0 if item.success else 0.0 for item in items),
            "collision_rate": _average(1.0 if item.collision else 0.0 for item in items),
            "near_miss_count_mean": _average(float(item.near_miss_count) for item in items),
            "risk_exposure_mean": _average(item.risk_exposure for item in items),
            "jerk_proxy_mean": _average(item.jerk_proxy for item in items),
            "detour_ratio_mean": _average(item.detour_ratio for item in items),
            "shield_intervention_rate_mean": _average(
                item.shield_intervention_rate for item in items
            ),
        }
        for key, items in sorted(groups.items())
    }


def _cadence_points(total_timesteps: int, cadence: int) -> list[int]:
    points = list(range(cadence, total_timesteps + 1, cadence))
    if not points or points[-1] != total_timesteps:
        points.append(total_timesteps)
    return points


def _average(values: Any) -> float:
    value_list = list(values)
    if not value_list:
        return 0.0
    return sum(value_list) / len(value_list)


def _termination_reason(*, collision: bool, goal_reached: bool, truncated: bool) -> str:
    if collision:
        return "collision"
    if goal_reached:
        return "goal_reached"
    if truncated:
        return "timeout"
    return "unknown"


def _git_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _path_for_report(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)

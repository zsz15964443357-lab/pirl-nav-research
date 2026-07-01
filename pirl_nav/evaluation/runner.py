"""Stage 4 evaluation runner for random and scripted smoke policies."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pirl_nav.evaluation.aggregation import aggregate_records
from pirl_nav.evaluation.metrics import (
    average_clearance,
    detour_ratio,
    jerk_proxy,
    shield_intervention_rate,
    success_from_done,
)
from pirl_nav.evaluation.records import EpisodeRecord
from pirl_nav.scenarios import load_yaml_file
from pirl_nav.sim import EnvConfig, IntentRiskEnv
from pirl_nav.sim.geometry import as_point, distance


@dataclass(frozen=True)
class EvaluationConfig:
    experiment_id: str
    stage: int
    manifest_path: Path
    episode_records_path: Path
    summary_path: Path
    run_mode: str = "policy_only"
    policy_types: tuple[str, ...] = ("random", "scripted")
    max_steps: int = 120
    env_dt: float = 0.2


def load_evaluation_config(repo_root: Path, config_path: Path) -> EvaluationConfig:
    payload = load_yaml_file(config_path)
    outputs = payload.get("outputs", {})
    if not isinstance(outputs, dict):
        raise ValueError(f"{config_path}: outputs must be a mapping")

    policy_types = payload.get("policy_types", ["random", "scripted"])
    if not isinstance(policy_types, list) or not policy_types:
        raise ValueError(f"{config_path}: policy_types must be a non-empty list")

    return EvaluationConfig(
        experiment_id=str(payload["experiment_id"]),
        stage=int(payload.get("stage", 4)),
        manifest_path=repo_root / str(payload["scenario_manifest"]),
        episode_records_path=repo_root / str(outputs["episode_records"]),
        summary_path=repo_root / str(outputs["summary"]),
        run_mode=str(payload.get("run_mode", "policy_only")),
        policy_types=tuple(str(policy_type) for policy_type in policy_types),
        max_steps=int(payload.get("max_steps", 120)),
        env_dt=float(payload.get("env_dt", 0.2)),
    )


def run_evaluation(
    repo_root: Path,
    config: EvaluationConfig,
) -> tuple[list[EpisodeRecord], dict[str, Any]]:
    commit = _git_commit(repo_root)
    env = IntentRiskEnv(
        repo_root=repo_root,
        manifest_path=config.manifest_path,
        config=EnvConfig(dt=config.env_dt, max_steps=config.max_steps),
    )
    records: list[EpisodeRecord] = []

    for policy_type in config.policy_types:
        if policy_type not in {"random", "scripted"}:
            raise ValueError(f"unsupported Stage 4 policy_type: {policy_type}")
        for scenario_index, _scenario in enumerate(env.scenarios):
            records.append(
                _run_episode(
                    env=env,
                    scenario_index=scenario_index,
                    policy_type=policy_type,
                    run_mode=config.run_mode,
                    experiment_id=config.experiment_id,
                    stage=config.stage,
                    commit=commit,
                )
            )

    summary = aggregate_records(records)
    _write_jsonl(config.episode_records_path, [record.to_dict() for record in records])
    _write_json(config.summary_path, summary)
    return records, summary


def _run_episode(
    *,
    env: IntentRiskEnv,
    scenario_index: int,
    policy_type: str,
    run_mode: str,
    experiment_id: str,
    stage: int,
    commit: str,
) -> EpisodeRecord:
    scenario = env.scenarios[scenario_index]
    spec = scenario.spec
    env.reset(seed=scenario.seed, scenario_index=scenario_index)
    actions: list[list[float]] = []
    clearances: list[float] = []
    near_miss_count = 0
    risk_exposure = 0.0
    shield_intervention_count = 0
    terminated = False
    truncated = False
    info: dict[str, Any] = {}

    for _ in range(env.config.max_steps):
        if policy_type == "random":
            action = env.sample_random_action()
        else:
            action = env.scripted_goal_action()
        actions.append(action)
        _, _, terminated, truncated, info = env.step(action)
        clearances.append(float(info["current_clearance"]))
        near_miss_count += 1 if info["near_miss"] else 0
        risk_exposure += float(info["risk_exposure_increment"])
        shield_intervention_count += 1 if info["shield_intervention"] else 0
        if terminated or truncated:
            break

    start = as_point(spec["ego"]["start"])
    goal = as_point(spec["ego"]["goal"])
    straight_line_distance = distance(start, goal)
    collision = bool(info["collision"])
    goal_reached = bool(terminated and not truncated and not collision)
    termination_reason = _termination_reason(
        goal_reached=goal_reached,
        collision=collision,
        truncated=truncated,
    )
    success = success_from_done(
        terminated=terminated,
        truncated=truncated,
        collision=collision,
    )
    steps = int(info["step_count"])

    return EpisodeRecord(
        experiment_id=experiment_id,
        commit=commit,
        stage=stage,
        scenario_id=scenario.scenario_id,
        family=scenario.family,
        difficulty=str(spec["difficulty"]),
        seed=scenario.seed,
        run_mode=run_mode,
        policy_type=policy_type,
        steps=steps,
        terminated=terminated,
        truncated=truncated,
        success=success,
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
            "Stage 4 smoke evaluation only; policy is not learned; risk exposure is "
            "a geometric proxy, not final action-conditioned predictive risk."
        ),
        goal_reached=goal_reached,
        termination_reason=termination_reason,
    )


def _termination_reason(*, goal_reached: bool, collision: bool, truncated: bool) -> str:
    if collision:
        return "collision"
    if goal_reached:
        return "goal_reached"
    if truncated:
        return "timeout"
    return "unknown"


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _git_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

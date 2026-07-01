"""Stage 5 dependency-light baseline training and validation entry points."""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
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
from pirl_nav.training.baseline_registry import BASELINE_REGISTRY
from pirl_nav.training.config import BaselineConfig, Stage5TrainingConfig
from pirl_nav.training.policies import (
    PolicyState,
    action_from_observation,
    initial_policy_state,
    update_policy_state,
)


def run_training_smoke(
    repo_root: Path,
    config: Stage5TrainingConfig,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Run deterministic smoke training over baseline-development train manifest."""

    output_path = output_path or config.training_summary_path
    assert_small_review_artifact(output_path)
    commit = _git_commit(repo_root)
    baseline_results = []

    for baseline in config.baseline_configs:
        _validate_artifact_policy(baseline)
        env = IntentRiskEnv(
            repo_root=repo_root,
            manifest_path=baseline.scenario_manifest,
            config=EnvConfig(max_steps=config.smoke_max_steps),
        )
        state = initial_policy_state(
            baseline.baseline_family,
            baseline.seed_plan.policy_init_seed,
        )
        episode_rows = []
        timesteps = 0
        for scenario_index, scenario in enumerate(env.scenarios):
            record = _run_policy_episode(
                env=env,
                scenario_index=scenario_index,
                policy_state=state,
                seed=baseline.seed_plan.environment_seed + scenario.seed,
                experiment_id=baseline.experiment_id,
                stage=baseline.stage,
                commit=commit,
                run_mode="policy_only",
                notes=(
                    "Stage 5 dependency-light smoke training episode; validates baseline "
                    "pipeline only and is not a paper baseline result."
                ),
            )
            timesteps += record.steps
            update_policy_state(
                state,
                success=record.success,
                collision=record.collision,
                near_miss_count=record.near_miss_count,
                risk_exposure=record.risk_exposure,
                cost_limit=baseline.cost_limit,
                learning_rate=baseline.learning_rate,
            )
            episode_rows.append(record.to_dict())

        baseline_results.append(
            {
                "baseline_family": baseline.baseline_family,
                "algorithm": baseline.algorithm,
                "implementation_source": baseline.implementation_source,
                "registry": BASELINE_REGISTRY[baseline.baseline_family].__dict__,
                "config": str(baseline.config_path.relative_to(repo_root)),
                "scenario_manifest": str(baseline.scenario_manifest.relative_to(repo_root)),
                "validation_manifest": str(baseline.validation_manifest.relative_to(repo_root)),
                "timesteps_executed": timesteps,
                "requested_total_timesteps": baseline.total_timesteps,
                "smoke_training": True,
                "paper_result": False,
                "checkpoint_written": False,
                "policy_state": state.to_dict(),
                "episodes": episode_rows,
            }
        )

    summary = {
        "schema": "pirl_nav_stage5_training_smoke_summary_v1",
        "experiment_id": config.experiment_id,
        "stage": config.stage,
        "commit": commit,
        "implementation_mode": config.implementation_mode,
        "baseline_count": len(baseline_results),
        "baselines": baseline_results,
        "artifact_policy_note": (
            "No model weights, checkpoints, large logs, or videos are written by smoke mode."
        ),
        "forbidden_scope_note": (
            "No PIRL-Nav full method, GRU intent predictor, action-conditioned predictive "
            "risk, or shield internalization is implemented."
        ),
    }
    _write_json(output_path, summary)
    return summary


def run_stage5_evaluation(
    repo_root: Path,
    config: Stage5TrainingConfig,
    *,
    training_summary_path: Path | None = None,
    records_path: Path | None = None,
    summary_path: Path | None = None,
) -> tuple[list[EpisodeRecord], dict[str, Any]]:
    """Evaluate Stage 5 smoke baselines using Stage 4 episode records and aggregation."""

    training_summary_path = training_summary_path or config.training_summary_path
    records_path = records_path or config.validation_episode_records_path
    summary_path = summary_path or config.validation_summary_path
    assert_small_review_artifact(records_path)
    assert_small_review_artifact(summary_path)
    commit = _git_commit(repo_root)
    trained_states = _load_policy_states(training_summary_path)
    records: list[EpisodeRecord] = []

    for baseline in config.baseline_configs:
        env = IntentRiskEnv(
            repo_root=repo_root,
            manifest_path=baseline.validation_manifest,
            config=EnvConfig(max_steps=config.smoke_max_steps),
        )
        state = trained_states.get(baseline.baseline_family)
        if state is None:
            state = initial_policy_state(
                baseline.baseline_family,
                baseline.seed_plan.policy_init_seed,
            )
        for scenario_index, scenario in enumerate(env.scenarios):
            records.append(
                _run_policy_episode(
                    env=env,
                    scenario_index=scenario_index,
                    policy_state=replace(state),
                    seed=baseline.seed_plan.evaluation_seed + scenario.seed,
                    experiment_id=baseline.experiment_id,
                    stage=baseline.stage,
                    commit=commit,
                    run_mode="policy_only",
                    notes=(
                        "Stage 5 policy-only smoke baseline validation; reuses Stage 4 "
                        "episode record and aggregation semantics; not a fixed-test or "
                        "paper result."
                    ),
                )
            )

    aggregate = aggregate_records(records)
    aggregate.update(
        {
            "schema": "pirl_nav_stage5_baseline_validation_summary_v1",
            "experiment_id": config.experiment_id,
            "stage": config.stage,
            "commit": commit,
            "policy_note": (
                "Stage 5 outputs are smoke baselines for pipeline validation, distinct "
                "from random/scripted smoke policies and not final learned baselines."
            ),
            "fixed_test_used": False,
            "run_mode": "policy_only",
            "goal_reached_and_termination_reason_present": True,
            "baseline_families": [baseline.baseline_family for baseline in config.baseline_configs],
        }
    )

    _write_jsonl(records_path, [record.to_dict() for record in records])
    _write_json(summary_path, aggregate)
    return records, aggregate


def _run_policy_episode(
    *,
    env: IntentRiskEnv,
    scenario_index: int,
    policy_state: PolicyState,
    seed: int,
    experiment_id: str,
    stage: int,
    commit: str,
    run_mode: str,
    notes: str,
) -> EpisodeRecord:
    scenario = env.scenarios[scenario_index]
    spec = scenario.spec
    observation, info = env.reset(seed=seed, scenario_index=scenario_index)
    actions: list[list[float]] = []
    clearances: list[float] = []
    near_miss_count = 0
    risk_exposure = 0.0
    shield_intervention_count = 0
    terminated = False
    truncated = False

    for _ in range(env.config.max_steps):
        action = action_from_observation(
            observation,
            policy_state=policy_state,
            scenario_family=scenario.family,
        )
        actions.append(action)
        observation, _, terminated, truncated, info = env.step(action)
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
        policy_type=policy_state.baseline_family,
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
        notes=notes,
        goal_reached=goal_reached,
        termination_reason=_termination_reason(
            collision=collision,
            goal_reached=goal_reached,
            truncated=truncated,
        ),
    )


def _validate_artifact_policy(baseline: BaselineConfig) -> None:
    if baseline.checkpoint_policy.commit_to_git:
        raise ValueError(f"{baseline.baseline_family}: checkpoint commit_to_git must be false")
    if baseline.artifact_policy.model_weights_committed:
        raise ValueError(f"{baseline.baseline_family}: model weights must not be committed")
    if baseline.artifact_policy.checkpoints_committed:
        raise ValueError(f"{baseline.baseline_family}: checkpoints must not be committed")
    if baseline.artifact_policy.large_logs_committed:
        raise ValueError(f"{baseline.baseline_family}: large logs must not be committed")
    if baseline.artifact_policy.videos_committed:
        raise ValueError(f"{baseline.baseline_family}: videos must not be committed")


def _load_policy_states(path: Path) -> dict[str, PolicyState]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    states = {}
    for item in payload.get("baselines", []):
        state = item.get("policy_state", {})
        family = str(state.get("baseline_family", item.get("baseline_family")))
        states[family] = PolicyState(
            baseline_family=family,
            speed_scale=float(state["speed_scale"]),
            avoidance_gain=float(state["avoidance_gain"]),
            lagrange_multiplier=float(state.get("lagrange_multiplier", 0.0)),
        )
    return states


def _termination_reason(*, collision: bool, goal_reached: bool, truncated: bool) -> str:
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

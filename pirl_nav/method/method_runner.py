"""Stage 6 PIRL-Nav method smoke and evaluation runners."""

from __future__ import annotations

import json
import subprocess
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
from pirl_nav.method.config import MethodConfig, Stage6Config
from pirl_nav.method.constrained_objective import score_objective
from pirl_nav.method.intent_predictor import HeuristicIntentPredictor
from pirl_nav.method.risk_model import RiskScore, score_action_candidates
from pirl_nav.method.shield_interface import shield_action
from pirl_nav.sim import EnvConfig, IntentRiskEnv
from pirl_nav.sim.geometry import as_point, distance
from pirl_nav.training.artifact_policy import assert_small_review_artifact


def run_method_smoke(
    repo_root: Path,
    config: Stage6Config,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    output_path = output_path or config.smoke_summary_path
    assert_small_review_artifact(output_path)
    commit = _git_commit(repo_root)
    results = []
    for method in config.method_configs:
        env = IntentRiskEnv(
            repo_root=repo_root,
            manifest_path=config.scenario_manifest,
            config=EnvConfig(max_steps=config.smoke_max_steps),
        )
        method_records = []
        method_diagnostics = []
        for scenario_index, scenario in enumerate(env.scenarios):
            record, diagnostics = _run_method_episode(
                env=env,
                scenario_index=scenario_index,
                method=method,
                config=config,
                seed=config.seed_plan.environment_seed + scenario.seed,
                experiment_id=f"{config.experiment_id}_{method.name}",
                commit=commit,
                run_mode="policy_only",
            )
            method_records.append(record.to_dict())
            method_diagnostics.append(diagnostics)
        results.append(
            {
                "method": method.name,
                "config": str(method.config_path.relative_to(repo_root)),
                "paper_claim_allowed": method.paper_claim_allowed,
                "records": method_records,
                "diagnostics": method_diagnostics,
            }
        )

    summary = {
        "schema": "pirl_nav_stage6_method_smoke_summary_v1",
        "experiment_id": config.experiment_id,
        "stage": config.stage,
        "commit": commit,
        "scenario_manifest": str(config.scenario_manifest.relative_to(repo_root)),
        "method_count": len(results),
        "methods": results,
        "fixed_test_used": False,
        "artifact_policy_note": "Stage 6 writes only lightweight JSON/JSONL review artifacts.",
        "proxy_note": (
            "Intent prediction is heuristic, risk is action-conditioned proxy, "
            "and shield internalization is a placeholder."
        ),
    }
    _write_json(output_path, summary)
    return summary


def run_method_evaluation(
    repo_root: Path,
    config: Stage6Config,
    *,
    records_path: Path | None = None,
    summary_path: Path | None = None,
) -> tuple[list[EpisodeRecord], dict[str, Any]]:
    records_path = records_path or config.validation_episode_records_path
    summary_path = summary_path or config.validation_summary_path
    assert_small_review_artifact(records_path)
    assert_small_review_artifact(summary_path)
    commit = _git_commit(repo_root)
    records: list[EpisodeRecord] = []
    diagnostics: list[dict[str, Any]] = []
    for method in config.method_configs:
        env = IntentRiskEnv(
            repo_root=repo_root,
            manifest_path=config.validation_manifest,
            config=EnvConfig(max_steps=config.smoke_max_steps),
        )
        for run_mode in config.run_modes:
            for scenario_index, scenario in enumerate(env.scenarios):
                record, episode_diagnostics = _run_method_episode(
                    env=env,
                    scenario_index=scenario_index,
                    method=method,
                    config=config,
                    seed=config.seed_plan.evaluation_seed + scenario.seed,
                    experiment_id=f"{config.experiment_id}_{method.name}",
                    commit=commit,
                    run_mode=run_mode,
                )
                records.append(record)
                diagnostics.append(episode_diagnostics)

    summary = aggregate_records(records)
    summary.update(
        {
            "schema": "pirl_nav_stage6_method_validation_summary_v1",
            "experiment_id": config.experiment_id,
            "stage": config.stage,
            "commit": commit,
            "fixed_test_used": False,
            "validation_manifest": str(config.validation_manifest.relative_to(repo_root)),
            "method_families": [method.name for method in config.method_configs],
            "run_modes": list(config.run_modes),
            "policy_note": (
                "Stage 6 method outputs are skeleton smoke evaluations, not final "
                "PIRL-Nav paper results or proof of baseline superiority."
            ),
            "risk_exposure_note": (
                "Stage 6 uses action-conditioned geometric + intent-probability proxy risk; "
                "not final learned predictive risk."
            ),
            "diagnostics": diagnostics,
        }
    )
    _write_jsonl(records_path, [record.to_dict() for record in records])
    _write_json(summary_path, summary)
    return records, summary


def _run_method_episode(
    *,
    env: IntentRiskEnv,
    scenario_index: int,
    method: MethodConfig,
    config: Stage6Config,
    seed: int,
    experiment_id: str,
    commit: str,
    run_mode: str,
) -> tuple[EpisodeRecord, dict[str, Any]]:
    scenario = env.scenarios[scenario_index]
    spec = scenario.spec
    observation, info = env.reset(seed=seed, scenario_index=scenario_index)
    predictor = HeuristicIntentPredictor(
        history_window=config.history_window,
        enabled=method.name != "no_intent_prediction",
    )
    predictor.reset(scenario)
    actions: list[list[float]] = []
    clearances: list[float] = []
    risk_scores: list[float] = []
    shield_intervention_count = 0
    near_miss_count = 0
    risk_exposure = 0.0
    terminated = False
    truncated = False

    for _ in range(env.config.max_steps):
        predictor.update(observation, info)
        action_candidates = _action_candidates(observation)
        intent_states = predictor.predict(action_candidates, config.prediction_horizon)
        action_conditioned = method.name != "no_action_conditioning"
        candidate_scores = score_action_candidates(
            action_candidates,
            intent_states,
            horizon=config.prediction_horizon,
            near_miss_distance=float(observation[10]),
            action_conditioned=action_conditioned,
        )
        selected_index, selected_risk = _select_action(
            action_candidates=action_candidates,
            candidate_scores=candidate_scores,
            method=method,
            config=config,
        )
        selected_action = action_candidates[selected_index]
        shield_enabled = run_mode == "policy_plus_shield"
        internalization_enabled = method.name != "no_shield_internalization"
        shield_decision = shield_action(
            selected_action,
            risk_score=selected_risk.risk_score,
            risk_threshold=config.risk_threshold,
            enabled=shield_enabled,
            internalization_enabled=internalization_enabled,
        )
        action_to_apply = shield_decision.action if shield_enabled else selected_action
        actions.append(action_to_apply)
        risk_scores.append(selected_risk.risk_score)
        shield_intervention_count += 1 if shield_decision.shield_intervention else 0

        observation, _, terminated, truncated, info = env.step(action_to_apply)
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
    mean_proxy_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
    notes = (
        f"Stage 6 {method.name}; heuristic intent placeholder; action-conditioned "
        f"proxy risk mean={mean_proxy_risk:.4f}; run_mode={run_mode}; "
        "not final PIRL-Nav training result."
    )
    record = EpisodeRecord(
        experiment_id=experiment_id,
        commit=commit,
        stage=config.stage,
        scenario_id=scenario.scenario_id,
        family=scenario.family,
        difficulty=str(spec["difficulty"]),
        seed=scenario.seed,
        run_mode=run_mode,
        policy_type=method.name,
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
        notes=notes,
        goal_reached=goal_reached,
        termination_reason=_termination_reason(
            collision=collision,
            goal_reached=goal_reached,
            truncated=truncated,
        ),
    )
    diagnostics = {
        "method": method.name,
        "scenario_id": scenario.scenario_id,
        "run_mode": run_mode,
        "mean_proxy_risk": mean_proxy_risk,
        "max_proxy_risk": max(risk_scores) if risk_scores else 0.0,
        "risk_is_proxy": True,
        "intent_predictor_is_placeholder": True,
        "shield_internalization_is_placeholder": True,
        "shield_interventions": shield_intervention_count,
    }
    return record, diagnostics


def _action_candidates(observation: list[float]) -> list[list[float]]:
    goal_dx, goal_dy = float(observation[4]), float(observation[5])
    norm = (goal_dx * goal_dx + goal_dy * goal_dy) ** 0.5
    if norm == 0.0:
        base = [0.0, 0.0]
    else:
        base = [goal_dx / norm, goal_dy / norm]
    left = [-base[1], base[0]]
    right = [base[1], -base[0]]
    return [
        [base[0] * 0.8, base[1] * 0.8],
        [base[0] * 0.45, base[1] * 0.45],
        [base[0] * 0.65 + left[0] * 0.35, base[1] * 0.65 + left[1] * 0.35],
        [base[0] * 0.65 + right[0] * 0.35, base[1] * 0.65 + right[1] * 0.35],
    ]


def _select_action(
    *,
    action_candidates: list[list[float]],
    candidate_scores: dict[int, RiskScore],
    method: MethodConfig,
    config: Stage6Config,
) -> tuple[int, RiskScore]:
    best_index = 0
    best_value = float("-inf")
    for index, action in enumerate(action_candidates):
        risk_score = candidate_scores[index]
        progress_alignment = _progress_alignment(action)
        objective = score_objective(
            progress_alignment=progress_alignment,
            risk_score=risk_score,
            cost_limit=config.cost_limit,
            lagrange_multiplier_placeholder=config.lagrange_multiplier_placeholder,
            constraint_enabled=method.name != "no_risk_constraint",
        )
        if objective.objective_value > best_value:
            best_index = index
            best_value = objective.objective_value
    return best_index, candidate_scores[best_index]


def _progress_alignment(action: list[float]) -> float:
    return float(action[0] * action[0] + action[1] * action[1]) ** 0.5


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

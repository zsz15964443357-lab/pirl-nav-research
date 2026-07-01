"""Stage 6 method config loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pirl_nav.method.ablation_registry import ABLATION_REGISTRY
from pirl_nav.scenarios import load_yaml_file
from pirl_nav.training.config import SeedPlan


@dataclass(frozen=True)
class MethodConfig:
    name: str
    enabled_components: tuple[str, ...]
    disabled_components: tuple[str, ...]
    risk_mode: str
    constraint_mode: str
    shield_mode: str
    paper_claim_allowed: bool
    config_path: Path


@dataclass(frozen=True)
class Stage6Config:
    experiment_id: str
    stage: int
    scenario_manifest: Path
    validation_manifest: Path
    seed_plan: SeedPlan
    method_configs: tuple[MethodConfig, ...]
    smoke_summary_path: Path
    validation_episode_records_path: Path
    validation_summary_path: Path
    smoke_max_steps: int
    history_window: int
    prediction_horizon: float
    risk_threshold: float
    cost_limit: float
    lagrange_multiplier_placeholder: float
    run_modes: tuple[str, ...]


def load_stage6_config(repo_root: Path, config_path: Path) -> Stage6Config:
    repo_root = repo_root.resolve()
    payload = load_yaml_file(config_path)
    method_paths = payload.get("method_configs")
    if not isinstance(method_paths, list) or not method_paths:
        raise ValueError(f"{config_path}: method_configs must be a non-empty list")

    outputs = _mapping(payload.get("outputs"), "outputs", config_path)
    smoke = _mapping(payload.get("smoke"), "smoke", config_path)
    predictor = _mapping(payload.get("intent_predictor"), "intent_predictor", config_path)
    risk = _mapping(payload.get("risk_model"), "risk_model", config_path)
    objective = _mapping(payload.get("constrained_objective"), "constrained_objective", config_path)
    shield = _mapping(payload.get("shield"), "shield", config_path)

    methods = tuple(_load_method_config(repo_root / str(path)) for path in method_paths)
    missing = set(ABLATION_REGISTRY) - {method.name for method in methods}
    if missing:
        raise ValueError(f"{config_path}: missing Stage 6 ablations: {sorted(missing)}")

    run_modes = payload.get("run_modes", ["policy_only", "policy_plus_shield"])
    if not isinstance(run_modes, list) or not run_modes:
        raise ValueError(f"{config_path}: run_modes must be a non-empty list")

    return Stage6Config(
        experiment_id=str(payload["experiment_id"]),
        stage=int(payload.get("stage", 6)),
        scenario_manifest=repo_root / str(payload["scenario_manifest"]),
        validation_manifest=repo_root / str(payload["validation_manifest"]),
        seed_plan=_seed_plan(payload.get("seed_plan"), config_path),
        method_configs=methods,
        smoke_summary_path=repo_root / str(outputs["method_smoke_summary"]),
        validation_episode_records_path=repo_root / str(outputs["validation_episode_records"]),
        validation_summary_path=repo_root / str(outputs["validation_summary"]),
        smoke_max_steps=int(smoke.get("max_steps_per_episode", 24)),
        history_window=int(predictor.get("history_window", 4)),
        prediction_horizon=float(risk.get("prediction_horizon", 3.0)),
        risk_threshold=float(shield.get("risk_threshold", 0.45)),
        cost_limit=float(objective.get("cost_limit", 0.3)),
        lagrange_multiplier_placeholder=float(
            objective.get("lagrange_multiplier_placeholder", 0.5)
        ),
        run_modes=tuple(str(mode) for mode in run_modes),
    )


def _load_method_config(path: Path) -> MethodConfig:
    payload = load_yaml_file(path)
    name = str(payload["name"])
    if name not in ABLATION_REGISTRY:
        raise ValueError(f"{path}: unknown Stage 6 method config {name!r}")
    if bool(payload.get("paper_claim_allowed", True)):
        raise ValueError(f"{path}: paper_claim_allowed must be false for Stage 6 skeleton")
    return MethodConfig(
        name=name,
        enabled_components=tuple(str(item) for item in payload.get("enabled_components", [])),
        disabled_components=tuple(str(item) for item in payload.get("disabled_components", [])),
        risk_mode=str(payload["risk_mode"]),
        constraint_mode=str(payload["constraint_mode"]),
        shield_mode=str(payload["shield_mode"]),
        paper_claim_allowed=False,
        config_path=path,
    )


def _seed_plan(payload: Any, path: Path) -> SeedPlan:
    data = _mapping(payload, "seed_plan", path)
    required = (
        "scenario_seed",
        "environment_seed",
        "policy_init_seed",
        "training_seed",
        "evaluation_seed",
    )
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{path}: seed_plan missing keys: {missing}")
    return SeedPlan(**{key: int(data[key]) for key in required})


def _mapping(payload: Any, name: str, path: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: {name} must be a mapping")
    return payload

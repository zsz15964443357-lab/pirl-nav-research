"""Training config schema for Stage 5 baseline development."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pirl_nav.scenarios import load_yaml_file
from pirl_nav.training.baseline_registry import BASELINE_REGISTRY


@dataclass(frozen=True)
class SeedPlan:
    scenario_seed: int
    environment_seed: int
    policy_init_seed: int
    training_seed: int
    evaluation_seed: int


@dataclass(frozen=True)
class CheckpointPolicy:
    enabled: bool
    save_every_timesteps: int
    output_dir: Path
    commit_to_git: bool


@dataclass(frozen=True)
class ArtifactPolicy:
    small_json_summaries_committed: bool
    model_weights_committed: bool
    checkpoints_committed: bool
    large_logs_committed: bool
    videos_committed: bool
    external_artifact_root: Path


@dataclass(frozen=True)
class BaselineConfig:
    experiment_id: str
    stage: int
    baseline_family: str
    algorithm: str
    implementation_source: str
    scenario_manifest: Path
    validation_manifest: Path
    evaluation_config: Path
    seed_plan: SeedPlan
    total_timesteps: int
    num_envs: int
    rollout_steps: int
    learning_rate: float
    gamma: float
    gae_lambda: float
    clip_range: float
    entropy_coef: float
    value_coef: float
    max_grad_norm: float
    cost_limit: float | None
    checkpoint_policy: CheckpointPolicy
    artifact_policy: ArtifactPolicy
    notes: tuple[str, ...]
    config_path: Path


@dataclass(frozen=True)
class Stage5TrainingConfig:
    experiment_id: str
    stage: int
    implementation_mode: str
    baseline_configs: tuple[BaselineConfig, ...]
    training_summary_path: Path
    validation_episode_records_path: Path
    validation_summary_path: Path
    smoke_max_steps: int


def load_training_config(repo_root: Path, config_path: Path) -> Stage5TrainingConfig:
    repo_root = repo_root.resolve()
    payload = load_yaml_file(config_path)
    baseline_paths = payload.get("baseline_configs")
    if not isinstance(baseline_paths, list) or not baseline_paths:
        raise ValueError(f"{config_path}: baseline_configs must be a non-empty list")

    outputs = payload.get("outputs")
    if not isinstance(outputs, dict):
        raise ValueError(f"{config_path}: outputs must be a mapping")

    smoke = payload.get("smoke", {})
    if not isinstance(smoke, dict):
        raise ValueError(f"{config_path}: smoke must be a mapping")

    baselines = tuple(
        _load_baseline_config(repo_root, repo_root / str(path))
        for path in baseline_paths
    )
    families = {baseline.baseline_family for baseline in baselines}
    missing = set(BASELINE_REGISTRY) - families
    if missing:
        raise ValueError(f"{config_path}: missing baseline families: {sorted(missing)}")

    return Stage5TrainingConfig(
        experiment_id=str(payload["experiment_id"]),
        stage=int(payload.get("stage", 5)),
        implementation_mode=str(payload.get("implementation_mode", "dependency_light_smoke")),
        baseline_configs=baselines,
        training_summary_path=repo_root / str(outputs["training_summary"]),
        validation_episode_records_path=repo_root / str(outputs["validation_episode_records"]),
        validation_summary_path=repo_root / str(outputs["validation_summary"]),
        smoke_max_steps=int(smoke.get("max_steps_per_episode", 24)),
    )


def _load_baseline_config(repo_root: Path, path: Path) -> BaselineConfig:
    payload = load_yaml_file(path)
    family = str(payload["baseline_family"])
    if family not in BASELINE_REGISTRY:
        raise ValueError(f"{path}: unknown baseline_family {family!r}")

    seed_plan = _seed_plan(payload.get("seed_plan"), path)
    checkpoint_policy = _checkpoint_policy(payload.get("checkpoint_policy"), repo_root, path)
    artifact_policy = _artifact_policy(payload.get("artifact_policy"), repo_root, path)
    notes = payload.get("notes", [])
    if not isinstance(notes, list):
        raise ValueError(f"{path}: notes must be a list")

    return BaselineConfig(
        experiment_id=str(payload["experiment_id"]),
        stage=int(payload.get("stage", 5)),
        baseline_family=family,
        algorithm=str(payload["algorithm"]),
        implementation_source=str(payload["implementation_source"]),
        scenario_manifest=repo_root / str(payload["scenario_manifest"]),
        validation_manifest=repo_root / str(payload["validation_manifest"]),
        evaluation_config=repo_root / str(payload["evaluation_config"]),
        seed_plan=seed_plan,
        total_timesteps=int(payload["total_timesteps"]),
        num_envs=int(payload["num_envs"]),
        rollout_steps=int(payload["rollout_steps"]),
        learning_rate=float(payload["learning_rate"]),
        gamma=float(payload["gamma"]),
        gae_lambda=float(payload["gae_lambda"]),
        clip_range=float(payload["clip_range"]),
        entropy_coef=float(payload["entropy_coef"]),
        value_coef=float(payload["value_coef"]),
        max_grad_norm=float(payload["max_grad_norm"]),
        cost_limit=_optional_float(payload.get("cost_limit")),
        checkpoint_policy=checkpoint_policy,
        artifact_policy=artifact_policy,
        notes=tuple(str(note) for note in notes),
        config_path=path,
    )


def _seed_plan(payload: Any, path: Path) -> SeedPlan:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: seed_plan must be a mapping")
    required = (
        "scenario_seed",
        "environment_seed",
        "policy_init_seed",
        "training_seed",
        "evaluation_seed",
    )
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"{path}: seed_plan missing keys: {missing}")
    return SeedPlan(**{key: int(payload[key]) for key in required})


def _checkpoint_policy(payload: Any, repo_root: Path, path: Path) -> CheckpointPolicy:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: checkpoint_policy must be a mapping")
    return CheckpointPolicy(
        enabled=bool(payload.get("enabled", False)),
        save_every_timesteps=int(payload.get("save_every_timesteps", 0)),
        output_dir=repo_root / str(payload["output_dir"]),
        commit_to_git=bool(payload.get("commit_to_git", False)),
    )


def _artifact_policy(payload: Any, repo_root: Path, path: Path) -> ArtifactPolicy:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: artifact_policy must be a mapping")
    return ArtifactPolicy(
        small_json_summaries_committed=bool(payload.get("small_json_summaries_committed", True)),
        model_weights_committed=bool(payload.get("model_weights_committed", False)),
        checkpoints_committed=bool(payload.get("checkpoints_committed", False)),
        large_logs_committed=bool(payload.get("large_logs_committed", False)),
        videos_committed=bool(payload.get("videos_committed", False)),
        external_artifact_root=repo_root / str(payload["external_artifact_root"]),
    )


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)

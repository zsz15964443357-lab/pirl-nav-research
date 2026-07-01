"""Stage 7 formal training configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pirl_nav.scenarios import load_yaml_file


@dataclass(frozen=True)
class Stage7Group:
    group_id: str
    display_name: str
    group_type: str
    source_family: str
    config_path: Path
    policy_modes: tuple[str, ...]
    paper_claim_allowed: bool


@dataclass(frozen=True)
class Stage7Config:
    experiment_id: str
    stage: int
    scenario_manifest: Path
    validation_manifest: Path
    training_groups: tuple[Stage7Group, ...]
    seeds: tuple[int, ...]
    total_timesteps: int
    evaluation_cadence: int
    visualization_cadence: int
    trainer_backend: str
    quick_debug: bool
    reduced_timesteps_for_review: bool
    checkpoint_output_dir: Path
    checkpoint_commit_to_git: bool
    training_metrics_path: Path
    validation_episode_records_path: Path
    validation_summary_path: Path
    comparison_summary_path: Path
    visual_index_path: Path
    figures_dir: Path
    max_steps_per_episode: int


def load_stage7_config(repo_root: Path, config_path: Path) -> Stage7Config:
    repo_root = repo_root.resolve()
    payload = load_yaml_file(config_path)
    outputs = _mapping(payload.get("outputs"), "outputs", config_path)
    review = _mapping(payload.get("reduced_review_run"), "reduced_review_run", config_path)
    checkpoint = _mapping(payload.get("checkpoint_policy"), "checkpoint_policy", config_path)

    group_paths = payload.get("training_groups")
    if not isinstance(group_paths, list) or not group_paths:
        raise ValueError(f"{config_path}: training_groups must be a non-empty list")
    groups = tuple(_load_group(repo_root / str(path)) for path in group_paths)
    group_ids = {group.group_id for group in groups}
    expected = {
        "vanilla_ppo",
        "ppo_ttc_proxy",
        "ppo_semantic_risk_proxy",
        "ppo_lagrangian_no_intent",
        "full_pirl_nav_skeleton",
        "no_intent_prediction",
        "no_action_conditioning",
        "no_risk_constraint",
        "no_shield_internalization",
    }
    missing = expected - group_ids
    if missing:
        raise ValueError(f"{config_path}: missing Stage 7 groups: {sorted(missing)}")

    seeds = payload.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ValueError(f"{config_path}: seeds must be a non-empty list")

    return Stage7Config(
        experiment_id=str(payload["experiment_id"]),
        stage=int(payload.get("stage", 7)),
        scenario_manifest=repo_root / str(payload["scenario_manifest"]),
        validation_manifest=repo_root / str(payload["validation_manifest"]),
        training_groups=groups,
        seeds=tuple(int(seed) for seed in seeds),
        total_timesteps=int(payload["total_timesteps"]),
        evaluation_cadence=int(payload["evaluation_cadence"]),
        visualization_cadence=int(payload["visualization_cadence"]),
        trainer_backend=str(payload["trainer_backend"]),
        quick_debug=bool(payload.get("quick_debug", False)),
        reduced_timesteps_for_review=bool(payload.get("reduced_timesteps_for_review", False)),
        checkpoint_output_dir=repo_root / str(checkpoint["output_dir"]),
        checkpoint_commit_to_git=bool(checkpoint.get("commit_to_git", False)),
        training_metrics_path=repo_root / str(outputs["training_metrics"]),
        validation_episode_records_path=repo_root / str(outputs["validation_episode_records"]),
        validation_summary_path=repo_root / str(outputs["validation_summary"]),
        comparison_summary_path=repo_root / str(outputs["comparison_summary"]),
        visual_index_path=repo_root / str(outputs["visual_index"]),
        figures_dir=repo_root / str(outputs["figures_dir"]),
        max_steps_per_episode=int(review.get("max_steps_per_episode", 24)),
    )


def _load_group(path: Path) -> Stage7Group:
    payload = load_yaml_file(path)
    policy_modes = payload.get("policy_modes", ["policy_only"])
    if not isinstance(policy_modes, list) or not policy_modes:
        raise ValueError(f"{path}: policy_modes must be a non-empty list")
    if bool(payload.get("paper_claim_allowed", True)):
        raise ValueError(f"{path}: paper_claim_allowed must be false for Stage 7 review run")
    return Stage7Group(
        group_id=str(payload["group_id"]),
        display_name=str(payload["display_name"]),
        group_type=str(payload["group_type"]),
        source_family=str(payload["source_family"]),
        config_path=path,
        policy_modes=tuple(str(mode) for mode in policy_modes),
        paper_claim_allowed=False,
    )


def _mapping(payload: Any, name: str, path: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: {name} must be a mapping")
    return payload

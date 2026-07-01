import json
from dataclasses import replace
from pathlib import Path

from pirl_nav.training import load_stage7_config, run_stage7_evaluation, run_stage7_training
from pirl_nav.visualization import (
    generate_rollout_visuals,
    generate_training_visuals,
    write_visual_index,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "training" / "stage7_formal_training.yaml"


def test_stage7_reduced_training_evaluation_and_visuals(tmp_path: Path) -> None:
    config = load_stage7_config(REPO_ROOT, CONFIG)
    test_config = replace(
        config,
        training_metrics_path=tmp_path / "training_metrics.jsonl",
        validation_episode_records_path=tmp_path / "validation_records.jsonl",
        validation_summary_path=tmp_path / "validation_summary.json",
        comparison_summary_path=tmp_path / "comparison_summary.json",
        visual_index_path=tmp_path / "visual_index.md",
        figures_dir=tmp_path / "figures",
        total_timesteps=24,
        evaluation_cadence=12,
        max_steps_per_episode=6,
    )

    training_summary = run_stage7_training(
        REPO_ROOT,
        test_config,
        reduced_review_run=True,
    )
    records, validation_summary, comparison_summary = run_stage7_evaluation(
        REPO_ROOT,
        test_config,
    )
    figures = generate_training_visuals(test_config) + generate_rollout_visuals(
        REPO_ROOT,
        test_config,
    )
    write_visual_index(test_config.visual_index_path, figures)

    assert training_summary["total_rows"] == 54
    assert len(records) == 108
    assert validation_summary["overall"]["episodes"] == 108
    assert comparison_summary["paper_claim_allowed"] is False
    assert test_config.training_metrics_path.is_file()
    assert test_config.validation_episode_records_path.is_file()
    assert test_config.comparison_summary_path.is_file()
    assert test_config.visual_index_path.is_file()
    assert len(list(test_config.figures_dir.glob("*.svg"))) >= 8

    first_row = json.loads(
        test_config.training_metrics_path.read_text(encoding="utf-8").splitlines()[0]
    )
    assert {
        "experiment_id",
        "method_or_baseline",
        "seed",
        "timestep",
        "reward",
        "cost",
        "risk_exposure",
        "policy_mode",
        "is_smoke_or_debug",
        "paper_claim_allowed",
    } <= set(first_row)

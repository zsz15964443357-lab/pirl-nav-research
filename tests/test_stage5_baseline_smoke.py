import json
from dataclasses import replace
from pathlib import Path

from pirl_nav.training import load_training_config, run_stage5_evaluation, run_training_smoke

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "training" / "stage5_baselines.yaml"


def test_stage5_smoke_training_and_evaluation_write_lightweight_artifacts(
    tmp_path: Path,
) -> None:
    config = load_training_config(REPO_ROOT, CONFIG)
    test_config = replace(
        config,
        training_summary_path=tmp_path / "training_summary.json",
        validation_episode_records_path=tmp_path / "records.jsonl",
        validation_summary_path=tmp_path / "summary.json",
        smoke_max_steps=6,
    )

    training_summary = run_training_smoke(REPO_ROOT, test_config)
    records, validation_summary = run_stage5_evaluation(REPO_ROOT, test_config)

    assert training_summary["baseline_count"] == 4
    assert len(records) == 8
    assert {record.policy_type for record in records} == {
        "vanilla_ppo",
        "ppo_ttc_proxy",
        "ppo_semantic_risk_proxy",
        "ppo_lagrangian_no_intent",
    }
    assert {record.run_mode for record in records} == {"policy_only"}
    assert all(
        record.termination_reason in {"collision", "goal_reached", "timeout"}
        for record in records
    )
    assert all(isinstance(record.goal_reached, bool) for record in records)
    assert validation_summary["overall"]["episodes"] == 8
    assert validation_summary["fixed_test_used"] is False

    rows = [
        json.loads(line)
        for line in test_config.validation_episode_records_path.read_text(
            encoding="utf-8",
        ).splitlines()
    ]
    assert len(rows) == 8
    assert {"goal_reached", "termination_reason"} <= set(rows[0])

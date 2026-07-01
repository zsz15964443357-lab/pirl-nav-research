import json
from dataclasses import replace
from pathlib import Path

from pirl_nav.method import load_stage6_config, run_method_evaluation, run_method_smoke

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "method" / "stage6_pirl_nav.yaml"


def test_stage6_method_smoke_and_evaluation_write_review_artifacts(tmp_path: Path) -> None:
    config = load_stage6_config(REPO_ROOT, CONFIG)
    test_config = replace(
        config,
        smoke_summary_path=tmp_path / "method_smoke_summary.json",
        validation_episode_records_path=tmp_path / "records.jsonl",
        validation_summary_path=tmp_path / "summary.json",
        smoke_max_steps=6,
    )

    smoke_summary = run_method_smoke(REPO_ROOT, test_config)
    records, validation_summary = run_method_evaluation(REPO_ROOT, test_config)

    assert smoke_summary["method_count"] == 5
    assert len(records) == 20
    assert validation_summary["overall"]["episodes"] == 20
    assert validation_summary["fixed_test_used"] is False
    assert set(validation_summary["run_modes"]) == {"policy_only", "policy_plus_shield"}
    assert all(record.risk_exposure_is_proxy for record in records)
    assert all("not final PIRL-Nav training result" in record.notes for record in records)

    rows = [
        json.loads(line)
        for line in test_config.validation_episode_records_path.read_text(
            encoding="utf-8",
        ).splitlines()
    ]
    assert len(rows) == 20
    assert {"goal_reached", "termination_reason"} <= set(rows[0])

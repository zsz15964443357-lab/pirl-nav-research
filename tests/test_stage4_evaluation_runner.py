import json
from pathlib import Path

from pirl_nav.evaluation import load_evaluation_config, run_evaluation

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "evaluation" / "stage4_random_scripted.yaml"


def test_stage4_runner_writes_records_and_summary(tmp_path: Path) -> None:
    config = load_evaluation_config(REPO_ROOT, CONFIG)
    test_config = type(config)(
        experiment_id=config.experiment_id,
        stage=config.stage,
        manifest_path=config.manifest_path,
        episode_records_path=tmp_path / "records.jsonl",
        summary_path=tmp_path / "summary.json",
        run_mode=config.run_mode,
        policy_types=config.policy_types,
        max_steps=8,
        env_dt=config.env_dt,
    )

    records, summary = run_evaluation(REPO_ROOT, test_config)

    assert len(records) == 12
    assert {record.policy_type for record in records} == {"random", "scripted"}
    assert {record.run_mode for record in records} == {"policy_only"}
    assert all(record.risk_exposure_is_proxy for record in records)
    assert test_config.episode_records_path.is_file()
    assert test_config.summary_path.is_file()

    jsonl_rows = [
        json.loads(line)
        for line in test_config.episode_records_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(jsonl_rows) == 12
    assert summary["overall"]["episodes"] == 12
    assert set(summary["per_family"]) == {
        "crowd_robot_flow",
        "latent_start",
        "multi_intent_crossing",
        "narrow_passage_yield",
        "occlusion_emergence",
        "vehicle_forklift_launch",
    }
    assert set(summary["per_difficulty"]) == {"easy", "hard", "medium"}

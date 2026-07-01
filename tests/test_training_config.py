from pathlib import Path

from pirl_nav.training import BASELINE_REGISTRY, load_training_config

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "training" / "stage5_baselines.yaml"


def test_stage5_training_config_loads_required_baselines() -> None:
    config = load_training_config(REPO_ROOT, CONFIG)

    assert config.stage == 5
    assert {item.baseline_family for item in config.baseline_configs} == set(BASELINE_REGISTRY)
    assert config.training_summary_path.name == "baseline_training_smoke_summary.json"
    assert config.validation_summary_path.name == "baseline_validation_summary.json"


def test_stage5_seed_plan_and_artifact_policy_are_explicit() -> None:
    config = load_training_config(REPO_ROOT, CONFIG)

    for baseline in config.baseline_configs:
        assert baseline.seed_plan.scenario_seed > 0
        assert baseline.seed_plan.environment_seed > 0
        assert baseline.seed_plan.policy_init_seed > 0
        assert baseline.seed_plan.training_seed > 0
        assert baseline.seed_plan.evaluation_seed > 0
        assert baseline.checkpoint_policy.commit_to_git is False
        assert baseline.artifact_policy.model_weights_committed is False
        assert baseline.artifact_policy.checkpoints_committed is False
        assert baseline.artifact_policy.large_logs_committed is False
        assert baseline.artifact_policy.videos_committed is False

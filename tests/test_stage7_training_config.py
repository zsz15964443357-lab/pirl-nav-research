from pathlib import Path

from pirl_nav.training import load_stage7_config

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "training" / "stage7_formal_training.yaml"


def test_stage7_config_loads_required_groups() -> None:
    config = load_stage7_config(REPO_ROOT, CONFIG)

    assert config.stage == 7
    assert config.reduced_timesteps_for_review is True
    assert config.quick_debug is True
    assert config.checkpoint_commit_to_git is False
    assert set(config.seeds) == {0, 1, 2}
    assert len(config.training_groups) == 9
    assert {
        "vanilla_ppo",
        "ppo_ttc_proxy",
        "ppo_semantic_risk_proxy",
        "ppo_lagrangian_no_intent",
        "full_pirl_nav_skeleton",
        "no_intent_prediction",
        "no_action_conditioning",
        "no_risk_constraint",
        "no_shield_internalization",
    } == {group.group_id for group in config.training_groups}


def test_stage7_groups_disallow_paper_claims() -> None:
    config = load_stage7_config(REPO_ROOT, CONFIG)

    assert all(group.paper_claim_allowed is False for group in config.training_groups)
    assert all(
        set(group.policy_modes) == {"policy_only", "policy_plus_shield"}
        for group in config.training_groups
    )

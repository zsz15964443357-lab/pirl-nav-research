from pathlib import Path

from pirl_nav.sim import IntentRiskEnv, load_reviewed_scenarios

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "experiments" / "manifests" / "reviewed_stage2_2026-06-30.yaml"


def test_reviewed_stage2_manifest_loads_six_stage3_scenarios() -> None:
    scenarios = load_reviewed_scenarios(REPO_ROOT, MANIFEST)

    assert len(scenarios) == 6
    assert {scenario.review_status for scenario in scenarios} == {"approved_for_stage3"}
    assert {scenario.review_decision for scenario in scenarios} == {"approved"}


def test_environment_resets_all_reviewed_scenarios() -> None:
    env = IntentRiskEnv(repo_root=REPO_ROOT, manifest_path=MANIFEST)

    for scenario_index, scenario in enumerate(env.scenarios):
        observation, info = env.reset(seed=scenario.seed, scenario_index=scenario_index)

        assert len(observation) == 13
        assert info["scenario_id"] == scenario.scenario_id
        assert info["family"] == scenario.family
        assert info["seed"] == scenario.seed
        assert info["step_count"] == 0
        assert info["collision"] is False
        assert isinstance(env.render(), str)


def test_random_action_smoke_rollout_all_reviewed_scenarios() -> None:
    env = IntentRiskEnv(repo_root=REPO_ROOT, manifest_path=MANIFEST)
    required_info = {
        "scenario_id",
        "family",
        "seed",
        "min_clearance",
        "collision",
        "near_miss",
        "step_count",
        "risk_exposure_increment",
        "shield_intervention",
    }

    for scenario_index, scenario in enumerate(env.scenarios):
        _, info = env.reset(seed=scenario.seed, scenario_index=scenario_index)
        for _ in range(5):
            _, reward, terminated, truncated, info = env.step(env.sample_random_action())
            assert isinstance(reward, float)
            assert required_info <= set(info)
            if terminated or truncated:
                break

        assert info["scenario_id"] == scenario.scenario_id
        assert info["step_count"] >= 1


def test_scripted_goal_action_smoke_rollout() -> None:
    env = IntentRiskEnv(repo_root=REPO_ROOT, manifest_path=MANIFEST)
    observation, _ = env.reset(seed=1001, scenario_index=0)
    initial_goal_distance = (observation[4] ** 2 + observation[5] ** 2) ** 0.5

    for _ in range(8):
        observation, _, terminated, truncated, _ = env.step(env.scripted_goal_action())
        if terminated or truncated:
            break

    final_goal_distance = (observation[4] ** 2 + observation[5] ** 2) ** 0.5
    assert final_goal_distance < initial_goal_distance

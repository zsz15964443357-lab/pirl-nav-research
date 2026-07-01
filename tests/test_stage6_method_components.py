from pathlib import Path

from pirl_nav.method import ABLATION_REGISTRY, HeuristicIntentPredictor, load_stage6_config
from pirl_nav.method.risk_model import score_action, score_action_candidates
from pirl_nav.sim import IntentRiskEnv

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "method" / "stage6_pirl_nav.yaml"
MANIFEST = REPO_ROOT / "experiments" / "manifests" / "validation_stage5_baseline.yaml"


def test_stage6_config_loads_required_ablations() -> None:
    config = load_stage6_config(REPO_ROOT, CONFIG)

    assert config.stage == 6
    assert {method.name for method in config.method_configs} == set(ABLATION_REGISTRY)
    assert set(config.run_modes) == {"policy_only", "policy_plus_shield"}
    assert config.validation_manifest == MANIFEST


def test_heuristic_intent_predictor_is_placeholder() -> None:
    env = IntentRiskEnv(repo_root=REPO_ROOT, manifest_path=MANIFEST)
    scenario = env.scenarios[0]
    observation, info = env.reset(seed=scenario.seed, scenario_index=0)
    predictor = HeuristicIntentPredictor(history_window=4, enabled=True)

    predictor.reset(scenario)
    predictor.update(observation, info)
    states = predictor.predict([[0.8, 0.0], [0.0, 0.8]], horizon=3.0)

    assert states
    assert all(state.is_placeholder for state in states)
    assert all("not a trained GRU" in state.notes for state in states)
    assert states[0].candidate_intents


def test_action_conditioned_risk_changes_across_candidate_actions() -> None:
    env = IntentRiskEnv(repo_root=REPO_ROOT, manifest_path=MANIFEST)
    scenario = env.scenarios[0]
    observation, info = env.reset(seed=scenario.seed, scenario_index=0)
    predictor = HeuristicIntentPredictor(history_window=4, enabled=True)
    predictor.reset(scenario)
    predictor.update(observation, info)
    state = predictor.predict([[0.8, 0.0], [-0.8, 0.0]], horizon=3.0)[0]

    forward = score_action(
        [0.8, 0.0],
        state,
        horizon=3.0,
        near_miss_distance=float(observation[10]),
        action_conditioned=True,
    )
    backward = score_action(
        [-0.8, 0.0],
        state,
        horizon=3.0,
        near_miss_distance=float(observation[10]),
        action_conditioned=True,
    )

    assert forward.risk_is_proxy is True
    assert forward.action_conditioned is True
    assert forward.risk_score != backward.risk_score


def test_state_only_ablation_removes_action_conditioning() -> None:
    env = IntentRiskEnv(repo_root=REPO_ROOT, manifest_path=MANIFEST)
    scenario = env.scenarios[0]
    observation, info = env.reset(seed=scenario.seed, scenario_index=0)
    predictor = HeuristicIntentPredictor(history_window=4, enabled=True)
    predictor.reset(scenario)
    predictor.update(observation, info)
    states = predictor.predict([[0.8, 0.0], [-0.8, 0.0]], horizon=3.0)

    scores = score_action_candidates(
        [[0.8, 0.0], [-0.8, 0.0]],
        states,
        horizon=3.0,
        near_miss_distance=float(observation[10]),
        action_conditioned=False,
    )

    assert scores[0].risk_score == scores[1].risk_score
    assert scores[0].action_conditioned is False

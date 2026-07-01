"""Dependency-light policy state used for Stage 5 smoke training."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from random import Random

SEMANTIC_RISK_GAIN = {
    "latent_start": 0.12,
    "occlusion_emergence": 0.24,
    "multi_intent_crossing": 0.2,
    "narrow_passage_yield": 0.18,
    "vehicle_forklift_launch": 0.3,
    "crowd_robot_flow": 0.22,
}


@dataclass
class PolicyState:
    baseline_family: str
    speed_scale: float
    avoidance_gain: float
    lagrange_multiplier: float = 0.0

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


def initial_policy_state(baseline_family: str, seed: int) -> PolicyState:
    rng = Random(seed)
    jitter = rng.uniform(-0.02, 0.02)
    if baseline_family == "vanilla_ppo":
        return PolicyState(baseline_family, speed_scale=0.68 + jitter, avoidance_gain=0.0)
    if baseline_family == "ppo_ttc_proxy":
        return PolicyState(baseline_family, speed_scale=0.62 + jitter, avoidance_gain=0.28)
    if baseline_family == "ppo_semantic_risk_proxy":
        return PolicyState(baseline_family, speed_scale=0.6 + jitter, avoidance_gain=0.22)
    if baseline_family == "ppo_lagrangian_no_intent":
        return PolicyState(
            baseline_family,
            speed_scale=0.58 + jitter,
            avoidance_gain=0.24,
            lagrange_multiplier=0.02,
        )
    raise ValueError(f"unsupported baseline family: {baseline_family}")


def action_from_observation(
    observation: list[float],
    *,
    policy_state: PolicyState,
    scenario_family: str,
) -> list[float]:
    goal_dx, goal_dy = observation[4], observation[5]
    nearest_dx, nearest_dy = observation[6], observation[7]
    near_miss_distance = max(float(observation[10]), 1e-6)

    goal_norm = _norm(goal_dx, goal_dy)
    if goal_norm == 0.0:
        action = [0.0, 0.0]
    else:
        action = [
            policy_state.speed_scale * goal_dx / goal_norm,
            policy_state.speed_scale * goal_dy / goal_norm,
        ]

    distance_to_object = _norm(nearest_dx, nearest_dy)
    if distance_to_object < near_miss_distance * 2.0 and distance_to_object > 0.0:
        risk_gain = policy_state.avoidance_gain
        if policy_state.baseline_family == "ppo_semantic_risk_proxy":
            risk_gain += SEMANTIC_RISK_GAIN.get(scenario_family, 0.1)
        if policy_state.baseline_family == "ppo_lagrangian_no_intent":
            risk_gain += min(policy_state.lagrange_multiplier, 0.5)
        clearance_factor = 1.0 - min(distance_to_object / (near_miss_distance * 2.0), 1.0)
        action[0] += risk_gain * clearance_factor * (-nearest_dy / distance_to_object)
        action[1] += risk_gain * clearance_factor * (nearest_dx / distance_to_object)

    return action


def update_policy_state(
    policy_state: PolicyState,
    *,
    success: bool,
    collision: bool,
    near_miss_count: int,
    risk_exposure: float,
    cost_limit: float | None,
    learning_rate: float,
) -> None:
    if collision or near_miss_count > 0:
        policy_state.speed_scale = max(0.35, policy_state.speed_scale - 0.04)
        policy_state.avoidance_gain = min(0.9, policy_state.avoidance_gain + 0.04)
    elif success:
        policy_state.speed_scale = min(0.95, policy_state.speed_scale + 0.02)
        policy_state.avoidance_gain = max(0.0, policy_state.avoidance_gain - 0.01)

    if policy_state.baseline_family == "ppo_lagrangian_no_intent" and cost_limit is not None:
        violation = risk_exposure - cost_limit
        policy_state.lagrange_multiplier = max(
            0.0,
            policy_state.lagrange_multiplier + learning_rate * violation,
        )


def _norm(x: float, y: float) -> float:
    return sqrt(x * x + y * y)

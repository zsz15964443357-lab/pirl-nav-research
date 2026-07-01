"""Action-conditioned predictive risk proxy for Stage 6."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, sqrt
from typing import Any

from pirl_nav.method.intent_state import IntentState


@dataclass(frozen=True)
class RiskScore:
    risk_score: float
    expected_clearance: float
    predicted_near_miss_probability: float
    intent_entropy: float
    risk_is_proxy: bool
    action_conditioned: bool
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_action(
    action: list[float],
    intent_state: IntentState,
    *,
    horizon: float,
    near_miss_distance: float,
    action_conditioned: bool = True,
) -> RiskScore:
    effective_action = action if action_conditioned else [0.0, 0.0]
    rel_x, rel_y = intent_state.relative_position
    rel_vx, rel_vy = intent_state.relative_velocity
    predicted_x = rel_x + (rel_vx - float(effective_action[0])) * horizon
    predicted_y = rel_y + (rel_vy - float(effective_action[1])) * horizon
    expected_clearance = max(0.0, _norm(predicted_x, predicted_y) - near_miss_distance)
    clearance_pressure = exp(-expected_clearance / max(near_miss_distance, 1e-6))
    conflict_probability = intent_state.conflict_probability
    entropy_factor = min(intent_state.intent_entropy, 2.0) / 2.0
    risk_score = min(
        1.0,
        (0.65 * conflict_probability + 0.35 * entropy_factor) * clearance_pressure,
    )
    return RiskScore(
        risk_score=risk_score,
        expected_clearance=expected_clearance,
        predicted_near_miss_probability=min(1.0, risk_score + 0.15 * conflict_probability),
        intent_entropy=intent_state.intent_entropy,
        risk_is_proxy=True,
        action_conditioned=action_conditioned,
        notes=(
            "Stage 6 geometric + intent-probability proxy; not final learned "
            "action-conditioned predictive intent-risk."
        ),
    )


def score_action_candidates(
    action_candidates: list[list[float]],
    intent_states: list[IntentState],
    *,
    horizon: float,
    near_miss_distance: float,
    action_conditioned: bool = True,
) -> dict[int, RiskScore]:
    scores = {}
    for index, action in enumerate(action_candidates):
        action_scores = [
            score_action(
                action,
                state,
                horizon=horizon,
                near_miss_distance=near_miss_distance,
                action_conditioned=action_conditioned,
            )
            for state in intent_states
        ]
        if not action_scores:
            scores[index] = RiskScore(
                risk_score=0.0,
                expected_clearance=float("inf"),
                predicted_near_miss_probability=0.0,
                intent_entropy=0.0,
                risk_is_proxy=True,
                action_conditioned=action_conditioned,
                notes="No objects available for Stage 6 risk scoring.",
            )
        else:
            scores[index] = max(action_scores, key=lambda item: item.risk_score)
    return scores


def _norm(x: float, y: float) -> float:
    return sqrt(x * x + y * y)

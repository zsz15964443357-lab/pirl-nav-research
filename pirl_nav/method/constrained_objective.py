"""Constrained objective skeleton for PIRL-Nav Stage 6."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from pirl_nav.method.risk_model import RiskScore


@dataclass(frozen=True)
class ObjectiveResult:
    reward: float
    cost: float
    constraint_violation: float
    lagrange_multiplier_placeholder: float
    objective_value: float
    objective_notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_objective(
    *,
    progress_alignment: float,
    risk_score: RiskScore,
    cost_limit: float,
    lagrange_multiplier_placeholder: float,
    constraint_enabled: bool,
) -> ObjectiveResult:
    reward = progress_alignment - 0.02
    cost = risk_score.risk_score
    constraint_violation = max(0.0, cost - cost_limit)
    penalty = lagrange_multiplier_placeholder * constraint_violation if constraint_enabled else 0.0
    return ObjectiveResult(
        reward=reward,
        cost=cost,
        constraint_violation=constraint_violation,
        lagrange_multiplier_placeholder=lagrange_multiplier_placeholder,
        objective_value=reward - penalty,
        objective_notes=(
            "Stage 6 constrained objective skeleton; not formal PPO-Lagrangian training."
        ),
    )

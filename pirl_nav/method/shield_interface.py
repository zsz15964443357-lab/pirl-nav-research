"""Safety shield and internalization placeholder for Stage 6."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from typing import Any


@dataclass(frozen=True)
class ShieldDecision:
    action: list[float]
    shield_intervention: bool
    shield_reason: str
    student_policy_target: list[float] | None
    internalization_loss: float | None
    internalization_is_placeholder: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def shield_action(
    action: list[float],
    *,
    risk_score: float,
    risk_threshold: float,
    enabled: bool,
    internalization_enabled: bool,
) -> ShieldDecision:
    if not enabled or risk_score <= risk_threshold:
        return ShieldDecision(
            action=action,
            shield_intervention=False,
            shield_reason="not_triggered" if enabled else "shield_disabled",
            student_policy_target=action if internalization_enabled else None,
            internalization_loss=0.0 if internalization_enabled else None,
            internalization_is_placeholder=True,
        )

    scale = max(0.25, 1.0 - risk_score)
    safe_action = [float(action[0]) * scale, float(action[1]) * scale]
    magnitude = _norm(float(action[0]) - safe_action[0], float(action[1]) - safe_action[1])
    return ShieldDecision(
        action=safe_action,
        shield_intervention=True,
        shield_reason="proxy_risk_above_threshold",
        student_policy_target=safe_action if internalization_enabled else None,
        internalization_loss=magnitude if internalization_enabled else None,
        internalization_is_placeholder=True,
    )


def _norm(x: float, y: float) -> float:
    return sqrt(x * x + y * y)

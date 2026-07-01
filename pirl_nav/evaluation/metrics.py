"""Stage 4 metric helpers aligned with docs/04_metrics_contract.md."""

from __future__ import annotations

from math import sqrt
from statistics import mean


def euclidean_norm(values: tuple[float, float] | list[float]) -> float:
    return sqrt(float(values[0]) * float(values[0]) + float(values[1]) * float(values[1]))


def detour_ratio(*, path_length: float, straight_line_distance: float) -> float:
    if straight_line_distance <= 0.0:
        return 1.0 if path_length <= 0.0 else float("inf")
    return path_length / straight_line_distance


def average_clearance(clearances: list[float]) -> float:
    finite_clearances = [value for value in clearances if value != float("inf")]
    if not finite_clearances:
        return float("inf")
    return mean(finite_clearances)


def jerk_proxy(actions: list[list[float]], *, dt: float) -> float:
    """Mean command-change magnitude per second.

    This is a proxy because Stage 4 actions are velocity commands, not true UAV
    acceleration measurements.
    """

    if len(actions) < 2:
        return 0.0
    changes = []
    for previous, current in zip(actions, actions[1:], strict=False):
        changes.append(
            euclidean_norm(
                [
                    float(current[0]) - float(previous[0]),
                    float(current[1]) - float(previous[1]),
                ]
            )
            / dt
        )
    return mean(changes)


def success_from_done(*, terminated: bool, truncated: bool, collision: bool) -> bool:
    return bool(terminated and not truncated and not collision)


def shield_intervention_rate(*, shield_intervention_count: int, steps: int) -> float:
    if steps <= 0:
        return 0.0
    return shield_intervention_count / steps

"""Small geometry helpers for the Stage 3 environment gate."""

from __future__ import annotations

from math import sqrt
from typing import Any

Point = tuple[float, float]


def as_point(value: list[float] | tuple[float, float]) -> Point:
    return (float(value[0]), float(value[1]))


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def scale(value: Point, factor: float) -> Point:
    return (value[0] * factor, value[1] * factor)


def norm(value: Point) -> float:
    return sqrt(value[0] * value[0] + value[1] * value[1])


def clamp_magnitude(value: Point, limit: float) -> Point:
    magnitude = norm(value)
    if magnitude <= limit or magnitude == 0.0:
        return value
    return scale(value, limit / magnitude)


def distance(a: Point, b: Point) -> float:
    return norm(sub(a, b))


def move_toward(position: Point, target: Point, max_distance: float) -> Point:
    offset = sub(target, position)
    remaining = norm(offset)
    if remaining == 0.0 or remaining <= max_distance:
        return target
    return add(position, scale(offset, max_distance / remaining))


def clearance_between_circles(
    center_a: Point,
    radius_a: float,
    center_b: Point,
    radius_b: float,
) -> float:
    return distance(center_a, center_b) - radius_a - radius_b


def clearance_to_box(point: Point, radius: float, obstacle: dict[str, Any]) -> float:
    """Return circle clearance to an axis-aligned box obstacle."""

    center = as_point(obstacle["center"])
    size = as_point(obstacle["size"])
    half_width = size[0] / 2.0
    half_height = size[1] / 2.0

    dx = max(abs(point[0] - center[0]) - half_width, 0.0)
    dy = max(abs(point[1] - center[1]) - half_height, 0.0)
    outside_distance = sqrt(dx * dx + dy * dy)

    if dx == 0.0 and dy == 0.0:
        inside_depth = min(
            half_width - abs(point[0] - center[0]),
            half_height - abs(point[1] - center[1]),
        )
        return -inside_depth - radius
    return outside_distance - radius


def min_static_clearance(point: Point, radius: float, obstacles: list[dict[str, Any]]) -> float:
    if not obstacles:
        return float("inf")
    return min(clearance_to_box(point, radius, obstacle) for obstacle in obstacles)

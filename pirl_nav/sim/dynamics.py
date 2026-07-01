"""Minimal Stage 3 dynamics for reviewed scenario smoke rollouts."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any

from pirl_nav.sim.geometry import Point, as_point, distance, move_toward, sub

CLASS_RADIUS = {
    "pedestrian": 0.28,
    "cart": 0.38,
    "mobile_robot": 0.42,
    "forklift": 0.75,
}

CLASS_SPEED = {
    "pedestrian": 0.85,
    "cart": 0.75,
    "mobile_robot": 0.7,
    "forklift": 1.0,
}


@dataclass(frozen=True)
class IntentPlan:
    name: str
    probability: float
    target: Point | None
    trigger_time: tuple[float, float] | None
    conflicts_with_ego_nominal_path: bool


@dataclass
class DynamicObjectState:
    object_id: str
    object_class: str
    radius: float
    initial_position: Point
    initial_velocity: Point
    position: Point
    velocity: Point
    intent: IntentPlan
    activated: bool = False
    reached_target: bool = False


def build_dynamic_objects(spec: dict[str, Any], *, rng: Random) -> list[DynamicObjectState]:
    objects: list[DynamicObjectState] = []
    for raw_object in spec["objects"]:
        initial_state = raw_object["initial_state"]
        position = as_point(initial_state["position"])
        velocity = as_point(initial_state["velocity"])
        object_class = str(raw_object["class"])
        intent = _sample_intent(raw_object["intent_candidates"], rng)
        objects.append(
            DynamicObjectState(
                object_id=str(raw_object["id"]),
                object_class=object_class,
                radius=CLASS_RADIUS.get(object_class, 0.35),
                initial_position=position,
                initial_velocity=velocity,
                position=position,
                velocity=velocity,
                intent=intent,
            )
        )
    return objects


def step_dynamic_object(obj: DynamicObjectState, *, time_s: float, dt: float) -> None:
    should_activate = _is_active(obj.intent, time_s)
    if obj.intent.target is None:
        obj.activated = obj.activated or should_activate
        if _is_stationary_intent(obj.intent.name):
            obj.velocity = (0.0, 0.0)
            return
        obj.position = (
            obj.position[0] + obj.initial_velocity[0] * dt,
            obj.position[1] + obj.initial_velocity[1] * dt,
        )
        obj.velocity = obj.initial_velocity
        return

    if not should_activate and not obj.activated:
        obj.position = (
            obj.position[0] + obj.initial_velocity[0] * dt,
            obj.position[1] + obj.initial_velocity[1] * dt,
        )
        obj.velocity = obj.initial_velocity
        return

    obj.activated = True
    if obj.reached_target:
        obj.velocity = (0.0, 0.0)
        return

    speed = max(CLASS_SPEED.get(obj.object_class, 0.7), _speed_from_velocity(obj.initial_velocity))
    previous = obj.position
    obj.position = move_toward(obj.position, obj.intent.target, speed * dt)
    displacement = sub(obj.position, previous)
    obj.velocity = (displacement[0] / dt, displacement[1] / dt)
    if distance(obj.position, obj.intent.target) < 1e-6:
        obj.reached_target = True
        obj.velocity = (0.0, 0.0)


def _sample_intent(candidates: list[dict[str, Any]], rng: Random) -> IntentPlan:
    roll = rng.random()
    cumulative = 0.0
    selected = candidates[-1]
    for candidate in candidates:
        cumulative += float(candidate["probability"])
        if roll <= cumulative:
            selected = candidate
            break

    trigger_time = None
    raw_trigger = selected.get("trigger_time")
    if isinstance(raw_trigger, list) and len(raw_trigger) == 2:
        trigger_time = (float(raw_trigger[0]), float(raw_trigger[1]))

    raw_target = selected.get("target")
    target = as_point(raw_target) if isinstance(raw_target, list) and len(raw_target) == 2 else None

    return IntentPlan(
        name=str(selected["name"]),
        probability=float(selected["probability"]),
        target=target,
        trigger_time=trigger_time,
        conflicts_with_ego_nominal_path=bool(selected.get("conflicts_with_ego_nominal_path")),
    )


def _is_active(intent: IntentPlan, time_s: float) -> bool:
    if intent.trigger_time is None:
        return True
    return time_s >= intent.trigger_time[0]


def _is_stationary_intent(name: str) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in ("stay", "wait", "hold", "park", "stop"))


def _speed_from_velocity(velocity: Point) -> float:
    return (velocity[0] * velocity[0] + velocity[1] * velocity[1]) ** 0.5

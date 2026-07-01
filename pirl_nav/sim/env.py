"""Gymnasium-style Stage 3 environment gate for PIRL-Nav scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

from pirl_nav.sim.dynamics import DynamicObjectState, build_dynamic_objects, step_dynamic_object
from pirl_nav.sim.geometry import (
    Point,
    add,
    as_point,
    clamp_magnitude,
    clearance_between_circles,
    distance,
    min_static_clearance,
    norm,
    scale,
    sub,
)
from pirl_nav.sim.scenario_loader import ReviewedScenario, load_reviewed_scenarios


@dataclass(frozen=True)
class EnvConfig:
    """Stage 3 gate configuration.

    The action is a world-frame 2D velocity command. This preserves the high-level
    navigation interface without adding low-level UAV motor control before Stage 3
    has passed.
    """

    dt: float = 0.2
    max_steps: int = 240
    speed_limit: float = 1.6
    acceleration_limit: float = 1.8
    goal_tolerance: float = 0.45


class IntentRiskEnv:
    """Minimal reset/step/render environment for reviewed Stage 2 scenarios."""

    metadata = {
        "render_modes": ["ansi"],
        "stage": "stage3_environment_gate",
        "api": "gymnasium_style",
    }

    def __init__(
        self,
        *,
        repo_root: Path,
        manifest_path: Path,
        config: EnvConfig | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.manifest_path = manifest_path.resolve()
        self.config = config or EnvConfig()
        self.scenarios = load_reviewed_scenarios(self.repo_root, self.manifest_path)

        self._rng = Random(0)
        self._scenario: ReviewedScenario | None = None
        self._objects: list[DynamicObjectState] = []
        self._ego_position: Point = (0.0, 0.0)
        self._ego_velocity: Point = (0.0, 0.0)
        self._time_s = 0.0
        self._step_count = 0
        self._min_clearance = float("inf")
        self._path_length = 0.0
        self._last_goal_distance = 0.0

    def reset(
        self,
        *,
        seed: int | None = None,
        scenario_index: int = 0,
    ) -> tuple[list[float], dict[str, Any]]:
        if not 0 <= scenario_index < len(self.scenarios):
            raise IndexError(f"scenario_index out of range: {scenario_index}")

        self._scenario = self.scenarios[scenario_index]
        scenario_seed = self._scenario.seed if seed is None else seed
        self._rng = Random(scenario_seed)
        spec = self._scenario.spec
        self._objects = build_dynamic_objects(spec, rng=self._rng)
        self._ego_position = as_point(spec["ego"]["start"])
        self._ego_velocity = (0.0, 0.0)
        self._time_s = 0.0
        self._step_count = 0
        self._path_length = 0.0
        self._last_goal_distance = distance(self._ego_position, as_point(spec["ego"]["goal"]))
        self._min_clearance = self._compute_min_clearance()
        return self._observation(), self._info(collision=self._min_clearance <= 0.0)

    def step(
        self,
        action: list[float] | tuple[float, float],
    ) -> tuple[list[float], float, bool, bool, dict[str, Any]]:
        self._require_reset()
        assert self._scenario is not None

        command = clamp_magnitude(as_point(action), self.config.speed_limit)
        max_delta = self.config.acceleration_limit * self.config.dt
        velocity_delta = clamp_magnitude(sub(command, self._ego_velocity), max_delta)
        self._ego_velocity = add(self._ego_velocity, velocity_delta)

        previous_position = self._ego_position
        self._ego_position = add(self._ego_position, scale(self._ego_velocity, self.config.dt))
        self._path_length += distance(previous_position, self._ego_position)

        self._time_s += self.config.dt
        self._step_count += 1
        for obj in self._objects:
            step_dynamic_object(obj, time_s=self._time_s, dt=self.config.dt)

        current_clearance = self._compute_min_clearance()
        self._min_clearance = min(self._min_clearance, current_clearance)
        collision = current_clearance <= 0.0

        goal = as_point(self._scenario.spec["ego"]["goal"])
        goal_distance = distance(self._ego_position, goal)
        progress = self._last_goal_distance - goal_distance
        self._last_goal_distance = goal_distance
        reached_goal = goal_distance <= self.config.goal_tolerance

        terminated = bool(reached_goal or collision)
        truncated = self._step_count >= self.config.max_steps
        reward = progress - 0.01
        if reached_goal:
            reward += 5.0
        if collision:
            reward -= 10.0

        return (
            self._observation(),
            reward,
            terminated,
            truncated,
            self._info(collision=collision),
        )

    def render(self) -> str:
        self._require_reset()
        assert self._scenario is not None
        object_states = ", ".join(
            f"{obj.object_id}:{obj.intent.name}@({obj.position[0]:.2f},{obj.position[1]:.2f})"
            for obj in self._objects
        )
        return (
            f"{self._scenario.scenario_id} step={self._step_count} "
            f"t={self._time_s:.2f}s ego=({self._ego_position[0]:.2f},{self._ego_position[1]:.2f}) "
            f"min_clearance={self._min_clearance:.3f} objects=[{object_states}]"
        )

    def sample_random_action(self) -> list[float]:
        speed = self.config.speed_limit
        return [
            self._rng.uniform(-speed, speed),
            self._rng.uniform(-speed, speed),
        ]

    def scripted_goal_action(self) -> list[float]:
        self._require_reset()
        assert self._scenario is not None
        goal = as_point(self._scenario.spec["ego"]["goal"])
        direction = sub(goal, self._ego_position)
        if norm(direction) == 0.0:
            return [0.0, 0.0]
        velocity = clamp_magnitude(direction, self._scenario.spec["ego"]["nominal_speed"])
        return [velocity[0], velocity[1]]

    def _observation(self) -> list[float]:
        assert self._scenario is not None
        goal = as_point(self._scenario.spec["ego"]["goal"])
        nearest = self._nearest_object()
        if nearest is None:
            nearest_rel = (0.0, 0.0)
            nearest_velocity = (0.0, 0.0)
        else:
            nearest_rel = sub(nearest.position, self._ego_position)
            nearest_velocity = nearest.velocity
        risk = self._scenario.spec["risk"]
        goal_rel = sub(goal, self._ego_position)
        return [
            self._ego_position[0],
            self._ego_position[1],
            self._ego_velocity[0],
            self._ego_velocity[1],
            goal_rel[0],
            goal_rel[1],
            nearest_rel[0],
            nearest_rel[1],
            nearest_velocity[0],
            nearest_velocity[1],
            float(risk["near_miss_distance"]),
            float(risk["shield_trigger_distance"]),
            float(risk["exposure_horizon"]),
        ]

    def _info(self, *, collision: bool) -> dict[str, Any]:
        assert self._scenario is not None
        dynamic_clearance = self._compute_dynamic_clearance()
        near_miss_distance = float(self._scenario.spec["risk"]["near_miss_distance"])
        near_miss = dynamic_clearance < near_miss_distance and not collision
        return {
            "scenario_id": self._scenario.scenario_id,
            "family": self._scenario.family,
            "seed": self._scenario.seed,
            "step_count": self._step_count,
            "time_s": self._time_s,
            "min_clearance": self._min_clearance,
            "current_clearance": self._compute_min_clearance(),
            "collision": collision,
            "near_miss": near_miss,
            "risk_exposure_increment": self._risk_exposure_increment(dynamic_clearance),
            "shield_intervention": False,
            "shield_intervention_placeholder": True,
            "path_length": self._path_length,
            "active_intents": {
                obj.object_id: obj.intent.name
                for obj in self._objects
            },
        }

    def _risk_exposure_increment(self, dynamic_clearance: float) -> float:
        assert self._scenario is not None
        threshold = float(self._scenario.spec["risk"]["near_miss_distance"])
        if dynamic_clearance >= threshold:
            return 0.0
        return (threshold - dynamic_clearance) * self.config.dt

    def _compute_min_clearance(self) -> float:
        assert self._scenario is not None
        static_clearance = min_static_clearance(
            self._ego_position,
            float(self._scenario.spec["ego"]["radius"]),
            self._scenario.spec["map"].get("static_obstacles", []),
        )
        return min(static_clearance, self._compute_dynamic_clearance())

    def _compute_dynamic_clearance(self) -> float:
        assert self._scenario is not None
        ego_radius = float(self._scenario.spec["ego"]["radius"])
        if not self._objects:
            return float("inf")
        return min(
            clearance_between_circles(
                self._ego_position,
                ego_radius,
                obj.position,
                obj.radius,
            )
            for obj in self._objects
        )

    def _nearest_object(self) -> DynamicObjectState | None:
        if not self._objects:
            return None
        return min(self._objects, key=lambda obj: distance(self._ego_position, obj.position))

    def _require_reset(self) -> None:
        if self._scenario is None:
            raise RuntimeError("reset() must be called before step() or render()")

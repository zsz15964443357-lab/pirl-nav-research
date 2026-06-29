"""Lightweight validators for Stage 1 scenario specifications.

These checks intentionally cover only repository contracts. They do not
simulate motion, generate rollouts, or decide whether a scenario is approved.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CORE_FAMILIES = {
    "latent_start",
    "occlusion_emergence",
    "multi_intent_crossing",
    "narrow_passage_yield",
    "vehicle_forklift_launch",
    "crowd_robot_flow",
}

DIFFICULTIES = {"easy", "medium", "hard"}
REVIEW_STATUSES = {"candidate", "needs_revision", "approved", "rejected"}


class ScenarioValidationError(ValueError):
    """Raised when a scenario or manifest violates the repository contract."""


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ScenarioValidationError(f"{path}: expected a YAML mapping")
    return payload


def validate_scenario_spec(spec: dict[str, Any], *, source: str = "<memory>") -> None:
    _require_string(spec, "scenario_id", source)
    family = _require_string(spec, "family", source)
    if family not in CORE_FAMILIES:
        raise ScenarioValidationError(f"{source}: unknown core family {family!r}")

    difficulty = _require_string(spec, "difficulty", source)
    if difficulty not in DIFFICULTIES:
        raise ScenarioValidationError(f"{source}: invalid difficulty {difficulty!r}")

    seed = spec.get("seed")
    if not isinstance(seed, int):
        raise ScenarioValidationError(f"{source}: seed must be an integer")

    _validate_map(_require_mapping(spec, "map", source), source)
    _validate_ego(_require_mapping(spec, "ego", source), source)
    _validate_objects(_require_list(spec, "objects", source), source)
    _validate_risk(_require_mapping(spec, "risk", source), source)
    _validate_review(_require_mapping(spec, "review", source), source)


def validate_manifest(
    manifest: dict[str, Any],
    *,
    repo_root: Path,
    source: str = "<memory>",
) -> None:
    _require_string(manifest, "manifest_id", source)
    purpose = _require_string(manifest, "purpose", source)
    if purpose not in {"candidate", "train", "validation", "fixed_test"}:
        raise ScenarioValidationError(f"{source}: invalid purpose {purpose!r}")

    metrics_contract = _require_string(manifest, "metrics_contract", source)
    if not (repo_root / metrics_contract).is_file():
        raise ScenarioValidationError(
            f"{source}: metrics_contract does not exist: {metrics_contract}"
        )

    scenario_specs = _require_list(manifest, "scenario_specs", source)
    if not scenario_specs:
        raise ScenarioValidationError(f"{source}: scenario_specs must not be empty")

    seen_families: set[str] = set()
    for index, entry in enumerate(scenario_specs):
        if not isinstance(entry, dict):
            raise ScenarioValidationError(f"{source}: scenario_specs[{index}] must be a mapping")

        scenario_path = _require_string(entry, "path", f"{source}:scenario_specs[{index}]")
        full_path = repo_root / scenario_path
        if not full_path.is_file():
            raise ScenarioValidationError(
                f"{source}: scenario path does not exist: {scenario_path}"
            )

        spec = load_yaml_file(full_path)
        validate_scenario_spec(spec, source=scenario_path)

        for key in ("family", "difficulty", "seed"):
            if entry.get(key) != spec.get(key):
                raise ScenarioValidationError(
                    f"{source}: {scenario_path} manifest {key}={entry.get(key)!r} "
                    f"does not match spec {key}={spec.get(key)!r}"
                )
        review_status = entry.get("review_status")
        actual_status = _require_mapping(spec, "review", scenario_path).get("status")
        if review_status != actual_status:
            raise ScenarioValidationError(
                f"{source}: {scenario_path} manifest review_status={review_status!r} "
                f"does not match spec review.status={actual_status!r}"
            )
        seen_families.add(str(entry["family"]))

    missing = CORE_FAMILIES - seen_families
    if purpose == "candidate" and missing:
        missing_text = ", ".join(sorted(missing))
        raise ScenarioValidationError(
            f"{source}: candidate manifest missing families: {missing_text}"
        )


def _validate_map(section: dict[str, Any], source: str) -> None:
    size = section.get("size")
    if not _is_number_pair(size):
        raise ScenarioValidationError(f"{source}: map.size must be a numeric pair")
    obstacles = section.get("static_obstacles")
    if not isinstance(obstacles, list):
        raise ScenarioValidationError(f"{source}: map.static_obstacles must be a list")


def _validate_ego(section: dict[str, Any], source: str) -> None:
    for key in ("start", "goal"):
        if not _is_number_pair(section.get(key)):
            raise ScenarioValidationError(f"{source}: ego.{key} must be a numeric pair")
    for key in ("radius", "nominal_speed"):
        if not _is_positive_number(section.get(key)):
            raise ScenarioValidationError(f"{source}: ego.{key} must be positive")


def _validate_objects(objects: list[Any], source: str) -> None:
    if not objects:
        raise ScenarioValidationError(f"{source}: objects must not be empty")

    has_conflicting_intent = False
    for index, item in enumerate(objects):
        if not isinstance(item, dict):
            raise ScenarioValidationError(f"{source}: objects[{index}] must be a mapping")
        prefix = f"{source}:objects[{index}]"
        _require_string(item, "id", prefix)
        _require_string(item, "class", prefix)

        initial_state = _require_mapping(item, "initial_state", prefix)
        if not _is_number_pair(initial_state.get("position")):
            raise ScenarioValidationError(
                f"{prefix}: initial_state.position must be a numeric pair"
            )
        if not _is_number_pair(initial_state.get("velocity")):
            raise ScenarioValidationError(
                f"{prefix}: initial_state.velocity must be a numeric pair"
            )

        candidates = _require_list(item, "intent_candidates", prefix)
        if len(candidates) < 2:
            raise ScenarioValidationError(
                f"{prefix}: intent_candidates must contain at least 2 modes"
            )

        probability_sum = 0.0
        for candidate_index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                raise ScenarioValidationError(
                    f"{prefix}: intent_candidates[{candidate_index}] must be a mapping"
                )
            candidate_prefix = f"{prefix}:intent_candidates[{candidate_index}]"
            _require_string(candidate, "name", candidate_prefix)
            probability = candidate.get("probability")
            if not isinstance(probability, int | float) or probability < 0.0:
                raise ScenarioValidationError(
                    f"{candidate_prefix}: probability must be non-negative"
                )
            probability_sum += float(probability)
            has_conflicting_intent = has_conflicting_intent or bool(
                candidate.get("conflicts_with_ego_nominal_path")
            )

        if abs(probability_sum - 1.0) > 1e-6:
            raise ScenarioValidationError(
                f"{prefix}: intent candidate probabilities must sum to 1.0"
            )

    if not has_conflicting_intent:
        raise ScenarioValidationError(
            f"{source}: at least one intent candidate must conflict with ego nominal path"
        )


def _validate_risk(section: dict[str, Any], source: str) -> None:
    required_keys = (
        "min_clearance",
        "near_miss_distance",
        "exposure_horizon",
        "shield_trigger_distance",
    )
    for key in required_keys:
        if not _is_positive_number(section.get(key)):
            raise ScenarioValidationError(f"{source}: risk.{key} must be positive")


def _validate_review(section: dict[str, Any], source: str) -> None:
    status = _require_string(section, "status", source)
    if status not in REVIEW_STATUSES:
        raise ScenarioValidationError(f"{source}: invalid review.status {status!r}")


def _require_mapping(section: dict[str, Any], key: str, source: str) -> dict[str, Any]:
    value = section.get(key)
    if not isinstance(value, dict):
        raise ScenarioValidationError(f"{source}: {key} must be a mapping")
    return value


def _require_list(section: dict[str, Any], key: str, source: str) -> list[Any]:
    value = section.get(key)
    if not isinstance(value, list):
        raise ScenarioValidationError(f"{source}: {key} must be a list")
    return value


def _require_string(section: dict[str, Any], key: str, source: str) -> str:
    value = section.get(key)
    if not isinstance(value, str) or not value:
        raise ScenarioValidationError(f"{source}: {key} must be a non-empty string")
    return value


def _is_number_pair(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int | float) for item in value)
    )


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, int | float) and value > 0

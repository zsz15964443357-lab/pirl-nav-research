"""Load reviewed Stage 2 scenarios for the Stage 3 environment gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pirl_nav.scenarios import load_yaml_file, validate_scenario_spec


@dataclass(frozen=True)
class ReviewedScenario:
    """Scenario specification plus reviewed-manifest metadata."""

    path: Path
    spec: dict[str, Any]
    review_status: str
    review_decision: str

    @property
    def scenario_id(self) -> str:
        return str(self.spec["scenario_id"])

    @property
    def family(self) -> str:
        return str(self.spec["family"])

    @property
    def seed(self) -> int:
        return int(self.spec["seed"])


def load_reviewed_scenarios(repo_root: Path, manifest_path: Path) -> list[ReviewedScenario]:
    """Load scenarios approved only for Stage 3 environment integration."""

    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    manifest = load_yaml_file(manifest_path)
    source = str(manifest_path.relative_to(repo_root))

    if manifest.get("purpose") != "reviewed":
        raise ValueError(f"{source}: expected purpose='reviewed'")
    if manifest.get("status") != "human_reviewed":
        raise ValueError(f"{source}: expected status='human_reviewed'")

    entries = manifest.get("scenario_specs")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{source}: scenario_specs must be a non-empty list")

    scenarios: list[ReviewedScenario] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"{source}: scenario_specs[{index}] must be a mapping")
        if entry.get("review_status") != "approved_for_stage3":
            raise ValueError(
                f"{source}: scenario_specs[{index}] is not approved_for_stage3"
            )
        if entry.get("review_decision") != "approved":
            raise ValueError(f"{source}: scenario_specs[{index}] is not approved")

        scenario_path_text = entry.get("path")
        if not isinstance(scenario_path_text, str) or not scenario_path_text:
            raise ValueError(f"{source}: scenario_specs[{index}].path must be a string")
        scenario_path = repo_root / scenario_path_text
        spec = load_yaml_file(scenario_path)
        validate_scenario_spec(spec, source=scenario_path_text)

        for key in ("family", "difficulty", "seed"):
            if entry.get(key) != spec.get(key):
                raise ValueError(
                    f"{source}: {scenario_path_text} manifest {key}={entry.get(key)!r} "
                    f"does not match spec {key}={spec.get(key)!r}"
                )

        scenarios.append(
            ReviewedScenario(
                path=scenario_path,
                spec=spec,
                review_status=str(entry["review_status"]),
                review_decision=str(entry["review_decision"]),
            )
        )

    return scenarios

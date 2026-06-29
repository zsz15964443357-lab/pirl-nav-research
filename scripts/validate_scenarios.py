"""Validate Stage 1 scenario specs and manifests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pirl_nav.scenarios import (  # noqa: E402
    CORE_FAMILIES,
    ScenarioValidationError,
    load_yaml_file,
    validate_manifest,
    validate_scenario_spec,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    scenario_dir = repo_root / "experiments" / "scenario_specs"
    manifest_dir = repo_root / "experiments" / "manifests"

    try:
        families = set()
        for path in sorted(scenario_dir.glob("*.yaml")):
            spec = load_yaml_file(path)
            validate_scenario_spec(spec, source=str(path.relative_to(repo_root)))
            families.add(spec["family"])

        missing = CORE_FAMILIES - families
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ScenarioValidationError(f"scenario specs missing core families: {missing_text}")

        for path in sorted(manifest_dir.glob("candidate_*.yaml")):
            manifest = load_yaml_file(path)
            validate_manifest(
                manifest,
                repo_root=repo_root,
                source=str(path.relative_to(repo_root)),
            )
    except ScenarioValidationError as exc:
        print(f"scenario validation failed: {exc}")
        return 1

    print("scenario validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

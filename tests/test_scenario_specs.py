from pathlib import Path

from pirl_nav.scenarios import (
    CORE_FAMILIES,
    load_yaml_file,
    validate_manifest,
    validate_scenario_spec,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_all_stage1_scenario_specs_are_valid_candidates() -> None:
    scenario_paths = sorted((REPO_ROOT / "experiments" / "scenario_specs").glob("*.yaml"))
    assert scenario_paths

    families = set()
    for path in scenario_paths:
        spec = load_yaml_file(path)
        validate_scenario_spec(spec, source=str(path.relative_to(REPO_ROOT)))
        assert spec["review"]["status"] == "candidate"
        families.add(spec["family"])

    assert families == CORE_FAMILIES


def test_candidate_manifest_matches_scenario_specs() -> None:
    manifest_path = REPO_ROOT / "experiments" / "manifests" / "candidate_stage1_2026-06-29.yaml"
    manifest = load_yaml_file(manifest_path)

    validate_manifest(
        manifest,
        repo_root=REPO_ROOT,
        source=str(manifest_path.relative_to(REPO_ROOT)),
    )
    assert manifest["purpose"] == "candidate"
    assert manifest["commit"]
    assert {entry["family"] for entry in manifest["scenario_specs"]} == CORE_FAMILIES

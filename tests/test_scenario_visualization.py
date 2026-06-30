import json
from pathlib import Path

import yaml

from pirl_nav.visualization import render_review_artifacts

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage2_review_artifacts_are_generated(tmp_path: Path) -> None:
    artifacts = render_review_artifacts(
        repo_root=REPO_ROOT,
        manifest_path=REPO_ROOT
        / "experiments"
        / "manifests"
        / "candidate_stage1_2026-06-29.yaml",
        output_dir=tmp_path,
    )

    assert len(artifacts) == 6
    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "reviewed_stage2_draft.yaml").is_file()

    draft = yaml.safe_load((tmp_path / "reviewed_stage2_draft.yaml").read_text())
    assert draft["status"] == "draft"
    assert all(entry["review_status"] == "candidate" for entry in draft["scenario_specs"])
    assert all(
        entry["review_decision"] == "needs_human_review"
        for entry in draft["scenario_specs"]
    )

    for artifact in artifacts:
        assert artifact.layout_svg.is_file()
        assert artifact.timeline_svg.is_file()
        summary = json.loads(artifact.summary_json.read_text())
        assert summary["review_status"] == "candidate"
        assert summary["human_review_required"] is True
        assert summary["auto_approval"] is False
        assert summary["conflicting_intent_count"] >= 1

"""Generate Stage 2 scenario review artifacts.

The renderer intentionally uses HTML/SVG instead of a plotting dependency. Stage 2
needs deterministic review artifacts, not a simulation or rollout visualizer.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from pirl_nav.scenarios import load_yaml_file, validate_manifest, validate_scenario_spec


@dataclass(frozen=True)
class ReviewArtifact:
    """Paths generated for one scenario."""

    scenario_id: str
    scenario_dir: Path
    layout_svg: Path
    timeline_svg: Path
    summary_json: Path


def render_review_artifacts(
    *,
    repo_root: Path,
    manifest_path: Path,
    output_dir: Path,
) -> list[ReviewArtifact]:
    """Render all scenario review artifacts for a candidate manifest."""

    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    output_dir = output_dir.resolve()

    manifest = load_yaml_file(manifest_path)
    validate_manifest(
        manifest,
        repo_root=repo_root,
        source=str(manifest_path.relative_to(repo_root)),
    )

    artifacts: list[ReviewArtifact] = []
    for entry in manifest["scenario_specs"]:
        scenario_path = repo_root / entry["path"]
        spec = load_yaml_file(scenario_path)
        validate_scenario_spec(spec, source=entry["path"])

        scenario_dir = output_dir / spec["scenario_id"]
        scenario_dir.mkdir(parents=True, exist_ok=True)

        layout_svg = scenario_dir / "layout.svg"
        timeline_svg = scenario_dir / "timeline.svg"
        summary_json = scenario_dir / "summary.json"

        layout_svg.write_text(_render_layout_svg(spec), encoding="utf-8")
        timeline_svg.write_text(_render_timeline_svg(spec), encoding="utf-8")
        summary_json.write_text(
            json.dumps(_build_summary(spec), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        artifacts.append(
            ReviewArtifact(
                scenario_id=spec["scenario_id"],
                scenario_dir=scenario_dir,
                layout_svg=layout_svg,
                timeline_svg=timeline_svg,
                summary_json=summary_json,
            )
        )

    _write_index(output_dir, manifest, artifacts)
    _write_reviewed_manifest_draft(output_dir, manifest)
    return artifacts


def _render_layout_svg(spec: dict[str, Any]) -> str:
    width = 900
    height = 620
    margin = 70
    map_width, map_height = _number_pair(spec["map"]["size"])

    def sx(x: float) -> float:
        return margin + (x / map_width) * (width - 2 * margin)

    def sy(y: float) -> float:
        return height - margin - (y / map_height) * (height - 2 * margin)

    elements = [
        _svg_header(width, height, f"Layout: {spec['scenario_id']}"),
        f'<rect x="{margin}" y="{margin}" width="{width - 2 * margin}" '
        f'height="{height - 2 * margin}" fill="#fbfbfb" stroke="#222" stroke-width="2"/>',
    ]

    for obstacle in spec["map"].get("static_obstacles", []):
        center = _number_pair(obstacle["center"])
        size = _number_pair(obstacle["size"])
        x = sx(center[0] - size[0] / 2)
        y = sy(center[1] + size[1] / 2)
        w = (size[0] / map_width) * (width - 2 * margin)
        h = (size[1] / map_height) * (height - 2 * margin)
        fill = "#111111" if _is_occluder(obstacle) else "#9ca3af"
        elements.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" opacity="0.85"><title>{_esc(obstacle["id"])}</title></rect>'
        )

    start = _number_pair(spec["ego"]["start"])
    goal = _number_pair(spec["ego"]["goal"])
    corridor = spec["risk"]["near_miss_distance"]
    corridor_px = (corridor / map_height) * (height - 2 * margin)
    elements.append(
        f'<line x1="{sx(start[0]):.1f}" y1="{sy(start[1]):.1f}" '
        f'x2="{sx(goal[0]):.1f}" y2="{sy(goal[1]):.1f}" '
        'stroke="#2563eb" stroke-width="3" stroke-dasharray="8 8"/>'
    )
    elements.append(
        f'<line x1="{sx(start[0]):.1f}" y1="{sy(start[1]):.1f}" '
        f'x2="{sx(goal[0]):.1f}" y2="{sy(goal[1]):.1f}" '
        f'stroke="#93c5fd" stroke-width="{max(corridor_px, 4):.1f}" '
        'stroke-opacity="0.22"/>'
    )
    elements.append(_circle(sx(start[0]), sy(start[1]), 8, "#2563eb", "UAV start"))
    elements.append(_star(sx(goal[0]), sy(goal[1]), "Goal"))

    for obj in spec["objects"]:
        pos = _number_pair(obj["initial_state"]["position"])
        has_conflict = any(
            bool(candidate.get("conflicts_with_ego_nominal_path"))
            for candidate in obj["intent_candidates"]
        )
        fill = "#dc2626" if has_conflict else "#f97316"
        elements.append(_circle(sx(pos[0]), sy(pos[1]), 7, fill, f"{obj['id']} ({obj['class']})"))

        for candidate in obj["intent_candidates"]:
            target = candidate.get("target")
            if not _is_number_pair(target):
                continue
            target_pair = _number_pair(target)
            stroke = "#dc2626" if candidate.get("conflicts_with_ego_nominal_path") else "#f97316"
            elements.append(
                f'<line x1="{sx(pos[0]):.1f}" y1="{sy(pos[1]):.1f}" '
                f'x2="{sx(target_pair[0]):.1f}" y2="{sy(target_pair[1]):.1f}" '
                f'stroke="{stroke}" stroke-width="2" marker-end="url(#arrow)"/>'
            )
            elements.append(
                _circle(sx(target_pair[0]), sy(target_pair[1]), 4, stroke, candidate["name"])
            )

    elements.append(_layout_legend(width, height))
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def _render_timeline_svg(spec: dict[str, Any]) -> str:
    width = 920
    row_height = 36
    header_height = 76
    rows = sum(len(obj["intent_candidates"]) for obj in spec["objects"])
    height = header_height + rows * row_height + 70
    left = 250
    right = 860
    max_time = max(6.0, float(spec["risk"]["exposure_horizon"]))

    def tx(value: float) -> float:
        return left + (value / max_time) * (right - left)

    elements = [
        _svg_header(width, height, f"Intent timeline: {spec['scenario_id']}"),
        f'<line x1="{left}" y1="54" x2="{right}" y2="54" stroke="#111" stroke-width="2"/>',
    ]
    for second in range(int(max_time) + 1):
        x = tx(float(second))
        elements.append(f'<line x1="{x:.1f}" y1="48" x2="{x:.1f}" y2="60" stroke="#111"/>')
        elements.append(
            f'<text x="{x:.1f}" y="38" text-anchor="middle" '
            f'font-size="11">{second}s</text>'
        )

    y = header_height
    for obj in spec["objects"]:
        for candidate in obj["intent_candidates"]:
            conflict = bool(candidate.get("conflicts_with_ego_nominal_path"))
            stroke = "#dc2626" if conflict else "#f97316"
            label = f"{obj['id']} / {candidate['name']} p={candidate['probability']}"
            elements.append(
                f'<text x="20" y="{y + 18}" font-size="12" fill="#111">{_esc(label)}</text>'
            )
            elements.append(
                f'<line x1="{left}" y1="{y + 14}" x2="{right}" y2="{y + 14}" '
                'stroke="#e5e7eb" stroke-width="8"/>'
            )

            trigger = candidate.get("trigger_time")
            if _is_number_pair(trigger):
                start, end = _number_pair(trigger)
                elements.append(
                    f'<rect x="{tx(start):.1f}" y="{y + 7}" '
                    f'width="{max(tx(end) - tx(start), 2):.1f}" height="14" '
                    f'fill="{stroke}" opacity="0.55"><title>trigger window</title></rect>'
                )
            else:
                elements.append(
                    f'<circle cx="{tx(0):.1f}" cy="{y + 14}" r="5" fill="{stroke}">'
                    "<title>active from reset or no trigger window</title></circle>"
                )

            if conflict:
                elements.append(
                    f'<text x="{right + 12}" y="{y + 18}" font-size="12" fill="#dc2626">'
                    "conflict</text>"
                )
            y += row_height

    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def _build_summary(spec: dict[str, Any]) -> dict[str, Any]:
    conflicting = [
        {"object_id": obj["id"], "intent": candidate["name"]}
        for obj in spec["objects"]
        for candidate in obj["intent_candidates"]
        if candidate.get("conflicts_with_ego_nominal_path")
    ]
    return {
        "scenario_id": spec["scenario_id"],
        "family": spec["family"],
        "difficulty": spec["difficulty"],
        "seed": spec["seed"],
        "review_status": spec["review"]["status"],
        "object_count": len(spec["objects"]),
        "conflicting_intent_count": len(conflicting),
        "conflicting_intents": conflicting,
        "risk": spec["risk"],
        "human_review_required": True,
        "auto_approval": False,
        "recommended_review_decision": "needs_human_review",
    }


def _write_index(
    output_dir: Path,
    manifest: dict[str, Any],
    artifacts: list[ReviewArtifact],
) -> None:
    rows = []
    for artifact in artifacts:
        summary = json.loads(artifact.summary_json.read_text(encoding="utf-8"))
        rel = artifact.scenario_dir.name
        rows.append(
            "<tr>"
            f"<td>{_esc(summary['scenario_id'])}</td>"
            f"<td>{_esc(summary['family'])}</td>"
            f"<td>{_esc(summary['difficulty'])}</td>"
            f"<td>{summary['seed']}</td>"
            f"<td>{_esc(summary['review_status'])}</td>"
            f'<td><a href="{rel}/layout.svg">layout</a></td>'
            f'<td><a href="{rel}/timeline.svg">timeline</a></td>'
            f'<td><a href="{rel}/summary.json">summary</a></td>'
            "</tr>"
        )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>PIRL-Nav Stage 2 Scenario Review</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>PIRL-Nav Stage 2 Scenario Review</h1>
  <p>Manifest: <code>{_esc(manifest['manifest_id'])}</code></p>
  <p>Status: candidate artifacts only. No scenario is approved by this script.</p>
  <table>
    <thead>
      <tr><th>Scenario</th><th>Family</th><th>Difficulty</th><th>Seed</th>
      <th>Status</th><th>Layout</th><th>Timeline</th><th>Summary</th></tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html_doc, encoding="utf-8")


def _write_reviewed_manifest_draft(output_dir: Path, manifest: dict[str, Any]) -> None:
    draft = {
        "manifest_id": "reviewed_stage2_draft",
        "created_from": manifest["manifest_id"],
        "purpose": "reviewed_draft",
        "status": "draft",
        "notes": "Human review required. This draft does not approve any scenario.",
        "scenario_specs": [
            {**entry, "review_status": "candidate", "review_decision": "needs_human_review"}
            for entry in manifest["scenario_specs"]
        ],
    }
    (output_dir / "reviewed_stage2_draft.yaml").write_text(
        yaml.safe_dump(draft, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _svg_header(width: int, height: int, title: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
viewBox="0 0 {width} {height}">
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
    <path d="M0,0 L0,6 L7,3 z" fill="context-stroke"/>
  </marker>
</defs>
<rect width="100%" height="100%" fill="white"/>
<text x="20" y="28" font-size="18" font-weight="700">{_esc(title)}</text>"""


def _layout_legend(width: int, height: int) -> str:
    x = width - 245
    y = height - 150
    star_points = (
        f"{x + 18},{y + 57} {x + 22},{y + 66} {x + 12},{y + 61} "
        f"{x + 24},{y + 61} {x + 14},{y + 66}"
    )
    return f"""
<g>
  <rect x="{x}" y="{y}" width="220" height="122" fill="white" stroke="#d1d5db"/>
  <text x="{x + 12}" y="{y + 22}" font-size="13" font-weight="700">Legend</text>
  <circle cx="{x + 18}" cy="{y + 42}" r="6" fill="#2563eb"/>
  <text x="{x + 32}" y="{y + 46}" font-size="12">UAV start</text>
  <polygon points="{star_points}" fill="#16a34a"/>
  <text x="{x + 32}" y="{y + 65}" font-size="12">Goal</text>
  <rect x="{x + 12}" y="{y + 76}" width="13" height="10" fill="#9ca3af"/>
  <text x="{x + 32}" y="{y + 86}" font-size="12">Static obstacle</text>
  <circle cx="{x + 18}" cy="{y + 103}" r="6" fill="#dc2626"/>
  <text x="{x + 32}" y="{y + 107}" font-size="12">Potential risk object</text>
</g>"""


def _circle(x: float, y: float, radius: int, fill: str, title: str) -> str:
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}" '
        f'stroke="white" stroke-width="1.5"><title>{_esc(title)}</title></circle>'
    )


def _star(x: float, y: float, title: str) -> str:
    points = [
        (x, y - 11),
        (x + 3, y - 3),
        (x + 11, y - 3),
        (x + 5, y + 2),
        (x + 7, y + 10),
        (x, y + 5),
        (x - 7, y + 10),
        (x - 5, y + 2),
        (x - 11, y - 3),
        (x - 3, y - 3),
    ]
    points_text = " ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    return f'<polygon points="{points_text}" fill="#16a34a"><title>{_esc(title)}</title></polygon>'


def _number_pair(value: Any) -> tuple[float, float]:
    if not _is_number_pair(value):
        raise ValueError(f"expected numeric pair, got {value!r}")
    return (float(value[0]), float(value[1]))


def _is_number_pair(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int | float) for item in value)
    )


def _is_occluder(obstacle: dict[str, Any]) -> bool:
    text = f"{obstacle.get('id', '')} {obstacle.get('shape', '')}".lower()
    return "occlud" in text or "wall" in text


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)

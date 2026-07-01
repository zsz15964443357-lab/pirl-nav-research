"""Dependency-light SVG visualizations for Stage 7 review artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

COLORS = [
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#ff7f0e",
    "#17becf",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
]


def write_line_chart(
    path: Path,
    *,
    title: str,
    series: dict[str, list[tuple[float, float]]],
    y_label: str,
) -> None:
    width, height = 900, 520
    margin_left, margin_top = 80, 52
    plot_width, plot_height = 760, 360
    all_points = [point for points in series.values() for point in points]
    x_values = [point[0] for point in all_points] or [0.0]
    y_values = [point[1] for point in all_points] or [0.0]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(0.0, min(y_values)), max(y_values)
    if x_min == x_max:
        x_max += 1.0
    if y_min == y_max:
        y_max += 1.0

    parts = _svg_header(width, height, title)
    parts.append(_axes(margin_left, margin_top, plot_width, plot_height, y_label))
    for index, (name, points) in enumerate(sorted(series.items())):
        color = COLORS[index % len(COLORS)]
        polyline = " ".join(
            f"{_scale(x, x_min, x_max, margin_left, plot_width):.1f},"
            f"{_scale_y(y, y_min, y_max, margin_top, plot_height):.1f}"
            for x, y in points
        )
        parts.append(
            f'<polyline points="{polyline}" fill="none" stroke="{color}" '
            'stroke-width="2.2" />'
        )
        legend_y = margin_top + index * 20
        parts.append(
            f'<rect x="690" y="{legend_y}" width="12" height="12" fill="{color}" />'
        )
        parts.append(
            f'<text x="708" y="{legend_y + 11}" font-size="12">{_escape(name)}</text>'
        )
    parts.append("</svg>\n")
    _write(path, "".join(parts))


def write_bar_chart(
    path: Path,
    *,
    title: str,
    values: dict[str, float],
    y_label: str,
) -> None:
    width, height = 980, 560
    margin_left, margin_top = 80, 56
    plot_width, plot_height = 840, 330
    max_value = max(values.values()) if values else 1.0
    max_value = max(max_value, 1e-6)
    parts = _svg_header(width, height, title)
    parts.append(_axes(margin_left, margin_top, plot_width, plot_height, y_label))
    bar_width = plot_width / max(len(values), 1) * 0.72
    for index, (name, value) in enumerate(sorted(values.items())):
        x = margin_left + index * (plot_width / max(len(values), 1)) + bar_width * 0.2
        bar_height = (value / max_value) * plot_height
        y = margin_top + plot_height - bar_height
        color = COLORS[index % len(COLORS)]
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
            f'height="{bar_height:.1f}" fill="{color}" />'
        )
        parts.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{margin_top + plot_height + 18}" '
            'font-size="10" text-anchor="end" transform="rotate(-35 '
            f'{x + bar_width / 2:.1f},{margin_top + plot_height + 18})">'
            f'{_escape(name)}</text>'
        )
    parts.append("</svg>\n")
    _write(path, "".join(parts))


def write_rollout_svg(
    path: Path,
    *,
    title: str,
    scenario: dict[str, Any],
    ego_path: list[tuple[float, float]],
    shield_points: list[tuple[float, float]],
) -> None:
    width, height = 760, 520
    map_width, map_height = scenario["map"]["size"]
    parts = _svg_header(width, height, title)
    parts.append('<rect x="60" y="55" width="620" height="360" fill="#fbfbfb" stroke="#333" />')
    for obstacle in scenario["map"].get("static_obstacles", []):
        center = obstacle["center"]
        size = obstacle["size"]
        x = _map_x(center[0] - size[0] / 2, map_width)
        y = _map_y(center[1] + size[1] / 2, map_height)
        w = size[0] / map_width * 620
        h = size[1] / map_height * 360
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" fill="#999" />'
        )
    for obj in scenario["objects"]:
        pos = obj["initial_state"]["position"]
        x, y = _map_x(pos[0], map_width), _map_y(pos[1], map_height)
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" '
            'fill="#d62728" opacity="0.75" />'
        )
        risk_radius = scenario["risk"]["near_miss_distance"] / map_width * 620
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{risk_radius:.1f}" '
            'fill="none" stroke="#d62728" stroke-dasharray="4 3" />'
        )
    start = scenario["ego"]["start"]
    goal = scenario["ego"]["goal"]
    start_x = _map_x(start[0], map_width)
    start_y = _map_y(start[1], map_height)
    goal_x = _map_x(goal[0], map_width)
    goal_y = _map_y(goal[1], map_height)
    parts.append(
        f'<circle cx="{start_x:.1f}" cy="{start_y:.1f}" '
        'r="7" fill="#2ca02c" />'
    )
    parts.append(
        f'<rect x="{goal_x - 7:.1f}" y="{goal_y - 7:.1f}" '
        'width="14" height="14" fill="#1f77b4" />'
    )
    if ego_path:
        points = " ".join(
            f"{_map_x(x, map_width):.1f},{_map_y(y, map_height):.1f}"
            for x, y in ego_path
        )
        parts.append(
            f'<polyline points="{points}" fill="none" '
            'stroke="#111" stroke-width="2.5" />'
        )
    for point in shield_points:
        parts.append(
            f'<circle cx="{_map_x(point[0], map_width):.1f}" '
            f'cy="{_map_y(point[1], map_height):.1f}" '
            'r="5" fill="#ff7f0e" />'
        )
    parts.append(
        '<text x="60" y="450" font-size="13">'
        'green=start, blue=goal, red=latent-risk object, orange=shield intervention'
        '</text>'
    )
    parts.append("</svg>\n")
    _write(path, "".join(parts))


def _svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" ',
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white" />',
        f'<text x="40" y="32" font-size="20" font-weight="700">{_escape(title)}</text>',
    ]


def _axes(x: int, y: int, width: int, height: int, y_label: str) -> str:
    return (
        f'<line x1="{x}" y1="{y + height}" x2="{x + width}" '
        f'y2="{y + height}" stroke="#333" />'
        f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + height}" stroke="#333" />'
        f'<text x="{x - 58}" y="{y + 18}" font-size="12">{_escape(y_label)}</text>'
    )


def _scale(value: float, low: float, high: float, offset: int, span: int) -> float:
    return offset + (value - low) / (high - low) * span


def _scale_y(value: float, low: float, high: float, offset: int, span: int) -> float:
    return offset + span - (value - low) / (high - low) * span


def _map_x(value: float, map_width: float) -> float:
    return 60 + value / map_width * 620


def _map_y(value: float, map_height: float) -> float:
    return 55 + 360 - value / map_height * 360


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

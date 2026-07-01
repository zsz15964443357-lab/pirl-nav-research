"""Aggregation utilities for Stage 4 episode records."""

from __future__ import annotations

from collections.abc import Iterable
from statistics import mean, stdev
from typing import Any

from pirl_nav.evaluation.records import EpisodeRecord

NUMERIC_MEAN_FIELDS = (
    "steps",
    "near_miss_count",
    "min_clearance",
    "average_clearance",
    "path_length",
    "detour_ratio",
    "risk_exposure",
    "jerk_proxy",
    "active_time",
    "shield_intervention_count",
    "shield_intervention_rate",
)


def aggregate_records(records: list[EpisodeRecord]) -> dict[str, Any]:
    return {
        "schema": "pirl_nav_stage4_summary_v1",
        "policy_note": "random and scripted policies are smoke policies, not learned baselines",
        "risk_exposure_note": (
            "risk_exposure is a geometric proxy, not final action-conditioned predictive risk"
        ),
        "overall": summarize_group(records),
        "per_family": _group(records, "family"),
        "per_difficulty": _group(records, "difficulty"),
        "per_policy_type": _group(records, "policy_type"),
    }


def summarize_group(records: list[EpisodeRecord]) -> dict[str, Any]:
    count = len(records)
    if count == 0:
        return {"episodes": 0}

    summary: dict[str, Any] = {
        "episodes": count,
        "success_rate": _rate(record.success for record in records),
        "collision_rate": _rate(record.collision for record in records),
        "timeout_rate": _rate(record.truncated for record in records),
        "near_miss_rate": _rate(record.near_miss for record in records),
    }
    for field in NUMERIC_MEAN_FIELDS:
        values = [float(getattr(record, field)) for record in records]
        summary[f"{field}_mean"] = mean(values)
        summary[f"{field}_std"] = stdev(values) if len(values) > 1 else 0.0
        summary[f"{field}_min"] = min(values)
        summary[f"{field}_max"] = max(values)
    return summary


def _group(records: list[EpisodeRecord], field: str) -> dict[str, Any]:
    groups: dict[str, list[EpisodeRecord]] = {}
    for record in records:
        groups.setdefault(str(getattr(record, field)), []).append(record)
    return {key: summarize_group(value) for key, value in sorted(groups.items())}


def _rate(values: Iterable[bool]) -> float:
    value_list = list(values)
    if not value_list:
        return 0.0
    return sum(1 for value in value_list if value) / len(value_list)

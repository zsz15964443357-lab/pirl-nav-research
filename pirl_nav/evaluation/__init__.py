"""Evaluation and metric aggregation helpers."""

from pirl_nav.evaluation.aggregation import aggregate_records, summarize_group
from pirl_nav.evaluation.metrics import (
    average_clearance,
    detour_ratio,
    jerk_proxy,
    shield_intervention_rate,
    success_from_done,
)
from pirl_nav.evaluation.records import EPISODE_RECORD_FIELDS, EpisodeRecord
from pirl_nav.evaluation.runner import EvaluationConfig, load_evaluation_config, run_evaluation

__all__ = [
    "EPISODE_RECORD_FIELDS",
    "EpisodeRecord",
    "EvaluationConfig",
    "aggregate_records",
    "average_clearance",
    "detour_ratio",
    "jerk_proxy",
    "load_evaluation_config",
    "run_evaluation",
    "shield_intervention_rate",
    "success_from_done",
    "summarize_group",
]

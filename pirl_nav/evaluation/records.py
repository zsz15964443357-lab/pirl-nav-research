"""Episode record schema for Stage 4 evaluation outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class EpisodeRecord:
    experiment_id: str
    commit: str
    stage: int
    scenario_id: str
    family: str
    difficulty: str
    seed: int
    run_mode: str
    policy_type: str
    steps: int
    terminated: bool
    truncated: bool
    success: bool
    collision: bool
    near_miss: bool
    near_miss_count: int
    min_clearance: float
    average_clearance: float
    path_length: float
    detour_ratio: float
    risk_exposure: float
    risk_exposure_is_proxy: bool
    jerk_proxy: float
    active_time: float
    shield_intervention_count: int
    shield_intervention_rate: float
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


EPISODE_RECORD_FIELDS = tuple(EpisodeRecord.__dataclass_fields__)

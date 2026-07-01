"""Serializable latent intent state for Stage 6 PIRL-Nav skeleton."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log2
from typing import Any


@dataclass(frozen=True)
class CandidateIntent:
    name: str
    probability: float
    conflicts_with_ego_nominal_path: bool
    target: tuple[float, float] | None = None
    trigger_time: tuple[float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntentState:
    object_id: str
    object_class: str
    scenario_family: str
    history_window: int
    candidate_intents: tuple[CandidateIntent, ...]
    prediction_horizon: float
    is_placeholder: bool
    notes: str
    relative_position: tuple[float, float] = (0.0, 0.0)
    relative_velocity: tuple[float, float] = (0.0, 0.0)

    @property
    def intent_probabilities(self) -> tuple[float, ...]:
        return tuple(intent.probability for intent in self.candidate_intents)

    @property
    def intent_entropy(self) -> float:
        entropy = 0.0
        for probability in self.intent_probabilities:
            if probability > 0.0:
                entropy -= probability * log2(probability)
        return entropy

    @property
    def conflict_probability(self) -> float:
        return sum(
            intent.probability
            for intent in self.candidate_intents
            if intent.conflicts_with_ego_nominal_path
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["intent_probabilities"] = list(self.intent_probabilities)
        payload["intent_entropy"] = self.intent_entropy
        payload["conflict_probability"] = self.conflict_probability
        return payload


def candidate_from_spec(raw_candidate: dict[str, Any]) -> CandidateIntent:
    raw_trigger = raw_candidate.get("trigger_time")
    trigger_time = None
    if isinstance(raw_trigger, list) and len(raw_trigger) == 2:
        trigger_time = (float(raw_trigger[0]), float(raw_trigger[1]))

    raw_target = raw_candidate.get("target")
    target = None
    if isinstance(raw_target, list) and len(raw_target) == 2:
        target = (float(raw_target[0]), float(raw_target[1]))

    return CandidateIntent(
        name=str(raw_candidate["name"]),
        probability=float(raw_candidate["probability"]),
        conflicts_with_ego_nominal_path=bool(
            raw_candidate.get("conflicts_with_ego_nominal_path")
        ),
        target=target,
        trigger_time=trigger_time,
    )

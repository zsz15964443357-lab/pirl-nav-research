"""Intent predictor interface and deterministic Stage 6 placeholder."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from pirl_nav.method.intent_state import IntentState, candidate_from_spec
from pirl_nav.sim.geometry import as_point


class HeuristicIntentPredictor:
    """Placeholder predictor preserving the future GRU interface.

    This is not a trained GRU intent predictor and must not be reported as the
    final paper intent model.
    """

    def __init__(self, *, history_window: int, enabled: bool = True) -> None:
        self.history_window = history_window
        self.enabled = enabled
        self._states: list[IntentState] = []

    def reset(self, scenario: Any) -> None:
        spec = scenario.spec
        states: list[IntentState] = []
        for raw_object in spec["objects"]:
            position = as_point(raw_object["initial_state"]["position"])
            velocity = as_point(raw_object["initial_state"]["velocity"])
            candidates = tuple(
                candidate_from_spec(candidate)
                for candidate in raw_object["intent_candidates"]
            )
            if not self.enabled:
                uniform_probability = 1.0 / len(candidates)
                candidates = tuple(
                    replace(candidate, probability=uniform_probability)
                    for candidate in candidates
                )
            states.append(
                IntentState(
                    object_id=str(raw_object["id"]),
                    object_class=str(raw_object["class"]),
                    scenario_family=str(spec["family"]),
                    history_window=self.history_window,
                    candidate_intents=candidates,
                    prediction_horizon=float(spec["risk"]["exposure_horizon"]),
                    is_placeholder=True,
                    notes=(
                        "Heuristic Stage 6 placeholder; not a trained GRU intent predictor "
                        "and not final paper intent model."
                    ),
                    relative_position=position,
                    relative_velocity=velocity,
                )
            )
        self._states = states

    def update(self, observation: list[float], info: dict[str, Any]) -> None:
        if not self._states:
            return
        nearest_relative_position = (float(observation[6]), float(observation[7]))
        nearest_relative_velocity = (float(observation[8]), float(observation[9]))
        active_intents = info.get("active_intents", {})
        updated = []
        for index, state in enumerate(self._states):
            notes = state.notes
            if state.object_id in active_intents:
                notes = f"{notes} active_intent={active_intents[state.object_id]}"
            if index == 0:
                state = replace(
                    state,
                    relative_position=nearest_relative_position,
                    relative_velocity=nearest_relative_velocity,
                    notes=notes,
                )
            else:
                state = replace(state, notes=notes)
            updated.append(state)
        self._states = updated

    def predict(
        self,
        action_candidates: list[list[float]],
        horizon: float,
    ) -> list[IntentState]:
        return [
            replace(
                state,
                prediction_horizon=horizon,
                notes=f"{state.notes} action_candidates={len(action_candidates)}",
            )
            for state in self._states
        ]

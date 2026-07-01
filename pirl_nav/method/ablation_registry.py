"""Stage 6 method and ablation registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AblationSpec:
    name: str
    enabled_components: tuple[str, ...]
    disabled_components: tuple[str, ...]
    risk_mode: str
    constraint_mode: str
    shield_mode: str
    paper_claim_allowed: bool


ABLATION_REGISTRY: dict[str, AblationSpec] = {
    "full_pirl_nav_skeleton": AblationSpec(
        name="full_pirl_nav_skeleton",
        enabled_components=(
            "heuristic_intent_prediction_placeholder",
            "action_conditioned_proxy_risk",
            "constrained_objective_skeleton",
            "shield_internalization_placeholder",
        ),
        disabled_components=(),
        risk_mode="action_conditioned_proxy",
        constraint_mode="lagrangian_placeholder",
        shield_mode="interface_with_internalization_placeholder",
        paper_claim_allowed=False,
    ),
    "no_intent_prediction": AblationSpec(
        name="no_intent_prediction",
        enabled_components=(
            "uniform_intent_placeholder",
            "action_conditioned_proxy_risk",
            "constrained_objective_skeleton",
            "shield_internalization_placeholder",
        ),
        disabled_components=("heuristic_intent_prediction_placeholder",),
        risk_mode="action_conditioned_proxy_uniform_intent",
        constraint_mode="lagrangian_placeholder",
        shield_mode="interface_with_internalization_placeholder",
        paper_claim_allowed=False,
    ),
    "no_action_conditioning": AblationSpec(
        name="no_action_conditioning",
        enabled_components=(
            "heuristic_intent_prediction_placeholder",
            "state_only_proxy_risk",
            "constrained_objective_skeleton",
            "shield_internalization_placeholder",
        ),
        disabled_components=("action_conditioned_proxy_risk",),
        risk_mode="state_only_proxy",
        constraint_mode="lagrangian_placeholder",
        shield_mode="interface_with_internalization_placeholder",
        paper_claim_allowed=False,
    ),
    "no_risk_constraint": AblationSpec(
        name="no_risk_constraint",
        enabled_components=(
            "heuristic_intent_prediction_placeholder",
            "action_conditioned_proxy_risk",
            "unconstrained_objective",
            "shield_internalization_placeholder",
        ),
        disabled_components=("constrained_objective_skeleton",),
        risk_mode="action_conditioned_proxy",
        constraint_mode="disabled",
        shield_mode="interface_with_internalization_placeholder",
        paper_claim_allowed=False,
    ),
    "no_shield_internalization": AblationSpec(
        name="no_shield_internalization",
        enabled_components=(
            "heuristic_intent_prediction_placeholder",
            "action_conditioned_proxy_risk",
            "constrained_objective_skeleton",
            "shield_interface_only",
        ),
        disabled_components=("shield_internalization_placeholder",),
        risk_mode="action_conditioned_proxy",
        constraint_mode="lagrangian_placeholder",
        shield_mode="interface_only",
        paper_claim_allowed=False,
    ),
}

"""Stage 5 baseline family registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineSpec:
    family: str
    description: str
    risk_proxy: str
    constrained: bool
    forbidden_method_components: tuple[str, ...]


BASELINE_REGISTRY: dict[str, BaselineSpec] = {
    "vanilla_ppo": BaselineSpec(
        family="vanilla_ppo",
        description="Plain PPO baseline without explicit risk constraint.",
        risk_proxy="none",
        constrained=False,
        forbidden_method_components=(
            "latent intent predictor",
            "action-conditioned predictive risk",
            "shield internalization",
        ),
    ),
    "ppo_ttc_proxy": BaselineSpec(
        family="ppo_ttc_proxy",
        description="PPO baseline with TTC or clearance proxy shaping only.",
        risk_proxy="ttc_clearance_proxy",
        constrained=False,
        forbidden_method_components=(
            "latent intent predictor",
            "action-conditioned predictive risk",
            "shield internalization",
        ),
    ),
    "ppo_semantic_risk_proxy": BaselineSpec(
        family="ppo_semantic_risk_proxy",
        description="PPO baseline with static semantic/family risk proxy shaping only.",
        risk_proxy="semantic_family_proxy",
        constrained=False,
        forbidden_method_components=(
            "learned intent predictor",
            "action-conditioned predictive risk",
            "shield internalization",
        ),
    ),
    "ppo_lagrangian_no_intent": BaselineSpec(
        family="ppo_lagrangian_no_intent",
        description="Constrained PPO skeleton using cost proxy, without intent modeling.",
        risk_proxy="geometric_cost_proxy",
        constrained=True,
        forbidden_method_components=(
            "GRU intent predictor",
            "action-conditioned predictive risk",
            "shield internalization",
        ),
    ),
}

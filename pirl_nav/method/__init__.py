"""Stage 6 PIRL-Nav method skeleton and ablation helpers."""

from pirl_nav.method.ablation_registry import ABLATION_REGISTRY, AblationSpec
from pirl_nav.method.config import MethodConfig, Stage6Config, load_stage6_config
from pirl_nav.method.constrained_objective import ObjectiveResult, score_objective
from pirl_nav.method.intent_predictor import HeuristicIntentPredictor
from pirl_nav.method.intent_state import CandidateIntent, IntentState
from pirl_nav.method.method_runner import run_method_evaluation, run_method_smoke
from pirl_nav.method.risk_model import RiskScore, score_action, score_action_candidates
from pirl_nav.method.shield_interface import ShieldDecision, shield_action

__all__ = [
    "ABLATION_REGISTRY",
    "AblationSpec",
    "CandidateIntent",
    "HeuristicIntentPredictor",
    "IntentState",
    "MethodConfig",
    "ObjectiveResult",
    "RiskScore",
    "ShieldDecision",
    "Stage6Config",
    "load_stage6_config",
    "run_method_evaluation",
    "run_method_smoke",
    "score_action",
    "score_action_candidates",
    "score_objective",
    "shield_action",
]

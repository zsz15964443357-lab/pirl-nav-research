"""Stage 5 baseline training and reproducible experiment helpers."""

from pirl_nav.training.baseline_registry import BASELINE_REGISTRY, BaselineSpec
from pirl_nav.training.config import (
    BaselineConfig,
    CheckpointPolicy,
    SeedPlan,
    Stage5TrainingConfig,
    load_training_config,
)
from pirl_nav.training.formal_trainer import run_stage7_evaluation, run_stage7_training
from pirl_nav.training.stage7_config import Stage7Config, Stage7Group, load_stage7_config
from pirl_nav.training.trainer import run_stage5_evaluation, run_training_smoke

__all__ = [
    "BASELINE_REGISTRY",
    "BaselineConfig",
    "BaselineSpec",
    "CheckpointPolicy",
    "SeedPlan",
    "Stage7Config",
    "Stage7Group",
    "Stage5TrainingConfig",
    "load_stage7_config",
    "load_training_config",
    "run_stage7_evaluation",
    "run_stage7_training",
    "run_stage5_evaluation",
    "run_training_smoke",
]

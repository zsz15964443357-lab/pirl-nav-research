"""Artifact retention checks for Stage 5 baseline runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FORBIDDEN_COMMITTED_SUFFIXES = (
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".mp4",
    ".mov",
    ".avi",
    ".webm",
)


@dataclass(frozen=True)
class ArtifactRetentionPolicy:
    """Small-artifact policy used by Stage 5 smoke commands."""

    allow_git_json_summary: bool
    commit_model_weights: bool
    commit_checkpoints: bool
    commit_large_logs: bool
    commit_videos: bool
    external_artifact_root: Path

    def validate_for_git(self) -> None:
        if self.commit_model_weights:
            raise ValueError("Stage 5 must not commit model weights")
        if self.commit_checkpoints:
            raise ValueError("Stage 5 must not commit checkpoints")
        if self.commit_large_logs:
            raise ValueError("Stage 5 must not commit large logs")
        if self.commit_videos:
            raise ValueError("Stage 5 must not commit videos")


def assert_small_review_artifact(path: Path) -> None:
    if path.suffix.lower() in FORBIDDEN_COMMITTED_SUFFIXES:
        raise ValueError(f"forbidden Stage 5 review artifact suffix: {path}")

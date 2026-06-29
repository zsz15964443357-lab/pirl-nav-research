# PIRL-Nav Research Plan

Predictive Intent-Risk Constrained Reinforcement Learning for UAV Navigation under Latent Motion Intent Uncertainty.

This repository is a planning and execution-control repository, not an implementation repository yet. Its purpose is to give Codex CLI a stable, reviewed research specification before any code generation begins.

## Core Position

PIRL-Nav studies UAV navigation in environments where objects may be currently static but have latent future motion intent. The project focuses on proactive navigation rather than purely reactive collision avoidance.

The core contribution should remain:

1. Action-conditioned predictive intent-risk representation.
2. Intent-risk constrained reinforcement learning.
3. Safety shield internalization and reduction of shield dependence.
4. Visual-reviewable scenario benchmark and behavior-level evaluation metrics.

Semantic segmentation, detection, PyBullet, Gazebo, ROS2, and visualization are infrastructure layers. They serve the research question; they are not the primary novelty.

## Platform Decision

The current platform decision is:

```text
Auxiliary prototype: custom lightweight 2.5D Gymnasium environment
Main training: PyBullet-based UAV-IntentRisk environment
Final validation: Gazebo / ROS2 runtime validation, optionally with PX4 SITL
```

Training speed is not the main constraint. Effect quality, credibility, and reviewability are prioritized.

## Stage-Gated Workflow

Every stage must pass visual and conceptual review before the next stage starts.

```text
Design document -> Codex CLI implementation -> automatic artifacts -> web review -> revision -> next stage
```

No major training run should start before scenario visualization is reviewed.

## Repository Map

```text
docs/                         Research decisions and architecture documents
experiments/scenario_specs/    Scenario-family specifications
experiments/manifests/         Reviewed scenario manifest templates
experiments/review_checklists/ Review checklists for scenarios, training, and PRs
codex_tasks/                   Stage-specific task briefs for Codex CLI
.github/                       Issue and PR templates
```

## Recommended First Codex CLI Instruction

Ask Codex CLI to read only these files first:

```text
README.md
docs/00_PROJECT_BRIEF.md
docs/01_ARCHITECTURE_DECISION.md
codex_tasks/TASK_00_repo_bootstrap.md
```

Then require it to create only the repository skeleton and no RL implementation.

## Non-Negotiable Rules

1. Do not start with end-to-end RGB reinforcement learning.
2. Do not treat ROS2, Gazebo, or PyBullet as the main research novelty.
3. Do not start large-scale training before visual scenario review.
4. Do not rely on success rate alone; report near miss, risk exposure, AT, SDI, jerk, and detour.
5. Do not hide shield dependence; always compare policy-only and policy-plus-shield behavior.

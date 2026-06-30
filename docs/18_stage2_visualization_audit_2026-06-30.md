# 18 Stage 2 Visualization Audit - 2026-06-30

## Skill Invocation

- Skill invoked: `academic-research-suite`
- Stage: 2
- Task file: `codex_tasks/TASK_02_scenario_visualization_gate.md`

## Open-Source Scan

- Candidate projects or libraries: Matplotlib, Plotly, Bokeh, OpenCV, RViz visualization conventions, Python standard library HTML/JSON/path handling, and browser-native SVG.
- Reusable parts: established robotics visualization conventions such as top-down layout, object trajectory arrows, color-coded risk objects, and intent timelines.
- PIRL-Nav custom parts: mapping Stage 1 YAML intent candidates, trigger windows, conflict flags, and risk thresholds into review artifacts.
- License notes: no external code is copied and no new third-party dependency is introduced. The implementation uses Python standard library plus existing PyYAML already required by scenario validation.
- Reuse/adaptation decision: use lightweight HTML/SVG output instead of adding Matplotlib/Plotly at this stage. This keeps artifacts easy to review in GitHub and avoids dependency expansion before the review workflow stabilizes.

## Implemented Artifacts

The Stage 2 renderer reads `experiments/manifests/candidate_stage1_2026-06-29.yaml` and generates:

- per-scenario `layout.svg`
- per-scenario `timeline.svg`
- per-scenario `summary.json`
- `index.html`
- `reviewed_stage2_draft.yaml`

The reviewed draft keeps every scenario at `candidate` with `review_decision: needs_human_review`. It never marks a scenario as approved.

## Command

```bash
python scripts/preview_scenarios.py
```

Default output:

```text
experiments/review_artifacts/stage2/candidate_stage1_2026-06-29/
```

## Forbidden Scope Checked

- No PyBullet or Gymnasium environment.
- No RL algorithm.
- No training data generation.
- No policy rollout.
- No ROS2 or Gazebo runtime.
- No fixed-test approval.

## Known Limitations

- The renderer uses straight-line intent previews from initial object positions to candidate targets; it does not simulate dynamics.
- Risk visualization is currently represented through nominal corridor and conflict-flagged intent arrows, not a dense risk field.
- Human review is still required before any reviewed or fixed manifest can be created.

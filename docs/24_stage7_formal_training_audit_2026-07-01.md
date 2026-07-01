# 24 Stage 7 Formal Training and Visualization Audit - 2026-07-01

## Skill Invocation

- Skill invoked: `academic-research-suite`
- ARS workflow used: `ars/experiment-agent/WORKFLOW.md`
- Stage: 7
- Task file: `codex_tasks/TASK_07_formal_training_visualized_comparative_experiments.md`

## Repository Sync Status

- Repository sync status: latest `origin/main` fetched and local `main` fast-forwarded before branching.
- Base branch and commit: `main@ce02b4409485dd123b881410d5f76be089e07889`
- Working branch implementation commit: `codex/stage7-formal-training-visualized-comparison-20260701@654c6c3d430176957adbcd00ced3f959561f3fb8`
- Review artifacts generated from commit: `654c6c3d430176957adbcd00ced3f959561f3fb8`

## Open-Source Scan

- Candidate projects or libraries: Stable-Baselines3, CleanRL, RL Baselines3 Zoo, SafePO / PPO-Lagrangian examples, TensorBoard-style scalar logging, matplotlib-style training and rollout diagnostics, Gymnasium / Safety-Gymnasium lightweight evaluation conventions.
- Reusable parts: seed-explicit experiment configs, scalar metric rows, callback-like evaluation cadence, grouped baseline comparison summaries, policy-only versus policy-plus-shield reporting, lightweight curve and rollout diagnostic conventions.
- PIRL-Nav custom parts: Stage 4 `EpisodeRecord` reuse, Stage 5 baseline-development manifests, Stage 6 PIRL-Nav skeleton group semantics, semantic-risk proxy metrics, and SVG review artifacts that avoid adding plotting dependencies.
- License notes: no external source code was copied. The scan informed interface and reporting conventions only.
- Reuse/adaptation decision: implement a dependency-light reduced formal trainer and handwritten SVG visualizer for this review gate; keep optional external PPO backends for later stages.

References considered:

- Stable-Baselines3 documentation and repository: https://stable-baselines3.readthedocs.io/ and https://github.com/DLR-RM/stable-baselines3
- CleanRL documentation and repository: https://docs.cleanrl.dev/ and https://github.com/vwxyzjn/cleanrl
- RL Baselines3 Zoo documentation and repository: https://rl-baselines3-zoo.readthedocs.io/ and https://github.com/DLR-RM/rl-baselines3-zoo
- SafePO documentation and repository: https://safe-policy-optimization.readthedocs.io/ and https://github.com/PKU-Alignment/Safe-Policy-Optimization
- Matplotlib `savefig` documentation: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
- Safety-Gymnasium documentation: https://safety-gymnasium.readthedocs.io/

## Implemented Artifacts

Stage 7 adds:

- formal Stage 7 training config and nine group configs under `configs/training/`
- `pirl_nav/training/stage7_config.py` for typed config loading and required group validation
- `pirl_nav/training/formal_trainer.py` for reduced formal multi-seed training and validation
- `pirl_nav/training/experiment_tracker.py` for small JSON / JSONL review artifacts
- Stage 7 training, evaluation, training-visualization, and rollout-visualization scripts
- dependency-light SVG generation for learning curves, risk exposure curves, shield intervention curves, aggregate bars, and representative rollout snapshots
- Stage 7 tests for config coverage, artifact generation, and visual outputs

## Training Groups

The Stage 7 config covers all required groups:

- `vanilla_ppo`
- `ppo_ttc_proxy`
- `ppo_semantic_risk_proxy`
- `ppo_lagrangian_no_intent`
- `full_pirl_nav_skeleton`
- `no_intent_prediction`
- `no_action_conditioning`
- `no_risk_constraint`
- `no_shield_internalization`

Training run type:

- `reduced_formal_training_review_run`
- `trainer_backend: dependency_light_review_trainer`
- `seeds: [0, 1, 2]`
- `paper_claim_allowed: false`
- `fixed_test_used: false`

## Review Artifacts

Stage 7 artifacts are stored only under `experiments/review_artifacts/stage7/`:

- `training_metrics.jsonl` with 81 rows
- `validation_episode_records.jsonl` with 108 records
- `validation_summary.json`
- `comparison_summary.json`
- `visual_index.md`
- `figures/learning_curves.svg`
- `figures/risk_exposure_curves.svg`
- `figures/shield_intervention_curves.svg`
- `figures/aggregate_metric_bars.svg`
- four representative rollout SVGs for `vanilla_ppo` and `full_pirl_nav_skeleton`, each in `policy_only` and `policy_plus_shield` mode
- `gifs/index.md`
- user-approved rollout comparison GIFs and poster PNGs under `gifs/` for:
  - `latent_start_easy_0001`
  - `multi_intent_crossing_medium_0001`
  - `narrow_passage_yield_medium_0001`
  - `crowd_robot_flow_medium_0001`
  - `occlusion_emergence_medium_0001`
  - `vehicle_forklift_launch_hard_0001`

## Evaluation Compatibility

- Stage 7 reuses `EpisodeRecord` and `aggregate_records`.
- Stage 7 uses `experiments/manifests/train_stage5_baseline.yaml` and `experiments/manifests/validation_stage5_baseline.yaml`.
- Stage 7 does not create or use a fixed-test manifest.
- Stage 7 includes both baseline groups and PIRL-Nav skeleton / ablation groups in the same training, validation, and comparison pipeline.
- Stage 7 keeps old Stage 4 / Stage 5 / Stage 6 review artifacts unchanged.

## Validation Results

All Stage 7 checks passed locally on 2026-07-01 from implementation commit
`654c6c3d430176957adbcd00ced3f959561f3fb8`.

The local environment does not expose a `python` executable; equivalent commands were run with `/usr/bin/python3` (`Python 3.10.12`).

```text
python3 scripts/validate_scenarios.py
scenario validation passed

python3 scripts/train_stage7_formal.py --config configs/training/stage7_formal_training.yaml --reduced-review-run
wrote Stage 7 training metrics to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/training_metrics.jsonl
training groups: 9
training rows: 81

python3 scripts/evaluate_stage7_formal.py --config configs/training/stage7_formal_training.yaml
wrote 108 Stage 7 validation records to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/validation_episode_records.jsonl
wrote Stage 7 validation summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/validation_summary.json
wrote Stage 7 comparison summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/comparison_summary.json
paper claim allowed: False

python3 scripts/visualize_stage7_training.py --config configs/training/stage7_formal_training.yaml
wrote 4 Stage 7 training figures under /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures
wrote Stage 7 visual index to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/visual_index.md

python3 scripts/visualize_stage7_rollouts.py --config configs/training/stage7_formal_training.yaml
wrote 8 Stage 7 figures under /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures
wrote Stage 7 visual index to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/visual_index.md

python3 -m pytest
........................                                                 [100%]
24 passed in 1.22s

python3 -m ruff check .
All checks passed!
```

## Forbidden Scope Checked

- No fixed-test manifest was created.
- No model weights, checkpoints, TensorBoard event directories, wandb directories, large logs, videos, or large rollout dumps were added.
- GIFs were added only after explicit user approval as necessary Stage 7 visual diagnostics; they remain review artifacts and not paper results.
- No Stage 4 / Stage 5 / Stage 6 review artifacts were recommitted.
- No final paper claim is made.
- No claim that PIRL-Nav finally outperforms baselines is made.
- No Stage 5 smoke baseline is treated as a formal paper conclusion.
- No Stage 6 method skeleton smoke result is treated as a formal training conclusion.
- No baseline semantics were modified to favor PIRL-Nav.
- No duplicate task, audit, pass/fail, final, or updated document was created.

## Known Limitations

- Stage 7 remains a reduced formal review run, not full PPO training.
- The trainer is dependency-light and deterministic for reviewability.
- PIRL-Nav method groups remain skeleton / ablation groups, not the final full method.
- The SVG figures and GIFs are debug / review artifacts, not publication figures.
- Results are limited to baseline-development train / validation manifests and cannot support final paper claims.

## Review File Hygiene

This is the first Stage 7 audit document and a long-lived stage artifact. No `_v2`, `_final`, `_updated`, or pass/fail duplicate document was created.

## Next Recommended Stage

Stage 8 should freeze a fixed-test protocol and add final evaluation readiness checks without mutating Stage 7 review artifacts.

# 22 Stage 5 Baseline Training Audit - 2026-07-01

## Skill Invocation

- Skill invoked: `academic-research-suite`
- Stage: 5
- Task file: `codex_tasks/TASK_05_baseline_training_and_reproducible_experiments.md`

## Repository Sync Status

- Repository sync status: latest `origin/main` fetched and local `main` fast-forwarded before branching.
- Base branch and commit: `main@c501ce270fe66945feb5ad6497da49a6d288e954`
- Working branch source commit: `codex/stage5-baseline-training-20260701@2ee33eabd08640f6a0bdcd13b26d7cb3c1e0f47e`
- Review artifacts generated from commit: `2ee33eabd08640f6a0bdcd13b26d7cb3c1e0f47e`

## Open-Source Scan

- Candidate projects or libraries: Stable-Baselines3 PPO, CleanRL PPO, Safety-Gymnasium, Safe Policy Optimization / SafePO Lagrangian conventions, RL Baselines3 Zoo, and common JSON / JSONL experiment artifact conventions.
- Reusable parts: Gymnasium-style environment interface, PPO config fields, explicit seed plans, policy-only evaluation, cost reporting, Lagrangian multiplier terminology, checkpoint retention policies, and small summary artifacts.
- PIRL-Nav custom parts: reviewed / baseline-development manifest semantics, baseline family registry, Stage 4 episode record and aggregation reuse, geometric proxy risk labels, and forbidden-scope enforcement.
- License notes: no external source code is copied. Stable-Baselines3 is MIT-licensed, CleanRL is MIT-licensed, Safety-Gymnasium and SafePO are Apache-2.0. References are used only for interface and reporting conventions.
- Reuse/adaptation decision: keep Stage 5 dependency-light in-repo by adding a deterministic smoke trainer and baseline readiness pipeline. Formal PPO integration can later use Stable-Baselines3 or CleanRL after the environment backend is stable.

References considered:

- Stable-Baselines3 PPO documentation: https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html
- Stable-Baselines3 repository: https://github.com/DLR-RM/stable-baselines3
- CleanRL PPO documentation: https://docs.cleanrl.dev/rl-algorithms/ppo/
- CleanRL repository: https://github.com/vwxyzjn/cleanrl
- Safety-Gymnasium documentation: https://safety-gymnasium.readthedocs.io/
- SafePO Lagrangian documentation: https://safe-policy-optimization.readthedocs.io/en/latest/algorithms/lag.html
- RL Baselines3 Zoo documentation: https://rl-baselines3-zoo.readthedocs.io/

## Implemented Artifacts

Stage 5 adds:

- training config schema with explicit seed plan, checkpoint policy, artifact policy, and PPO-style hyperparameters
- baseline family registry for `vanilla_ppo`, `ppo_ttc_proxy`, `ppo_semantic_risk_proxy`, and `ppo_lagrangian_no_intent`
- Stage 5 baseline train / validation manifests marked `baseline_development`, `not_fixed_test`, and `not_for_final_reporting`
- dependency-light smoke training entry point
- policy-only Stage 5 evaluation entry point using Stage 4 `EpisodeRecord` and `aggregate_records`
- backward-compatible `goal_reached` and `termination_reason` fields on episode records
- lightweight JSON / JSONL review artifacts only
- tests for config loading, artifact policy, smoke training, and Stage 5 validation

## Commands

```bash
python3 scripts/train_stage5_baselines.py --config configs/training/stage5_baselines.yaml --smoke
python3 scripts/evaluate_stage5_baselines.py --config configs/training/stage5_baselines.yaml
```

Default outputs:

```text
experiments/review_artifacts/stage5/baseline_training_smoke_summary.json
experiments/review_artifacts/stage5/baseline_validation_episode_records.jsonl
experiments/review_artifacts/stage5/baseline_validation_summary.json
```

## Baseline Readiness

- `vanilla_ppo`: config and smoke training path complete; formal PPO backend not yet enabled.
- `ppo_ttc_proxy`: config and smoke training path complete with geometric TTC / clearance proxy only.
- `ppo_semantic_risk_proxy`: config and smoke training path complete with static semantic / family proxy only.
- `ppo_lagrangian_no_intent`: config and smoke training path complete with geometric cost proxy and Lagrangian multiplier placeholder only.

These are smoke baselines for reproducibility plumbing. They are not final learned baselines and must not be used for paper claims.

## Artifact and Checkpoint Policy

- Model weights are not committed to git.
- Checkpoints are not committed to git.
- Large logs, TensorBoard / wandb directories, and videos are not committed to git.
- Small JSON summaries, JSONL episode records, configs, manifests, tests, and audits may be committed.
- Future full training checkpoints should be written under ignored or external artifact paths such as `artifacts/stage5/`.

## Forbidden Scope Checked

- No PIRL-Nav full method.
- No GRU intent predictor.
- No action-conditioned predictive intent-risk.
- No shield internalization.
- No fixed-test manifest.
- No model weights, checkpoints, large logs, or videos.
- No claim that smoke results prove PIRL-Nav effectiveness.
- No duplicate task, audit, pass/fail, final, or updated document.

## Validation Results

All Stage 5 checks passed locally on 2026-07-01 from implementation commit
`2ee33eabd08640f6a0bdcd13b26d7cb3c1e0f47e`:

```text
python3 scripts/validate_scenarios.py
scenario validation passed

python3 scripts/evaluate_stage4.py
wrote 12 Stage 4 episode records to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage4/random_scripted_episode_records.jsonl
wrote Stage 4 summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage4/random_scripted_summary.json
overall episodes: 12

python3 scripts/train_stage5_baselines.py --config configs/training/stage5_baselines.yaml --smoke
wrote Stage 5 smoke training summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage5/baseline_training_smoke_summary.json
baseline families: 4

python3 scripts/evaluate_stage5_baselines.py --config configs/training/stage5_baselines.yaml
wrote 8 Stage 5 validation episode records to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage5/baseline_validation_episode_records.jsonl
wrote Stage 5 validation summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage5/baseline_validation_summary.json
overall episodes: 8

python3 -m pytest
................                                                         [100%]
16 passed in 0.49s

python3 -m ruff check .
All checks passed!
```

## Review Artifacts

- `experiments/review_artifacts/stage5/baseline_training_smoke_summary.json`
- `experiments/review_artifacts/stage5/baseline_validation_episode_records.jsonl`
- `experiments/review_artifacts/stage5/baseline_validation_summary.json`
- `experiments/review_artifacts/stage4/random_scripted_episode_records.jsonl` was regenerated to include backward-compatible `goal_reached` and `termination_reason` fields.

## Known Limitations

- Stage 5 uses the lightweight 2.5D Gymnasium-style Stage 3 gate, not a full PyBullet physics backend.
- The smoke trainer is deterministic and dependency-light; it validates the experiment pipeline, not PPO learning quality.
- Risk exposure remains a geometric proxy and is not final action-conditioned predictive risk.
- `ppo_lagrangian_no_intent` is a constrained RL skeleton only.
- Validation uses baseline-development manifests, not a fixed test set.

## Review File Hygiene

This is the first Stage 5 audit document and a long-lived stage artifact. No `_v2`, `_final`, `_updated`, or pass/fail duplicate document was created.

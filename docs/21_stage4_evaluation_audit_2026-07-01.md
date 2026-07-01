# 21 Stage 4 Evaluation Audit - 2026-07-01

## Skill Invocation

- Skill invoked: `academic-research-suite`
- Stage: 4
- Task file: `codex_tasks/TASK_04_evaluation_pipeline_and_baseline_readiness.md`

## Repository Sync Status

- Repository sync status: latest `origin/main` fetched and local `main` fast-forwarded before branching.
- Base branch and commit: `main@f1be673d02df4e680f45fd3d7495d7db459cc88b`
- Working branch: `codex/stage4-evaluation-pipeline-20260701`

## Open-Source Scan

- Candidate projects or libraries: Stable-Baselines3 `evaluate_policy`, CleanRL episode logging conventions, Safety Gymnasium safe-RL cost reporting, JSON Lines episode logging, and common RL experiment aggregation patterns.
- Reusable parts: fixed-episode evaluation loops, per-episode records, mean/std aggregation, per-group reporting, explicit cost/risk fields, and JSONL output for streamable records.
- PIRL-Nav custom parts: Stage 3 reviewed manifest entry, PIRL-Nav metrics contract, per-family / per-difficulty summary, train / validation draft semantics, and explicit distinction between geometric risk proxy and final action-conditioned predictive risk.
- License notes: no external code is copied. The implementation uses Python standard library plus existing PyYAML. References are used only as interface and reporting conventions.
- Reuse/adaptation decision: keep Stage 4 dependency-light and deterministic. Do not import Stable-Baselines3, CleanRL, or Safety Gymnasium before Stage 5 training work requires them.

References considered:

- Stable-Baselines3 evaluation helper: https://stable-baselines3.readthedocs.io/en/master/common/evaluation.html
- CleanRL logging metric examples: https://docs.cleanrl.dev/rl-algorithms/ppo/
- Safety Gymnasium documentation: https://safety-gymnasium.readthedocs.io/
- Safety Gymnasium basic usage: https://safety-gymnasium.readthedocs.io/en/latest/introduction/basic_usage.html
- JSON Lines format: https://jsonlines.org/

## Implemented Artifacts

Stage 4 adds:

- metrics helpers for success, detour ratio, clearance aggregation, jerk proxy, and shield intervention rate
- episode record schema for Stage 5 / Stage 6 comparable outputs
- aggregation with overall, per-family, per-difficulty, and per-policy summaries
- evaluation runner for random and scripted smoke policies over `reviewed_stage2_2026-06-30.yaml`
- Stage 4 config for policy-only random/scripted evaluation
- draft train and validation manifests marked `not_fixed_test` and `not_for_final_reporting`
- review artifacts with JSONL episode records and JSON summary
- tests for metric helpers and the evaluation runner

## Command

```bash
python3 scripts/evaluate_stage4.py
```

Default outputs:

```text
experiments/review_artifacts/stage4/random_scripted_episode_records.jsonl
experiments/review_artifacts/stage4/random_scripted_summary.json
```

## Metrics Contract

Implemented Stage 4 metrics:

```text
success
collision
near_miss
near_miss_count
risk_exposure
path_length
detour_ratio
min_clearance
average_clearance
jerk_proxy
active_time
shield_intervention_count
shield_intervention_rate
```

`risk_exposure` is currently a geometric proxy accumulated from Stage 3 `risk_exposure_increment`. It is not final action-conditioned predictive risk.

`jerk_proxy` is based on velocity-command changes. It is not true UAV acceleration or attitude jerk.

`shield_intervention_count` and `shield_intervention_rate` are placeholders while Stage 3 has no active safety supervisor.

`detour_ratio` is computed from the path traveled during the episode divided by the start-to-goal straight-line distance. In failed or truncated smoke episodes it can be below 1.0 because the policy did not reach the goal; Stage 5 must refine reporting once training/evaluation termination semantics are fixed.

## Episode Record Schema

Each episode record contains:

```text
experiment_id
commit
stage
scenario_id
family
difficulty
seed
run_mode
policy_type
steps
terminated
truncated
success
collision
near_miss
near_miss_count
min_clearance
average_clearance
path_length
detour_ratio
risk_exposure
risk_exposure_is_proxy
jerk_proxy
active_time
shield_intervention_count
shield_intervention_rate
notes
```

## Manifest Split Drafts

Draft manifests:

```text
experiments/manifests/train_stage4_draft.yaml
experiments/manifests/validation_stage4_draft.yaml
```

Both are marked:

```text
status: draft
not_fixed_test: true
not_for_final_reporting: true
```

They are not fixed-test manifests and must not be used for final paper reporting.

## Baseline Readiness Checklist

Before Stage 5 starts, the project still needs:

- training config schema for each baseline family
- baseline algorithm choice and exact implementation source
- seed plan for scenario, environment, policy initialization, training, and evaluation
- compute budget and wall-clock limits
- checkpoint retention policy that avoids committing weights
- evaluation cadence during training
- failure-case retention policy
- policy-only and policy+shield evaluation entry points
- finalized train / validation manifests with clear separation from future fixed test

## Forbidden Scope Checked

- No PPO, SAC, RLlib, Stable-Baselines3, or learned-policy training.
- No model checkpoint.
- No fixed-test manifest.
- No claim that random or scripted policies are paper baselines.
- No PIRL-Nav effectiveness claim.
- No use of current risk proxy as final action-conditioned predictive risk.
- No bypass of reviewed manifest.
- No duplicate task, audit, pass/fail, final, or updated document.

## Validation Results

All Stage 4 checks passed locally on 2026-07-01:

```text
python3 scripts/evaluate_stage4.py
wrote 12 Stage 4 episode records to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage4/random_scripted_episode_records.jsonl
wrote Stage 4 summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage4/random_scripted_summary.json
overall episodes: 12

python3 scripts/validate_scenarios.py
scenario validation passed

python3 -m pytest
.............                                                            [100%]
13 passed in 0.32s

python3 -m ruff check .
All checks passed!
```

## Known Limitations

- Random and scripted policies are smoke policies only, not learned baselines.
- Stage 4 risk exposure remains a geometric proxy.
- Stage 4 uses the lightweight 2.5D Gymnasium-style Stage 3 gate, not full PyBullet physics.
- Detour ratio for failed or truncated smoke episodes is a path-progress diagnostic and can be below 1.0.
- Draft train / validation manifests are planning artifacts and not final data splits.

## Review File Hygiene

This is the first Stage 4 audit document and a long-lived stage artifact. Future Stage 4 corrections should update this file directly instead of creating `_v2`, `_final`, `_updated`, or pass/fail duplicate documents.

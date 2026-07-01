# 23 Stage 6 PIRL-Nav Method Audit - 2026-07-01

## Skill Invocation

- Skill invoked: `academic-research-suite`
- Stage: 6
- Task file: `codex_tasks/TASK_06_pirl_nav_method_and_ablation_skeleton.md`

## Repository Sync Status

- Repository sync status: latest `origin/main` fetched and local `main` fast-forwarded before branching.
- Base branch and commit: `main@a0de8a94381a927dcdc7807c56453eb16c8eb9a1`
- Working branch source commit: `codex/stage6-pirl-nav-method-20260701@583577aa09fb34e39c9216451cc9ffb655ea3428`
- Review artifacts generated from commit: `583577aa09fb34e39c9216451cc9ffb655ea3428`

## Open-Source Scan

- Candidate projects or libraries: Trajectron / Trajectron++, Social GAN and trajectory prediction repositories, SafePO, Safety Starter Agents, Safety-Gymnasium, and shielded / safety-layer RL examples.
- Reusable parts: multimodal intent state shape, observed-history predictor interface, action-candidate risk scoring, cost / constraint naming, Lagrangian placeholder conventions, shield intervention reporting, and ablation registry patterns.
- PIRL-Nav custom parts: latent motion intent uncertainty tied to reviewed scenario specs, action-conditioned proxy risk over candidate actions, Stage 4 `EpisodeRecord` reuse, Stage 5 baseline-development manifest reuse, and explicit placeholder / forbidden-scope labels.
- License notes: no external source code is copied. Trajectron / Trajectron++ are MIT-licensed; SafePO and Safety-Gymnasium are Apache-2.0; references are used for interface and reporting conventions only.
- Reuse/adaptation decision: implement a dependency-light PIRL-Nav method skeleton in `pirl_nav/method/` and keep future GRU / learned risk / PPO-Lagrangian integration behind stable interfaces.

References considered:

- Trajectron++ repository: https://github.com/StanfordASL/Trajectron-plus-plus
- Trajectron repository: https://github.com/StanfordASL/Trajectron
- Social GAN repository: https://github.com/agrimgupta92/sgan
- SafePO documentation: https://safe-policy-optimization.readthedocs.io/
- SafePO repository: https://github.com/PKU-Alignment/Safe-Policy-Optimization
- Safety Starter Agents repository: https://github.com/openai/safety-starter-agents
- Safety-Gymnasium documentation: https://safety-gymnasium.readthedocs.io/

## Implemented Artifacts

Stage 6 adds:

- `pirl_nav/method/` package for PIRL-Nav method skeletons
- serializable latent intent state with placeholder intent probabilities
- `HeuristicIntentPredictor` interface with `reset`, `update`, and `predict`
- action-conditioned proxy risk scoring with candidate-action differentiation
- constrained objective skeleton with cost, violation, and Lagrange multiplier placeholder
- shield interface with optional policy-plus-shield action modification and internalization placeholder
- ablation registry and configs for:
  - `full_pirl_nav_skeleton`
  - `no_intent_prediction`
  - `no_action_conditioning`
  - `no_risk_constraint`
  - `no_shield_internalization`
- Stage 6 smoke and validation scripts
- Stage 6 review artifacts under `experiments/review_artifacts/stage6/`
- tests for method components and Stage 6 smoke evaluation

## Commands

```bash
python3 scripts/run_stage6_method_smoke.py --config configs/method/stage6_pirl_nav.yaml
python3 scripts/evaluate_stage6_method.py --config configs/method/stage6_pirl_nav.yaml
```

Default outputs:

```text
experiments/review_artifacts/stage6/method_smoke_summary.json
experiments/review_artifacts/stage6/method_validation_episode_records.jsonl
experiments/review_artifacts/stage6/method_validation_summary.json
```

## Evaluation Compatibility

- Stage 6 reuses `EpisodeRecord` and `aggregate_records`.
- Stage 6 uses `experiments/manifests/validation_stage5_baseline.yaml`, not a fixed-test manifest.
- Stage 6 produces policy-only and policy-plus-shield smoke records.
- Method-specific diagnostics are stored in JSON summary diagnostics and record notes while keeping the episode schema backward-compatible.

## Validation Results

All Stage 6 checks passed locally on 2026-07-01 from implementation commit
`583577aa09fb34e39c9216451cc9ffb655ea3428`:

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

python3 scripts/run_stage6_method_smoke.py --config configs/method/stage6_pirl_nav.yaml
wrote Stage 6 method smoke summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage6/method_smoke_summary.json
method configs: 5

python3 scripts/evaluate_stage6_method.py --config configs/method/stage6_pirl_nav.yaml
wrote 20 Stage 6 method records to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage6/method_validation_episode_records.jsonl
wrote Stage 6 method summary to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage6/method_validation_summary.json
overall episodes: 20

python3 -m pytest
.....................                                                    [100%]
21 passed in 0.69s

python3 -m ruff check .
All checks passed!
```

## Review Artifacts

- `experiments/review_artifacts/stage6/method_smoke_summary.json`
- `experiments/review_artifacts/stage6/method_validation_episode_records.jsonl`
- `experiments/review_artifacts/stage6/method_validation_summary.json`
- Stage 4 / Stage 5 review artifacts were regenerated by validation commands from the Stage 6 implementation commit for traceability.

## Forbidden Scope Checked

- No model weights, checkpoints, large logs, or videos.
- No fixed-test manifest.
- No claim that PIRL-Nav outperforms baselines.
- No claim that the heuristic predictor is the final GRU intent predictor.
- No claim that proxy risk is the final learned action-conditioned predictive risk.
- No use of Stage 5 smoke baseline as formal paper baseline.
- No bypass of Stage 4 / Stage 5 evaluation pipeline.
- No modification of baseline family semantics to favor PIRL-Nav.
- No duplicate task, audit, pass/fail, final, or updated document.

## Known Limitations

- Stage 6 still uses the lightweight 2.5D Gymnasium-style gate, not a full PyBullet physics backend.
- Intent prediction is heuristic and deterministic.
- Risk scoring is action-conditioned but remains a geometric + intent-probability proxy.
- Constrained RL is an objective skeleton, not formal PPO-Lagrangian training.
- Shield internalization is an interface placeholder, not a trained student policy.
- Stage 6 results are smoke integration artifacts only and are not paper claims.

## Review File Hygiene

This is the first Stage 6 audit document and a long-lived stage artifact. No `_v2`, `_final`, `_updated`, or pass/fail duplicate document was created.

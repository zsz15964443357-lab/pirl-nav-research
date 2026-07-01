# 20 Stage 3 Environment Audit - 2026-07-01

## Skill Invocation

- Skill invoked: `academic-research-suite`
- Stage: 3
- Task file: `codex_tasks/TASK_03_pybullet_environment_gate.md`

## Repository Sync Status

- Repository sync status: latest `origin/main` fetched and local `main` fast-forward checked before branching.
- Base branch and commit: `main@cec5505207d54382755726e7e6e47d9a96973e44`
- Working branch and commit: `codex/stage3-environment-gate-20260701@71a7cd963b0227771266f4d9ff8cbb1052f88f4c`

## Open-Source Scan

- Candidate projects or libraries: PyBullet examples, Gymnasium Env API, gym-pybullet-drones, Safety Gymnasium / Safety-Gym style safe RL interfaces, and common mobile-robot navigation benchmark conventions.
- Reusable parts: Gymnasium-style `reset` / `step` / `render` semantics, action and observation contracts, per-step `info` diagnostics, collision and clearance smoke tests, and rollout summary conventions.
- PIRL-Nav custom parts: loading `reviewed_stage2_2026-06-30.yaml`, preserving latent intent candidate semantics, exposing near-miss / risk-exposure / shield-dependence placeholders, and keeping reviewed scenarios separate from train / validation / fixed-test manifests.
- License notes: no external source code is copied. `gymnasium` and `pybullet` are listed only as optional `prototype` dependencies. The Stage 3 gate implementation uses Python standard library plus existing PyYAML for tests.
- Reuse/adaptation decision: implement a small deterministic 2.5D Gymnasium-style gate first, then leave PyBullet as an optional prototype dependency. This keeps CI and review artifacts lightweight while preserving the Stage 3 interface expected by the later PyBullet backend.

References considered:

- Gymnasium Env API: https://gymnasium.farama.org/api/env/
- Gymnasium environment creation guide: https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
- Bullet / PyBullet repository and quickstart material: https://github.com/bulletphysics/bullet3
- gym-pybullet-drones: https://github.com/utiasDSL/gym-pybullet-drones
- Safety Gymnasium: https://github.com/PKU-Alignment/safety-gymnasium
- Bullet-Safety-Gym: https://github.com/SvenGronauer/Bullet-Safety-Gym

## Implemented Artifacts

The Stage 3 gate adds:

- lightweight 2.5D Gymnasium-style environment gate, not a full PyBullet physics backend
- reviewed manifest loader for `experiments/manifests/reviewed_stage2_2026-06-30.yaml`
- Gymnasium-style `IntentRiskEnv.reset()`, `step()`, `render()`
- world-frame 2D velocity action command with speed and acceleration clipping
- observation vector documenting ego state, goal vector, nearest object state, and risk thresholds
- dynamic object intent placeholders for stay / wait / hold / cross / yield / emerge / launch-style candidates
- static box and dynamic-circle clearance checks
- collision and near-miss flags
- Stage 4 placeholder fields for `risk_exposure_increment` and `shield_intervention`
- random and scripted smoke rollout entry point

## Command

```bash
python3 scripts/rollout_random_policy.py --mode random
python3 scripts/rollout_random_policy.py --mode scripted
```

Default output:

```text
experiments/review_artifacts/stage3/rollout_random_smoke_summary.json
experiments/review_artifacts/stage3/rollout_scripted_smoke_summary.json
```

## Observation Contract

Stage 3 observation is a list of 13 floats:

```text
ego_x, ego_y,
ego_vx, ego_vy,
goal_dx, goal_dy,
nearest_object_dx, nearest_object_dy,
nearest_object_vx, nearest_object_vy,
near_miss_distance,
shield_trigger_distance,
exposure_horizon
```

## Action Contract

Stage 3 action is a 2D world-frame velocity command:

```text
[vx_cmd, vy_cmd]
```

The environment clips speed and velocity change using `EnvConfig.speed_limit` and `EnvConfig.acceleration_limit`. This is a navigation-level command interface, not a low-level UAV motor controller.

## Info Contract

`step()` returns at least:

```text
scenario_id
family
seed
step_count
time_s
min_clearance
current_clearance
collision
near_miss
risk_exposure_increment
shield_intervention
shield_intervention_placeholder
path_length
active_intents
```

`shield_intervention` is always `False` in Stage 3 and is explicitly marked by `shield_intervention_placeholder: True`.

## Forbidden Scope Checked

- No PPO, SAC, RLlib, Stable-Baselines3, or other training loop.
- No policy training or model checkpoint.
- No fixed-test manifest.
- No ROS2, Gazebo, PX4, rosbag, large video, or large generated asset.
- No changes to Stage 1 / Stage 2 scenario YAML semantics.
- No policy performance claim.

## Validation Results

All Stage 3 checks passed locally on 2026-07-01:

```text
python3 scripts/rollout_random_policy.py --mode random --steps 8
wrote 6 Stage 3 smoke rollout summaries to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage3/rollout_random_smoke_summary.json

python3 scripts/rollout_random_policy.py --mode scripted --steps 8
wrote 6 Stage 3 smoke rollout summaries to /home/zsz/pirl-nav-research/experiments/review_artifacts/stage3/rollout_scripted_smoke_summary.json

python3 scripts/validate_scenarios.py
scenario validation passed

python3 -m pytest
........                                                                 [100%]
8 passed in 0.25s

python3 -m ruff check .
All checks passed!
```

## Known Limitations

- This is a lightweight 2.5D Gymnasium-style gate. It is not a complete PyBullet physics backend and does not yet validate rigid-body dynamics, contact response, UAV attitude dynamics, or PyBullet-native collision geometry.
- Dynamic object behavior chooses one candidate intent per reset and follows a simple straight-line target motion after trigger time.
- `risk_exposure_increment` is a geometric near-miss proxy placeholder, not the final action-conditioned predictive risk metric.
- `shield_intervention` is a placeholder until the Stage 4 / Stage 6 safety supervisor work.
- Gymnasium and PyBullet are optional prototype dependencies; local validation may run without installing them.

## Review File Hygiene

This is the first Stage 3 audit document and is a new long-lived stage artifact. No `_v2`, `_final`, `_updated`, or duplicate pass/fail review file was created.

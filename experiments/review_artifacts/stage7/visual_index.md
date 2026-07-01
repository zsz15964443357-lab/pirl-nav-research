# Stage 7 Visual Review Index

## learning_curves.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/learning_curves.svg`
- What it shows: reward over reduced formal training timesteps.
- How to interpret it: Trend inspection only; use to detect obvious instability.
- Known limitation: Reduced deterministic review run, not final training curve.

## risk_exposure_curves.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/risk_exposure_curves.svg`
- What it shows: risk_exposure over reduced formal training timesteps.
- How to interpret it: Trend inspection only; use to detect obvious instability.
- Known limitation: Reduced deterministic review run, not final training curve.

## shield_intervention_curves.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/shield_intervention_curves.svg`
- What it shows: shield_intervention_rate over reduced formal training timesteps.
- How to interpret it: Trend inspection only; use to detect obvious instability.
- Known limitation: Reduced deterministic review run, not final training curve.

## aggregate_metric_bars.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/aggregate_metric_bars.svg`
- What it shows: Mean reduced formal training reward per method/group.
- How to interpret it: Use for review/debug only; higher is not a final paper claim.
- Known limitation: Reduced deterministic review run, not full PPO training.

## rollout_occlusion_emergence_medium_0001_vanilla_ppo_policy_only.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/rollout_occlusion_emergence_medium_0001_vanilla_ppo_policy_only.svg`
- What it shows: Representative trajectory for vanilla_ppo on occlusion_emergence_medium_0001 in policy_only mode.
- How to interpret it: Inspect whether the path moves toward the goal and whether shield points appear near latent-risk objects.
- Known limitation: Single representative rollout for review, not a full result.

## rollout_occlusion_emergence_medium_0001_vanilla_ppo_policy_plus_shield.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/rollout_occlusion_emergence_medium_0001_vanilla_ppo_policy_plus_shield.svg`
- What it shows: Representative trajectory for vanilla_ppo on occlusion_emergence_medium_0001 in policy_plus_shield mode.
- How to interpret it: Inspect whether the path moves toward the goal and whether shield points appear near latent-risk objects.
- Known limitation: Single representative rollout for review, not a full result.

## rollout_occlusion_emergence_medium_0001_full_pirl_nav_skeleton_policy_only.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/rollout_occlusion_emergence_medium_0001_full_pirl_nav_skeleton_policy_only.svg`
- What it shows: Representative trajectory for full_pirl_nav_skeleton on occlusion_emergence_medium_0001 in policy_only mode.
- How to interpret it: Inspect whether the path moves toward the goal and whether shield points appear near latent-risk objects.
- Known limitation: Single representative rollout for review, not a full result.

## rollout_occlusion_emergence_medium_0001_full_pirl_nav_skeleton_policy_plus_shield.svg

- Figure path: `/home/zsz/pirl-nav-research/experiments/review_artifacts/stage7/figures/rollout_occlusion_emergence_medium_0001_full_pirl_nav_skeleton_policy_plus_shield.svg`
- What it shows: Representative trajectory for full_pirl_nav_skeleton on occlusion_emergence_medium_0001 in policy_plus_shield mode.
- How to interpret it: Inspect whether the path moves toward the goal and whether shield points appear near latent-risk objects.
- Known limitation: Single representative rollout for review, not a full result.

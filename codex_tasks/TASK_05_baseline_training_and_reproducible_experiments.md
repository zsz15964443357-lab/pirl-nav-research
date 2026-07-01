# TASK 05：Baseline 训练与可复现实验

## Academic Research Suite 要求

执行本任务时，Codex CLI 必须显式调用 `academic-research-suite` skill。

终端 prompt 第一行必须写：

```text
Use the academic-research-suite skill.
```

## 仓库同步要求

读取仓库文件或修改任何文件前，必须先拉取最新项目状态：

```bash
git status
git fetch origin
git checkout main
git pull --ff-only origin main
```

如果在任务分支继续工作，必须先同步最新 `main`：

```bash
git checkout <task-branch>
git merge --ff-only origin/main
```

如果不能 fast-forward，必须停止并报告冲突，不得覆盖、force-push 或重写历史。

Codex 最终报告必须包含：

```text
Repository sync status:
Base branch and commit:
Working branch and commit:
```

## 必须先读

开始任何实现前，必须先读：

- `README.md`
- `ROADMAP.md`
- `docs/15_codex_cli_academic_research_suite.md`
- `docs/03_experimental_protocol.md`
- `docs/04_metrics_contract.md`
- `docs/05_scenario_benchmark.md`
- `docs/20_stage3_environment_audit_2026-07-01.md`
- `docs/21_stage4_evaluation_audit_2026-07-01.md`
- `experiments/manifests/reviewed_stage2_2026-06-30.yaml`
- `experiments/manifests/train_stage4_draft.yaml`
- `experiments/manifests/validation_stage4_draft.yaml`
- `configs/evaluation/stage4_random_scripted.yaml`
- `codex_tasks/TASK_05_baseline_training_and_reproducible_experiments.md`

如果 Stage 4 分支尚未合并到 `main`，必须停止并报告，不要基于缺失 Stage 4 产物继续实现 Stage 5。

## 阶段粒度说明

本阶段跨度应覆盖一个完整的 baseline training capability，不要只做一个 PPO 脚本，也不要把每个 baseline 拆成独立 stage。

Stage 5 的目标是一次性建立：

```text
training config schema
-> train / validation manifest finalization for baseline development
-> baseline implementation selection
-> reproducible training entry point
-> checkpoint and artifact policy
-> evaluation cadence
-> baseline evaluation reports through Stage 4 pipeline
-> Stage 5 audit and next-stage readiness
```

本阶段允许进行 baseline 训练，但不得实现 PIRL-Nav 完整方法。

## 开源优先要求

本阶段不要闭门造车。Codex 在写代码前必须做 open-source scan，调研并比较：

- Stable-Baselines3 PPO implementation and evaluation workflow；
- CleanRL PPO single-file implementation and logging conventions；
- Safety Gymnasium / safe-RL cost reporting conventions；
- PPO-Lagrangian or constrained PPO reference implementations；
- common RL checkpoint / config / seed management patterns；
- lightweight experiment tracking formats that do not require committing model weights；
- reproducible RL benchmark reporting practices。

任务开始前必须输出：

```text
Open-source scan:
- candidate projects or libraries
- reusable parts
- parts that must stay custom for PIRL-Nav
- license / attribution notes
- adaptation plan
```

如果复用或改造外部项目，必须记录来源、版本、许可证和改动范围。许可证不清楚的代码不得复制进仓库。

## 目标

建立 PIRL-Nav 的 baseline 训练与可复现实验闭环，使后续 Stage 6 PIRL-Nav 完整方法可以和 baseline 共享：

- 同一环境接口；
- 同一 train / validation manifest 语义；
- 同一 metrics contract；
- 同一 episode record schema；
- 同一 evaluation runner / aggregation；
- 同一 artifact retention policy。

本阶段的目标不是证明 PIRL-Nav 有效，而是建立可信 baseline。

## Baseline 范围

Stage 5 至少应覆盖以下 baseline families 的配置与最小训练入口：

```text
vanilla_ppo
ppo_ttc_proxy
ppo_semantic_risk_proxy
ppo_lagrangian_no_intent
```

说明：

- `vanilla_ppo` 是无显式风险约束的普通 PPO baseline；
- `ppo_ttc_proxy` 可以使用 TTC / clearance proxy 作为 reward shaping 或 safety-cost observation，不得使用 latent intent predictor；
- `ppo_semantic_risk_proxy` 可以使用 class / family / object-type risk proxy，不得使用 learned intent predictor；
- `ppo_lagrangian_no_intent` 可以实现 constrained RL skeleton，但不得接入 action-conditioned intent risk 或 GRU intent predictor。

如果资源不足，可以先实现 dependency-light fallback trainer 或 smoke-training mode，但必须保留上述 baseline family 的 config schema、entry point 和 audit 说明。

## 允许输出

建议路径：

```text
pirl_nav/training/
  __init__.py
  config.py
  policies.py
  rollout_buffer.py
  ppo.py
  baseline_registry.py
  trainer.py
  artifact_policy.py
configs/training/stage5_baselines.yaml
configs/training/baselines/
  vanilla_ppo.yaml
  ppo_ttc_proxy.yaml
  ppo_semantic_risk_proxy.yaml
  ppo_lagrangian_no_intent.yaml
scripts/train_stage5_baselines.py
scripts/evaluate_stage5_baselines.py
experiments/manifests/train_stage5_baseline.yaml
experiments/manifests/validation_stage5_baseline.yaml
experiments/review_artifacts/stage5/baseline_training_smoke_summary.json
experiments/review_artifacts/stage5/baseline_validation_summary.json
tests/test_training_config.py
tests/test_stage5_baseline_smoke.py
docs/22_stage5_baseline_training_audit_2026-07-01.md
```

可以根据实际实现简化，但不得新增重复 task、duplicate audit、`_final` 或 `_updated` 文件。

## 必须实现或固化的能力

### 1. Training config schema

训练 config 至少包含：

```text
experiment_id
stage
baseline_family
algorithm
implementation_source
scenario_manifest
validation_manifest
evaluation_config
seed_plan
total_timesteps
num_envs
rollout_steps
learning_rate
gamma
gae_lambda
clip_range
entropy_coef
value_coef
max_grad_norm
cost_limit placeholder
checkpoint_policy
artifact_policy
notes
```

### 2. Seed plan

必须明确区分：

```text
scenario_seed
environment_seed
policy_init_seed
training_seed
evaluation_seed
```

不能只写一个笼统 seed。

### 3. Manifest finalization for baseline development

允许从 Stage 4 draft manifest 生成 Stage 5 baseline train / validation manifest：

```text
experiments/manifests/train_stage5_baseline.yaml
experiments/manifests/validation_stage5_baseline.yaml
```

必须标注：

```text
purpose: baseline_train 或 baseline_validation
status: baseline_development
not_fixed_test: true
not_for_final_reporting: true
```

不得创建 fixed-test manifest。

### 4. Training entry point

必须提供统一入口：

```bash
python scripts/train_stage5_baselines.py --config configs/training/stage5_baselines.yaml --smoke
```

要求：

- 能遍历 baseline families；
- 能读取 config；
- 能设置 seed；
- 能产生 lightweight training summary；
- 能调用或准备调用 Stage 4 evaluation pipeline；
- smoke mode 必须能在低资源环境快速跑完。

### 5. Evaluation entry point

必须提供统一入口：

```bash
python scripts/evaluate_stage5_baselines.py --config configs/training/stage5_baselines.yaml
```

要求：

- 复用 Stage 4 episode record / aggregation 语义；
- 输出 policy-only validation summary；
- 明确区分 learned baseline、smoke baseline 和 random/scripted smoke policy；
- 不使用 fixed-test。

### 6. Artifact and checkpoint policy

必须实现或记录：

```text
model weights are not committed to git
large logs are not committed to git
large videos are not committed to git
small JSON summaries and audit files may be committed
checkpoints should be written under ignored or external artifact paths
```

如果需要更新 `.gitignore`，应只添加必要规则，不要破坏已有结构。

### 7. Baseline readiness and limitations

Stage 5 audit 必须说明：

- 哪些 baseline 已经完成 smoke training；
- 哪些 baseline 只有 config / skeleton；
- 是否使用外部 RL library；
- 训练结果是否只是 smoke result；
- 哪些结果不能用于论文；
- Stage 6 PIRL-Nav full method 开始前还缺什么。

## 推荐实现策略

优先顺序：

1. 先实现 config schema、manifest finalization、artifact policy 和 runner skeleton；
2. 再实现 dependency-light PPO smoke trainer 或接入 Stable-Baselines3 的可选依赖路径；
3. 再为四类 baseline 建立统一 registry；
4. 再输出 lightweight training summary；
5. 最后接入 Stage 4 evaluation summary。

如果外部依赖不可用，不要失败成半成品；应提供 deterministic smoke trainer / mock-learning baseline，用于验证训练管线和 artifact policy，同时在 audit 中明确它不是正式论文 baseline。

## 禁止事项

- 不实现 PIRL-Nav full method；
- 不实现 GRU intent predictor；
- 不实现 action-conditioned predictive intent-risk；
- 不实现 shield internalization；
- 不声称 Stage 5 baseline 结果证明 PIRL-Nav 有效；
- 不创建 fixed-test manifest；
- 不提交模型权重、checkpoint、大日志或视频；
- 不把 random / scripted smoke policy 当 learned baseline；
- 不修改 Stage 4 episode schema 的已提交字段，除非保持向后兼容；
- 不绕过 reviewed / baseline manifest；
- 不新增重复 task、audit、pass/fail、final、updated 文档。

## 最低验收标准

- Codex 输出 open-source scan；
- Codex 报告 repository sync status、base branch commit 和 working branch commit；
- 只保留一个 Task 5 文件：`codex_tasks/TASK_05_baseline_training_and_reproducible_experiments.md`；
- Stage 4 产物存在并被复用；
- `python scripts/validate_scenarios.py` 通过；
- `python scripts/evaluate_stage4.py` 通过；
- `python scripts/train_stage5_baselines.py --config configs/training/stage5_baselines.yaml --smoke` 通过；
- `python scripts/evaluate_stage5_baselines.py --config configs/training/stage5_baselines.yaml` 通过；
- `python -m pytest` 通过；
- `python -m ruff check .` 通过；
- Stage 5 audit 明确记录 forbidden scope checked；
- 没有提交 checkpoint、模型权重、大日志或大视频。

## 审查门槛

网页端 / 人工审查以下问题：

1. Stage 5 是否真正复用了 Stage 4 evaluation pipeline？
2. baseline family 是否清楚地区分 vanilla / TTC proxy / semantic risk proxy / Lagrangian no-intent？
3. 是否没有提前实现 PIRL-Nav full method？
4. 是否没有创建 fixed-test manifest？
5. 是否没有提交模型权重或大规模实验产物？
6. config 是否足以复现实验？
7. seed plan 是否区分 scenario / environment / policy init / training / evaluation？
8. policy-only 与 policy+shield 的接口是否为 Stage 6 留好，但没有越界实现 shield internalization？
9. Stage 6 的入口是否清楚？
10. 是否没有新增重复 task 或重复 audit？

## 输出报告格式

Codex 完成任务后必须写明：

```text
Skill invoked: academic-research-suite
Repository sync status:
Base branch and commit:
Working branch and commit:
Stage: 5
Task file: codex_tasks/TASK_05_baseline_training_and_reproducible_experiments.md
Open-source references considered:
Reuse/adaptation decision:
License notes:
Files changed:
New files created and why:
Existing files updated:
Duplicate-file check:
Validation commands:
Review artifacts:
Known limitations:
Forbidden scope checked:
GitHub sync status:
Next recommended stage:
```

## 推荐 Codex CLI 终端提示词

```text
Use the academic-research-suite skill.

You are working in the pirl-nav-research repository.
Current stage: Stage 5 baseline training and reproducible experiments.
Task file: codex_tasks/TASK_05_baseline_training_and_reproducible_experiments.md.

Before reading repository files or editing anything, sync the latest repository state:
- git status
- git fetch origin
- git checkout main
- git pull --ff-only origin main

First read:
- README.md
- ROADMAP.md
- docs/15_codex_cli_academic_research_suite.md
- docs/03_experimental_protocol.md
- docs/04_metrics_contract.md
- docs/05_scenario_benchmark.md
- docs/20_stage3_environment_audit_2026-07-01.md
- docs/21_stage4_evaluation_audit_2026-07-01.md
- experiments/manifests/reviewed_stage2_2026-06-30.yaml
- experiments/manifests/train_stage4_draft.yaml
- experiments/manifests/validation_stage4_draft.yaml
- configs/evaluation/stage4_random_scripted.yaml
- codex_tasks/TASK_05_baseline_training_and_reproducible_experiments.md

Before coding, perform an open-source scan for baseline PPO training, safe-RL cost reporting, seed/config/checkpoint management, and reproducible RL experiment reporting.

Allowed scope:
- baseline training config schema
- baseline family registry
- train / validation baseline-development manifests
- smoke training entry point
- Stage 5 evaluation entry point reusing Stage 4 records and aggregation
- artifact/checkpoint policy
- tests and audit documentation

Forbidden scope:
- no PIRL-Nav full method
- no GRU intent predictor
- no action-conditioned predictive risk
- no shield internalization
- no fixed-test manifest
- no committed model weights/checkpoints/large logs/videos
- no duplicate task or review files

After editing files, run:
- python scripts/validate_scenarios.py
- python scripts/evaluate_stage4.py
- python scripts/train_stage5_baselines.py --config configs/training/stage5_baselines.yaml --smoke
- python scripts/evaluate_stage5_baselines.py --config configs/training/stage5_baselines.yaml
- python -m pytest
- python -m ruff check .

Final answer must include skill invoked, repository sync status, base branch and commit, working branch and commit, stage, task file, open-source references considered, reuse/adaptation decision, license notes, files changed, new files created and why, existing files updated, duplicate-file check, validation results, review artifacts, known limitations, forbidden scope checked, GitHub sync status, and next recommended stage.
```

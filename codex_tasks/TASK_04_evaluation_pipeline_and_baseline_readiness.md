# TASK 04：评估指标、数据划分与 baseline-ready 实验管线

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

必须先读：

- `README.md`
- `ROADMAP.md`
- `docs/15_codex_cli_academic_research_suite.md`
- `docs/03_experimental_protocol.md`
- `docs/04_metrics_contract.md`
- `docs/05_scenario_benchmark.md`
- `docs/20_stage3_environment_audit_2026-07-01.md`
- `experiments/manifests/reviewed_stage2_2026-06-30.yaml`
- `codex_tasks/TASK_04_evaluation_pipeline_and_baseline_readiness.md`

## 阶段粒度说明

本阶段跨度应比前几个 stage 更大。不要只实现单个指标函数，也不要直接跳到 PPO 训练。

Stage 4 的目标是一次性建立：

```text
metrics definitions
-> episode record schema
-> evaluation runner
-> aggregation report
-> train / validation manifest draft
-> baseline readiness checklist
```

这会让项目从“环境能跑”推进到“可以准备严谨 baseline 训练和方法比较”。

## 开源优先要求

本阶段不要闭门造车。Codex 在写代码前必须做 open-source scan，调研并比较：

- RL evaluation pipeline examples；
- Stable-Baselines3 evaluation utilities；
- CleanRL logging / evaluation conventions；
- Safety Gymnasium metric and cost conventions；
- RL experiment aggregation patterns；
- bootstrap / confidence interval implementation examples；
- CSV / JSONL episode logging conventions。

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

建立 PIRL-Nav 的 Stage 4 评估基础设施，使后续 Stage 5 baseline 训练可以复用同一指标、同一 episode record、同一 aggregation 和同一 manifest 语义。

本阶段仍然不训练任何 RL policy。

## 允许输出

建议路径：

```text
pirl_nav/evaluation/
  __init__.py
  metrics.py
  records.py
  aggregation.py
  runner.py
configs/evaluation/stage4_random_scripted.yaml
scripts/evaluate_stage4.py
experiments/manifests/train_stage4_draft.yaml
experiments/manifests/validation_stage4_draft.yaml
experiments/review_artifacts/stage4/random_scripted_episode_records.jsonl
experiments/review_artifacts/stage4/random_scripted_summary.json
tests/test_evaluation_metrics.py
tests/test_stage4_evaluation_runner.py
docs/21_stage4_evaluation_audit_2026-07-01.md
```

可以根据实际结构简化，但不得新增重复 task、duplicate audit、`_final` 或 `_updated` 文件。

## 必须实现或固化的能力

### 1. Metrics

至少覆盖：

```text
success
collision
near_miss
risk_exposure
path_length
detour_ratio
min_clearance
average_clearance
jerk_proxy
active_time
shield_intervention_count placeholder
shield_intervention_rate placeholder
```

其中 risk exposure 可以暂时使用 Stage 3 的 geometric proxy，但必须明确标注：

```text
not final action-conditioned predictive risk
```

### 2. Episode record schema

每个 episode 至少记录：

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
min_clearance
path_length
detour_ratio
risk_exposure
active_time
shield_intervention_count
notes
```

### 3. Evaluation runner

runner 至少支持：

```text
random policy
scripted goal policy
reviewed_stage2_2026-06-30.yaml
policy_only run_mode
JSONL episode output
summary JSON output
overall aggregation
per-family aggregation
per-difficulty aggregation
```

### 4. Manifest split draft

允许生成 train / validation draft manifest，但必须标注：

```text
status: draft
not_fixed_test
not_for_final_reporting
```

不得生成 fixed-test manifest。

### 5. Baseline readiness checklist

需要在 audit 中明确 Stage 5 开始前还缺什么，例如：

```text
training config schema
baseline algorithm choice
seed plan
compute budget
checkpoint policy
evaluation cadence
failure-case retention policy
```

## 禁止事项

- 不训练 PPO、SAC、RLlib、Stable-Baselines3 或任何学习策略；
- 不生成 model checkpoint；
- 不创建 fixed-test manifest；
- 不声称 random / scripted policy 是论文 baseline；
- 不声称 PIRL-Nav 有效；
- 不把 current risk proxy 当最终 action-conditioned risk；
- 不绕过 reviewed manifest；
- 不新增重复 task、audit、pass/fail、final、updated 文档；
- 不提交大规模日志、视频、模型权重或未筛选图片。

## 最低验收标准

- Codex 输出 open-source scan；
- Codex 报告 repository sync status、base branch commit 和 working branch commit；
- `python scripts/validate_scenarios.py` 通过；
- `python scripts/evaluate_stage4.py` 能对 6 个 reviewed scenarios 运行 random / scripted evaluation；
- 输出 episode records 和 summary；
- summary 包含 overall、per-family、per-difficulty；
- `python -m pytest` 通过；
- `python -m ruff check .` 通过；
- audit 明确记录 forbidden scope checked。

## 审查门槛

网页端 / 人工审查以下问题：

1. 指标是否与 `docs/04_metrics_contract.md` 一致？
2. risk exposure 是否明确标注为 proxy，而不是最终 action-conditioned risk？
3. episode record 是否足以支撑 Stage 5 / Stage 6 方法比较？
4. aggregation 是否支持 per-family 和 per-difficulty？
5. train / validation draft 是否没有被错误标记为 fixed test？
6. 是否没有训练任何 policy？
7. 是否没有新增重复或过期文档？
8. Stage 5 baseline training 的入口是否清楚？

## 输出报告格式

Codex 完成任务后必须写明：

```text
Skill invoked: academic-research-suite
Repository sync status:
Base branch and commit:
Working branch and commit:
Stage: 4
Task file: codex_tasks/TASK_04_evaluation_pipeline_and_baseline_readiness.md
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
Current stage: Stage 4 evaluation pipeline and baseline readiness.
Task file: codex_tasks/TASK_04_evaluation_pipeline_and_baseline_readiness.md.

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
- experiments/manifests/reviewed_stage2_2026-06-30.yaml
- codex_tasks/TASK_04_evaluation_pipeline_and_baseline_readiness.md

Before coding, perform an open-source scan for RL evaluation pipelines, metric aggregation, episode logging, and safety-cost reporting conventions.

Allowed scope:
- metrics implementation
- episode record schema
- random/scripted evaluation runner
- aggregation report
- train/validation draft manifests
- baseline readiness checklist
- tests and audit documentation

Forbidden scope:
- no PPO/SAC/RLlib/Stable-Baselines3 training
- no learned policy training
- no model checkpoints
- no fixed-test manifest
- no PIRL-Nav effectiveness claims
- no duplicate task or review files

After editing files, run:
- python scripts/validate_scenarios.py
- python scripts/evaluate_stage4.py
- python -m pytest
- python -m ruff check .

Final answer must include skill invoked, repository sync status, base branch and commit, working branch and commit, stage, task file, open-source references considered, reuse/adaptation decision, license notes, files changed, new files created and why, existing files updated, duplicate-file check, validation results, review artifacts, known limitations, forbidden scope checked, GitHub sync status, and next recommended stage.
```

# 15 Codex CLI Academic Research Suite Skill Invocation

使用 Codex CLI 执行本仓库任务时，必须在终端提示中显式调用 `academic-research-suite` skill。

任务 prompt 第一行应写：

```text
Use the academic-research-suite skill.
```

如果 Codex CLI 环境支持显式参数，也可以同时使用：

```bash
codex --skill academic-research-suite
```

如果当前 Codex CLI 不支持 `--skill` 参数，仍必须在 prompt 第一行写明 `Use the academic-research-suite skill.`，并要求 Codex 在修改文件前确认：

```text
Skill invoked: academic-research-suite
```

## 两层约束

本文件不能替代终端中的 skill 调用。正确方式是：

```text
1. 在 Codex CLI prompt 中显式调用 academic-research-suite skill。
2. 让 Codex 读取 README、ROADMAP、本文件和当前 stage task。
```

## 每次任务的固定顺序

Codex CLI 必须按以下顺序工作：

```text
skill invocation
-> read repository stage docs
-> identify current stage
-> open-source scan
-> choose reuse/adaptation strategy
-> minimal current-stage implementation
-> validation commands
-> review artifacts
-> update existing review docs/manifests
-> GitHub sync
-> next-stage recommendation
```

不得跳过当前 stage，也不得为了实现方便改变论文主线。

## 开源优先要求

本项目不要闭门造车，不要默认从零开始。每个实现类任务在写代码前，必须先调研可参考的开源项目、论文代码、标准库和成熟工具链。

修改文件前，Codex 必须输出：

```text
Open-source scan:
- candidate projects or libraries
- reusable parts
- parts that must stay custom for PIRL-Nav
- license / attribution notes
- adaptation plan
```

可以复用、改造或重构已有开源实现，但必须记录来源、版本、许可信息和改动范围。通用基础设施优先参考成熟项目；PIRL-Nav 的创新应集中在 latent motion intent uncertainty、action-conditioned predictive risk、constrained RL 和 shield internalization。

## 审查文件卫生规则

网页端和 Codex CLI 端审查时，必须避免因为每次审查都新增一个独立文件而造成仓库膨胀和信息重复。

优先规则：

```text
已有 task / audit / manifest / checklist 能表达的内容，直接更新原文件。
只有当进入一个新的 stage 或产生一种新的长期资产时，才新增文件。
```

Codex CLI 不得随意新增以下重复文件：

```text
*_review_pass_*.md
*_review_fix_*.md
*_audit_v2_*.md
*_final_*.md
*_updated_*.md
```

如果审查结论发生变化，应优先修改：

```text
现有 stage audit 文档
现有 reviewed manifest
现有 codex task 文件
PR 描述或 PR 模板检查项
```

例如 Stage 2 的人工审查通过结论应记录在：

```text
docs/18_stage2_visualization_audit_2026-06-30.md
experiments/manifests/reviewed_stage2_2026-06-30.yaml
```

而不是再新增一个独立的 `stage2_review_pass` 文件。

如果必须新增文件，Codex 必须在最终报告中说明：

```text
Why a new file is necessary:
Why existing files cannot be updated instead:
Duplicate-file check:
```

## 每次执行前必须读

无论任务属于哪个 stage，Codex 在调用 skill 后都必须先读：

```text
README.md
ROADMAP.md
docs/15_codex_cli_academic_research_suite.md
```

然后再读对应阶段的 task 文件，例如：

```text
codex_tasks/TASK_02_scenario_visualization_gate.md
```

如果 task 文件和 README / ROADMAP / 本文件冲突，以更保守、更严格的 stage gate 为准。

## 输出报告格式

每次 Codex 提交必须在 PR、commit summary 或审查文档中包含：

```text
Skill invoked:
Stage:
Task file:
Open-source references considered:
Reuse/adaptation decision:
License notes:
Files changed:
New files created and why:
Existing files updated:
Duplicate-file check:
Allowed scope:
Forbidden scope checked:
Validation commands:
Review artifacts:
Known limitations:
GitHub sync status:
Next recommended stage:
```

`Skill invoked` 必须写：

```text
academic-research-suite
```

## 禁止行为

Codex CLI 不得：

- 未显式调用 `academic-research-suite` skill 就开始修改文件；
- 跳过 open-source scan 就从零实现已有成熟工具；
- 不记录来源和许可信息就引入外部代码；
- 把外部通用工具包装成本项目论文创新；
- 能更新原文件却新增重复审查文件；
- 使用 `_v2`、`_final`、`_updated` 等方式逃避整理；
- 只停留在本地临时代码而不同步到 GitHub；
- 未经 stage task 要求就实现 PyBullet、Gymnasium、ROS2、RL 或训练脚本；
- 未通过可视化审查就把 candidate 场景放进 fixed test；
- 只报告 success rate 或 collision rate；
- 隐藏 policy-only 与 policy+shield 的差异；
- 提交模型权重、大日志、rosbag、大视频或未筛选图片；
- 为了让测试通过而削弱研究约束。

## Stage 2 推荐终端提示词

```text
Use the academic-research-suite skill.

You are working in the pirl-nav-research repository.
Current stage: Stage 2 scenario visualization gate.
Task file: codex_tasks/TASK_02_scenario_visualization_gate.md.

First read:
- README.md
- ROADMAP.md
- docs/15_codex_cli_academic_research_suite.md
- codex_tasks/TASK_02_scenario_visualization_gate.md
- experiments/manifests/candidate_stage1_2026-06-29.yaml
- experiments/review_checklists/scenario_review.md

Before coding, perform an open-source scan for visualization approaches and reusable libraries.
Before creating any new review document, check whether an existing task, audit, manifest, or checklist can be updated instead.

Allowed scope:
- scenario top-down preview images
- object intent timeline plots
- risk preview or placeholder visualization
- review artifact summaries
- reviewed manifest draft only
- visualization script and tests

Forbidden scope:
- no PyBullet
- no Gymnasium environment
- no RL
- no training
- no ROS2
- no policy rollout
- no approved fixed test manifest
- no duplicate review files

After editing files, run:
- python scripts/validate_scenarios.py
- python -m pytest
- python -m ruff check .

Final answer must include skill invoked, stage, task file, open-source references considered, reuse/adaptation decision, license notes, files changed, new files created and why, existing files updated, duplicate-file check, validation results, review artifacts, known limitations, forbidden scope checked, GitHub sync status, and next recommended stage.
```

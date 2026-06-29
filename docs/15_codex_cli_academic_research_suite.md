# 15 Codex CLI Academic Research Suite Workflow

本仓库后续使用 Codex CLI 时，必须按 `academic-research-suite` 的研究工作流执行。这里的 `academic-research-suite` 是本项目对 Codex 的使用协议：Codex 不直接自由发挥写代码，而是按学术研究流程、阶段门控和审查证据链工作。

## 总原则

Codex CLI 每次任务必须遵循：

```text
research question -> stage task -> source documents -> minimal implementation -> mechanical checks -> review artifacts -> human/web review -> next stage
```

任何任务都不得跳过当前 stage，也不得因为实现方便而改变论文主线。

## 必须遵守的角色分工

### 1. academic-pipeline

用于保持论文主线和阶段顺序。

Codex 必须先判断当前任务属于哪个 stage，并只完成该 stage 的最小产物。不能把 Stage 2、Stage 3、Stage 4 的内容提前混在一起。

### 2. experiment-agent

用于保证实验可复现。

Codex 生成任何场景、配置、manifest、指标或脚本时，必须记录：

- seed；
- config path；
- manifest path；
- expected output；
- validation command；
- known limitations。

### 3. reviewer-style gate

用于模拟论文审稿和网页端审查。

Codex 完成任务后必须说明：

- 产物是否支撑 PIRL-Nav 的 latent motion intent uncertainty 主线；
- 是否产生了可人工审查的证据；
- 是否有越界实现；
- 当前结论不能支持什么；
- 下一阶段仍然需要什么。

## Codex CLI 每次执行前必须读

无论任务属于哪个 stage，Codex 都必须先读：

```text
README.md
ROADMAP.md
docs/15_codex_cli_academic_research_suite.md
```

然后再读对应 stage 的 task 文件，例如：

```text
codex_tasks/TASK_01_scenario_specification.md
```

如果 task 文件和 README / ROADMAP / 本文件冲突，以更保守、更严格的 stage gate 为准。

## Codex CLI 输出格式要求

每次 Codex 提交必须在 PR 或审查文档中包含：

```text
Stage:
Task file:
Files changed:
Allowed scope:
Forbidden scope checked:
Validation commands:
Review artifacts:
Known limitations:
Next recommended stage:
```

## 禁止行为

Codex CLI 不得：

- 未经 stage task 要求就实现 PyBullet、Gymnasium、ROS2、RL 或训练脚本；
- 未通过可视化审查就把 candidate 场景放进 fixed test；
- 未记录 manifest / seed / config 就生成实验结果；
- 只报告 success rate 或 collision rate；
- 隐藏 policy-only 与 policy+shield 的差异；
- 将 PyBullet、Gazebo、ROS2、PX4、语义分割写成论文主创新；
- 提交模型权重、大日志、rosbag、大视频或未筛选图片；
- 为了让测试通过而削弱研究约束。

## 当前推荐下一步

当前仓库已经完成 Stage 0 和 Stage 1。下一次 Codex CLI 应执行 Stage 2：场景可视化流水线。

Stage 2 的目标不是训练，也不是仿真环境，而是针对 `experiments/manifests/candidate_stage1_2026-06-29.yaml` 生成：

- 俯视布局图；
- 对象意图时间线；
- 风险区域预览图或占位图；
- 每个场景的人工审查包；
- reviewed manifest 的草稿，但不得自动批准。

## 推荐 Codex CLI 提示词模板

```text
Use the academic-research-suite workflow.

You must first read:
- README.md
- ROADMAP.md
- docs/15_codex_cli_academic_research_suite.md
- <current codex_tasks/TASK_xx_*.md>

Work only within the current stage.
Do not implement later-stage functionality.
Produce minimal code and reviewable artifacts.
Run the validation commands.
Summarize allowed scope, forbidden scope checked, known limitations, and next stage.
```

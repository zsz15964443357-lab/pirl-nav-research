# PIRL-Nav

**Predictive Intent-Risk Constrained Reinforcement Learning for UAV Navigation under Latent Motion Intent Uncertainty**  
中文定位：**面向潜在运动意图不确定性的无人机预测式意图风险约束强化学习导航**。

本仓库用于支撑后续实验、论文写作和 Codex CLI 分阶段实现。它不是“一上来就训练模型”的代码堆，而是一个**文档契约 + 最小工程骨架 + 审查门控**的科研仓库。

## 研究问题

低空无人机在仓库、走廊、门口、路口、货架遮挡等环境中，经常面对一类隐蔽风险：对象当前可能静止或低速，但未来可能突然启动、横穿、让行、停留或从遮挡处出现。

PIRL-Nav 研究的问题是：

> 在 latent motion intent uncertainty 下，如何让无人机在安全屏障被迫介入之前，基于动作相关的未来风险主动、平滑、低绕行地调整导航策略？

## 核心研究假设

如果策略能够接收并优化**动作相关的预测式意图风险**，并通过约束强化学习显式控制 near miss、risk exposure 与 shield dependence，那么它应当比普通 PPO、TTC reward、语义风险 reward 或纯 safety shield 更早规避潜在风险，同时不显著牺牲到达率、路径效率和平滑性。

## 贡献边界

本项目的论文主线应固定在以下四点：

1. **Action-conditioned predictive intent-risk representation**：风险不是静态语义标签，而是“当前候选动作是否会进入未来风险区域”。
2. **Intent-risk constrained reinforcement learning**：将 near miss、risk exposure 等安全行为指标作为约束，而不是只做 reward shaping。
3. **Safety shield internalization**：保留安全监督器，但训练策略减少对末端安全修正的依赖。
4. **Visual-reviewable benchmark and behavior-level metrics**：场景先可视化审查，再进入训练、验证或固定测试集。

语义分割、检测、PyBullet、Gazebo、ROS2、PX4、可视化工具均是基础设施，不应写成论文主创新。

## Platform 策略

```text
辅助原型：自建轻量 2.5D Gymnasium 环境
主训练：PyBullet-based UAV-IntentRisk Env
最终验证：Gazebo / ROS2 Runtime，后期可选 PX4 SITL
```

优先级排序：**论文可信度 > 动力学合理性 > 可视化可审查性 > 训练速度**。

## 阶段门控流程

每个阶段都必须产生可审查产物，并在进入下一阶段前通过人工检查。

```text
研究文档
  ↓
Codex CLI 单任务实现
  ↓
自动生成可审查产物
  ↓
网页端 / 人工审查
  ↓
修正原文档或原 manifest
  ↓
进入下一阶段
```

硬规则：**未通过场景可视化审查，不允许开始大规模训练。**

## 开源优先原则

本项目不要闭门造车，也不要默认从零开始。每个实现阶段在写代码前，都应先调研相关开源项目、论文代码、标准库和成熟工具链。

Codex CLI 每次执行实现类任务前，必须先输出：

```text
Open-source scan:
- candidate projects or libraries
- reusable parts
- parts that must stay custom for PIRL-Nav
- license / attribution notes
- adaptation plan
```

可以参考、复用或改造已有开源项目，但必须记录来源、版本、许可信息和改动范围。通用基础设施优先参考成熟项目；PIRL-Nav 的创新应集中在 latent motion intent uncertainty、action-conditioned predictive risk、constrained RL 和 shield internalization。

改造后的代码、文档和审查产物必须同步到 GitHub，不能只停留在本地临时代码。

## 文件卫生原则

网页端和 Codex CLI 端审查后，优先直接修改原 task、原 audit、原 manifest 或原 checklist，并在原文件中记录审查结论。不要为了每次审查都新增一个相似文件。

禁止用以下方式制造重复文件：

```text
*_review_pass_*.md
*_review_fix_*.md
*_audit_v2_*.md
*_final_*.md
*_updated_*.md
```

如果必须新增文件，必须说明为什么不能修改已有文件。Codex CLI 的最终报告必须包含：

```text
New files created and why:
Existing files updated:
Duplicate-file check:
```

## Codex CLI skill 调用要求

后续使用 Codex CLI 时，必须在终端任务提示中显式调用 `academic-research-suite` skill。任务 prompt 第一行应写：

```text
Use the academic-research-suite skill.
```

如果 Codex CLI 环境支持显式参数，也应同时使用对应参数，例如：

```bash
codex --skill academic-research-suite
```

调用 skill 后，Codex 每次任务都要先读：

```text
README.md
ROADMAP.md
docs/15_codex_cli_academic_research_suite.md
```

再读取对应阶段的 `codex_tasks/TASK_xx_*.md` 文件。Codex 只能完成当前 stage 的最小可审查产物，不能提前实现后续阶段。

## 仓库结构

```text
README.md                         项目定位与入口
ROADMAP.md                        阶段路线图和验收门槛
pyproject.toml                    最小 Python 工程配置
pirl_nav/                         后续实现包，只保留阶段化骨架
configs/                          配置模板和命名约定
scripts/                          人工审查和后续工具脚本入口
experiments/
  scenario_specs/                 场景 family / difficulty / seed 规格
  manifests/                      固定验证集、测试集、审查记录模板
  review_checklists/              场景、训练、PR、阶段门控审查清单
docs/                             研究决策、实验协议、指标契约、论文边界
codex_tasks/                      给 Codex CLI 的单阶段任务说明
tests/                            最小可运行性和后续单元测试
.github/                          CI、Issue / PR 模板
```

## 首次本地检查

当前阶段只要求仓库结构、Python 包骨架和 Stage 1 场景规格可检查，不要求实现仿真或 RL：

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python scripts/validate_scenarios.py
```

## Codex CLI 首次读取文件

仓库初始化或全新会话首次让 Codex CLI 只读取以下文件：

```text
README.md
ROADMAP.md
docs/15_codex_cli_academic_research_suite.md
docs/00_项目简述.md
docs/01_架构决策.md
docs/11_仓库结构.md
codex_tasks/TASK_00_仓库初始化.md
```

首次任务只允许建立或维护仓库骨架，不允许实现 PyBullet 环境、强化学习算法、训练脚本或 ROS2 节点。

## Stage 1 审查读取文件

当目标是审查或继续 Stage 1 场景规格工作时，Codex CLI 应先读取：

```text
docs/ARS_SESSION_CONFIG.md
docs/13_stage1_scenario_audit_2026-06-29.md
codex_tasks/TASK_01_scenario_specification.md
experiments/scenario_specs/README.md
experiments/manifests/candidate_stage1_2026-06-29.yaml
scripts/validate_scenarios.py
```

Stage 1 的正式任务入口只有 `codex_tasks/TASK_01_scenario_specification.md`。

## 禁止事项

1. 不要从端到端 RGB 强化学习开始。
2. 不要把 PyBullet、Gazebo、ROS2、PX4 写成主创新。
3. 不要在场景未可视化审查前启动大规模训练。
4. 不要只报告 success rate 和 collision rate。
5. 不要隐藏 shield dependence，必须报告 policy-only 与 policy+shield。
6. 不要提交大规模训练日志、wandb / tensorboard 目录、rosbag、大视频或未筛选图片。
7. 不要跳过开源调研而从零实现已有成熟工具。
8. 不要为了记录审查结论而重复新建相似文档；优先修改原文档并记录变更。

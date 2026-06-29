# PIRL-Nav 研究方案

PIRL-Nav 是一个面向无人机导航的研究项目，全称为：**预测式意图风险约束强化学习导航**。

本仓库不是立即写代码的实现仓库，而是一个**研究方案与执行控制仓库**。它的作用是先把研究主线、平台选择、训练场景、可视化审查和 Codex CLI 执行边界整理清楚，再让 Codex CLI 按阶段读取文档执行任务。

## 一句话定位

让无人机不只对“已经运动、已经靠近”的障碍物做反应式避障，而是能识别“当前静止但未来可能启动、横穿或从遮挡处出现”的潜在风险对象，并在安全屏障触发前主动、平滑、低绕行地避险。

## 核心贡献边界

本项目的核心贡献应固定在以下四点：

1. **动作相关的预测式意图风险表示**：不是只判断哪里危险，而是判断“当前这个动作会不会进入未来风险区域”。
2. **意图风险约束强化学习**：将 near miss、risk exposure 等行为安全指标作为约束，而不是只做 reward shaping。
3. **安全屏障内化**：保留 safety supervisor，但训练策略减少对末端安全修正的依赖。
4. **可视化审查的场景基准与指标体系**：所有场景先可视化审查，再进入训练或测试集。

语义分割、目标检测、PyBullet、Gazebo、ROS2、可视化工具都是基础设施，不是论文主创新。

## 当前平台决策

```text
辅助原型平台：自建轻量 2.5D Gymnasium 环境
主训练平台：PyBullet-based UAV-IntentRisk Env
最终验证平台：Gazebo / ROS2 Runtime，后期可选 PX4 SITL
```

本项目不把训练速度作为第一约束。优先级是：**效果可信度、动力学合理性、可视化可审查性、论文可发表性**。

## 阶段门控流程

每个阶段必须经过网页端和 Codex CLI 双重审查：

```text
方案文档
  ↓
Codex CLI 按单个任务执行
  ↓
自动生成可审查产物
  ↓
网页端审查
  ↓
修正
  ↓
进入下一阶段
```

硬规则：**未通过场景可视化审查，不允许开始大规模训练。**

## 仓库结构

```text
docs/                         研究方案、架构决策、训练策略、审查规范
experiments/scenario_specs/    六类核心训练场景规格
experiments/manifests/         固定测试集与场景审查记录模板
experiments/review_checklists/ 场景、训练、PR、阶段门控审查清单
codex_tasks/                   Codex CLI 分阶段任务说明
.github/                       Issue / PR 模板
```

## 建议 Codex CLI 首次读取

第一次让 Codex CLI 只读取以下文件：

```text
README.md
docs/00_项目简述.md
docs/01_架构决策.md
codex_tasks/TASK_00_仓库初始化.md
```

首次任务只允许建立代码仓库骨架，不允许实现 PyBullet 环境，不允许实现强化学习算法。

## 禁止事项

1. 不要从端到端 RGB 强化学习开始。
2. 不要把 PyBullet、Gazebo、ROS2 写成主创新。
3. 不要在场景未可视化审查前启动大规模训练。
4. 不要只报告 success rate 和 collision rate。
5. 不要隐藏 shield dependence，必须报告 policy-only 与 policy+shield。
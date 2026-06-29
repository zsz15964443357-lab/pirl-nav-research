# 12 Repository Audit - 2026-06-29

本文档记录本次仓库审查结论和优化方向。

## 总体判断

PIRL-Nav 当前选题具有论文潜力，关键不在于使用 PyBullet、Gazebo、ROS2 或语义分割，而在于把“当前静止或部分可见对象的未来运动意图风险”转化为动作相关的风险约束，并通过强化学习产生提前、平滑、低绕行的导航行为。

仓库原始方向正确，但作为后续实验与论文仓库，还需要加强以下方面：

1. 研究假设、消融矩阵和论文证据链需要显式化；
2. 场景 family 命名和论文主线需要统一；
3. 固定测试集、manifest、review checklist 和指标契约需要提前建立；
4. 工程骨架需要最小可运行检查，避免后续 Codex CLI 直接生成大量不可审查代码；
5. PR / CI / gitignore 需要在早期就限制大文件、日志和越界实现。

## 已完成优化

### 研究定位

- 重写 README，使仓库入口明确表达研究问题、假设、贡献边界、平台策略、阶段门控和禁止事项；
- 新增 research hypotheses and ablation matrix，固定 H1-H4、baseline、消融变量和伪贡献边界；
- 新增 paper argument scaffold，提前约束论文结构、图表、结论边界和审稿风险。

### 实验协议

- 新增 experimental protocol，明确 experiment_id、commit、config、manifest、seed、run_mode；
- 新增 metrics contract，固定 near miss、risk exposure、AT、SDI、jerk、detour、clearance 等指标；
- 新增 manifest contract 和 fixed test template，防止后续随意更换测试集。

### 场景 benchmark

- 将核心场景统一为 latent_start、occlusion_emergence、multi_intent_crossing、narrow_passage_yield、vehicle_forklift_launch、crowd_robot_flow；
- 将 static_clutter、dynamic_crossing、semantic_distractor 调整为 sanity check / supporting scenario；
- 新增 scenario review checklist，要求场景进入 fixed test 前必须可视化审查。

### 工程结构

- 新增 `pyproject.toml`、`.gitignore`、CI、PR 模板和 issue 模板；
- 新增 `pirl_nav/` 包骨架和最小导入测试；
- 新增 `configs/`、`scripts/`、`experiments/` 目录说明；
- 保持 Stage 0 不实现仿真、RL、ROS2 或训练脚本。

## 后续建议

### 下一步应做 Stage 1

建议下一步让 Codex CLI 执行：

```text
codex_tasks/TASK_01_scenario_specification.md
```

只生成六类场景 YAML 示例、candidate manifest 和最小 schema 检查，不实现仿真和训练。

### 再下一步应做 Stage 2

Stage 2 再实现场景可视化流水线，自动输出俯视图、对象时间线和风险预览。只有通过人工审查的场景才能进入 reviewed set 或 fixed test set。

### 暂不建议做的事

- 暂不训练 PPO；
- 暂不实现 PyBullet 环境；
- 暂不写 ROS2 节点；
- 暂不做端到端 RGB；
- 暂不提交模型权重、训练日志或视频。

## 审查结论

该仓库已经从“研究想法说明”升级为“可阶段化执行的学术实验仓库骨架”。当前最重要的工作不是立即写训练代码，而是先把场景规格、可视化审查和指标契约落地。这样后续实验结果才更容易支撑论文主张，也更容易经得起审稿人质疑。

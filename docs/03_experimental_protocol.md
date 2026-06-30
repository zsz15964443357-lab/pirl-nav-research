# 03 Experimental Protocol

本文档是 PIRL-Nav 实验对象、数据划分、训练顺序、运行模式、输出产物和结果解释边界的唯一入口。不要再新增独立的“训练策略”文档；训练相关修订应直接更新本文档、ROADMAP 或对应 stage task。

核心目标是防止“先训练、后挑图、再解释”的不可复现流程。

## 实验对象

每次实验必须明确以下字段：

```yaml
experiment_id: pirl_nav_stageX_methodY_YYYYMMDD
commit: <git-commit-sha>
method: <baseline-or-pirl-nav-variant>
scenario_manifest: experiments/manifests/<manifest-name>.yaml
config: configs/<config-name>.yaml
seeds: [0, 1, 2, 3, 4]
run_mode: policy_only | policy_plus_shield
```

## 数据划分原则

场景应按 family / difficulty / seed 划分：

- **candidate set**：自动生成的候选场景；
- **reviewed set**：人工可视化审查通过的场景；
- **train set**：允许训练使用；
- **validation set**：用于调参和 early stopping；
- **fixed test set**：最终论文报告，只能在方法冻结后使用。

固定测试集一旦冻结，不允许因为某个方法表现不好而删除或替换场景。

## 训练与方法推进顺序

训练不要一开始就把 GRU predictor、PPO-Lagrangian、risk field、shield internalization、ROS2 全部打开。必须阶段化推进：

```text
场景规格与指标单元测试
  ↓
场景可视化审查
  ↓
环境 gate 与随机 / 脚本 rollout
  ↓
普通 PPO baseline
  ↓
TTC / semantic risk baseline
  ↓
PPO-Lagrangian without intent
  ↓
rule-prior PIRL-Nav
  ↓
GRU intent predictor
  ↓
PIRL-Nav full
  ↓
Gazebo / ROS2 验证
```

硬规则：场景未通过可视化审查、环境未通过 reset / step / rollout gate 之前，不启动大规模训练。

## Curriculum 原则

Curriculum 只用于稳定训练和诊断，不应被写成论文主创新。

推荐顺序：

1. **基础导航 sanity check**：空场景或少量静态障碍，目标是学会到达目标且不碰撞。
2. **普通动态避障 sanity check**：对象从一开始就运动，用于验证基础动态避障能力。
3. **Latent Start**：对象当前静止但未来可能启动或横穿，验证提前响应。
4. **Occlusion and Multi-Intent**：加入遮挡出现与多意图对象，验证多模态未来风险。
5. **Narrow Passage and High-Inertia Objects**：加入狭窄通道、叉车、移动机器人等高惯性对象。
6. **Robust Interaction**：加入 crowd_robot_flow、tracking noise、dropout、delay 和 control disturbance。

## Reward / Cost 原则

基础 reward 保持简单：

```text
R = progress_reward
  + goal_reward
  - collision_penalty
  - time_penalty
  - jerk_penalty
  - detour_penalty
```

不要把所有安全目标都塞进 reward，否则无法证明 constrained RL 的必要性。

第一版主约束只保留：

```text
C_near
C_risk
```

稳定后再加入：

```text
C_shield
```

指标定义必须与 `docs/04_metrics_contract.md` 一致。

## Shield 使用策略

训练早期可以使用强 shield 防止大量碰撞，但论文中必须同时报告 policy-only 与 policy+shield。

训练中期应记录 policy action 与 safe action，并为后续 shield intervention cost / shield dependence index 预留字段。

训练后期必须降低 shield 依赖，并分别评估 policy-only 和 policy+shield。论文中必须同时报告 SDI frequency 和 SDI magnitude。

## 基线方法

至少包括：

1. Vanilla PPO；
2. PPO + TTC reward；
3. PPO + semantic risk reward；
4. PPO-Lagrangian without intent；
5. PIRL-Nav rule prior；
6. PIRL-Nav full。

## 运行模式

所有关键方法至少报告两种模式：

1. **policy-only**：直接执行策略输出，观察策略自身是否学会提前避险；
2. **policy+shield**：策略输出经过 safety supervisor 修正，观察系统级安全性和 shield dependence。

如果只报告 policy+shield，不能支撑“策略已经内化安全行为”的论文结论。

## 随机种子协议

每个实验必须记录：

- scenario seed；
- environment seed；
- policy initialization seed；
- training seed；
- evaluation seed。

如果平台或物理仿真无法完全 deterministic，必须在报告中标注非确定性来源。

## 输出产物

每次正式实验至少输出：

```text
metrics.csv                         每个 episode 的原始指标
summary.json                        聚合指标和置信区间
rollout_samples/                    少量代表性轨迹，不提交大视频
scenario_manifest_used.yaml         实际使用的 manifest 快照
config_used.yaml                    实际配置快照
README.md                           该次实验的文字说明
```

大型日志、模型权重和视频不进 Git。可在外部存储中保存，并在实验 README 中记录路径或编号。

## 统计报告要求

对每个方法至少报告：

- mean；
- standard deviation；
- median；
- bootstrap confidence interval 或至少多 seed 结果；
- per-family breakdown；
- per-difficulty breakdown。

仅报告 overall average 不够，因为 PIRL-Nav 的优势可能主要体现在 latent-start、occlusion-crossing 等高风险 family。

## 训练结果进入论文表格前

必须满足：

- 使用固定 manifest；
- 多 seed 评估；
- 同时报告 policy-only 与 policy+shield；
- 报告 per-family 和 per-difficulty breakdown；
- 报告 near miss、risk exposure、AT、SDI、jerk、detour、clearance；
- 失败案例不得被删除，只能解释。

## 结果解释边界

实验结果只能支撑实际测试过的结论。例如：

- 只在 2.5D Gymnasium 中测试，不能声称真实无人机可用；
- 只在 PyBullet 中测试，不能声称 ROS2 链路实时稳定；
- 只在 policy+shield 模式安全，不能声称策略本身安全；
- 只降低 near miss 但 jerk 大幅变差，不能声称整体导航质量提升。

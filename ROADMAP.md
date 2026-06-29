# PIRL-Nav 路线图

## Stage 0：仓库初始化

目标：建立清晰的实现仓库骨架。

阶段门槛：只建结构，不写仿真、不写强化学习、不引入大依赖。

## Stage 1：场景生成器

目标：基于 YAML 规格实现六类核心场景的候选 seed 生成。

阶段门槛：同一 family / difficulty / seed 必须可复现。

## Stage 2：场景可视化流水线

目标：自动输出俯视布局图、对象轨迹时间线、风险热力图或风险占位图。

阶段门槛：未通过人工可视化审查的场景不得进入固定测试集。

## Stage 3：PyBullet 主训练环境

目标：实现 UAV-IntentRisk PyBullet 环境，采用 Gymnasium 风格 API。

阶段门槛：随机动作与脚本策略 rollout 可视化正常，碰撞、clearance、控制延迟可检查。

## Stage 4：奖励、约束与指标

目标：实现 progress reward、near-miss cost、risk exposure、AT、SDI、jerk、detour 等核心指标。

阶段门槛：指标单元测试与手工案例检查通过。

## Stage 5：基线方法

目标：训练 Vanilla PPO、PPO+TTC、PPO+semantic risk、PPO-Lagrangian without intent。

阶段门槛：必须输出训练曲线、代表性 rollout、分场景指标表。

## Stage 6：PIRL-Nav 完整方法

目标：实现 rule prior、GRU intent predictor、action-conditioned risk、PPO-Lagrangian、shield internalization。

阶段门槛：相对 baseline 在 near miss、risk exposure、AT、SDI 上有一致优势，同时 detour 和 jerk 不显著恶化。

## Stage 7：Gazebo / ROS2 验证

目标：验证策略在 ROS2 节点链路中的可运行性与延迟稳定性。

阶段门槛：报告 mean / p95 / p99 / max latency、deadline miss、policy-only 与 policy+shield。
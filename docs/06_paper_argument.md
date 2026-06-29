# 06 Paper Argument Scaffold

本文档用于约束后续论文写作，不替代正式 manuscript。它的作用是提前固定 PIRL-Nav 的主张、证据链和边界，避免实验做完后才临时拼贡献。

## 建议标题方向

Predictive Intent-Risk Constrained Reinforcement Learning for UAV Navigation under Latent Motion Intent Uncertainty

## 核心论点

现有反应式避障或普通动态避障通常在对象已经运动、距离已经接近或 TTC 已经危险时才强烈响应。PIRL-Nav 的论点是：在低空无人机场景中，很多关键风险来自“当前未必运动、但未来可能启动或从遮挡处出现”的对象，因此策略需要学习动作相关的未来意图风险，并通过约束强化学习提前规避。

## 论文贡献写法

建议贡献表述：

1. We formulate UAV navigation under latent motion intent uncertainty, where currently static or partially observed objects may become future collision risks.
2. We introduce an action-conditioned predictive intent-risk representation that estimates future risk exposure induced by candidate ego actions.
3. We train navigation policies with intent-risk constraints and shield intervention signals to reduce near misses and shield dependence.
4. We construct a visually reviewable scenario benchmark and report behavior-level metrics including risk exposure, Anticipation Time, and Shield Dependence Index.

## 论文结构建议

```text
1. Introduction
2. Related Work
   2.1 UAV navigation and collision avoidance
   2.2 Safe and constrained reinforcement learning
   2.3 Intent prediction and risk-aware planning
   2.4 Simulation benchmarks and evaluation metrics
3. Problem Formulation
   3.1 Latent motion intent uncertainty
   3.2 Observation, action, and risk process
   3.3 Safety supervisor and policy modes
4. Method
   4.1 Intent candidate representation
   4.2 Action-conditioned predictive risk
   4.3 Intent-risk constrained RL
   4.4 Shield internalization
5. Benchmark and Metrics
   5.1 Scenario families
   5.2 Visual review protocol
   5.3 Metrics contract
6. Experiments
   6.1 Baselines
   6.2 Main results
   6.3 Ablations
   6.4 Policy-only vs policy+shield
   6.5 Failure cases
7. Gazebo / ROS2 validation
8. Limitations and conclusion
```

## 必要图表

- 方法总览图：observation -> intent candidates -> action-conditioned risk -> constrained RL -> safety supervisor；
- 场景 family 图：latent start、occlusion emergence、multi-intent crossing 等；
- 风险热力图或动作条件风险对比图；
- rollout 对比图：baseline late reaction vs PIRL-Nav early avoidance；
- 主结果表：per-family 指标；
- 消融表：去掉 intent、去掉 action conditioning、去掉 constraint、去掉 shield signal；
- policy-only / policy+shield 对比图或表。

## 不能写过头的结论

- 没有真实飞行实验时，不声称已经验证真实无人机部署；
- Gazebo / ROS2 只证明链路可运行和延迟可测，不等于真实世界安全；
- 如果只在 PyBullet 中测试，不声称跨仿真泛化；
- 如果 policy-only 仍不安全，不声称策略已经完全内化 safety；
- 如果 detour 或 jerk 明显恶化，不能只强调 near miss 降低。

## 审稿风险与应对

| 风险 | 应对 |
|---|---|
| 被认为只是 reward shaping | 强调 constrained RL、固定指标合同和 reward baseline 对比 |
| 被认为只是 intent prediction + RL 拼接 | 展示 action-conditioned risk 的必要消融 |
| 被认为仿真场景人为 | 使用可视化审查、固定 manifest、per-family breakdown 和失败案例 |
| 被认为 safety shield 掩盖策略能力 | 必报 policy-only 与 policy+shield，以及 SDI |
| 被认为平台贡献弱 | 明确平台是验证层，不是主创新 |

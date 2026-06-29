# 02 Research Hypotheses and Ablation Matrix

本文档把 PIRL-Nav 的论文假设、消融变量和预期证据写成可执行实验协议，避免后续实现偏离论文主线。

## 主假设

**H0 / Null**：动作相关意图风险不会显著改善无人机在潜在运动意图不确定场景中的安全行为。  
**H1 / PIRL-Nav**：动作相关预测式意图风险 + 约束强化学习 + shield internalization 能显著降低 near miss、risk exposure 和 shield dependence，并提前 Anticipation Time，同时不显著降低 success rate 或显著增加 detour / jerk。

## 子假设

### H1：动作相关风险优于状态静态风险

只使用“对象是否危险”的静态风险图不够，因为同一位置在不同动作下会产生不同未来暴露。需要比较：

- state-only risk；
- semantic risk；
- TTC risk；
- action-conditioned predictive risk。

预期证据：action-conditioned risk 在横穿、突然启动、遮挡出现等场景中更早产生规避行为。

### H2：约束优化优于纯 reward shaping

如果 near miss 和 risk exposure 只是 reward penalty，策略可能通过牺牲稳定性或路径效率来换取局部奖励。需要比较：

- Vanilla PPO；
- PPO + TTC reward；
- PPO + semantic risk reward；
- PPO-Lagrangian without intent risk；
- PIRL-Nav constrained variant。

预期证据：约束版本在安全指标上更稳定，且不会只通过极端绕行刷低风险。

### H3：shield internalization 应减少末端安全修正

Safety supervisor 不应只作为最终保险，而应作为训练信号帮助策略提前学习。需要比较：

- policy-only；
- policy + shield；
- policy trained with shield intervention signal；
- policy trained without shield intervention signal。

预期证据：PIRL-Nav 的 policy-only 行为已经更安全，policy+shield 的干预频率和干预幅度下降。

### H4：可视化审查场景能提升论文可信度

固定测试集必须来自人工审查通过的 scenario manifest。不能只用随机 seed 报告平均效果。

预期证据：论文可以展示代表性场景的俯视图、对象意图时间线、风险热力图和 rollout 行为。

## 最小消融矩阵

| 方法 | 意图建模 | 风险形式 | RL 约束 | Shield 信号 | 必报指标 |
|---|---|---|---|---|---|
| Vanilla PPO | 无 | 无 | 无 | 无 | success, collision, jerk, detour |
| PPO + TTC | 无 | TTC | reward penalty | 可选 | 全部 |
| PPO + semantic risk | 无 | 语义风险 | reward penalty | 可选 | 全部 |
| PPO-Lagrangian no intent | 无 | near-miss / exposure cost | 有 | 可选 | 全部 |
| PIRL-Nav no shield signal | 有 | action-conditioned risk | 有 | 无 | 全部 |
| PIRL-Nav full | 有 | action-conditioned risk | 有 | 有 | 全部 |

## 必须避免的伪贡献

- 只换一个仿真平台，但研究问题没有变化；
- 只把语义分割结果接入 RL，但没有动作相关未来风险；
- 只展示漂亮视频，不报告固定测试集指标；
- 只报告 success rate，忽略 near miss 和 shield dependence；
- 只展示 policy+shield，隐藏 policy-only 的真实能力。

# 05 Scenario Benchmark

本文档是 PIRL-Nav 场景 family、难度分级、sanity check 和 fixed-test 进入条件的唯一入口。不要再新增独立的“场景设计”文档；场景相关修订应直接更新本文档、scenario YAML 或 manifest。

场景基准的目标不是堆随机障碍，而是稳定触发 latent motion intent uncertainty，让方法差异能被观察和量化。

## 场景设计原则

1. **潜在意图明确**：对象可以 stay、start、cross、yield、accelerate 或 emerge。
2. **风险提前可见但不确定**：策略应有机会提前规避，但不能直接知道唯一未来。
3. **动作相关**：同一场景中，不同候选动作导致不同未来风险暴露。
4. **可视化可审查**：人工能从俯视图和时间线判断场景是否合理。
5. **难度可分级**：easy / medium / hard 应在速度、遮挡、距离、启动时间和通道宽度上可解释。

每个 reset 或 scenario spec 应能明确追溯：地图、起点、终点、静态障碍物、动态对象、潜在运动对象、遮挡物、对象候选意图、启动或出现时间、语义类别、感知噪声和控制扰动。

普通静态避障和普通动态避障可以作为 sanity check，但不应占据 PIRL-Nav 的论文主线。

## Family A：Latent Start

对象当前静止，但未来可能启动并穿越无人机路径。

关键变量：

- start probability；
- start time distribution；
- object class；
- crossing angle；
- initial distance；
- ego speed。

预期考察：策略是否在对象尚未运动时提前调整速度或侧向路径。

## Family B：Occlusion Emergence

对象从门口、拐角、货架或车辆后方突然出现。

关键变量：

- occluder geometry；
- emergence time；
- visible cue strength；
- object speed；
- reaction corridor width。

预期考察：策略是否对遮挡边缘保持更合理 clearance，而不是贴边高速通过。

## Family C：Multi-Intent Crossing

多个对象具有 stay / cross / yield 等候选意图，轨迹在早期高度相似。

关键变量：

- number of objects；
- intent prior；
- intent switch time；
- crossing density；
- goal conflict。

预期考察：策略是否能在不确定期间选择低风险动作，而不是等对象真实运动后才急刹。

## Family D：Narrow Passage with Yield

无人机必须通过狭窄通道，对象可能让行、停留或突然进入通道。

关键变量：

- passage width；
- object yield probability；
- wait time；
- allowed detour；
- static obstacle density。

预期考察：策略是否能平衡到达效率与潜在风险，而不是过度保守或鲁莽抢行。

## Family E：Vehicle / Forklift Launch

车辆、叉车、移动机器人或推车从静止状态启动，造成低空无人机路径冲突。

关键变量：

- acceleration profile；
- launch trigger；
- vehicle footprint；
- stopping distance；
- turn radius。

预期考察：策略是否能对高惯性对象更早规避，并避免近距离横穿。

## Family F：Goal-Directed Crowd / Robot Flow

多个移动体沿各自目标行动，局部流向可能短时间内改变。

关键变量：

- flow density；
- local goal distribution；
- temporary stop / restart；
- crowd crossing angle；
- observation noise。

预期考察：策略是否能在复杂交互中降低 risk exposure 和 shield intervention。

## 支撑性 sanity check 场景

以下场景可用于调试环境和基础导航能力，但不应作为主要论文贡献：

- `static_clutter`：基础静态避障；
- `dynamic_crossing`：对象从一开始就运动的普通动态横穿；
- `semantic_distractor`：语义上高风险但未来不进入路径的反过度保守场景。

## 难度分级建议

| Difficulty | 风险触发 | 空间裕度 | 观测条件 | 预期行为 |
|---|---|---|---|---|
| easy | 触发较晚、速度低 | 通道宽 | 无遮挡或弱遮挡 | 轻微提前减速或绕行 |
| medium | 触发中等、速度中 | 通道中等 | 局部遮挡 / 噪声 | 明显提前调整 |
| hard | 触发早、速度高 | 通道窄 | 强遮挡 / 延迟 / dropout | 必须主动保守，否则 near miss |

补充参数范围建议：

| 参数 | Easy | Medium | Hard |
|---|---:|---:|---:|
| 潜在风险对象数量 | 1 | 2-3 | 3-5 |
| 对象速度 | 0.3-0.8 m/s | 0.5-1.2 m/s | 0.8-1.8 m/s |
| 启动 / 出现时间 | 3-6 s | 1.5-5 s | 0.5-3 s |
| 通道 / 规避空间 | 宽 | 中 | 窄 |
| 语义或意图噪声 | 0% | 10% | 20% |
| 位置噪声 | 0.02 m | 0.05 m | 0.10 m |
| 控制延迟 | 0 s | 0.05 s | 0.10 s |

## 数据集与 manifest 规则

训练集可以随机生成，但 validation set 和 fixed test set 必须来自 manifest。

建议固定测试规模先从小到大：

```text
最小论文前检查：6 类场景 × 5 seeds × 3 difficulty = 90 episodes / method / run_mode
正式固定测试集：6 类场景 × 20 seeds × 3 difficulty = 360 episodes / method / run_mode
```

未经可视化审查的候选场景只能留在 candidate set。reviewed set 只说明可以进入后续环境或实验阶段；fixed test set 必须另行冻结，不得由 candidate 或 reviewed manifest 自动升级。

## 进入固定测试集的条件

场景必须同时满足：

- YAML 规格完整；
- 同一 seed 可复现；
- 可视化审查通过；
- PyBullet / Gymnasium 环境中无几何穿模、不可达目标或不合理初始重叠；
- 风险事件不是纯随机噪声；
- 至少一个 baseline 会表现出可解释失败模式；
- train / validation / fixed test manifest 明确分离。 

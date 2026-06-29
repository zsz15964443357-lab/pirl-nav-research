# 05 Scenario Benchmark

本文档定义 PIRL-Nav 的核心场景 family。场景基准的目标不是堆随机障碍，而是稳定触发 latent motion intent uncertainty，让方法差异能被观察和量化。

## 场景设计原则

1. **潜在意图明确**：对象可以 stay、start、cross、yield、accelerate 或 emerge。
2. **风险提前可见但不确定**：策略应有机会提前规避，但不能直接知道唯一未来。
3. **动作相关**：同一场景中，不同候选动作导致不同未来风险暴露。
4. **可视化可审查**：人工能从俯视图和时间线判断场景是否合理。
5. **难度可分级**：easy / medium / hard 应在速度、遮挡、距离、启动时间和通道宽度上可解释。

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

## 难度分级建议

| Difficulty | 风险触发 | 空间裕度 | 观测条件 | 预期行为 |
|---|---|---|---|---|
| easy | 触发较晚、速度低 | 通道宽 | 无遮挡或弱遮挡 | 轻微提前减速或绕行 |
| medium | 触发中等、速度中 | 通道中等 | 局部遮挡 / 噪声 | 明显提前调整 |
| hard | 触发早、速度高 | 通道窄 | 强遮挡 / 延迟 / dropout | 必须主动保守，否则 near miss |

## 进入固定测试集的条件

场景必须同时满足：

- YAML 规格完整；
- 同一 seed 可复现；
- 可视化审查通过；
- 风险事件不是纯随机噪声；
- 至少一个 baseline 会表现出可解释失败模式；
- 没有几何穿模、不可达目标或不合理初始重叠。

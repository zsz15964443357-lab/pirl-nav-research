# Scenario Review Checklist

用于审查场景是否可以进入 reviewed set、train set、validation set 或 fixed test set。

## 基本完整性

- [ ] 场景 YAML 字段完整；
- [ ] family 与 `docs/05_scenario_benchmark.md` 一致；
- [ ] difficulty 可解释；
- [ ] seed 可复现；
- [ ] ego start / goal 合理且可达；
- [ ] 没有初始碰撞、重叠或穿模。

## 潜在意图风险

- [ ] 场景确实包含 latent motion intent uncertainty；
- [ ] 对象候选意图清晰，例如 stay / start / cross / yield / emerge；
- [ ] 风险不是纯随机噪声；
- [ ] 不同候选动作会导致不同未来风险暴露；
- [ ] 至少一个 baseline 可能产生可解释失败模式。

## 可视化审查

- [ ] 俯视布局可读；
- [ ] 对象轨迹时间线可读；
- [ ] 遮挡体、通道、启动点或横穿点清晰；
- [ ] 风险区域或风险占位图与场景文字一致；
- [ ] 人工审查意见已记录。

## 进入固定测试集前

- [ ] 该场景不用于调参；
- [ ] manifest 记录 path / family / difficulty / seed；
- [ ] 审查状态为 approved；
- [ ] 固定后不因方法表现而删除。

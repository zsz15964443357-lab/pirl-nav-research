# Training Review Checklist

用于审查训练实验是否能进入正式结果汇总。

## 实验记录

- [ ] experiment_id 唯一；
- [ ] commit SHA 已记录；
- [ ] config 快照已保存；
- [ ] scenario manifest 已记录；
- [ ] seeds 已记录；
- [ ] run mode 为 `policy_only` 或 `policy_plus_shield`。

## 方法公平性

- [ ] baseline 与 PIRL-Nav 使用同一环境；
- [ ] baseline 与 PIRL-Nav 使用同一 fixed test manifest；
- [ ] 没有为单个方法更换测试场景；
- [ ] 相同指标阈值用于所有方法；
- [ ] policy-only 与 policy+shield 都有报告入口。

## 指标完整性

- [ ] success rate；
- [ ] collision rate；
- [ ] near miss；
- [ ] integrated risk exposure；
- [ ] Anticipation Time；
- [ ] SDI frequency；
- [ ] SDI magnitude；
- [ ] jerk；
- [ ] detour ratio；
- [ ] min clearance。

## 产物

- [ ] metrics.csv；
- [ ] summary.json；
- [ ] per-family breakdown；
- [ ] per-difficulty breakdown；
- [ ] representative rollout samples；
- [ ] known failure cases。

## 禁止

- [ ] 没有只挑成功 episode 做平滑性统计；
- [ ] 没有只用漂亮视频代替固定测试集；
- [ ] 没有隐藏 shield intervention；
- [ ] 没有提交大日志、模型权重或视频到 Git。

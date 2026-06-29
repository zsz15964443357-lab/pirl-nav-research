# TASK 04：奖励、约束与指标

## 目标

实现训练 reward、约束 cost 和评价指标。

## 必须先读

- `docs/04_训练策略.md`
- `docs/06_评价指标.md`

## Reward

- progress reward；
- goal reward；
- collision penalty；
- time penalty；
- jerk penalty；
- detour penalty。

## Cost

第一版至少实现：

- near-miss cost；
- risk exposure cost 占位；
- shield intervention cost 占位。

## Metrics

必须实现：

- success rate；
- collision rate；
- near-miss rate；
- min clearance；
- min TTC；
- integrated risk exposure；
- Anticipation Time；
- Shield Dependence Index；
- jerk；
- detour ratio。

## 审查门槛

AT 和 SDI 必须有手工案例验证，不能只依赖训练输出。
# TASK 05：基线方法

## 目标

先建立公平、可解释的 baseline，再实现 PIRL-Nav full。

## 必须先读

- `docs/04_训练策略.md`
- `docs/06_评价指标.md`

## Baselines

至少实现：

1. Vanilla PPO；
2. PPO + TTC reward；
3. PPO + semantic risk reward；
4. PPO-Lagrangian without intent；
5. rule-prior risk baseline。

## 必须输出

- 训练曲线；
- 分场景评估表；
- 代表性 rollout GIF；
- policy-only 与 policy+shield 对比；
- 每个 baseline 的失败案例。

## 禁止事项

- 不故意削弱 baseline；
- 不只比较 success / collision；
- 不隐藏失败行为。

## 审查门槛

网页端必须审查代表性 rollout，再进入 PIRL-Nav full。
# TASK 06：完整方法

## 目标

在基线方法建立后，实现 PIRL-Nav 完整版本。

## 必须先读

- `docs/02_研究主线.md`
- `docs/04_训练策略.md`
- `docs/06_评价指标.md`

## 必须组件

1. 规则先验意图风险版本；
2. GRU 意图预测器；
3. 动作相关预测风险代价；
4. PPO-Lagrangian；
5. 安全监督器；
6. shield 内化训练信号。

## 训练顺序

1. 先训练规则先验风险版本；
2. 单独训练意图预测器；
3. 冻结预测器训练策略；
4. 加入 shield 内化；
5. 分别评估 policy-only 与 policy-plus-shield。

## 消融实验

- 去掉意图预测器；
- 去掉语义先验；
- 去掉概率风险；
- 去掉约束训练；
- 去掉 shield 内化；
- 去掉循环记忆。

## 审查门槛

必须证明 near miss、risk exposure、AT、SDI 有一致改善，同时 detour 和 jerk 不可明显恶化。
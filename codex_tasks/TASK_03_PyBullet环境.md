# TASK 03：PyBullet 主训练环境

## 目标

实现 PyBullet-based UAV-IntentRisk Env，作为主训练环境。

## 必须先读

- `docs/01_架构决策.md`
- `docs/03_场景设计.md`
- `docs/04_训练策略.md`

## API 要求

采用 Gymnasium 风格：

```python
env = PirlNavBulletEnv(config)
obs, info = env.reset(seed=seed)
obs, reward, terminated, truncated, info = env.step(action)
```

## 观测

至少包含：

- ego state；
- relative goal；
- local occupancy 或 scan；
- Top-K object tracks；
- intent-risk feature 占位；
- last action。

## 动作

第一版使用 body-frame velocity command 或 acceleration command，不直接输出电机推力。

## 必须支持

- UAV 半径或碰撞体；
- 速度 / 加速度 / yaw-rate 限制；
- 碰撞检测；
- clearance 计算；
- 控制延迟；
- 按场景配置驱动动态对象。

## 审查门槛

训练前必须提供随机策略和脚本策略 rollout 可视化。
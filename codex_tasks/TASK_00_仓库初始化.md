# TASK 00：仓库初始化

## 目标

只建立实现仓库骨架，不实现任何仿真、强化学习或 ROS2 功能。

## 必须先读

- `README.md`
- `docs/00_项目简述.md`
- `docs/01_架构决策.md`
- `docs/11_仓库结构.md`

## 允许输出

建立以下目录和最小占位文件：

```text
pirl_nav/
  sim/
  perception/
  intent/
  risk/
  rl/
  safety/
  evaluation/
  visualization/
configs/
experiments/
scripts/
tests/
```

## 禁止事项

- 不实现 PyBullet 环境；
- 不实现 RL 算法；
- 不安装大型依赖；
- 不改研究主线；
- 不提前创建训练脚本。

## 审查门槛

网页端审查目录是否简洁、清晰、符合文档架构。
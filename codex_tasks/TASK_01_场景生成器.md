# TASK 01B：场景生成器（暂缓）

> 状态：暂不执行。当前 Stage 1 的正式入口是
> `codex_tasks/TASK_01_scenario_specification.md`。
>
> 本文件保留为后续 Stage 1.5 / Stage 2 前置任务草案。只有在六类 seed-level
> candidate YAML、candidate manifest、schema validation 和 Stage 2 可视化审查入口
> 稳定后，才允许重新激活本任务。

## 目标

实现基于已审查 YAML 规格的六类核心场景生成器。

## 必须先读

- `codex_tasks/TASK_01_scenario_specification.md`
- `docs/13_stage1_scenario_audit_2026-06-29.md`
- `docs/03_场景设计.md`
- `docs/05_可视化审查规范.md`
- `experiments/scenario_specs/README.md`

## 输入

- 场景类型；
- 难度等级；
- 随机种子；
- 场景配置文件。

## 输出

每个场景实例应包含：

- 地图边界；
- UAV 起点和目标；
- 静态障碍物；
- 动态对象；
- 语义类别；
- 潜在意图模式；
- 对象运动参数；
- 感知噪声设置；
- 控制误差设置。

## 必须完成

- 场景实例导出为 JSON；
- 命令行生成入口；
- 同一 seed 重复生成结果一致；
- 基础单元测试。

## 禁止事项

- 不替代 `experiments/scenario_specs/*.yaml` 中的人工可审查 seed-level 规格；
- 不训练强化学习；
- 不实现 PyBullet 主环境；
- 不跳过可视化审查。

## 审查门槛

生成器输出必须进入下一阶段可视化流水线，人工审查后才能进入固定测试集。

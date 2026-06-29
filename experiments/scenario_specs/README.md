# 场景规格说明

本目录保存六类核心场景的配置规格。Codex CLI 实现场景生成器时，必须先读取 `docs/03_场景设计.md` 和本目录文件。

## 六类核心场景

1. `static_clutter.yaml`：基础静态避障；
2. `dynamic_crossing.yaml`：普通动态横穿；
3. `sudden_start.yaml`：当前静止后突然启动；
4. `occluded_emergence.yaml`：遮挡后突然出现；
5. `intent_ambiguous.yaml`：多意图不确定；
6. `semantic_distractor.yaml`：高风险语义但不进入路径。

## 生成原则

- 训练集可以随机生成；
- 测试集必须固定 seed；
- 所有固定测试 seed 必须通过可视化审查；
- 每个场景都要有 easy / medium / hard 难度。
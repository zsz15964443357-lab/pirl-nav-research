# Scenario Specs

本目录保存 PIRL-Nav 的场景 family 规格和 YAML 示例。场景规格的核心职责是稳定表达 latent motion intent uncertainty，而不是随机堆障碍。

场景设计应与 `docs/05_scenario_benchmark.md` 保持一致。

## 当前 schema

```yaml
scenario_id: latent_start_easy_0001
family: latent_start
difficulty: easy
seed: 1001
map:
  size: [20.0, 12.0]
  static_obstacles: []
ego:
  start: [1.0, 6.0]
  goal: [18.0, 6.0]
  radius: 0.3
  nominal_speed: 1.0
objects:
  - id: pedestrian_0
    class: pedestrian
    initial_state:
      position: [10.0, 4.0]
      velocity: [0.0, 0.0]
    intent_candidates:
      - name: stay
        probability: 0.4
        conflicts_with_ego_nominal_path: false
      - name: cross
        probability: 0.6
        trigger_time: [2.0, 4.0]
        target: [10.0, 8.0]
        conflicts_with_ego_nominal_path: true
risk:
  min_clearance: 0.8
  near_miss_distance: 1.0
  exposure_horizon: 4.0
  shield_trigger_distance: 0.55
review:
  status: candidate
  reviewer: null
  notes: null
```

## 场景 family

- `latent_start`：静止对象未来可能启动；
- `occlusion_emergence`：对象从遮挡后出现；
- `multi_intent_crossing`：多个对象候选意图不确定；
- `narrow_passage_yield`：狭窄通道中对象可能让行或抢占；
- `vehicle_forklift_launch`：高惯性对象从静止启动；
- `crowd_robot_flow`：多移动体流向局部变化。

## 校验入口

```bash
python scripts/validate_scenarios.py
```

校验器只检查仓库契约：字段完整性、六类核心 family 覆盖、候选意图概率和为 1、至少一个候选意图与无人机名义路径冲突、review status 可追溯。它不替代 Stage 2 可视化审查。

## 进入 reviewed / fixed manifest 前必须满足

- YAML 字段完整；
- seed 可复现；
- 可视化审查通过；
- 风险事件与 family 定义一致；
- 不存在初始重叠、不可达目标或几何穿模。

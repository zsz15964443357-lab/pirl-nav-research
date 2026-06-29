# Scenario Specs

本目录保存 PIRL-Nav 的场景 family 规格和 YAML 示例。场景规格的核心职责是稳定表达 latent motion intent uncertainty，而不是随机堆障碍。

场景设计应与 `docs/05_scenario_benchmark.md` 保持一致。

## 推荐 schema

```yaml
scenario_id: latent_start_easy_0001
family: latent_start
difficulty: easy
seed: 1
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
      - name: cross
        probability: 0.6
        trigger_time: [2.0, 4.0]
        target: [10.0, 8.0]
risk:
  min_clearance: 0.8
  near_miss_distance: 1.0
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

## 进入 manifest 前必须满足

- YAML 字段完整；
- seed 可复现；
- 可视化审查通过；
- 风险事件与 family 定义一致；
- 不存在初始重叠、不可达目标或几何穿模。

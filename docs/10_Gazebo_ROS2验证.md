# 10 Gazebo / ROS2 验证

## 定位

Gazebo / ROS2 是最终系统验证层，不是主训练平台，也不是论文主创新。

其作用是证明：训练出的策略可以进入接近真实部署的节点链路，并在延迟、消息对齐、policy inference、safety supervisor 等方面可运行。

## 推荐节点

```text
/pirl_state_bridge
/pirl_tracker_node
/pirl_intent_node
/pirl_risk_field_node
/pirl_policy_node
/pirl_safety_supervisor_node
/pirl_cmd_mux_node
/pirl_latency_profiler
/pirl_logger
/pirl_visualizer
```

## QoS 原则

- sensor / depth / lidar：Best effort，Keep last，depth 1-5；
- odom / imu：Reliable 或 Best effort，按实际延迟测试；
- tracked_objects：Reliable，Keep last 1；
- policy_cmd / safe_cmd：Reliable，Keep last 1；
- visualization / logs：独立 executor，不能阻塞控制链路。

## 必须报告的延迟指标

| 节点 | Mean | p95 | p99 | Max | Deadline miss |
|---|---:|---:|---:|---:|---:|
| tracker | | | | | |
| intent predictor | | | | | |
| risk field | | | | | |
| policy inference | | | | | |
| safety supervisor | | | | | |
| end-to-end | | | | | |

## 验证场景

至少复现：

- sudden_start；
- occluded_emergence；
- intent_ambiguous；
- semantic_distractor。

## 不允许的表述

- 不声称硬实时；
- 不只报告平均延迟；
- 不把 ROS2 demo 当作算法效果主证据；
- 不让日志和可视化阻塞控制链路。
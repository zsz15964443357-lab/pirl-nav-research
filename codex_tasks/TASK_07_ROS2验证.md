# TASK 07：Gazebo / ROS2 验证

## 目标

将训练后的策略放入 Gazebo / ROS2 链路中验证可运行性和延迟稳定性。

## 必须先读

- `docs/10_Gazebo_ROS2验证.md`

## 推荐节点

- state bridge；
- tracker node；
- intent node；
- risk field node；
- policy node；
- safety supervisor node；
- command mux node；
- latency profiler；
- logger / visualizer。

## 必须输出

- 代表性场景回放；
- 节点级延迟表；
- mean / p95 / p99 / max latency；
- deadline miss；
- policy-only 与 policy-plus-shield 对比。

## 禁止事项

- 不声称硬实时；
- 不只报告平均延迟；
- 不让日志阻塞控制链路；
- 不把 ROS2 demo 当作算法主证据。
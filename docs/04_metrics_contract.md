# 04 Metrics Contract

本文档定义 PIRL-Nav 必须报告的行为级指标。后续实现指标时，应先写单元测试和手工案例，再用于正式训练报告。

## 基础指标

### Success Rate

Episode 在时间限制内到达目标并且没有碰撞，则记为成功。

必须同时报告：

- success rate；
- timeout rate；
- collision rate；
- failure reason breakdown。

### Collision Rate

发生几何碰撞或 safety supervisor 判定不可恢复接触时记为 collision。必须记录碰撞对象类别、场景 family、发生时间和相对速度。

## 安全行为指标

### Near Miss

当无人机与动态对象、潜在启动对象或遮挡出现对象的最小距离低于阈值，但尚未碰撞时，记为 near miss。

建议记录：

```text
near_miss_count
near_miss_min_clearance
near_miss_duration
```

阈值必须随平台尺度写入配置，不允许在不同方法间更改。

### Integrated Risk Exposure

Risk exposure 衡量策略在整个 episode 中暴露于未来意图风险区域的累计程度。

抽象形式：

```text
risk_exposure = integral_t risk(x_t, a_t, scene_t) dt
```

实现时必须记录单位、积分步长、是否归一化、是否区分对象类别。

### Anticipation Time, AT

AT 衡量策略相对风险真正显现之前提前调整行为的时间。

典型定义：

```text
AT = t_risk_event - t_first_avoidance_action
```

其中 `t_first_avoidance_action` 可由速度方向变化、横向偏移、减速或风险规避动作触发判定。必须在文档中固定判定规则。

### Shield Dependence Index, SDI

SDI 衡量策略依赖 safety supervisor 的程度。至少记录两类：

```text
SDI_frequency = number_of_shield_interventions / episode_steps
SDI_magnitude = sum(||safe_cmd - policy_cmd||) / episode_steps
```

论文中必须同时报告 policy-only 与 policy+shield，不能只报告系统加 shield 后的安全性。

## 运动质量指标

### Jerk

Jerk 衡量控制平滑性。可以基于速度命令、加速度命令或实际轨迹计算，但必须固定口径。

```text
jerk_t = ||a_t - a_{t-1}|| / dt
```

如果动作空间不是加速度，需要说明转换方式。

### Detour Ratio

Detour 衡量路径绕行程度。

```text
detour_ratio = actual_path_length / shortest_feasible_path_length
```

如果 shortest feasible path 难以精确计算，可使用无动态风险下的规划路径或静态地图最短路径作为参考，并在报告中说明。

### Clearance

记录 episode 中最小 clearance、平均 clearance 和低 clearance 持续时间。Clearance 应区分静态障碍和动态 / 潜在动态对象。

## 延迟指标

Gazebo / ROS2 阶段必须报告：

- mean latency；
- p95 latency；
- p99 latency；
- max latency；
- deadline miss count；
- policy inference time；
- safety supervisor correction time。

## 指标报告最低要求

正式论文表格不能少于以下列：

```text
method
scenario_family
difficulty
run_mode
success_rate
collision_rate
near_miss_count
risk_exposure
AT
SDI_frequency
SDI_magnitude
jerk
detour_ratio
min_clearance
```

## 指标反作弊规则

- 不允许不同方法使用不同 near-miss 阈值；
- 不允许只报告成功 episode 的 jerk / detour；
- 不允许剔除失败 episode 后再算 safety 指标；
- 不允许只用少数漂亮 rollout 替代固定测试集统计；
- 不允许隐藏 shield intervention。

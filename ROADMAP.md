# PIRL-Nav 路线图

路线图采用 stage-gated workflow。每一阶段都必须留下可审查产物，不能只留下口头结论或一次性脚本。

## Stage 0：仓库初始化

**目标**：建立科研代码仓库的最小骨架和审查协议。  
**允许**：目录、占位包、配置模板、CI、文档契约、测试入口。  
**禁止**：仿真环境、RL 算法、大依赖、训练脚本、ROS2 节点。

验收门槛：

- `pirl_nav/` 包可导入；
- `pytest` 至少包含最小导入测试；
- `ruff check .` 可作为基础静态检查入口；
- README、ROADMAP、仓库结构文档和 Codex 任务说明一致。

## Stage 1：场景规格与候选 manifest

**目标**：基于 YAML 场景规格固化候选 seed，不实现仿真或 rollout。
**核心产物**：scenario family schema、difficulty 定义、seed 复现协议、候选 manifest、schema 校验脚本。

验收门槛：

- 六类核心 family 至少各有一个 candidate YAML；
- 同一 family / difficulty / seed 必须可复现；
- 每个场景必须记录对象初始状态、潜在意图集合、触发条件、遮挡体、终点和安全距离；
- `python scripts/validate_scenarios.py` 必须通过；
- 未进入固定测试集前，场景不得被用于报告最终效果。

## Stage 2：场景可视化流水线

**目标**：自动生成俯视布局图、对象轨迹时间线、风险区域预览图或占位图。  
**核心产物**：每个候选场景的 PNG / HTML / JSON 审查包。

验收门槛：

- 人工能看懂对象何时启动、横穿、遮挡出现或让行；
- 风险触发逻辑与场景文字规格一致；
- 未通过人工可视化审查的场景不得进入训练集、验证集或固定测试集。

## Stage 3：PyBullet 主训练环境

**目标**：实现 UAV-IntentRisk PyBullet 环境，采用 Gymnasium 风格 API。  
**核心产物**：reset / step / render / seed / info 语义稳定的环境。

验收门槛：

- 随机动作和脚本策略 rollout 可视化正常；
- 速度、加速度、yaw-rate、clearance、碰撞、控制延迟可检查；
- 观测噪声、延迟、dropout 有显式配置；
- 环境日志足以复现实验失败案例。

## Stage 4：奖励、约束与指标

**目标**：实现 progress reward、near-miss cost、risk exposure、AT、SDI、jerk、detour 等核心指标。  
**核心产物**：指标单元测试、手工案例、聚合报告。

验收门槛：

- 每个指标都有定义、单位、边界条件和失败案例；
- 至少覆盖 policy-only 与 policy+shield 两种运行模式；
- 指标不依赖视觉展示才能解释。

## Stage 5：基线方法

**目标**：训练 Vanilla PPO、PPO+TTC、PPO+semantic risk、PPO-Lagrangian without intent 等基线。  
**核心产物**：训练曲线、代表性 rollout、分场景指标表。

验收门槛：

- baseline 共享同一环境、同一测试 manifest、同一统计口径；
- 不允许为某个方法单独调换测试场景；
- 不允许只报告总成功率，必须报告 near miss、risk exposure、AT、SDI、jerk、detour。

## Stage 6：PIRL-Nav 完整方法

**目标**：实现 rule prior、GRU intent predictor、action-conditioned risk、PPO-Lagrangian、shield internalization。  
**核心产物**：完整训练、消融实验、固定测试集报告。

验收门槛：

- 相对 baseline 在 near miss、risk exposure、AT、SDI 上有一致优势；
- success rate 不明显下降；
- detour 和 jerk 不显著恶化；
- 必须同时展示 policy-only 与 policy+shield 行为。

## Stage 7：Gazebo / ROS2 验证

**目标**：验证策略在 ROS2 节点链路中的可运行性与延迟稳定性。  
**核心产物**：节点图、topic contract、ONNX / C++ 推理记录、延迟统计。

验收门槛：

- 报告 mean / p95 / p99 / max latency；
- 报告 deadline miss；
- 报告 safety supervisor 介入次数和介入幅度；
- 不将 ROS2 或 Gazebo 包装成论文主创新，只作为系统可信度验证。

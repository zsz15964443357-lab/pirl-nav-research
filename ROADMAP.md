# PIRL-Nav 路线图

路线图采用 stage-gated workflow。每一阶段都必须留下可审查产物，不能只留下口头结论或一次性脚本。

每个实现类阶段在写代码前都必须先做 open-source scan：调研可参考的开源项目、论文代码、标准库和成熟工具链，说明复用 / 改造 / 自定义的边界，并记录许可证与来源。通用基础设施优先复用成熟项目，PIRL-Nav 的创新集中在 latent motion intent uncertainty、action-conditioned predictive risk、constrained RL 和 shield internalization。

## 阶段粒度原则

后续阶段应从整体项目推进角度设计，不要把每个小函数、单个脚本或单个文档拆成一个独立 stage。一个 stage 可以覆盖一组紧密相关的能力，例如 metrics + evaluation aggregation + manifest split + baseline readiness。

判断一个 stage 是否过小：

```text
如果该阶段通过后仍然不能让项目进入一个新的研究能力层级，说明阶段切得太碎。
```

判断一个 stage 是否过大：

```text
如果该阶段同时引入环境、指标、训练算法、论文结果和系统部署，导致审查者无法隔离问题，说明阶段过大。
```

当前建议采用“中等跨度 stage”：每个阶段应能推进一个完整研究能力层级，同时保留清晰 forbidden scope、validation commands 和 review artifacts。

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

- 完成可视化相关开源项目 / 库调研，并记录复用或自定义决策；
- 人工能看懂对象何时启动、横穿、遮挡出现或让行；
- 风险触发逻辑与场景文字规格一致；
- 未通过人工可视化审查的场景不得进入训练集、验证集或固定测试集。

## Stage 3：环境门控与场景接入

**目标**：把 Stage 2 reviewed scenarios 接入可执行环境 API，完成 reset / step / render / info / random rollout / scripted rollout 的环境门控。  
**核心产物**：Gymnasium-style environment gate、reviewed scenario loader、基础几何与动态对象占位、smoke rollout summaries。

说明：Stage 3 可以先是轻量 2.5D environment gate，不必一次完成最终 PyBullet physics backend。完整 PyBullet backend 可以在后续训练前逐步替换或增强，但必须保持同一 API 和同一 reviewed manifest 入口。

验收门槛：

- 完成 PyBullet / Gymnasium / navigation benchmark 开源调研，并记录复用或自定义决策；
- 环境能加载 reviewed manifest，并 reset / step 所有 reviewed scenarios；
- 随机动作和脚本策略 smoke rollout 正常；
- `info` 至少包含 scenario_id、family、seed、step_count、min_clearance、collision、near_miss、risk_exposure_increment、shield_intervention placeholder；
- 不训练任何 policy；
- 不创建 fixed-test manifest；
- 不接 ROS2 / Gazebo / PX4。

## Stage 4：评估指标、数据划分与 baseline-ready 实验管线

**目标**：一次性建立从 environment rollout 到 metrics、episode records、aggregation report、manifest split 和 baseline readiness 的完整评估基础设施。  
**核心产物**：metrics module、evaluation runner、episode record schema、summary aggregation、train / validation manifest draft、baseline training readiness checklist。

Stage 4 不应只做几个指标函数。它应让项目从“环境能跑”推进到“可以严谨比较方法之前的评估管线已就绪”。

允许：

- near_miss、risk_exposure、AT、SDI placeholder / interface、jerk、detour、path_length、clearance 等指标；
- episode-level metrics record；
- per-family / per-difficulty aggregation；
- policy-only / policy+shield run_mode 字段；
- train / validation manifest 草案，但不得生成 fixed test；
- random / scripted baseline evaluation runner；
- baseline readiness checklist；
- Stage 4 audit。

禁止：

- 不训练 PPO / SAC / RLlib / Stable-Baselines3；
- 不声称 PIRL-Nav 有效；
- 不创建 fixed-test manifest；
- 不把 current proxy risk 当最终 action-conditioned predictive risk；
- 不绕过 reviewed manifest；
- 不新增重复 task / audit / final 文档。

验收门槛：

- 完成安全指标、轨迹指标、统计聚合和 RL evaluation tooling 调研；
- 所有指标都有定义、单位、边界条件和最小测试；
- evaluation runner 能对 reviewed scenarios 运行 random / scripted policy，并输出 episode records 与 summary；
- summary 至少支持 overall、per-family、per-difficulty；
- 输出明确标注 current policies are not learned baselines；
- 为 Stage 5 baseline training 提供明确 config / manifest / metric contract。

## Stage 5：基线训练与可复现实验

**目标**：训练 Vanilla PPO、PPO+TTC、PPO+semantic risk、PPO-Lagrangian without intent 等基线，并建立可复现实验目录。  
**核心产物**：baseline configs、training scripts、training curves、representative rollouts、per-family metric tables。

验收门槛：

- 完成 Stable-Baselines3、CleanRL、safe RL / constrained RL 开源调研；
- baseline 共享同一环境、同一测试 manifest、同一统计口径；
- 不允许为某个方法单独调换测试场景；
- 不允许只报告总成功率，必须报告 near miss、risk exposure、AT、SDI、jerk、detour；
- 训练结果必须可追溯到 commit、config、manifest 和 seed。

## Stage 6：PIRL-Nav 完整方法与消融

**目标**：实现 rule prior、GRU intent predictor、action-conditioned risk、PPO-Lagrangian、shield internalization，并完成与 Stage 5 baseline 的同口径比较。  
**核心产物**：完整训练、消融实验、固定测试集报告。

验收门槛：

- 完成 intent prediction、trajectory forecasting、risk-aware RL、shielded RL 相关开源和论文代码调研；
- 相对 baseline 在 near miss、risk exposure、AT、SDI 上有一致优势；
- success rate 不明显下降；
- detour 和 jerk 不显著恶化；
- 必须同时展示 policy-only 与 policy+shield 行为。

## Stage 7：Gazebo / ROS2 验证

**目标**：验证策略在 ROS2 节点链路中的可运行性与延迟稳定性。  
**核心产物**：节点图、topic contract、ONNX / C++ 推理记录、延迟统计。

验收门槛：

- 完成 ROS2、Gazebo、PX4 SITL、ONNX Runtime deployment 示例调研；
- 报告 mean / p95 / p99 / max latency；
- 报告 deadline miss；
- 报告 safety supervisor 介入次数和介入幅度；
- 不将 ROS2 或 Gazebo 包装成论文主创新，只作为系统可信度验证。

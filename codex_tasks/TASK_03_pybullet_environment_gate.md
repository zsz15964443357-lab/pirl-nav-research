# TASK 03：PyBullet / Gymnasium 环境门控

## Academic Research Suite 要求

执行本任务时，Codex CLI 必须显式调用 `academic-research-suite` skill。

终端 prompt 第一行必须写：

```text
Use the academic-research-suite skill.
```

## 仓库同步要求

读取仓库文件或修改任何文件前，必须先拉取最新项目状态：

```bash
git status
git fetch origin
git checkout main
git pull --ff-only origin main
```

如果在任务分支继续工作，必须先同步最新 `main`：

```bash
git checkout <task-branch>
git merge --ff-only origin/main
```

如果不能 fast-forward，必须停止并报告冲突，不得覆盖、force-push 或重写历史。

Codex 最终报告必须包含：

```text
Repository sync status:
Base branch and commit:
Working branch and commit:
```

必须先读：

- `README.md`
- `ROADMAP.md`
- `docs/15_codex_cli_academic_research_suite.md`
- `docs/01_架构决策.md`
- `docs/03_experimental_protocol.md`
- `docs/04_metrics_contract.md`
- `docs/05_scenario_benchmark.md`
- `docs/18_stage2_visualization_audit_2026-06-30.md`
- `experiments/manifests/reviewed_stage2_2026-06-30.yaml`
- `experiments/review_checklists/scenario_review.md`

## 开源优先要求

本阶段不要闭门造车。Codex 在写环境代码前，必须先做 open-source scan，调研并比较：

- PyBullet 示例环境；
- Gymnasium Env API；
- UAV / quadrotor PyBullet examples；
- mobile robot navigation benchmark structures；
- safe RL / constrained RL environment interface conventions；
- collision checking and trajectory logging examples。

任务开始前必须输出：

```text
Open-source scan:
- candidate projects or libraries
- reusable parts
- parts that must stay custom for PIRL-Nav
- license / attribution notes
- adaptation plan
```

如果复用或改造外部项目，必须记录来源、版本、许可证和改动范围。许可证不清楚的代码不得复制进仓库。

## 目标

建立最小可运行的 PyBullet / Gymnasium 风格环境门控，用于把 Stage 2 已审查场景接入可执行仿真。

本阶段只验证环境 API、场景加载、基础几何、对象动态占位和随机 / 脚本动作 rollout。它不是训练阶段。

## 允许输出

- `pirl_nav/sim/` 下的最小环境模块；
- Gymnasium 风格的 `reset` / `step` / `render` / `seed` / `info` 接口；
- 从 `reviewed_stage2_2026-06-30.yaml` 读取场景的 loader；
- 简单 ego 状态更新；
- 简单对象意图动态占位；
- 基础碰撞 / clearance 检查；
- episode termination 条件；
- random action rollout smoke test；
- scripted policy rollout smoke test；
- 小型 render 或 debug export；
- pytest 测试；
- Stage 3 audit 文档。

建议路径：

```text
pirl_nav/sim/
  __init__.py
  env.py
  geometry.py
  scenario_loader.py
  dynamics.py
scripts/rollout_random_policy.py
tests/test_pybullet_environment_gate.py
docs/20_stage3_environment_audit_2026-06-30.md
```

## 禁止事项

- 不实现 PPO、SAC、RLlib、Stable-Baselines3 训练；
- 不训练任何策略；
- 不生成论文结果表；
- 不创建 fixed-test manifest；
- 不把 Stage 2 approved-for-stage3 场景当作最终测试集；
- 不接 ROS2 / Gazebo / PX4；
- 不引入大规模资产、模型权重、大视频或 rosbag；
- 不改变 Stage 1 / Stage 2 场景语义来适配环境；
- 不为了让测试通过而弱化 near-miss、risk exposure 或 shield dependence 的后续指标定义。

## 最低验收标准

- Codex 输出 open-source scan；
- Codex 报告 repository sync status、base branch commit 和 working branch commit；
- 环境能加载 `experiments/manifests/reviewed_stage2_2026-06-30.yaml`；
- 环境能 reset 到至少 6 个 reviewed scenarios；
- 每个场景可以执行随机动作 smoke rollout；
- `info` 至少包含 `scenario_id`、`family`、`seed`、`min_clearance`、`collision`、`near_miss`、`step_count`；
- 不训练任何 policy；
- `python scripts/validate_scenarios.py` 通过；
- `python -m pytest` 通过；
- `python -m ruff check .` 通过。

## 设计要求

### Observation

Stage 3 observation 可以先保持简单，但必须显式文档化。建议包括：

```text
ego position
ego velocity
goal vector
nearest object relative position
nearest object velocity
basic risk threshold values
```

### Action

Stage 3 action 可以先用 2D velocity command 或 acceleration command，但必须保留后续扩展到 UAV yaw-rate / acceleration limits 的接口。

### Dynamics

Stage 3 只需要最小动力学，不需要高保真飞控。必须记录：

```text
time step
speed limit
acceleration or velocity clipping
object trigger windows
collision radius
near-miss threshold
```

### Info contract

`step()` 返回的 `info` 必须为 Stage 4 指标预留字段：

```text
scenario_id
family
seed
step_count
min_clearance
collision
near_miss
risk_exposure_increment
shield_intervention
```

如果某些字段 Stage 3 只能占位，必须明确标注为 placeholder。

## 审查门槛

网页端 / 人工审查以下问题：

1. 环境是否仍然服务 latent motion intent uncertainty 主线？
2. 是否只实现环境门控，没有越界训练？
3. 每个 reviewed Stage 2 场景是否能 reset / step？
4. 对象动态是否至少反映 stay / cross / yield / emerge / launch 等意图差异？
5. collision 和 near-miss 是否有可解释几何定义？
6. info 字段是否足以支撑 Stage 4 指标实现？
7. 是否保留后续 policy-only 与 policy+shield 评估入口？

## 输出报告格式

Codex 完成任务后必须写明：

```text
Skill invoked: academic-research-suite
Repository sync status:
Base branch and commit:
Working branch and commit:
Stage: 3
Task file: codex_tasks/TASK_03_pybullet_environment_gate.md
Open-source references considered:
Reuse/adaptation decision:
License notes:
Files changed:
New files created and why:
Existing files updated:
Duplicate-file check:
Validation commands:
Review artifacts:
Known limitations:
Forbidden scope checked:
GitHub sync status:
Next recommended stage:
```

## 推荐 Codex CLI 终端提示词

```text
Use the academic-research-suite skill.

You are working in the pirl-nav-research repository.
Current stage: Stage 3 PyBullet / Gymnasium environment gate.
Task file: codex_tasks/TASK_03_pybullet_environment_gate.md.

Before reading repository files or editing anything, sync the latest repository state:
- git status
- git fetch origin
- git checkout main
- git pull --ff-only origin main

First read:
- README.md
- ROADMAP.md
- docs/15_codex_cli_academic_research_suite.md
- docs/01_架构决策.md
- docs/03_experimental_protocol.md
- docs/04_metrics_contract.md
- docs/05_scenario_benchmark.md
- docs/18_stage2_visualization_audit_2026-06-30.md
- experiments/manifests/reviewed_stage2_2026-06-30.yaml
- experiments/review_checklists/scenario_review.md

Before coding, perform an open-source scan for PyBullet, Gymnasium, UAV navigation environments, safe RL environment interfaces, and collision checking examples.

Allowed scope:
- minimal environment API
- reviewed scenario loader
- basic geometry and dynamics
- random/scripted rollout smoke tests
- info fields for future metrics
- tests and audit documentation

Forbidden scope:
- no RL training
- no PPO/SAC/RLlib/Stable-Baselines3 training
- no fixed-test manifest
- no ROS2/Gazebo/PX4
- no policy performance claims
- no large generated artifacts
- no duplicate task or review files

After editing files, run:
- python scripts/validate_scenarios.py
- python -m pytest
- python -m ruff check .

Final answer must include skill invoked, repository sync status, base branch and commit, working branch and commit, stage, task file, open-source references considered, reuse/adaptation decision, license notes, files changed, new files created and why, existing files updated, duplicate-file check, validation results, review artifacts, known limitations, forbidden scope checked, GitHub sync status, and next recommended stage.
```

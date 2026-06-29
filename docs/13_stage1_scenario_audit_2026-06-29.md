# 13 Stage 1 Scenario Audit - 2026-06-29

本文档记录本轮基于 Academic Research Suite 思路的仓库审查与 Stage 1 优化。

## 审查入口

- ARS 路由：`academic-pipeline` + `experiment-agent` + reviewer-style gate。
- 当前阶段：Stage 1 场景规格与候选 manifest。
- 审查目标：让 GitHub 仓库能被网页端 GPT / 人工审查，同时能被 Codex CLI 和 CI 做机械校验。

## 主要发现

1. 原有 README、指标契约和论文边界较清楚，研究主线已经聚焦 latent motion intent uncertainty。
2. 原有 `experiments/scenario_specs/*.yaml` 仍是 family-level 旧规格，字段名与 Stage 1 任务要求不一致。
3. 原仓库没有机器可运行的 scenario schema gate，后续 Codex 容易直接越界进入仿真或训练。
4. candidate manifest 尚未列出六类核心场景，网页端审查缺少稳定输入清单。

## 已完成优化

- 将场景规格改为六个 seed-level candidate YAML：
  - `latent_start`
  - `occlusion_emergence`
  - `multi_intent_crossing`
  - `narrow_passage_yield`
  - `vehicle_forklift_launch`
  - `crowd_robot_flow`
- 新增 `experiments/manifests/candidate_stage1_2026-06-29.yaml`。
- 新增 `pirl_nav.scenarios` 轻量 schema 校验模块。
- 新增 `scripts/validate_scenarios.py`，用于检查 YAML 与 candidate manifest。
- 新增 `tests/test_scenario_specs.py`，把 Stage 1 场景契约纳入 pytest。
- 将 scenario validation 加入 GitHub Actions CI。

## 当前校验规则

校验器检查：

- 六类核心 family 都被覆盖；
- 每个 YAML 包含 `scenario_id`、`family`、`difficulty`、`seed`、`map`、`ego`、`objects`、`risk`、`review`；
- `review.status` 必须能被 manifest 追溯；
- 每个对象至少有两个 intent candidates；
- intent probability sum 必须为 1；
- 至少一个候选意图需要标记为会与无人机名义路径冲突；
- candidate manifest 中的 family / difficulty / seed / review status 必须与 YAML 一致。

## 本地验证结果

```text
python3 scripts/validate_scenarios.py
scenario validation passed

python3 -m pytest
3 passed

python3 -m ruff check .
All checks passed

git diff --check
passed
```

## 剩余门槛

- Stage 2 前仍不能训练 RL 或实现 PyBullet 环境。
- Stage 2 应生成每个 candidate 场景的俯视图、对象时间线和风险预览。
- 只有通过可视化审查的场景才能进入 reviewed manifest 或 fixed test manifest。
- 当前 candidate manifest 不能用于论文最终结果。

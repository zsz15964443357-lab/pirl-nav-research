# TASK 02：场景可视化审查流水线

## Academic Research Suite 要求

执行本任务时，Codex CLI 必须按 `academic-research-suite` 工作流运行。

必须先读：

- `README.md`
- `ROADMAP.md`
- `docs/15_codex_cli_academic_research_suite.md`
- `docs/05_scenario_benchmark.md`
- `experiments/review_checklists/scenario_review.md`
- `experiments/manifests/candidate_stage1_2026-06-29.yaml`

## 目标

为 Stage 1 candidate manifest 中的每个场景生成可人工审查的可视化产物。

本阶段只做场景审查工具，不实现 PyBullet 环境，不生成 RL rollout，不训练模型。

## 允许输出

- 场景俯视布局图；
- 对象意图时间线图；
- 风险区域预览图或风险占位图；
- 每个场景的 JSON / Markdown 审查摘要；
- reviewed manifest 草稿，但不得自动批准；
- 可运行的可视化脚本；
- 对应测试。

建议路径：

```text
pirl_nav/visualization/
scripts/preview_scenarios.py
experiments/review_artifacts/stage2/
experiments/manifests/reviewed_stage2_draft.yaml
tests/test_scenario_visualization.py
```

## 禁止事项

- 不实现 PyBullet / Gymnasium 环境；
- 不实现 RL 算法；
- 不生成训练数据；
- 不生成 policy rollout；
- 不把任何场景标记为 `approved`；
- 不把 reviewed draft 当作 fixed test manifest；
- 不提交大型视频或未筛选图片；
- 不改变 Stage 1 场景语义来适配画图脚本。

## 最低验收标准

- `python scripts/validate_scenarios.py` 通过；
- 可视化脚本能读取 `candidate_stage1_2026-06-29.yaml`；
- 每个 candidate 场景至少生成一个俯视图和一个意图时间线；
- 输出目录可清理、可复现，不依赖个人绝对路径；
- 生成的审查摘要明确标注 `candidate`，不能写成 `approved`；
- `python -m pytest` 通过；
- `python -m ruff check .` 通过。

## 审查门槛

网页端 / 人工审查以下问题：

1. 俯视图是否能看懂 ego、goal、障碍物、对象初始位置？
2. 时间线是否能看懂 stay / start / cross / yield / emerge 等候选意图？
3. 风险预览是否与场景 family 和文字规格一致？
4. 场景是否仍然体现 latent motion intent uncertainty？
5. 是否存在初始重叠、不可达目标或不合理路径？
6. 哪些场景可以进入 reviewed set，哪些需要 revision？

## 输出报告格式

Codex 完成任务后必须写明：

```text
Stage: 2
Task file: codex_tasks/TASK_02_scenario_visualization_gate.md
Files changed:
Validation commands:
Review artifacts:
Known limitations:
Forbidden scope checked:
Next recommended stage:
```

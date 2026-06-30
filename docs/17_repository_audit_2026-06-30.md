# 17 Repository Audit - 2026-06-30

## 审查结论

当前仓库已经从研究想法说明升级为 stage-gated research repository。主线清楚：PIRL-Nav 应围绕 latent motion intent uncertainty、action-conditioned predictive risk、constrained RL 和 shield internalization 展开，而不是把 PyBullet、Gazebo、ROS2、PX4 或通用可视化工具包装成论文创新。

## 已确认的强项

- README 明确了研究问题、贡献边界、平台策略和禁止事项。
- ROADMAP 覆盖 Stage 0 到 Stage 7，并加入每个实现阶段的 open-source scan gate。
- Stage 1 已有六类 candidate scenarios、candidate manifest、schema validation、测试和 CI 入口。
- Codex CLI 规则已明确要求显式调用 `academic-research-suite` skill。
- README、Stage 2 task 和 PR 模板已经要求开源调研、许可证记录和 GitHub 同步。

## 仍需注意的风险

- Stage 2 不应提前实现 PyBullet / Gymnasium / RL / ROS2。
- 可视化产物只能支持场景审查，不能支持论文性能结论。
- 任何外部项目复用都必须记录来源、版本、许可证和改动范围。
- candidate manifest 不能直接变成 fixed test manifest。
- 后续如果引入训练框架，必须保证 baseline 和 PIRL-Nav 使用同一环境、同一 manifest 和同一指标口径。

## 本轮优化

- 在 README 中加入 open-source-first 原则。
- 在 ROADMAP 中为 Stage 2 到 Stage 7 加入开源调研验收门槛。
- 在 `docs/15_codex_cli_academic_research_suite.md` 中加入 skill 调用、open-source scan、GitHub sync 和输出报告要求。
- 在 PR 模板中加入 Codex skill、开源调研、许可证和同步检查项。
- 在 Stage 2 task 中加入可视化开源调研要求。

## 当前推荐下一步

执行 Stage 2：场景可视化审查流水线。

Codex CLI 终端提示必须以以下内容开头：

```text
Use the academic-research-suite skill.
```

然后要求 Codex 读取：

```text
README.md
ROADMAP.md
docs/15_codex_cli_academic_research_suite.md
codex_tasks/TASK_02_scenario_visualization_gate.md
experiments/manifests/candidate_stage1_2026-06-29.yaml
experiments/review_checklists/scenario_review.md
```

Stage 2 只允许生成场景俯视图、对象意图时间线、风险预览、审查摘要、reviewed manifest 草稿、可视化脚本和测试。不得实现仿真环境、RL、训练、ROS2 或 policy rollout。

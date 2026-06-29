# TASK 00：仓库初始化

## 目标

只建立科研实现仓库的最小骨架，不实现任何仿真、强化学习、ROS2、感知或训练功能。

本任务的价值是让后续每个实现阶段都有清晰落点，并让仓库在一开始就具备 lint、test、review、manifest、scenario spec 的基本入口。

## 必须先读

- `README.md`
- `ROADMAP.md`
- `docs/00_项目简述.md`
- `docs/01_架构决策.md`
- `docs/11_仓库结构.md`

## 允许输出

建立或维护以下最小结构：

```text
pirl_nav/
  __init__.py
  sim/__init__.py
  perception/__init__.py
  intent/__init__.py
  risk/__init__.py
  rl/__init__.py
  safety/__init__.py
  evaluation/__init__.py
  visualization/__init__.py
configs/README.md
scripts/README.md
experiments/scenario_specs/README.md
experiments/manifests/README.md
experiments/review_checklists/*.md
tests/test_package_import.py
pyproject.toml
.gitignore
.github/workflows/ci.yml
.github/pull_request_template.md
```

## 禁止事项

- 不实现 PyBullet 环境；
- 不实现 Gymnasium step/reset；
- 不实现 RL 算法；
- 不创建训练入口脚本；
- 不安装或强绑定大型依赖；
- 不实现 ROS2 节点；
- 不提交模型权重、日志、视频或数据集；
- 不改研究主线；
- 不把仓库改成普通避障项目。

## 最低验收标准

Codex CLI 完成后必须满足：

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
```

并且：

- `README.md`、`ROADMAP.md`、`docs/11_仓库结构.md` 中的目录描述一致；
- 所有新增模块只包含 docstring 或导入边界，不包含算法实现；
- PR 描述必须说明哪些内容只是占位契约，哪些内容是可执行检查；
- 如果自动检查失败，必须在 PR 中解释失败原因和下一步修复。

## 审查门槛

网页端审查以下问题：

1. 目录是否简洁、清晰、符合 PIRL-Nav 的研究主线？
2. Stage 0 是否越界实现了仿真、RL、感知或 ROS2？
3. README、ROADMAP、仓库结构文档是否互相一致？
4. 后续 Stage 1 是否能直接基于 `experiments/scenario_specs/` 和 `codex_tasks/TASK_01_scenario_specification.md` 开始？

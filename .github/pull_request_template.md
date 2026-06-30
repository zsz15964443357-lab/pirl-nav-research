# PR 审查模板

## 对应阶段

- 对应 task 文件：
- 阶段门控：
- 本 PR 是否进入下一阶段：是 / 否

## Codex CLI / Skill 检查

- [ ] 若由 Codex CLI 生成，prompt 中显式调用了 `academic-research-suite` skill
- [ ] Codex 先读取了 `README.md`、`ROADMAP.md`、`docs/15_codex_cli_academic_research_suite.md` 和对应 task 文件
- [ ] 本 PR 只完成当前 stage 的最小可审查产物
- [ ] 没有提前实现后续 stage 的功能

## 开源调研与复用检查

- [ ] 实现前做了 open-source scan
- [ ] 记录了参考项目 / 库 / 论文代码
- [ ] 记录了来源 URL、版本或 commit、许可证和改动范围
- [ ] 说明了哪些部分复用 / 改造，哪些部分保持 PIRL-Nav 自定义
- [ ] 没有把外部通用工具包装成本项目论文创新

## 文件卫生与重复文件检查

- [ ] 审查后优先修改原 task / audit / manifest / checklist，而不是新增重复文件
- [ ] 没有新增 `_v2`、`_final`、`_updated`、`review_pass`、`review_fix` 等重复记录文件
- [ ] 如果新增了文件，下面说明为什么不能更新已有文件
- [ ] 删除或合并了本 PR 产生的临时、重复或过时文档

新增文件必要性说明：

```text
New files created and why:
Existing files updated instead of duplicated:
Duplicate-file check:
```

## 变更类型

- [ ] 文档 / 研究决策
- [ ] 场景规格 / manifest
- [ ] 指标 / 评估
- [ ] 仿真环境
- [ ] 强化学习 / 训练
- [ ] 安全屏障 / supervisor
- [ ] 可视化 / 审查产物
- [ ] 工程维护

## 本次变更

请说明本 PR 做了什么，以及为什么现在需要做。

## 研究主线检查

- [ ] 没有把 PyBullet / Gazebo / ROS2 / PX4 写成主创新
- [ ] 没有提前开始大规模训练
- [ ] 没有只围绕 success rate / collision rate 优化
- [ ] 保留 policy-only 与 policy+shield 的报告入口
- [ ] 场景或指标变更能追溯到 docs / manifests / checklists

## 可复现性检查

- [ ] 记录了 config / manifest / seed / commit
- [ ] 没有提交大日志、模型权重、视频或未筛选图片
- [ ] 新增实验能被固定 manifest 复现

## 自动检查

- [ ] `python scripts/validate_scenarios.py`
- [ ] `python -m pytest`
- [ ] `python -m ruff check .`

## 可视化或审查证据

请附上必要的场景图、rollout 图、指标表或失败案例说明。大型媒体文件不要直接提交到 Git。

## GitHub 同步状态

- [ ] 所有代码、文档、配置和审查产物已同步到 GitHub
- [ ] 没有只存在于本地的关键实现或结果

## 已知限制

请说明当前阶段仍未解决的问题，尤其是暂时不能支持论文结论的部分。

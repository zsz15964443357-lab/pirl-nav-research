# PR 审查模板

## 对应阶段

- 对应 task 文件：
- 阶段门控：
- 本 PR 是否进入下一阶段：是 / 否

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

- [ ] `python -m pytest`
- [ ] `python -m ruff check .`

## 可视化或审查证据

请附上必要的场景图、rollout 图、指标表或失败案例说明。大型媒体文件不要直接提交到 Git。

## 已知限制

请说明当前阶段仍未解决的问题，尤其是暂时不能支持论文结论的部分。

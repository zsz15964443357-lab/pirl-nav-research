# TASK 01：场景规格与候选 manifest

## 目标

建立 PIRL-Nav 六类核心场景的 YAML 规格模板、候选 manifest 和最小 schema 校验，不实现仿真环境，不生成训练数据，不训练模型。

本任务应把 latent motion intent uncertainty 具体化为可复现、可视化、可审查的场景输入。

## 必须先读

- `README.md`
- `ROADMAP.md`
- `docs/03_experimental_protocol.md`
- `docs/04_metrics_contract.md`
- `docs/05_scenario_benchmark.md`
- `experiments/scenario_specs/README.md`
- `experiments/manifests/README.md`
- `experiments/review_checklists/scenario_review.md`

## 允许输出

- `experiments/scenario_specs/*.yaml` 示例；
- `experiments/manifests/candidate_*.yaml` 候选 manifest；
- schema 校验脚本；
- 场景字段说明文档；
- 简单 YAML 完整性测试。

## 禁止事项

- 不实现 PyBullet / Gymnasium 环境；
- 不生成 rollout；
- 不训练 RL；
- 不引入大型依赖；
- 不把固定测试集冻结；
- 不把没有可视化审查的场景标记为 approved。

## 最低验收标准

- 六类场景 family 都有至少一个 YAML 示例；
- 每个 YAML 包含 family、difficulty、seed、ego、objects、intent candidates、risk、review；
- candidate manifest 能列出所有示例场景；
- 所有场景 review status 必须是 `candidate`；
- `python scripts/validate_scenarios.py` 和 `python -m pytest` 必须通过；
- 文档中说明哪些字段将在 Stage 2 可视化审查中使用。

## 审查门槛

网页端审查以下问题：

1. 场景是否真正体现 latent motion intent uncertainty？
2. 场景 family 是否覆盖突然启动、遮挡出现、多意图、让行、高惯性启动和群体流？
3. 难度分级是否可解释？
4. 是否避免了普通静态避障或普通动态避障占据主线？
5. 是否为 Stage 2 场景可视化留下足够字段？

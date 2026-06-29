# Manifests

Manifest 用来固定候选集、训练集、验证集和最终测试集。所有正式实验必须引用 manifest，而不是临时扫描某个输出目录。

## Manifest 类型

```text
candidate_<stage>_<date>.yaml
reviewed_<stage>_<date>.yaml
train_<scenario_mix>_<version>.yaml
validation_<scenario_mix>_<version>.yaml
fixed_test_<scenario_mix>_<version>.yaml
```

## 推荐 schema

```yaml
manifest_id: candidate_stage1_2026_06_29
created_at: 2026-06-29
commit: null
purpose: candidate
status: draft
scenario_specs:
  - path: experiments/scenario_specs/latent_start_easy_0001.yaml
    family: latent_start
    difficulty: easy
    seed: 1001
    review_status: candidate
metrics_contract: docs/04_metrics_contract.md
notes: null
```

## 使用规则

- 固定测试集一旦冻结，不允许因为某个方法表现差而替换；
- train / validation / fixed_test 必须分开；
- 每个场景必须能追溯到 YAML、seed 和可视化审查记录；
- 正式论文表格必须注明使用的 manifest 版本。
- `candidate_*.yaml` 可以用 `python scripts/validate_scenarios.py` 检查，但不能替代人工可视化审查。

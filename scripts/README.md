# Scripts

本目录用于后续保存人工审查、场景预览、指标聚合和实验报告生成脚本。

Stage 0 不创建训练脚本，也不创建一键跑大规模实验的入口。

Stage 1 当前提供：

```text
scripts/validate_scenarios.py   # 检查六类核心场景 YAML 与 candidate manifest
```

Stage 2 当前提供：

```text
scripts/preview_scenarios.py    # 生成 HTML/SVG/JSON 场景可视化审查包
```

## 后续允许脚本类型

```text
scripts/
  preview_scenarios.py       # Stage 2：生成场景可视化审查包
  summarize_metrics.py       # Stage 4：聚合固定测试集指标
  validate_scenarios.py      # Stage 1/2：检查 scenario specs 与 candidate manifest
```

## 禁止事项

- 不在 Stage 0 创建 `train.py`；
- 不把 notebook 临时代码作为正式实验入口；
- 不在脚本中硬编码个人绝对路径；
- 不绕过 `experiments/manifests/` 直接扫描随机输出目录。

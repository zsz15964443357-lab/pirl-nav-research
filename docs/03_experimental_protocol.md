# 03 Experimental Protocol

本文档定义 PIRL-Nav 后续实验必须遵守的协议。核心目标是防止“先训练、后挑图、再解释”的不可复现流程。

## 实验对象

每次实验必须明确以下字段：

```yaml
experiment_id: pirl_nav_stageX_methodY_YYYYMMDD
commit: <git-commit-sha>
method: <baseline-or-pirl-nav-variant>
scenario_manifest: experiments/manifests/<manifest-name>.yaml
config: configs/<config-name>.yaml
seeds: [0, 1, 2, 3, 4]
run_mode: policy_only | policy_plus_shield
```

## 数据划分原则

场景应按 family / difficulty / seed 划分：

- **candidate set**：自动生成的候选场景；
- **reviewed set**：人工可视化审查通过的场景；
- **train set**：允许训练使用；
- **validation set**：用于调参和 early stopping；
- **fixed test set**：最终论文报告，只能在方法冻结后使用。

固定测试集一旦冻结，不允许因为某个方法表现不好而删除或替换场景。

## 运行模式

所有关键方法至少报告两种模式：

1. **policy-only**：直接执行策略输出，观察策略自身是否学会提前避险；
2. **policy+shield**：策略输出经过 safety supervisor 修正，观察系统级安全性和 shield dependence。

如果只报告 policy+shield，不能支撑“策略已经内化安全行为”的论文结论。

## 随机种子协议

每个实验必须记录：

- scenario seed；
- environment seed；
- policy initialization seed；
- training seed；
- evaluation seed。

如果平台或物理仿真无法完全 deterministic，必须在报告中标注非确定性来源。

## 输出产物

每次正式实验至少输出：

```text
metrics.csv                         每个 episode 的原始指标
summary.json                        聚合指标和置信区间
rollout_samples/                    少量代表性轨迹，不提交大视频
scenario_manifest_used.yaml         实际使用的 manifest 快照
config_used.yaml                    实际配置快照
README.md                           该次实验的文字说明
```

大型日志、模型权重和视频不进 Git。可在外部存储中保存，并在实验 README 中记录路径或编号。

## 统计报告要求

对每个方法至少报告：

- mean；
- standard deviation；
- median；
- bootstrap confidence interval 或至少多 seed 结果；
- per-family breakdown；
- per-difficulty breakdown。

仅报告 overall average 不够，因为 PIRL-Nav 的优势可能主要体现在 latent-start、occlusion-crossing 等高风险 family。

## 结果解释边界

实验结果只能支撑实际测试过的结论。例如：

- 只在 2.5D Gymnasium 中测试，不能声称真实无人机可用；
- 只在 PyBullet 中测试，不能声称 ROS2 链路实时稳定；
- 只在 policy+shield 模式安全，不能声称策略本身安全；
- 只降低 near miss 但 jerk 大幅变差，不能声称整体导航质量提升。

# Configs

本目录用于保存后续实验配置模板。Stage 0 不放正式训练配置。

## 命名约定

```text
configs/
  env_<platform>_<scenario_family>.yaml
  train_<method>_<stage>.yaml
  eval_<manifest>_<run_mode>.yaml
```

示例：

```text
env_pybullet_latent_start.yaml
train_ppo_lagrangian_stage6.yaml
eval_fixed_test_policy_only.yaml
```

## 配置必须记录

正式实验配置至少应包含：

- scenario manifest 路径；
- environment seed；
- training seed；
- method name；
- run mode: `policy_only` 或 `policy_plus_shield`；
- metric thresholds；
- safety supervisor 开关；
- 输出目录；
- commit SHA 或实验记录中的 commit 字段。

## 禁止事项

- 不在配置里写绝对路径；
- 不为不同方法偷偷使用不同测试集；
- 不把大规模训练产物放进本目录；
- 不在 Stage 0 添加真实训练配置。

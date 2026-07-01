# TASK 07：正式训练、可视化与对比实验

## Academic Research Suite 要求

执行本任务时，Codex CLI 必须显式调用 `academic-research-suite` skill。

终端 prompt 第一行必须写：

```text
Use the academic-research-suite skill.
```

## 仓库同步要求

读取仓库文件或修改任何文件前，必须先拉取最新项目状态：

```bash
git status
git fetch origin
git checkout main
git pull --ff-only origin main
```

如果在任务分支继续工作，必须先同步最新 `main`：

```bash
git checkout <task-branch>
git merge --ff-only origin/main
```

如果不能 fast-forward，必须停止并报告冲突，不得覆盖、force-push 或重写历史。

Codex 最终报告必须包含：

```text
Repository sync status:
Base branch and commit:
Working branch and commit:
```

## 必须先读

开始任何实现前，必须先读：

- `README.md`
- `ROADMAP.md`
- `docs/15_codex_cli_academic_research_suite.md`
- `docs/03_experimental_protocol.md`
- `docs/04_metrics_contract.md`
- `docs/05_scenario_benchmark.md`
- `docs/20_stage3_environment_audit_2026-07-01.md`
- `docs/21_stage4_evaluation_audit_2026-07-01.md`
- `docs/22_stage5_baseline_training_audit_2026-07-01.md`
- `docs/23_stage6_pirl_nav_method_audit_2026-07-01.md`
- `experiments/manifests/train_stage5_baseline.yaml`
- `experiments/manifests/validation_stage5_baseline.yaml`
- `configs/training/stage5_baselines.yaml`
- `configs/method/stage6_pirl_nav.yaml`
- `pirl_nav/training/`
- `pirl_nav/method/`
- `pirl_nav/evaluation/`
- `codex_tasks/TASK_07_formal_training_visualized_comparative_experiments.md`

如果 Stage 5 或 Stage 6 产物尚未合入 `main`，必须停止并报告，不得继续 Stage 7。

## 阶段定位

Stage 7 是第一次进入正式训练闭环，但仍然不是最终论文 fixed-test 阶段。

本阶段目标是建立：

```text
formal baseline training
-> formal PIRL-Nav skeleton training
-> multi-seed validation
-> lightweight visual diagnostics
-> comparative summary tables
-> training / rollout visualization artifacts
-> Stage 7 audit and next-stage readiness
```

本阶段可以开始训练，但必须限定在 baseline-development train / validation manifests 上。

不得创建 fixed-test manifest，不得声称最终论文结论。

## 为什么需要可视化

从 Stage 7 起，训练过程不能只输出 JSON 数字。必须提供可人工直观看懂的轻量可视化，使研究者能判断：

- agent 是否真的朝目标移动；
- 是否提前绕开 latent-risk 对象；
- shield 是否频繁介入；
- risk exposure 是否随训练下降；
- detour / jerk 是否因为避险过度而变差；
- policy-only 与 policy-plus-shield 的差别是否合理；
- baseline 与 PIRL-Nav skeleton 的差异是否符合预期。

这些可视化是 debug / review artifact，不是论文图。

## 开源优先要求

本阶段不要闭门造车。Codex 在写代码前必须做 open-source scan，调研并比较：

- Stable-Baselines3 / CleanRL 的 PPO 训练循环、日志和 checkpoint 约定；
- SafePO / PPO-Lagrangian 的 constrained training 报告方式；
- RL Baselines3 Zoo 的实验目录、seed、evaluation 和 curve 管理；
- TensorBoard / CSV / JSONL 轻量日志格式；
- matplotlib 轨迹图、learning curve 和 rollout diagnostic 的常见做法；
- gymnasium / safety-gymnasium 中 episode video 或 rendered-frame 的 lightweight 替代方案。

任务开始前必须输出：

```text
Open-source scan:
- candidate projects or libraries
- reusable parts
- parts that must stay custom for PIRL-Nav
- license / attribution notes
- adaptation plan
```

如果复用或改造外部项目，必须记录来源、版本、许可证和改动范围。许可证不清楚的代码不得复制进仓库。

## 训练范围

Stage 7 至少覆盖以下 training groups：

```text
vanilla_ppo
ppo_ttc_proxy
ppo_semantic_risk_proxy
ppo_lagrangian_no_intent
full_pirl_nav_skeleton
no_intent_prediction
no_action_conditioning
no_risk_constraint
no_shield_internalization
```

允许先使用 dependency-light trainer 或 optional external PPO backend，但必须明确：

- 哪些是正式训练；
- 哪些仍是 smoke / skeleton training；
- 是否用了 Stable-Baselines3 / CleanRL / 自研轻量 trainer；
- 结果是否可用于后续论文前实验；
- 结果是否还不能作为 final paper claim。

## 推荐新增或更新路径

可以根据现有结构调整，但建议包括：

```text
pirl_nav/training/formal_trainer.py
pirl_nav/training/experiment_tracker.py
pirl_nav/training/checkpoint_policy.py
pirl_nav/visualization/
  __init__.py
  training_curves.py
  rollout_plots.py
  comparison_plots.py
  diagnostics.py
configs/training/stage7_formal_training.yaml
configs/training/stage7_groups/
  baseline_vanilla_ppo.yaml
  baseline_ttc_proxy.yaml
  baseline_semantic_risk_proxy.yaml
  baseline_lagrangian_no_intent.yaml
  method_full_pirl_nav_skeleton.yaml
  ablation_no_intent_prediction.yaml
  ablation_no_action_conditioning.yaml
  ablation_no_risk_constraint.yaml
  ablation_no_shield_internalization.yaml
scripts/train_stage7_formal.py
scripts/evaluate_stage7_formal.py
scripts/visualize_stage7_training.py
scripts/visualize_stage7_rollouts.py
experiments/review_artifacts/stage7/
  training_metrics.jsonl
  validation_episode_records.jsonl
  validation_summary.json
  comparison_summary.json
  visual_index.md
  figures/
    learning_curves.png
    risk_exposure_curves.png
    shield_intervention_curves.png
    aggregate_metric_bars.png
    rollout_<scenario>_<method>_<mode>.png
tests/test_stage7_training_config.py
tests/test_stage7_visualization_artifacts.py
docs/24_stage7_formal_training_audit_2026-07-01.md
```

## 必须实现或固化的能力

### 1. Formal training config

Stage 7 config 至少包含：

```text
experiment_id
stage
training_groups
scenario_manifest
validation_manifest
seed_plan
num_seeds
total_timesteps
checkpoint_policy
artifact_policy
evaluation_cadence
visualization_cadence
trainer_backend
notes
```

必须支持多 seed，哪怕默认先用小规模：

```text
seeds: [0, 1, 2]
```

如果算力不足，可设置 `quick_debug: true` 或 `reduced_timesteps_for_review: true`，但必须明示。

### 2. Training metrics JSONL

训练过程必须输出 lightweight JSONL：

```text
experiments/review_artifacts/stage7/training_metrics.jsonl
```

每行至少包含：

```text
experiment_id
stage
method_or_baseline
seed
timestep
episode
reward
cost
success
collision
near_miss_count
risk_exposure
min_clearance
detour_ratio
jerk_proxy
shield_intervention_rate
policy_mode
is_smoke_or_debug
paper_claim_allowed
```

### 3. Evaluation records and comparison summary

必须复用 Stage 4 / Stage 5 / Stage 6 的 `EpisodeRecord` 和 `aggregate_records`，输出：

```text
experiments/review_artifacts/stage7/validation_episode_records.jsonl
experiments/review_artifacts/stage7/validation_summary.json
experiments/review_artifacts/stage7/comparison_summary.json
```

`comparison_summary.json` 至少包含：

```text
per_method
per_seed
per_scenario_family
policy_only_vs_policy_plus_shield
baseline_vs_method_skeleton
known_limitations
paper_claim_allowed: false
```

### 4. 可视化 artifacts

Stage 7 必须生成轻量 PNG 或 SVG，不生成大视频。

至少生成：

```text
learning_curves.png
risk_exposure_curves.png
shield_intervention_curves.png
aggregate_metric_bars.png
rollout trajectory snapshots for representative scenarios
```

每个 rollout 图必须尽量包含：

```text
ego path
start and goal
objects / latent-risk objects
near-miss radius or risk zone
shield intervention points
policy-only vs policy-plus-shield if applicable
method / baseline label
scenario id
seed
```

必须生成索引文件：

```text
experiments/review_artifacts/stage7/visual_index.md
```

`visual_index.md` 必须列出每张图：

```text
figure path
what it shows
how to interpret it
known limitation
```

### 5. 不提交大产物

禁止提交：

```text
model weights
checkpoints
TensorBoard event directories
wandb directories
large logs
videos / GIFs
large rollout dumps
```

允许提交：

```text
small JSON / JSONL summaries
small PNG / SVG figures for review
audit documents
config files
tests
```

如果有 checkpoint，必须写入 ignored or external artifact path，例如：

```text
artifacts/stage7/checkpoints/
```

并确保不进入 git。

### 6. 不改旧 stage artifacts

从 Stage 7 起，不得重新提交旧阶段 review artifacts：

```text
experiments/review_artifacts/stage4/*
experiments/review_artifacts/stage5/*
experiments/review_artifacts/stage6/*
```

跨阶段验证结果应写入 Stage 7 自己的 summary 或 audit。

### 7. 不创建 fixed-test

Stage 7 仍然只使用 baseline-development train / validation manifests。

禁止新增：

```text
fixed_test_manifest
final_test_manifest
paper_final_results
```

## 推荐实现策略

优先顺序：

1. 建立 Stage 7 config 和 training group registry；
2. 建立 lightweight formal trainer / backend adapter；
3. 统一 baseline 与 PIRL-Nav skeleton 的训练调用；
4. 输出 training_metrics.jsonl；
5. 复用 evaluation pipeline 输出 Stage 7 records / summary；
6. 生成 learning curves 和 rollout trajectory snapshots；
7. 写 visual_index.md；
8. 写 tests 和 Stage 7 audit。

如果一次性正式训练太重，允许先完成：

```text
reduced formal training review run
```

但必须和 smoke training 区分开。

## 禁止事项

- 不创建 fixed-test manifest；
- 不提交权重、checkpoint、大日志、视频或 GIF；
- 不声称 PIRL-Nav 已经最终优于 baseline；
- 不把 Stage 5 smoke baseline 当正式 baseline 结论；
- 不把 Stage 6 method skeleton smoke 结果当正式训练结论；
- 不重新提交 Stage 4 / Stage 5 / Stage 6 旧 review artifacts；
- 不新增重复 task、audit、pass/fail、final、updated 文档；
- 不修改 baseline semantics 来抬高 PIRL-Nav；
- 不跳过可视化。

## 最低验收标准

- Codex 输出 open-source scan；
- Codex 报告 repository sync status、base branch commit 和 working branch commit；
- 只保留一个 Task 7 文件：`codex_tasks/TASK_07_formal_training_visualized_comparative_experiments.md`；
- Stage 7 training config 可加载；
- 至少一个 reduced formal training review run 可运行；
- baseline 与 PIRL-Nav skeleton 至少各有一个 group 进入训练/验证闭环；
- `training_metrics.jsonl` 生成；
- `validation_episode_records.jsonl`、`validation_summary.json`、`comparison_summary.json` 生成；
- learning curves、risk exposure curves、shield intervention curves、aggregate metric bars 和至少若干代表性 rollout trajectory snapshots 生成；
- `visual_index.md` 生成并解释图像；
- 没有提交大产物、权重、checkpoint、视频、GIF；
- 没有修改 Stage 4 / Stage 5 / Stage 6 旧 review artifacts；
- 没有创建 fixed-test；
- `python scripts/validate_scenarios.py` 通过；
- `python scripts/train_stage7_formal.py --config configs/training/stage7_formal_training.yaml --reduced-review-run` 通过；
- `python scripts/evaluate_stage7_formal.py --config configs/training/stage7_formal_training.yaml` 通过；
- `python scripts/visualize_stage7_training.py --config configs/training/stage7_formal_training.yaml` 通过；
- `python scripts/visualize_stage7_rollouts.py --config configs/training/stage7_formal_training.yaml` 通过；
- `python -m pytest` 通过；
- `python -m ruff check .` 通过；
- Stage 7 audit 明确记录 forbidden scope checked。

## 审查门槛

网页端 / 人工审查以下问题：

1. 是否真正开始 formal / reduced formal training，而不仅是 Stage 5/6 smoke 重命名？
2. 是否同时覆盖 baseline 和 PIRL-Nav skeleton / ablations？
3. 是否复用统一 metrics、episode record 和 aggregation？
4. 是否有足够可视化让人直观看到轨迹、风险、shield 和曲线变化？
5. 可视化是否轻量、可解释、不会污染仓库？
6. 是否没有 fixed-test？
7. 是否没有提交权重、checkpoint、大日志、视频、GIF？
8. 是否没有改旧 Stage 4/5/6 artifacts？
9. 是否没有声称最终论文结论？
10. 是否给 Stage 8 的正式评估 / fixed-test freeze 留出清楚边界？

## 输出报告格式

Codex 完成任务后必须写明：

```text
Skill invoked: academic-research-suite
Repository sync status:
Base branch and commit:
Working branch and commit:
Stage: 7
Task file: codex_tasks/TASK_07_formal_training_visualized_comparative_experiments.md
Open-source references considered:
Reuse/adaptation decision:
License notes:
Files changed:
New files created and why:
Existing files updated:
Duplicate-file check:
Training groups:
Training run type:
Validation commands:
Visualization artifacts:
Review artifacts:
Known limitations:
Forbidden scope checked:
GitHub sync status:
Next recommended stage:
```

## 推荐 Codex CLI 短提示词

```text
Use the academic-research-suite skill.

你正在处理 pirl-nav-research 仓库。

当前阶段：Stage 7。
唯一任务文件：codex_tasks/TASK_07_formal_training_visualized_comparative_experiments.md。

开始前必须同步最新仓库，并确认只存在一个 Task 7 文件。

请读取 README、ROADMAP、docs/15、Stage 3/4/5/6 audit、Stage 5 training pipeline、Stage 6 method pipeline 和 Task 7 文件，然后按 Task 7 推进。

本阶段目标：开始 formal / reduced formal training，并生成可视化 review artifacts，让训练过程不再是黑盒。

硬性禁止：不创建 fixed-test；不提交权重/checkpoint/大日志/视频/GIF；不重新提交 Stage 4/5/6 旧 artifacts；不声称最终论文结论；不新增重复 task/audit/final/updated 文档；不跳过可视化。

完成后运行 Task 7 要求的 validation commands，并把代码、配置、测试、轻量 JSON/JSONL、PNG/SVG 可视化、visual_index.md 和 audit 同步到 GitHub。

最终报告必须包含 repository sync status、base commit、working branch commit、training groups、visualization artifacts、files changed、duplicate-file check、validation results、forbidden scope checked 和 next recommended stage。
```

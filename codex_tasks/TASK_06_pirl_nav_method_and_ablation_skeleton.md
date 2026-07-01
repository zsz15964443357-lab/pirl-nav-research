# TASK 06：PIRL-Nav 方法骨架与消融协议

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
- `experiments/manifests/train_stage5_baseline.yaml`
- `experiments/manifests/validation_stage5_baseline.yaml`
- `configs/training/stage5_baselines.yaml`
- `pirl_nav/evaluation/records.py`
- `pirl_nav/evaluation/aggregation.py`
- `pirl_nav/training/baseline_registry.py`
- `pirl_nav/training/config.py`
- `pirl_nav/training/trainer.py`
- `codex_tasks/TASK_06_pirl_nav_method_and_ablation_skeleton.md`

如果 Stage 5 产物尚未合入 `main`，必须停止并报告，不得基于缺失 baseline pipeline 继续实现 Stage 6。

## 阶段粒度说明

本阶段跨度应覆盖 PIRL-Nav 方法的一组紧密相关核心能力，不要拆成 predictor、risk、shield、ablation 四个独立小阶段。

Stage 6 的目标是建立：

```text
latent intent representation
-> action-conditioned predictive risk interface
-> constrained RL integration skeleton
-> safety shield internalization interface
-> method and ablation config registry
-> Stage 5 baseline-compatible evaluation protocol
-> Stage 6 audit and next-stage readiness
```

本阶段允许实现 PIRL-Nav 方法骨架、可运行 smoke integration 和消融配置；不要求完成论文级训练结果。

## 开源优先要求

本阶段不要闭门造车。Codex 在写代码前必须做 open-source scan，调研并比较：

- intent prediction / trajectory prediction baseline interfaces；
- GRU / RNN sequence encoder examples for motion intent modeling；
- action-conditioned risk or model-predictive safety cost patterns；
- constrained RL / PPO-Lagrangian implementation conventions；
- safety layer / shield integration and shield distillation patterns；
- ablation management conventions in RL research；
- deterministic smoke tests for method integration without large training runs。

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

## 当前项目边界

Stage 0-5 已经建立：

- 仓库结构、文档治理和 Codex CLI 文件卫生规则；
- reviewed scenarios；
- Stage 3 lightweight 2.5D Gymnasium-style environment gate；
- Stage 4 evaluation metrics、episode record 和 aggregation pipeline；
- Stage 5 baseline config、baseline manifests、smoke training 和 policy-only validation pipeline。

Stage 6 必须复用 Stage 4 / Stage 5 的 record、aggregation、manifest 和 artifact policy，不得另起一套不可比的实验输出。

## 目标

建立 PIRL-Nav 方法骨架，使后续正式训练可以比较：

```text
baseline families
vs
PIRL-Nav full skeleton
vs
PIRL-Nav ablations
```

本阶段的研究主线必须保持：

```text
Predictive Intent-Risk Constrained Reinforcement Learning for UAV Navigation under Latent Motion Intent Uncertainty
```

也就是说，Stage 6 关注的是：

- 当前静止 / 低速 / 部分可见对象的未来启动、横穿、让行、停留、遮挡出现等 latent motion intent uncertainty；
- action-conditioned predictive intent-risk；
- constrained RL cost interface；
- safety shield internalization 的接口和消融协议。

不要把项目退化成普通动态避障、普通 semantic risk shaping 或纯 geometric TTC baseline。

## 方法组件范围

Stage 6 至少应建立以下模块或等价结构：

```text
pirl_nav/method/
  __init__.py
  intent_state.py
  intent_predictor.py
  risk_model.py
  constrained_objective.py
  shield_interface.py
  ablation_registry.py
  method_runner.py
configs/method/stage6_pirl_nav.yaml
configs/method/ablations/
  full_pirl_nav_skeleton.yaml
  no_intent_prediction.yaml
  no_action_conditioning.yaml
  no_risk_constraint.yaml
  no_shield_internalization.yaml
scripts/run_stage6_method_smoke.py
scripts/evaluate_stage6_method.py
experiments/review_artifacts/stage6/method_smoke_summary.json
experiments/review_artifacts/stage6/method_validation_episode_records.jsonl
experiments/review_artifacts/stage6/method_validation_summary.json
tests/test_stage6_method_components.py
tests/test_stage6_method_smoke.py
docs/23_stage6_pirl_nav_method_audit_2026-07-01.md
```

可以根据仓库实际结构简化，但必须保留一套清楚的 method / ablation registry，不得把 PIRL-Nav 逻辑散落进 Stage 5 baseline 文件里。

## 必须实现或固化的能力

### 1. Latent intent representation

必须定义可序列化 intent state，例如：

```text
object_id
object_class
scenario_family
history_window
candidate_intents
intent_probabilities
prediction_horizon
is_placeholder
notes
```

本阶段可以使用 deterministic / heuristic placeholder predictor，但必须明确：

```text
not a trained GRU intent predictor
not final paper intent model
```

### 2. Intent predictor interface

必须提供统一接口，为未来 GRU / sequence model 留入口：

```text
reset(scenario)
update(observation, info)
predict(action_candidates, horizon)
```

当前实现可以是 heuristic predictor，但接口必须支持未来 action-conditioned risk 评估。

### 3. Action-conditioned predictive intent-risk

必须实现 risk model interface：

```text
score(action, intent_state, horizon)
score_candidates(action_candidates, intent_state, horizon)
```

Stage 6 可以用 geometric + intent-probability proxy，但必须明确：

```text
risk is action-conditioned proxy
not final learned predictive risk
```

风险输出至少应包含：

```text
risk_score
expected_clearance
predicted_near_miss_probability
intent_entropy
risk_is_proxy
```

### 4. Constrained objective skeleton

必须建立 constrained RL cost 接口，和 Stage 5 `ppo_lagrangian_no_intent` 区分开：

```text
reward
cost
constraint_violation
lagrange_multiplier_placeholder
objective_notes
```

不得声称已经完成正式 PPO-Lagrangian 学习。

### 5. Shield internalization interface

必须建立 safety shield 接口和 internalization placeholder：

```text
shield_action(action, risk_score)
shield_intervention
shield_reason
student_policy_target placeholder
internalization_loss placeholder
```

本阶段可以不训练 shield student，但必须能在 records / summary 中标明 policy-only 与 future policy+shield 的接口差异。

### 6. Ablation registry

至少定义：

```text
full_pirl_nav_skeleton
no_intent_prediction
no_action_conditioning
no_risk_constraint
no_shield_internalization
```

每个 ablation config 必须说明：

```text
enabled_components
disabled_components
risk_mode
constraint_mode
shield_mode
paper_claim_allowed: false
```

### 7. Stage 4 / Stage 5 evaluation compatibility

Stage 6 必须复用：

- `EpisodeRecord`；
- `aggregate_records`；
- baseline-development validation manifest；
- small JSON / JSONL review artifact policy；
- `not_fixed_test` / `not_for_final_reporting` 语义。

如果需要添加 method-specific fields，必须保持向后兼容，优先放在 `notes` 或新增 optional fields。

## 推荐实现策略

优先顺序：

1. 建立 method config 和 ablation registry；
2. 建立 intent state / predictor interface；
3. 建立 action-conditioned risk interface；
4. 建立 constrained objective 和 shield interface；
5. 用 Stage 5 validation manifest 跑 method smoke episodes；
6. 输出 Stage 6 JSON / JSONL review artifacts；
7. 写 tests 和 Stage 6 audit。

本阶段不要追求训练性能，先保证方法概念和实验接口正确。

## 禁止事项

- 不提交模型权重、checkpoint、大日志或视频；
- 不创建 fixed-test manifest；
- 不声称 PIRL-Nav 已经优于 baseline；
- 不声称 heuristic predictor 是最终 GRU intent predictor；
- 不声称 proxy risk 是最终 action-conditioned predictive risk；
- 不把 Stage 5 smoke baseline 当正式论文 baseline；
- 不绕过 Stage 4 / Stage 5 evaluation pipeline；
- 不修改 baseline family 语义来抬高 PIRL-Nav；
- 不新增重复 task、audit、pass/fail、final、updated 文档。

## 最低验收标准

- Codex 输出 open-source scan；
- Codex 报告 repository sync status、base branch commit 和 working branch commit；
- 只保留一个 Task 6 文件：`codex_tasks/TASK_06_pirl_nav_method_and_ablation_skeleton.md`；
- Stage 6 method / ablation registry 可加载；
- method smoke runner 可运行；
- Stage 6 evaluation 复用 Stage 4 / Stage 5 record 和 aggregation 语义；
- `python scripts/validate_scenarios.py` 通过；
- `python scripts/evaluate_stage4.py` 通过；
- `python scripts/train_stage5_baselines.py --config configs/training/stage5_baselines.yaml --smoke` 通过；
- `python scripts/evaluate_stage5_baselines.py --config configs/training/stage5_baselines.yaml` 通过；
- `python scripts/run_stage6_method_smoke.py --config configs/method/stage6_pirl_nav.yaml` 通过；
- `python scripts/evaluate_stage6_method.py --config configs/method/stage6_pirl_nav.yaml` 通过；
- `python -m pytest` 通过；
- `python -m ruff check .` 通过；
- Stage 6 audit 明确记录 forbidden scope checked；
- 没有提交 checkpoint、模型权重、大日志或大视频。

## 审查门槛

网页端 / 人工审查以下问题：

1. Stage 6 是否仍围绕 latent motion intent uncertainty，而不是退化成普通动态避障？
2. risk 是否真的 action-conditioned，至少在接口和 proxy 上体现 action candidate 差异？
3. intent predictor 是否明确是 placeholder，而非最终 GRU model？
4. constrained objective 是否和 Stage 5 no-intent baseline 有清楚区别？
5. shield internalization 是否只是接口 / placeholder，没有越界声称训练完成？
6. ablation registry 是否完整？
7. Stage 6 是否复用了 Stage 4 / Stage 5 evaluation pipeline？
8. 是否没有 fixed-test？
9. 是否没有提交权重、checkpoint、大日志、视频？
10. 是否没有新增重复 task 或重复 audit？

## 输出报告格式

Codex 完成任务后必须写明：

```text
Skill invoked: academic-research-suite
Repository sync status:
Base branch and commit:
Working branch and commit:
Stage: 6
Task file: codex_tasks/TASK_06_pirl_nav_method_and_ablation_skeleton.md
Open-source references considered:
Reuse/adaptation decision:
License notes:
Files changed:
New files created and why:
Existing files updated:
Duplicate-file check:
Validation commands:
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

当前阶段：Stage 6。
唯一任务文件：codex_tasks/TASK_06_pirl_nav_method_and_ablation_skeleton.md。

开始前必须同步最新仓库，并确认只存在一个 Task 6 文件。

请读取 README、ROADMAP、docs/15、Stage 3/4/5 audit、Stage 5 baseline pipeline 和 Task 6 文件，然后按 Task 6 推进 Stage 6。

本阶段目标：建立 PIRL-Nav method and ablation skeleton capability，跨度不要过小。

硬性禁止：不提交权重/checkpoint/大日志/视频；不创建 fixed-test；不声称 PIRL-Nav 已经优于 baseline；不把 heuristic predictor 或 proxy risk 当最终模型；不绕过 Stage 4/5 evaluation pipeline；不新增重复 task/audit/final/updated 文档。

完成后运行 Task 6 要求的 validation commands，并把代码、配置、测试、轻量 review artifacts 和 audit 同步到 GitHub。

最终报告必须包含 repository sync status、base commit、working branch commit、files changed、duplicate-file check、validation results、forbidden scope checked 和 next recommended stage。
```

# ERP-Bench deep dive (agentic-labs / "Anchor" paper)

Research date: 2026-08-11. Source: local checkout at `research/external/repos/erp-bench` (CC0-1.0 — `erp-bench/LICENSE:1-3`, so this is a fact-source *and* a legal code-source, unlike the GPL/AGPL repos). All paths below are relative to `research/external/repos/`.

**Why this repo matters most in the wave:** it ships 300 tasks in *true Harbor per-task-directory format* — the same packaging target finance-world exports (`research/harbor-format.md`) — with a fully generated, CP-SAT-certified oracle and a 3-dimension weighted verifier. It is the closest existing thing to what finance-world is building, in a different domain (Odoo 19 procurement/manufacturing).

Items marked **UNVERIFIED** could not be confirmed inside the checkout.

---

## 1. The Anchor methodology: one solved spec → four artifacts

### 1.1 The claim

> "Anchor's central claim is that benchmark tasks should not be hand-assembled from separate instructions, environments, oracle solutions, and verifiers. In this repo, each task is compiled from one CP-SAT-backed procurement specification into: `instruction.md` … `environment/` … `solution/` … `tests/`. The result is a benchmark where rewards are tied to end-state business correctness, not to a particular action trace."
> — `erp-bench/README.md:18-27`

"Artifact drift" = the four artifacts of a hand-built task drift out of agreement (instruction says one thing, seeded DB another, oracle a third, verifier a fourth). Anchor's answer is a **single compiler**: sample a `ScenarioBlueprint` → solve it to certified optimality → emit *all four artifacts from the same solved object*.

The paper itself is **not in the checkout** (no PDF/`paper/` dir); the argument is reconstructed from README + generator code. **UNVERIFIED**: any claim beyond the README wording about what the paper says.

### 1.2 The compile pipeline (verified, code-level)

| Stage | Where | What it does |
|---|---|---|
| Dataset manifest | `erp-bench/erp_bench/procurement/examples/diverse_300_dataset.toml` | 29 `[[entries]]`, each `config = <pattern>.toml` + `count`; `seed = 20260506`, `start_number = 2000` |
| Seed derivation | `erp-bench/erp_bench/generation/runner.py:174-176, 243-283` | `np.random.default_rng(dataset.seed).integers(0, 2**63)` → one seed per task; `scenario_number` increments from `start_number`. Fully deterministic. |
| Sample blueprint | `erp-bench/erp_bench/procurement/sampler.py` (`ProcurementSampler.build_blueprint`), invoked at `erp_bench/procurement/category.py:60-67` | Draws customers/demands/deadlines/budgets, vendors + tiered offers, BOM graph, workcenters, stock from the pattern's ranges |
| Solve | `erp-bench/erp_bench/procurement/solver.py:743-852` (`ScenarioGenerator._solve`) | CP-SAT: build model → optionally `Minimize(primary)` → **freeze** objective (`model.Add(primary == target)`) → optional spend secondary tie-break → lexicographic tie-break phase → extract `PlanResult` |
| Accept/reject + resample | `erp-bench/erp_bench/procurement/sampler.py:2804-2929` (`_build_and_solve`), `MAX_RESAMPLE_ATTEMPTS = 150` at `:2343` | See §1.3 |
| Render | `erp-bench/erp_bench/procurement/category.py:100-174` (`render()`) + `erp_bench/generation/render.py` | Jinja2 → `instruction.md`, `tests/test.sh`, `tests/checks.py`, `solution/solver.py`, `solution/solve.sh`; JSON dump → `solution/optimal_plan.json` (the `JsonOutputFile` block at `category.py:168-172`); env from `templates/procurement/supply_planning/setup_scenario.py.jinja2` + `templates/shared/{Dockerfile,entrypoint.sh,odoo.conf,task.toml}` |

One shared template context feeds instruction, verifier, and oracle: `HarborTaskExporter._build_template_context(scenario, plan, blueprint)` (`erp-bench/erp_bench/harbor.py:309`, called from `category.py:_template_context`). **That single context object is the anti-drift mechanism** — the verifier's expected numbers and the oracle's plan are literally the same Python values.

### 1.3 The admission gates (this is the transferable part)

`_build_and_solve` loops up to 150 times, resampling the seed on any `RuntimeError`:

| Gate | Code | Rejects when |
|---|---|---|
| Solver certifies OPTIMAL | `solver.py:805-811` — `raise RuntimeError(f"Solver failed to certify optimality (status={solver.StatusName(status)})")` | CP-SAT returns FEASIBLE-but-not-proven, or times out (5s, retried at 15s) |
| Spend tie-break certified | `solver.py:823-834` | secondary lexicographic phase not OPTIMAL |
| Unsat-demand shape | `sampler.py:2864-2880` | screened scenario produced no kept orders, or no cancelled orders, or no `cancel_seeded` action, or (mixed-seed) no `create_confirm_prompt` |
| Timing feasibility | `sampler.py:2888-2891` — `_plan_timing_feasible` | plan infeasible under explicit MO/component scheduling |
| **Objective non-collapse** | `sampler.py:2769-2801` `_objective_family_certified` | the fancy objective is achievable *for free* by the spend-optimal plan |

The non-collapse gate is the sharpest idea and directly portable. It re-solves the same blueprint twice — once for `min_new_spend`, once for the real objective *with spend pinned to the spend-optimum* — and demands the real objective improve by ≥ threshold:

```python
spend_plan = generator.solve_plan_for_objective(ProcurementObjectiveKind.min_new_spend)
spend_frontier_plan = generator.solve_plan_for_objective(
    blueprint.objective_kind, fixed_spend_cents=int(round(spend_plan.optimal_new_spend * 100)))
improvement = round(spend_frontier_plan.objective_value - candidate_plan.objective_value, 2)
return improvement + 1e-6 >= threshold
```
Thresholds: `vendor_consolidation: 1.0`, `capacity_preservation: 1.0` (`sampler.py:110-113`). i.e. *"a task only ships if optimizing the stated objective actually changes the answer by at least one whole unit versus the naive cost-minimizer."* Finance-world analogue: reject a task whose "correct" answer equals the answer a lazy heuristic would give.

Failure mode after 150 tries: `RuntimeError("Failed to generate provably-optimal procurement scenario …")` (`sampler.py:2926-2929`) — the task is *not shipped*. Same ship-honest posture as blobfish-0/lawfirm-qwen.

### 1.4 QA contract for a shipped task

`erp-bench/agents/task-reviewer.md:10-13` states the gates plainly:
- `nop` must score `0`
- `oracle` must score `100`
- generation must be deterministic for a fixed seed

plus an explicit alignment chain to audit: `solver <-> instruction <-> data loader <-> verifier` (`task-reviewer.md:35-36`), and a source-of-truth rule: *"Do not rely on manual edits under `tasks/` for permanent fixes"* (`:47`). That is exactly the discipline finance-world needs for its cloners.

Note the reward scale: **0–100 float, not binary**. Verbatim: `"passed": float(sys.argv[1]) >= 99,` — inside the heredoc'd Python that writes `reward.json` (`erp-bench/tasks/2001_easy_01_buy_only_baseline/tests/test.sh:279`; same line at `tasks/2060_.../tests/test.sh:365`).

---

## 2. Task-pattern taxonomy: all 29 patterns

300 task dirs (`ls tasks | wc -l` → 300, plus `tasks/dataset.toml` + `tasks/README.md`). Tier split from dir names: **easy 50 / medium 166 / hard 84**. Objective split from `task.toml` `[metadata].objective_kind`: `min_new_spend` 183, `vendor_consolidation` 34, `capacity_preservation` 31, `repair_plan` 28, `constraint_only` 24. Tag `unsat_demand` on 77 of 300 (set at `category.py:110-112` when `blueprint.unsat_demand`).

Config sources: `erp-bench/erp_bench/procurement/examples/diverse_300/*.toml` (26 files) + `examples/repair_plan_{easy,medium,hard}.toml` (3) = 29.

| # | Pattern (dir suffix) | Tier | Objective | Routes | Acceptance | Invoicing | Domain | Count |
|---|---|---|---|---|---|---|---|---|
| 01 | `buy_only_baseline` | easy | constraint_only | buy_only | accept_all | – | sound_panels | 8 |
| 02 | `buy_only_immediate_invoicing` | easy | constraint_only | buy_only | accept_all | immediate | server_racks | 8 |
| 03 | `buy_only_fixed_downpayment` | easy | constraint_only | buy_only | accept_all | net_30 + fixed DP | conveyor_modules | 8 |
| 04 | `buy_only_percentage_downpayment` | easy | min_new_spend | buy_only | accept_all | net_30 + % DP | workstations | 8 |
| 05 | `screened_buy_only_all_seeded` | medium | min_new_spend | buy_only | screen_by_policy (all seeded) | – | lab_benches | 10 |
| 06 | `screened_buy_only_mixed_seeded` | medium | min_new_spend | buy_only | screen (mixed seeded+prompt) | – | cable_assemblies | 11 |
| 07 | `screened_buy_only_mixed_seeded_invoicing` | medium | min_new_spend | buy_only | screen (mixed) | net_30 | hvac_units | 11 |
| 08 | `single_bom_single_workcenter` | medium | min_new_spend | buy_and_manufacture | accept_all | – | led_fixtures | 11 |
| 09 | `single_bom_lowest_cost` | medium | min_new_spend | buy_and_manufacture | accept_all | – | packaging_machines | 11 |
| 10 | `single_bom_split_by_capacity` | medium | capacity_preservation | buy_and_manufacture | accept_all | – | safety_enclosures | 11 |
| 11 | `restricted_subassembly_qualified_workcenters` | hard | min_new_spend | buy_and_manufacture | accept_all | – | solar_panels | 10 |
| 12 | `single_subassembly_lowest_cost` | medium | min_new_spend | buy_and_manufacture | accept_all | – | robotic_arms | 11 |
| 13 | `single_subassembly_qualified_workcenters` | medium | min_new_spend | buy_and_manufacture | accept_all | – | water_filters | 11 |
| 14 | `single_subassembly_shared_overflow_capacity` | medium | min_new_spend | buy_and_manufacture | accept_all | – | elevator_parts | 11 |
| 15 | `parallel_subassemblies_branch_assigned` | hard | capacity_preservation | buy_and_manufacture | accept_all | – | battery_packs | 10 |
| 16 | `serial_subassemblies_branch_assigned` | hard | capacity_preservation | buy_and_manufacture | accept_all | – | air_compressors | 10 |
| 17 | `shared_component_subassemblies_branch_assigned` | hard | min_new_spend | buy_and_manufacture | accept_all | – | fire_systems | 11 |
| 18 | `manufacture_only_policy_forbidden` | medium | min_new_spend | manufacture_only_policy_forbidden | accept_all | – | clean_rooms | 11 |
| 19 | `manufacture_only_no_buy_route` | medium | min_new_spend | manufacture_only_no_buy_route | accept_all | – | dock_levelers | 11 |
| 20 | `manufacture_only_no_available_vendors` | medium | min_new_spend | manufacture_only_no_available_vendors | accept_all | – | transformer_units | 12 |
| 21 | `single_bom_lowest_cost_screened_mixed_seeded` | medium | **vendor_consolidation** | buy_and_manufacture | screen (mixed) | – | packaging_machines | 12 |
| 22 | `single_bom_split_by_capacity_invoicing` | medium | min_new_spend | buy_and_manufacture | accept_all | immediate | safety_enclosures | 12 |
| 23 | `restricted_subassembly_qualified_workcenters_screened_all_seeded` | hard | vendor_consolidation | buy_and_manufacture | screen (all seeded) | – | solar_panels | 11 |
| 24 | `single_subassembly_shared_overflow_capacity_screened_invoicing` | hard | vendor_consolidation | buy_and_manufacture | screen | net_30 | elevator_parts | 11 |
| 25 | `shared_component_subassemblies_branch_assigned_screened_all_seeded` | hard | min_new_spend | buy_and_manufacture | screen (all seeded) | – | fire_systems | 11 |
| 26 | `buy_only_net_30_no_adjacent_data` | easy | min_new_spend | buy_only | accept_all | net_30 | sound_panels | 10 |
| R1 | `repair_plan_easy` | easy | repair_plan | buy_only | accept_all | – | sound_panels | 8 |
| R2 | `repair_plan_medium` | medium | repair_plan | buy_and_manufacture | accept_all | – | led_fixtures | 10 |
| R3 | `repair_plan_hard` | hard | repair_plan | buy_and_manufacture | accept_all | – | solar_panels | 10 |

Grouped: **buy-only (01-04, 26 + R1)** · **order screening (05-07, 21, 23-25)** · **single-BOM manufacturing (08-10, 22)** · **subassembly topologies (11-17, 23-25)** · **manufacture-forced (18-20)** · **plan repair (R1-R3)** · **invoicing overlay (02-04, 07, 22, 24)**.

Pattern 26 is the deliberate **control**: `include_adjacent_data = false` (`examples/diverse_300/26_buy_only_net_30_no_adjacent_data.toml`) — the only pattern with no distractor records. Everything else ships 150 distractor entities per task.

### 2.1 Difficulty axes (what the tier knobs actually move)

From `erp-bench/erp_bench/procurement/presets.py:29-115` (easy / medium / hard presets):

| Axis | easy | medium | hard |
|---|---|---|---|
| `customers.count_range` | (2,4) | (8,10) | (20,32) |
| `customers.demand_range` | (5,11) | (14,25) | (18,31) |
| `customers.deadline_range` | (5,9) days | (8,14) | (8,13) |
| `supply.stock_ratio_range` (how much demand pre-covered by stock) | (0.75, 0.92) | (0.38, 0.52) | (0.28, 0.42) |
| finished vendors / limit | 3 / 4 | 4-5 / 6 | 5-6 / 8 |
| components | none | 5-7 | 8-10 |
| `vendor_capacity_primary_ratio_range` (how much one vendor can cover) | (0.4, 0.9) | (0.1, 0.36) | (0.07, 0.26) |
| `sampling_tightness` | 0.25 | 0.55 | 0.72 |
| assembly capacity ratio | – | (0.24, 0.46) | (0.20, 0.34) |

Independent axes stacked on top: BOM structure (6 values), workcenter choice path (5 values, with a legality matrix `SUPPORTED_WORKCENTER_CHOICE_PATHS_BY_BOM_STRUCTURE` at `erp_bench/procurement/config.py:79-97`), route availability (5 values, `AvailableRoutes` at `config.py:19-28`), acceptance mode + reject rules (`budget_below_list_price` / `quantity_outside_window` / `lead_time_below_minimum`, `config.py:41-44`), invoicing (payment term × downpayment mode), and repair kind (`supplier_cancellation` / `workcenter_outage`, `config.py:57-60`).

The tier label is only *one* dimension — but only **pattern 11** actually demonstrates that. `11_restricted_subassembly_qualified_workcenters.toml:2,6,15` is `difficulty = "hard"` on *medium-preset volume* (`customers.count_range = [8, 10]`, `component_count_range = [5, 7]`), so its difficulty comes from topology, not volume. The other three hard subassembly patterns do **not** work that way: `15_parallel_subassemblies_branch_assigned.toml:2,7,16`, `16_serial_subassemblies_branch_assigned.toml:2,7,16` and `17_shared_component_subassemblies_branch_assigned.toml:2,6,15` all set `count_range = [20, 32]` and `component_count_range = [8, 10]` — full hard-preset volume stacked *on top of* hard topology. `constraint_only` is hard-restricted to easy (`config.py:318-322`).

---

## 3. Task anatomy: three tasks end to end

Layout is identical for all 300 (`README.md:120-137`): `task.toml`, `instruction.md`, `environment/{Dockerfile,entrypoint.sh,odoo.conf,scenario_data.json,setup_scenario.py}`, `tests/{test.sh,checks.py}`, `solution/{solve.sh,solver.py,optimal_plan.json}`.

Byte sizes for `tasks/2001_easy_01_buy_only_baseline` — note how *large the generated verifier is*: `tests/checks.py` 102 KB / 2819 lines, `environment/setup_scenario.py` 64 KB, `environment/scenario_data.json` 65 KB, `solution/solver.py` 37 KB, `tests/test.sh` 11 KB, `instruction.md` 4.8 KB, `task.toml` 639 B.

### 3.1 `task.toml` (`tasks/2001_easy_01_buy_only_baseline/task.toml`)

```toml
schema_version = "1.1"
artifacts = []
[task]
name = "agentic-labs/2001_easy_01_buy_only_baseline"
description = ""            # empty
authors = []                # empty
keywords = []               # empty
[metadata]
scenario_number = 2001
name = "Door Seal Acoustic Kit"
difficulty = "easy"
category = "erp"
objective_kind = "constraint_only"
task_pattern = "01_buy_only_baseline"
tags = [ "odoo", "erp-bench", "procurement",]
seed = 4684432955164814774
[verifier]      timeout_sec = 300.0
[agent]         timeout_sec = 3600.0
[environment]   build_timeout_sec = 600.0; cpus = 3; memory_mb = 4096; storage_mb = 2048; gpus = 0
                allow_internet = true; mcp_servers = []
[verifier.env]  [environment.env]  [solution.env]     # all empty
```

Differences vs the finance-world plan in `research/harbor-format.md`: `schema_version = "1.1"` (not 1.4); no `network_mode` anywhere (they use `allow_internet = true` — the Dockerfile pulls `uv` + postgres-18 apt repo at build time); `[metadata]` carries `scenario_number / difficulty / objective_kind / task_pattern / seed`; there is an `mcp_servers = []` key. **The `seed` in metadata is the reproducibility anchor** — copy that idea.

Sibling manifest `tasks/dataset.toml` is a Harbor dataset file: `[dataset] name/description`, `[[dataset.authors]] name = "Maks Ivanov"`, then 300 × `[[tasks]] name = "agentic-labs/<task>"` + **`digest = "sha256:…"`**. Content-addressed per task — a cheap drift detector finance-world should copy.

### 3.2 Easy: `2001_easy_01_buy_only_baseline` (constraint_only)

**instruction.md:1-35** — the business half is ~35 lines (ending with the Execution Autonomy paragraph at `:35`, then a `---` rule at `:37`), then a fixed Odoo-access appendix (`# Odoo Environment` header at `:39`, running to the end of the 108-line file — lines 39-108, identical across tasks, from `templates/procurement/supply_planning/instruction.md.jinja2`):

> Ensure all these Door Seal Acoustic Kit customer orders are supplied on schedule:
> - Arrow Works: 8 units due in 6 days (pretax budget cap $1,529)
> - Evergreen Observatory: 12 units due in 7 days (pretax budget cap $2,287)  … (4 customers)
>
> On-hand finished stock covers 38 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.
>
> Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.2% at selling price.

Policy bullets that become verifier rules 1:1 (`instruction.md:14-31`): cover every order · clear the margin floor · stock may be used · create and confirm SOs and POs · budgets are pretax · **"Link Sales Orders to the related Purchase Orders for traceability"** · **"For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI)"** · "the lineage must be SO -> PO" · sell at List Price · set commitment date on SOs · set delivery date on POs · **"Review Internal Notes/comments on stock, customers, and vendors before you confirm entries"** · min/max quantities are horizon-wide totals · one consolidated PO per supplier offer · "Check each vendor's Internal Notes in Odoo for maximum order quantity limits".

Then a fixed "Execution Autonomy" block: *"Work with full autonomy. Do not ask the user for confirmation… If multiple feasible plans satisfy the constraints, choose the one that best optimizes the stated objective."*

**environment/scenario_data.json** (validated by `schemas/schema.json`, title `ScenarioData`) — top-level keys and this task's shape:

| Key | Shape here | Notes |
|---|---|---|
| `scenario_number`, `name`, `seed` | 2001, "Door Seal Acoustic Kit", 4684432955164814774 | |
| `instruction`, `background_and_policy` | strings | same text rendered into instruction.md |
| `invoicing_policy` | `{invoice_required, payment_term, downpayment_required, downpayment_threshold_amount, downpayment_mode, downpayment_value}` | all null/false here |
| `warehouses` | `[]` | |
| `vendors` | 54 (4 task + 50 adjacent) | `{name, ref, supplier_rank, comment}` |
| `customers` | 54 (4 task + 50 adjacent) | `{name, ref, email, budget_dollars, is_company, comment, credit_limit, payment_term, tags}` |
| `products` | 51 (1 finished + 50 adjacent) | `{name, code, category, type:"consu", list_price, standard_price, routes, vendor_info[]}`; `vendor_info` = `{partner_ref, delay, min_qty, max_qty, price, name}` |
| `boms` | 10 | `{product_code, type:"normal", quantity, components[{component_code,quantity}], warehouse_code}` |
| `workcenters` | `[]` (buy-only) | |
| `stock_levels` | 51 | `{product_code, warehouse_code, quantity, location_type:"stock"}` |
| `existing_{sales,purchase,manufacturing}_orders` | `[]` | populated in screened/repair patterns |
| `repair_context` | `null` | |
| `system_parameters` | `[{key:"erp_bench.min_margin_percent", value:"29.2"}]` | the margin floor lives in `ir.config_parameter` |

Refs are namespaced with an opaque per-scenario token: task entities `rD5BD7E1C25_c01`/`_q01`, products `PD5BD7E1C25-SPP-DSK-007`; adjacent entities get a *different* channel token `r2EF13BB94B_p01`/`_q02`, `P2EF13BB94B-A001` (`sampler.py:116-118` `_opaque_namespace_token` = `blake2s(f"{scenario_number}:{channel}")[:5]`). The agent cannot pattern-match "which records are mine".

**solution/optimal_plan.json** — the solved spec, dumped verbatim (`JsonOutputFile(path="solution/optimal_plan.json", payload=plan)` at `category.py:168-172`; `:159-164` is the sibling `solution/solve.sh` template entry). Keys: `objective_kind`, `objective_value`, `stock_cost`, `component_cost`, `assembly_cost`, `allocations[]`, `purchase_orders[]`, `manufacturing_orders[]`, `stock_report[]`, plus scalar KPIs (`optimal_new_spend`, `distinct_vendors_used`, `total_scheduled_minutes`, `finished_purchase_spend`, `component_purchase_spend`, `expected_new_spend`, `new_spend_units`, `revenue_from_new_spend`, `new_spend_coverage_ratio`, `new_spend_margin`, `total_revenue`, `assembly_units`, `total_cost`, `margin`).

Per-allocation record (one per customer) carries the *decision and its reason*:
```json
{"ref":"rD5BD7E1C25_c01","accepted":true,"action":"create_confirm_prompt","task_order_source":"prompt_only",
 "task_order_ref":"rD5BD7E1C25_c01","seeded_order_state":null,"reject_reasons":[],"reject_reason_text":null,
 "stock_allocated":0,"demand":8,"fulfilled_demand":8,"deadline":6,"price":186.08,"purchase_units":8,
 "assembly_units":0,"requested_revenue":1488.64,"revenue":1488.64,"variable_cost":733.28,
 "component_cost":0.0,"assembly_cost":0.0,"margin":0.5074161650902838}
```
Per-PO record carries an `offer_key` and origin lineage:
```json
{"plan_ref":"po:finished:rD5BD7E1C25_q01:PD5BD7E1C25-SPP-DSK-007:8:91.66:6",
 "vendor_ref":"rD5BD7E1C25_q01","offer_key":"rD5BD7E1C25_q01|PD5BD7E1C25-SPP-DSK-007|8|91.66|6",
 "quantity":8,"unit_cost":91.66,"total_cost":733.28,"lead_time":6,"planned_arrival_days":6,
 "description":"Priority Shuttle lane (6d transit, 8-43 units)","product_code":"PD5BD7E1C25-SPP-DSK-007",
 "supply_role":"finished",
 "origin_customer_refs":["rD5BD7E1C25_c01"],"origin_plan_refs":[],"consumer_product_codes":[]}
```
`action` vocabulary seen across tasks: `create_confirm_prompt`, `confirm_seeded`, `cancel_seeded`, `skip_prompt`. `reject_reasons` vocabulary: `min_qty`, `max_qty`, `min_lead_time` (+ budget rule).

**solution/solver.py** is *not* a solver — it is a generated Odoo-writing script with the plan baked in as `SOLVER_PLAN = {...}` and `INVOICE_REQUIREMENTS = [...]` (`tasks/2001_.../solution/solver.py:32,67`), driving a class `OptimalSolver` with methods `_create_sale_orders`, `_create_confirmed_sale_order`, `_confirm_seeded_sale_order`, `_cancel_seeded_sale_order`, `_create_manufacturing_orders`, `_create_purchase_orders`, `_assign_workcenter_and_dates`, `_create_required_invoice`, `_cancel_repair_artifacts`, `execute_plan`. `solve.sh` waits for `/tmp/saas_setup_complete`, pip-installs `odoo-client-lib==2.0.2`, runs `python3 /solution/solver.py`, and echoes a summary. This is exactly blobfish-0's `trace.json` replay pattern, with the trace inlined as Python.

**Odoo runtime** (`environment/Dockerfile`, `entrypoint.sh`): `FROM odoo:19` + postgres-18; entrypoint starts pg, creates DB `bench` over `POST /web/database/create`, then generates an API key inside `odoo shell` via `env['res.users.apikeys']._generate('rpc','benchmark', today+90d)` and writes it to `/etc/odoo/api_key`; runs `setup_scenario.py` against the **JSON-2 API**; then **deletes `/setup/setup_scenario.py` and `/setup/scenario_data.json`** (`entrypoint.sh:86`) so the agent cannot read the ground truth off disk; finally `touch /tmp/saas_setup_complete`. That sentinel file's mtime *is the scenario anchor date*:

```python
def _scenario_anchor_date():
    if not os.path.exists(SETUP_COMPLETE_SENTINEL): raise RuntimeError(...)
    return datetime.fromtimestamp(os.path.getmtime(SETUP_COMPLETE_SENTINEL)).date()
def _scenario_deadline(days_from_anchor):
    return _scenario_anchor_date() + timedelta(days=int(days_from_anchor))
```
(`tasks/2001_.../tests/checks.py:839-846`). All dates in instruction/verifier are **relative** ("due in 6 days"), resolved against setup time. Neat trick — no date rot, ever.

### 3.3 Medium: `2060_medium_07_screened_buy_only_mixed_seeded_invoicing` (min_new_spend, `unsat_demand`)

8 customers, 73 units on stock, `objective_kind = "min_new_spend"`, tags include `unsat_demand`. The instruction adds an acceptance policy and an invoicing policy — **abridged** from `tasks/2060_.../instruction.md:18-29` (the `## Background & Policy` list runs `:17-35`; `…` marks bullets dropped here):

> * Accepted orders must request between 17 and 24 units and allow at least 10 days of lead time. *(:18)*
> * Reject or cancel any order that fails those acceptance rules. *(:19)*
> * After acceptance, cover each qualifying order while achieving the lowest possible new outlay. *(:20)*
> * … *(:21 — the margin floor: "The combined units covered through new purchasing or manufacturing must clear at least 24.6% portfolio-level new-spend margin at selling price.")*
> * Finance considers the existing stock as sunk cost. *(:22)*
> * **Some sales documents may already exist in draft; review existing documents before creating new ones.** *(:23)*
> * Cancel any already-drafted sales order that fails those acceptance rules. *(:24)*
> * … *(:25 pre-tax budgets, :26 SO↔PO link)*
> * After confirming each retained sales order, create and post exactly one linked customer invoice. *(:27)*
> * Use 30 Days terms on retained sales orders and all linked customer invoices. *(:28)*
> * Rejected, cancelled, or skipped orders must not be invoiced. *(:29)*

(The remainder of the list, `:30-35`, covers the same lineage / origin-field / list-price / commitment-date / delivery-date / Internal-Notes family of bullets listed for task 2001 in §3.2, with minor wording differences — e.g. 2060`:35` reads "before you release anything" where 2001 reads "before you confirm entries".)

Ground truth: 6 of 8 rejected, each with a machine-generated human reason —
`"reject_reasons":["min_qty","min_lead_time"], "reject_reason_text":"requested quantity 16 is below the 17-unit minimum; requested lead time of 8 days is below the 10-day minimum"`. Two survivors (c06 prompt-only, c07 seeded) are fully covered from stock, so `optimal_new_spend = 0.0` and no POs — an interesting degenerate optimum that still discriminates, because the *acceptance decisions* carry the signal.

The verifier for this task adds ~20 rules the easy one lacks: `task_state_transitions_completed`, `seeded_order_confirmed`, 4× `seeded_order_cancelled`, 2× `prompt_request_not_confirmed`, and the whole invoicing family (`retained_order_has_expected_invoice_flow … regular`, `retained_order_has_expected_payment_term … net_30`, `linked_posted_invoices_match_order_partner`, `linked_posted_invoices_have_expected_payment_term`, `regular_invoice_amount_matches_policy … 138618.2`, `linked_posted_invoices_are_tax_free`, 6× `rejected_order_not_invoiced`).

It also installs a **no-op hard-zero gate**:
```bash
tracked_and_aspect_lines PARTIAL_ACCEPTANCE_ACTIVITY_OK <<'EOF'
has_relevant_activity
EOF
...
[ "$PARTIAL_ACCEPTANCE_ACTIVITY_OK" -eq 1 ] || HARD_SCORE_GATE_OK=0
```
(`tasks/2060_.../tests/test.sh:195-198, 314`) — because on a screened task where the optimal move is mostly "cancel things", a literal no-op could otherwise accidentally satisfy several rules.

### 3.4 Hard: `2298_hard_repair_plan_hard` (repair_plan, workcenter_outage)

10 customers, 49 finished units on hand, `objective_kind = "repair_plan"`, `objective_value = 154.0` (the *disruption distance*, not money). Instruction opener (`tasks/2298_.../instruction.md:1`):

> Existing confirmed sales orders and current manufacturing commitments for Portable Solar Generator Kit are already in Odoo. Assembly Line 1 is experiencing an equipment outage, and confirmed manufacturing work is already scheduled on that line. Reuse the existing sales orders, review the commitments already in place, cancel the affected manufacturing orders, keep unaffected work where it still makes sense, and adjust the plan for … using the best feasible alternative fulfillment route.

Key policy line: *"Adjust the existing supply plan with the least disruption to what is already committed. When more than one feasible option changes the plan by the same amount, keep new purchasing and manufacturing spend as low as possible."* — a lexicographic objective stated in English.

Pre-seeded world state: 10 confirmed SOs, 22 confirmed POs, 4 confirmed MOs. Each seeded record carries a *narrative note*:
- MO note: `"Existing confirmed manufacturing commitment that is part of the pre-disruption plan. This workcenter path is down and cannot be used for replacement work."`
- PO note: `"Existing confirmed purchase commitment that is part of the pre-disruption plan."`
- Workcenter WC01 note: `"Power Equipment workcenter pool 1\nRepair scenario disruption: this workcenter is down for the task-critical manufacturing path and should not be used for replacement work."`, `capacity_minutes: 0.0`, with `alternative_workcenter_codes: ["…WC02","…WC03"]` at 4675 / 3150 minutes.

`repair_context` block in `scenario_data.json`:
```json
{"kind":"workcenter_outage","broken_supplier_offer_key":null,"broken_supplier_vendor_ref":null,
 "broken_workcenter_code":"P6984A087C0-WC01",
 "impacted_customer_refs":[5 refs],"seeded_sales_order_refs":[10],
 "seeded_purchase_order_refs":[22],"seeded_manufacturing_order_refs":[4],
 "broken_purchase_order_refs":[],"broken_manufacturing_order_refs":["…_mo01","…_mo03","…_mo04"]}
```
The repair blueprint is built by **solving twice**: solve the undisrupted scenario first, then derive the disruption from that plan and re-solve with `objective_kind = repair_plan` (`sampler.py:2741-2766`, `_repair_workcenter_context` / `_repair_supplier_context`). The "baseline plan" is therefore itself certified-optimal, which is what makes "minimum disruption" well-defined.

---

## 4. Verifier design (the part to benchmark finance-world against)

### 4.1 Architecture

`tests/test.sh` is a **bash scoring harness**; `tests/checks.py` is a **long-lived coprocess** holding one Odoo connection and answering `PASS` / `FAIL` / `NA` per line:

```bash
coproc ODOO { python3 /tests/checks.py 2>/logs/verifier/checks.log; }
check() { echo "$*" >&"${ODOO[1]}"; read -r -t 300 r <&"${ODOO[0]}" || r=FAIL
          case "$r" in PASS|FAIL|NA) ;; *) r=FAIL ;; esac; printf "%s\n" "$r"; }
```
(`tasks/2001_.../tests/test.sh:31-41`). `checks.py`'s dispatcher — `CHECKS` at `tests/checks.py:2775-2798`, the loop at `:2800-2820`, **condensed here** (the shipped code spells the two branches out as `if`/`else` rather than the inline conditionals below, and the `CHECKS` list enumerates every check function rather than trailing off):
```python
CHECKS = {f.__name__: f for f in [demand_coverage, deadline_fulfillment, new_spend_margin_policy, ...]}
if __name__ == "__main__":
    conn = connect()
    for line in sys.stdin:
        parts = line.strip().split()
        if not parts or parts[0] == "QUIT": break
        name, args = parts[0], parts[1:]
        fn = CHECKS.get(name)
        if not fn: logger.error("Unknown check: %s", name); print("FAIL", flush=True); continue
        try:
            result = fn(*args)
            print(NOT_APPLICABLE if result == NOT_APPLICABLE else ("PASS" if result else "FAIL"), flush=True)
        except Exception as e:
            logger.error("%s(%s): %s", name, " ".join(args), e); print("FAIL", flush=True)
```
Two design choices worth stealing: **exceptions are FAIL, never crash**, and **`NA` is a first-class third state** for rules that don't apply to the route the agent chose.

Before any of that, `test.sh:9-27` polls up to 180s for `/tmp/saas_setup_complete` *and* an HTTP 200 from Odoo; if setup never completed it dumps `/tmp/saas_setup_error` and `exit 1` — infrastructure failure is distinguished from task failure.

### 4.2 Aggregation: three dimensions, one gate

| Dimension | Weight | Combiner | Contents |
|---|---|---|---|
| `constraint` | **25 %** | `and_aspect` (all-or-nothing per aspect group) + a few `sum_aspect` groups | feasibility: coverage, deadlines, price, revenue, budget, margin, PO/MO scheduling & consolidation & tiering, capacity caps, supply coverage, acceptance transitions, invoicing flow |
| `optimality` | **60 %** | continuous 0–100 from `optimality.json` | how close to the certified optimum |
| `hygiene` | **15 %** | `sum_aspect` (partial credit) | origin traceability, `adjacent_data_untouched` |

Two combinators, and the difference is the whole point (`tests/test.sh:62-115`):
- `and_aspect` — evaluate every rule in the group; if **any** applicable rule FAILs, the group earns **0 of N**. Used for feasibility clusters (you don't get 3/4 credit for a plan that misses a deadline).
- `sum_aspect` — per-rule credit, 1 point each. Used for hygiene and for per-order state transitions.
- `NA` results are excluded from both earned and total, so unused routes neither help nor hurt.

Final score (`tests/test.sh:257-269`):
```awk
cs = (ct > 0) ? ce / ct * 100 : 100
hs = (ht > 0) ? he / ht * 100 : 100
if (hgo < 1)       printf "0.00"                                  # hard no-op gate
else if (cs < 100) printf "%.2f", cs * 0.25                       # constraints gate everything
else               printf "%.2f", cs * 0.25 + ss * 0.60 + hs * 0.15
```
**Constraints gate the other two dimensions completely.** An infeasible plan can score at most 25, no matter how cheap or tidy it is. And `HARD_SCORE_GATE_OK=0` zeroes everything.

Outputs written to `/logs/verifier/`: `reward.txt` (the float), `reward.json` (rich), `rule_results.tsv` (dimension⇥rule-expr⇥status), `optimality.json`, `spend.json`, `checks.log`. `reward.json` includes `overall_score`, `passed` (≥99), per-dimension earned/total, and a `rules` block with `total/applicable/passed/failed/not_applicable/by_dimension/failed_rules` — every rule with its parsed name + args. **This per-rule telemetry is the single most copyable thing in the repo**: it turns a score into a diagnosis.

### 4.3 The check functions (quoted)

All read *terminal Odoo records* via `odoolib` search/read — never the agent's actions. Confirmed-state filters are constants: `PO_CONFIRMED_STATES = ["purchase"]`, `MO_CONFIRMED_STATES = ["confirmed","progress","to_close","done"]`, SOs matched on `state in ["sale","done"]`.

**Coverage** — sums confirmed SO lines for the (customer, product) pair:
```python
def demand_coverage(customer_ref, product_code, expected, cmp="gte"):
    pid, prd = _partner(customer_ref), _product(product_code)
    sos = M("sale.order").search(domain=[("partner_id","=",pid),("state","in",["sale","done"])])
    lines = M("sale.order.line").search_read(domain=[("order_id","in",sos),("product_id","=",prd)],
                                             fields=["product_uom_qty"])
    total = sum(float(row.get("product_uom_qty",0) or 0) for row in lines)
    return _cmp(total, float(expected), cmp)
```
Note the comparator is an argument: easy tasks emit `gte`, screened tasks emit `equals` (accepting *more* than the screened quantity is itself a violation).

**Deadline + physical fulfillment path** — not just a date field, an actual supply document:
```python
def deadline_fulfillment(customer_ref, product_code, deadline_days):
    ...
    for so_id in so_ids:
        commit = _read1(SO, so_id, ["commitment_date","name"]).get("commitment_date")
        if not commit: return False
        if commit_dt > _scenario_deadline(deadline_days): return False
        if not _fulfillment_path(so_id, d.get("name",""), product_code): return False
    return True

def _fulfillment_path(so_id, so_name, product_code):
    # 1) a live stock.move linked to the SO line
    for lid in SOL.search(domain=[("order_id","=",so_id),("product_id","=",prd)]):
        if SM.search(domain=[("sale_line_id","=",lid),
                             ("state","in",["assigned","confirmed","done","partially_available"])]): return True
    # 2) a confirmed PO whose origin mentions the SO name AND has a line for the product
    for po_id in _confirmed_po_ids(("origin","ilike",so_name)):
        if so_name in _origin_tokens(PO, po_id):
            if POL.search(domain=[("order_id","=",po_id),("product_id","=",prd)]): return True
    if product_code == PRODUCT_CODE and not FINISHED_MANUFACTURING_ALLOWED: return False
    # 3) a confirmed MO with positive qty whose origin mentions the SO name
    ...
```

**Margin policy** — recomputed from ERP state, not read off a field:
```python
def new_spend_margin_policy(min_margin):
    sb = _spend_breakdown(); spend = float(sb["total_new_spend"] or 0.0)
    sold_units = <sum of confirmed SO line qty across CUSTOMER_DEMANDS>
    if spend <= SPEND_TOLERANCE: return sold_units > 0.01          # zero-spend plans pass trivially
    new_spend_units = min(float(TOTAL_DEMAND), sold_units, purchased_finished + produced_finished)
    revenue_from_new_spend = round(PRODUCT_LIST_PRICE * new_spend_units, 2)
    actual_margin = (revenue_from_new_spend - spend) / revenue_from_new_spend
    return actual_margin is not None and actual_margin + 0.0001 >= min_margin
```

**Spend accounting** — and the trap it defends against. Line price is *not trusted*; the verifier re-prices against the scenario's tier table and only falls back to the typed `price_unit` when no tier applies:
```python
tp = _resolve_tier_price(vendor, lpid, qty)
if tp is None: unverifiable_count += 1; total = round(qty * lpu, 2)
else:          total = round(qty * tp, 2)
...
"verified_spend_complete": relevant_count == 0 or unverifiable_count == 0,
```
Tier resolution itself is strict — pick the highest `min_qty` tier the quantity qualifies for, and **refuse to resolve if two tiers at that min_qty disagree on price** (`checks.py:864-878`).

**Optimality scoring** (`checks.py:1010-1185`) — exponential decay on the distance from the certified optimum:
```python
def _minimize_metric_score(actual, expected, *, tolerance, decay_k):
    if actual <= expected + tolerance: return 100.0
    baseline = max(expected, 1.0)
    return round(math.exp(-decay_k * (actual - expected) / baseline) * 100, 2)

def _lexicographic_score(primary_score, secondary_score):   # SECONDARY_SPEND_BAND_WEIGHT = 0.10
    if primary_score >= 100.0:
        return round((100.0 - 100.0*W) + secondary_score*W, 2)   # 90 + 10% of the spend score
    return round(primary_score * (1.0 - W), 2)                   # capped at 90 if primary missed
```
with per-objective constants `SPEND_DECAY_K = 5.0`, `SPEND_TOLERANCE = 0.25`, `VENDOR_CONSOLIDATION_DECAY_K = 2.0`, `CAPACITY_PRESERVATION_DECAY_K = 5.0`, `REPAIR_PLAN_DECAY_K = 2.0`.

Per objective kind:

| `objective_kind` | primary metric | source |
|---|---|---|
| `min_new_spend` | total new spend vs `EXPECTED_SPEND` | `_spend_breakdown()["spend_score"]` |
| `vendor_consolidation` | count of distinct vendors on relevant confirmed POs | `_distinct_relevant_vendors_used()` |
| `capacity_preservation` | scheduled workcenter minutes (`qty × WORKCENTER_OPTION_TIMES`) | `_scheduled_minutes_used()` — returns `None` (score 0) if any MO lacks a legal (product, workcenter) pair |
| `repair_plan` | **L1 disruption distance** vs the baseline plan | `_repair_penalty()` |
| `constraint_only` | fixed 100.0 | — |

`_repair_penalty` is the elegant one: sum of absolute deltas between the agent's final per-offer purchase quantities / per-(product,workcenter) manufacturing quantities and the pre-disruption baseline (`REPAIR_EXPECTATIONS["baseline_offer_quantities"]` / `["baseline_manufacturing_quantities"]`), returning `None`→score 0 if any PO can't be resolved to a legal offer or any MO lacks a workcenter (`checks.py:1047-1085`). "Least disruption" becomes a number.

There is also a floor against underspending your way to a high score:
```python
def spend_floor():
    if OBJECTIVE_KIND != "min_new_spend": return True
    return _spend_breakdown()["total_new_spend"] >= EXPECTED_SPEND - SPEND_TOLERANCE
```

**Traceability** (`hygiene`) is a *flow feasibility* problem, not a string match. `po_origin_traceability(product_code, supply_role)` collects the origin tokens on each relevant PO, computes a `required_covered_qty` per PO, and then runs `_traceability_capacity_feasible(supply_rows, demand_by_name)` — a bipartite feasibility check that the claimed origins can actually absorb the purchased quantity. When the route is unused entirely it returns `NOT_APPLICABLE` (`checks.py:2478-2540`). `mrp_origin_traceability` does the same for MOs, recursing through component consumers.

**Blast-radius / side-effect control:**
```python
def adjacent_data_untouched():
    adj_pids = {…ADJACENT_PRODUCT_CODES…}; adj_vids = {…ADJACENT_PARTNER_REFS…}
    if adj_vids and M("sale.order").search(domain=[("partner_id","in",list(adj_vids)),("state","!=","cancel")]): return False
    if adj_pids and M("sale.order.line").search(domain=[("product_id","in",list(adj_pids))]): return False
    if adj_vids and M("purchase.order").search(domain=_live_po_domain(("partner_id","in",list(adj_vids)))): return False
    if adj_pids and M("purchase.order.line").search(domain=[("product_id","in",list(adj_pids))]): return False
    if adj_pids and M("mrp.production").search(domain=_live_mo_domain(("product_id","in",list(adj_pids)))): return False
    return True
```
50 decoy vendors + 50 decoy customers + 50 decoy products + ~10 decoy BOMs per task exist **specifically so this check can catch collateral damage**.

Other notable rules, one line each: `po_consolidation_compliance` (≥2 POs on the same `offer_key` ⇒ fail); `po_min_qty_compliance` (a PO qty below every tier's `min_qty` ⇒ unresolvable ⇒ fail); `po_price_tier_compliance` (`abs(price_unit - tier) > max(0.02, tier*1e-4)` ⇒ fail); `po_delivery_schedule_compliance` (planned date must be ≥ vendor lead time *and* ≤ the need date of every origin it claims); `assembly_capacity_compliance` (minutes per workcenter ≤ `WORKCENTER_CAPACITY_MINUTES` + 0.01); `finished_vendor_max_qty_compliance` / `component_vendor_max_qty_compliance` (against limits that exist **only in free-text Internal Notes** — see §6.2); `finished_stock_capacity_compliance` (implied stock draw = demand − purchased − produced must fit on hand); `forbidden_finished_po_absent` / `forbidden_finished_mo_absent` (route prohibitions); `repair_state_compliance` (every `broken_*_ref` must end in state `cancel`, and no live MO may sit on `broken_workcenter_code`).

### 4.4 How finance-world's verifiers compare

| Dimension | ERP-Bench | finance-world (current plan, `research/harbor-format.md`) |
|---|---|---|
| Reward | 0–100 float, weighted 25/60/15, `passed >= 99` | binary 0/1, "multi-probe, ALL must pass" |
| Gating | constraints gate optimality+hygiene; separate hard-zero no-op gate | all-probes-AND (equivalent to a single gate) |
| Optimality | continuous, exponential decay vs CP-SAT optimum | none (no optimization tasks yet) |
| Non-applicability | explicit `NA`, excluded from denominator | — |
| Diagnosis | `rule_results.tsv` + `reward.json.rules.failed_rules` with parsed args | `checks.json` |
| Blast radius | `adjacent_data_untouched` over 150 decoys | state-diff vs `db_baseline.sqlite` |
| Anti-gaming | re-price against tier table; `verified_spend_complete`; `spend_floor`; hard no-op gate | ship-honest replay; multi-probe (single-probe gaming already burned them) |

**Takeaways to import:** (a) the `NA` third state; (b) per-rule TSV/JSON telemetry with parsed args; (c) `and_aspect` vs `sum_aspect` as an explicit authoring choice per cluster; (d) recompute money from primitives rather than trusting a stored total; (e) a decoy-untouched hygiene check; (f) an explicit no-op hard gate for tasks whose correct answer is mostly "do nothing / cancel".

---

## 5. `schemas/` and `agents/`

**`schemas/`** — four files (`__init__.py`, `models.py`, `procurement_invoicing_validation.py`, `schema.json`). `schemas/models.py` (426 lines) holds **all 16** Pydantic scenario models: `VendorData` (:14), `CustomerData` (:23), `ProcurementInvoicingPolicyData` (:47), `WarehouseData` (:86), `VendorInfoData` (:100), `ProductData` (:116), `BOMComponentData` (:138), `BOMData` (:145), `WorkcenterData` (:158), `StockLevelData` (:201), `ExistingPurchaseOrderData` (:212), `ExistingManufacturingOrderData` (:249), `ExistingSalesOrderData` (:284), `ProcurementRepairData` (:305), `SystemParameterData` (:344), and the top-level `ScenarioData` (:351). Note that three of those — `ExistingPurchaseOrderData`, `ExistingManufacturingOrderData`, `ProcurementRepairData` — are exactly the models with **no counterpart in `schema.json`**, which is the §8 staleness finding stated from the Pydantic side. `schemas/schema.json` is the exported JSON Schema (`title: "ScenarioData"`, `required: [scenario_number, name, instruction, customers, products]`). `schemas/procurement_invoicing_validation.py` is one shared validator reused by *both* the config layer and the data layer (`erp_bench/procurement/config.py:12` imports it) — one rule, two enforcement points, no drift.

Field details worth copying into finance-world's own schema: `VendorInfoData.max_qty: float | None` is described as *"Maximum order quantity supported by this vendor (None means unbounded)"* — it exists in the schema but has **no Odoo counterpart**, which is precisely why it becomes free text (§6.2). `CustomerData` carries both `budget_dollars` (task-invented) and `credit_limit` (*"native Odoo field"*) — a clean separation of benchmark-only vs system-native fields.

**`agents/`** — the harness contract, not a task artifact. `agents/pi.py` subclasses harbor's `BaseInstalledAgent`: `install()` clones `github.com/agentic-labs/pi-mono`, builds, `npm install -g ./packages/coding-agent`; `run()` shells `pi --print --mode json --no-session --provider <p> --model <m> [--thinking off|minimal|low|medium|high|xhigh] [--max-turns N] '<instruction>' | tee /logs/agent/pi.txt`; `populate_context_post_run()` parses the JSONL for `message_end` events and accumulates `usage.{input,output,cacheRead,cacheWrite}` + `cost.total` into harbor's `AgentContext`. Provider→env-key map covers anthropic / openai / google / xai / groq / mistral / fireworks / openrouter / huggingface / github-copilot / amazon-bedrock. There's also a skills hook: `_build_register_skills_command` copies `self.skills_dir` into `$HOME/.agents/skills`.

`agents/pi_browser_use.py` (Playwright/chromium extension) and `agents/pi_computer_use.py` (Xvfb + fluxbox + chromium at 1024×768, with `PI_COMPUTER_USE_*_DELAY_MS` knobs) are the **UI-modality agents** — they exist to run `tasks_ui/`. `agents/task-reviewer.md` is a Claude-style subagent spec (see §1.4).

Harbor invocations documented in `README.md:66-93`: `harbor run -p tasks/<task> -a oracle --env daytona` · `-a nop` · `harbor run -p tasks -a oracle --env daytona -n 10` · `--env docker` local fallback · `-a claude-code -m claude-sonnet-4-5-20250929`.

---

## 6. What ports to finance-world, and what doesn't

### 6.1 Portable (methodology, verbatim-adaptable)

| Idea | ERP-Bench form | finance-world (D365/QBO/sheets/email) form |
|---|---|---|
| One solved spec compiles all four artifacts | `_build_template_context(scenario, plan, blueprint)` shared by instruction/verifier/oracle | one task-spec object feeding instruction.md, seed.db, trace.json, checks |
| Optimality certification + resample | CP-SAT OPTIMAL or reject, 150 attempts | any task with a *computed* answer: reject if the generator can't prove uniqueness/optimality |
| **Objective non-collapse gate** | `_objective_family_certified` re-solves with spend pinned | reject a task whose answer equals the naive-heuristic answer (e.g. "pay the largest invoice first" gives the same set as the discount-optimal set) |
| Relative dates anchored at setup | `_scenario_anchor_date()` from sentinel mtime | anchor aging/due-date tasks on DB build time; never bake absolute dates |
| Opaque per-scenario ref namespacing | `blake2s(f"{n}:{channel}")[:5]`, different token for decoys | prevents "the relevant records are the ones with pretty names" |
| Decoy volume + `adjacent_data_untouched` | 150 unrelated entities/task | 50 unrelated customers/vendors/invoices per task + a blast-radius check |
| Three-state rule results (`PASS/FAIL/NA`) | dispatcher protocol | same |
| `and_aspect` vs `sum_aspect` clusters | bash combinators | encode per-cluster in `checks.json` |
| Per-rule telemetry | `rule_results.tsv` + `reward.json.rules` | emit the same; it makes failure triage cheap |
| Recompute money from primitives | tier-price re-derivation, `verified_spend_complete` | recompute balance/aging from `cust_trans` ± settlements; never trust a stored `balance` |
| Hard no-op gate | `has_relevant_activity` → `HARD_SCORE_GATE_OK=0` | mandatory for "which invoices to write off / which to leave" tasks |
| Setup-artifact deletion | `rm /setup/scenario_data.json` in entrypoint | delete any ground-truth JSON from the image after seeding |
| Content digests per task | `tasks/dataset.toml` sha256 per task | add digests to the exporter; detect silent drift |
| Reference/oracle as replay script | `SOLVER_PLAN` baked into `solution/solver.py` | already the blobfish `trace.json` replay pattern |
| "Execution autonomy" boilerplate | fixed paragraph in every instruction | one shared block; prevents "should I ask?" failure mode |
| Dual-modality tasks | `tasks/` (API) vs `tasks_ui/` (browser) from one spec | a "portal" modality later, if ever |

Directly analogous *objective families* for a finance world: `min_new_spend` → minimize discount forfeited / minimize late fees; `vendor_consolidation` → minimize number of payment runs or wire fees; `capacity_preservation` → minimize cash drawn from a facility / preserve a covenant headroom; `repair_plan` → **re-plan a payment run after a bank rejects a batch or a customer disputes an invoice** (least-disruption re-allocation, scored by L1 distance from the approved run); `constraint_only` → pure policy compliance.

### 6.2 The chaos patterns (all verified, all portable)

| Pattern | Evidence | Finance-world analogue |
|---|---|---|
| **A hard constraint that exists only in free text.** Odoo's `product.supplierinfo` has no `max_qty`, so the generator writes `f"Maximum order quantity for {code}: {int(mq)} units"` into `res.partner.comment` (Internal Notes) and the verifier enforces it. | `erp_bench/templates/procurement/supply_planning/setup_scenario.py.jinja2:986-1008`; instruction warns *"no `max_qty` field exists — read vendor capacity limits from `res.partner.comment`"* (`instruction.md.jinja2`) | a credit-limit exception or a payment-hold reason that lives only in a customer note / an email thread, not in a field |
| **Capacity buried in a note.** Workcenter notes get appended `"Benchmark capacity rule: hard horizon-wide limit shared across all products using this workcenter."` + `"Benchmark capacity: {N} total processing minutes across the scenario horizon."` | `setup_scenario.py.jinja2:99-114` | approval-threshold or cash-limit stated in a policy memo, enforced by the grader |
| **Decoy entities in bulk.** 50 vendors + 50 customers + 50 products + ~10 BOMs per task, drawn from combinatorial name pools ("Precision Bearing Housing", "…Manufacturing HQ Procurement"), with plausible prices, stock and lead times. | `erp_bench/procurement/adjacent_data.py:245-423`, `item_count = 50` | 50 unrelated customers/vendors with real-looking aging |
| **Different namespace token for decoys.** Task refs `rD5BD7E1C25_c01`, decoys `r2EF13BB94B_p01` | `sampler.py:116-118` + `checks.py:103-120` | same trick on account numbers |
| **Draft documents already in the system.** Screened patterns seed draft SOs some of which *must* be cancelled. | `tasks/2060_.../instruction.md:26` "Some sales documents may already exist in draft; review existing documents before creating new ones" | pre-existing draft payment batches / unposted journal entries the agent must reconcile with |
| **Pre-committed state + a disruption.** 10 SOs + 22 POs + 4 MOs already confirmed; one workcenter down; notes on the records say so. | `tasks/2298_.../environment/scenario_data.json` `repair_context` | an approved payment run + a returned ACH + a disputed invoice |
| **Instruction-visible policy that contradicts the easy path.** e.g. `manufacture_only_no_available_vendors` — demand is visible, finished-goods vendors exist in the data but are not usable. | `examples/diverse_300/20_*.toml`, verifier `forbidden_finished_po_absent` | vendor exists but is on hold; the "obvious" payment path is blocked by policy |
| **Unsatisfiable demand as a first-class tag.** 77/300 tasks are `unsat_demand` — the correct answer includes rejections. | `category.py:110-112`; `sampler.py:2864-2880` | 77-style tasks where "the right answer is you cannot pay all of these" |
| **A control arm with no chaos.** Pattern 26 sets `include_adjacent_data = false`. | `examples/diverse_300/26_*.toml` | ship a clean-data control family to measure how much the chaos costs |
| **Ambiguity-resolution rule stated in the prompt.** "If multiple feasible plans satisfy the constraints, choose the one that best optimizes the stated objective." | every `instruction.md` | say it once, everywhere |

### 6.3 Odoo-specific (do not port)

- Every model/field name: `sale.order`, `sale.order.line`, `purchase.order(.line)`, `mrp.production`, `mrp.workorder`, `stock.move`, `stock.picking`, `account.move`, `account.payment.term`, `sale.advance.payment.inv`, `product.supplierinfo`, `res.partner`, `ir.config_parameter`.
- Odoo state machines: SO `draft→sale/done/cancel`, PO `draft→purchase→cancel`, MO `confirmed/progress/to_close/done`, `stock.move` `assigned/confirmed/partially_available/done`. The *shape* (draft → confirmed → posted, with cancel) is portable; the labels aren't.
- The JSON-2 API / `odoolib` access idiom, the API-key-via-`odoo shell` bootstrap, `FROM odoo:19` + postgres-18 image (~building a full ERP per task is why each task dir is ~350 KB of code and the image build budget is 600 s / 4 GB RAM / 3 CPU).
- Manufacturing semantics: BOMs, workcenter minutes, `time_efficiency`/`oee_target`, subassembly topologies. Finance-world has no BOM analogue; the *graph-with-capacity* shape maps loosely onto payment sequencing under a cash-balance constraint, but don't force it.
- CP-SAT itself is only needed where the answer is a genuine optimization. For AP/AR Q&A, a deterministic recomputation from the seed DB is the equivalent "certified oracle".

---

## 7. `tasks_ui/`: eval content or bloat?

**Both, and mostly bloat as shipped.** `tasks_ui/` contains the *same 300 task directories* as `tasks/`. Across 12 randomly sampled tasks, exactly **two files differ**: `instruction.md` and `task.toml`. `environment/*`, `tests/*`, `solution/*` are byte-identical.

- `instruction.md` swaps the API appendix for a browser appendix: *"Access Odoo in the browser at http://127.0.0.1:8069 … Login: admin / Password: pass"* and, critically, *"Interact with Odoo only through the web UI. Do not use Odoo models, direct database access, API calls, or scripts."* Then ~90 lines of UI walkthroughs (Sales / Contacts / Products / Purchase / Inventory / Invoicing) naming the actual buttons: `New`, `Save manually`, `Confirm`, `Validate`, `Create Invoice`, `Register Payment`, `Reset to Draft`.
- `task.toml` in `tasks_ui/` is a **different, older dialect**: `version = "1.0"` instead of `schema_version = "1.1"`, no `[task]` section, no `artifacts`/`allow_internet`/`mcp_servers`/`*.env` sections, `storage_mb = 4096` instead of 2048, and no trailing newline.
- `tasks_ui/` has **no `dataset.toml` and no `README.md`** (both present in `tasks/`), so it is not a publishable Harbor dataset.

Cost: `du -sh` → `tasks/` 107 MB and `tasks_ui/` 107 MB. **~107 MB (50 % of the repo) is a duplicate that differs by ~2 small files per task.** The correct design is one task tree plus a modality flag rendering a different instruction appendix — which is trivially available given both come from `instruction.md.jinja2`.

**Verdict for finance-world:** the *idea* is real eval content — same ground truth, same verifier, different interaction modality, which cleanly isolates "can the model do the business reasoning" from "can it drive this interface". Keep the idea, never the duplication. If finance-world ever ships a portal/UI modality, emit it as a variant at export time from one spec, or at minimum symlink the shared subtrees.

---

## 8. Doc-vs-shipped disagreements (shipped data wins)

| Claim | Where | Shipped reality |
|---|---|---|
| "Extended Croissant metadata is provided in `croissant.json`… The RAI-only overlay is also available in `croissant_rai.json`." | `erp-bench/README.md:31` | **Neither file exists** in the checkout (repo root has only `README.md`, `LICENSE`, `pyproject.toml`, `uv.lock`, `.env.example`, `.gitignore`, `.python-version` + 4 dirs). |
| `schemas/schema.json` is the ScenarioData contract | `erp-bench/schemas/schema.json` | Its `properties` **omit** `existing_purchase_orders`, `existing_manufacturing_orders`, and `repair_context`, all of which are present in shipped `environment/scenario_data.json` for repair/screened tasks. The schema is stale relative to the data. |
| `task.toml` dialect | `tasks/` uses `schema_version = "1.1"` | `tasks_ui/` uses `version = "1.0"` with a different key set — two dialects in one repo. |
| Install line `uv pip install "odoo-client-lib==2.0.0"` | `environment/Dockerfile:18-19` | `tests/test.sh:28` and `solution/solve.sh:22` both re-install `odoo-client-lib==2.0.2` at runtime, overriding the baked 2.0.0. |
| README run example `tasks/2000_easy_01_buy_only_baseline`, `tasks/2053_medium_07_…`, `tasks/2299_hard_repair_plan_hard` | `README.md:44-46, 70` | All three exist. ✅ |
| README "29 task patterns", "300 tasks" | `README.md:35-37` | Confirmed: 29 dataset entries summing to exactly 300; 300 task dirs. ✅ |

---

## 9. Open questions

- The Anchor paper itself is absent — the drift taxonomy, baselines, and reported model scores are **UNVERIFIED**. Worth fetching the paper if we want the framing language for finance-world's own writeup.
- No `pytest` suite is checked in despite `task-reviewer.md:52` telling reviewers to run `uv run pytest`; `pyproject.toml` dev-deps are only `ruff` + `ty`. **UNVERIFIED** whether tests exist upstream.
- No published `generation_metrics.json` in the repo, so the actual resample/discard rates for the shipped 300 (how often the optimality gate fired) are **UNVERIFIED** — `runner.py:96-132` (`_write_generation_metrics`) shows most of the schema (`pre_solver_discards` :120, `solver_discards` :121, `discarded_samples` :122, `resampled_tasks` :123), and `solve_status_counts` is declared at `runner.py:44` and assembled separately in the solver-trace payload at `:170` — but the artifact isn't committed. This would be the single most interesting number in the repo.
- No baseline agent scores are committed anywhere; we don't know how hard these actually are for a frontier model.
- Solve time limit is 5 s (×3 on retry) per phase (`solver.py:711, 763, 790`); for the 32-customer hard patterns it's **UNVERIFIED** whether that ever silently forces a resample rather than a genuinely hard instance.

---

## Evidence index

Generator: `erp-bench/erp_bench/generation/{cli,config,models,render,runner}.py` · `erp-bench/erp_bench/procurement/{category,config,presets,prompts,sampler,solver,topologies,product_domains,adjacent_data,procurement_objectives,procurement_qa_scenarios}.py` · `erp-bench/erp_bench/harbor.py`
Templates: `erp-bench/erp_bench/templates/procurement/supply_planning/{instruction.md,checks.py,test.sh,solver.py,solve.sh,setup_scenario.py}.jinja2` · `erp-bench/erp_bench/templates/shared/{Dockerfile,entrypoint.sh,task.toml}.jinja2`, `odoo.conf`
Configs: `erp-bench/erp_bench/procurement/examples/diverse_300_dataset.toml` · `.../diverse_300/*.toml` (26) · `.../repair_plan_{easy,medium,hard}.toml`
Schemas/agents: `erp-bench/schemas/{models.py,schema.json,procurement_invoicing_validation.py}` · `erp-bench/agents/{pi.py,pi_browser_use.py,pi_computer_use.py,task-reviewer.md}`
Tasks read end-to-end: `erp-bench/tasks/2001_easy_01_buy_only_baseline/*` · `erp-bench/tasks/2060_medium_07_screened_buy_only_mixed_seeded_invoicing/*` · `erp-bench/tasks/2298_hard_repair_plan_hard/*`
Manifests: `erp-bench/tasks/dataset.toml` · `erp-bench/tasks/README.md` · `erp-bench/README.md` · `erp-bench/pyproject.toml` · `erp-bench/LICENSE`
UI variant: `erp-bench/tasks_ui/2000_easy_01_buy_only_baseline/{instruction.md,task.toml}` (+ 12-task sample diff)

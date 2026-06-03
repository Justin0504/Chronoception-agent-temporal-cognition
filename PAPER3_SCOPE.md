# Paper 3 — *The Agentic Frontier* (scope, 2026-06-03)

Provisional title: **The Agentic Frontier: Spatiotemporal Cognition in LLM Agents**

Status: scope locked, framework derivation complete (FRAMING.md §14), experiments E6-E10 designed, implementation deferred.

## TL;DR

Paper 1 (this repo) bounds autonomous-agent deployment in **time** (the Augustine Problem). Paper 3 bounds it in **space** (the Cartographic Problem). Together they specify the **Agentic Frontier** — the joint $(T, S)$ region in which an agent can be deployed without compounding spatiotemporal cognition failures.

## Why this paper exists

Paper 1's Agentic Timeline Hypothesis (§9.4) bounds an agent's maximum viable deployment horizon $T_{\max}(A) \propto 1/\varepsilon(A)$. But every realistic long-horizon agent task — coding (SWE-Bench), web (WebArena), open-ended (GAIA, MLE-Bench) — is also a **spatial** task. The agent must navigate a codebase, a website, the open web. There is no a-priori reason to think the same agent that mis-perceives time correctly perceives space.

Paper 1's central theorem (CIT) says token-only loss has no gradient signal aligning external metrics with internal representations. The theorem is stated for $\tau_{\text{wall}}$ but the structural argument applies identically to any external metric — including spatial extent $\sigma_{\text{world}}$. So **chronoception fails for the same reason cartography fails**, and they fail jointly.

## The framework (FRAMING.md §14)

**Six Coordinates** (mirror Three Times):

| Axis pair | Symbol | Name |
|---|---|---|
| time, external | τ_wall | wall-clock time |
| time, internal | τ_step | policy invocation count |
| time, narrative | τ_self | agent's narrated work duration |
| space, external | σ_world | file-set / page-set / location-set agent has touched |
| space, internal | σ_visit | distinct-location count |
| space, narrative | σ_self | agent's narrated "where I've been" |

**Theorem 3 (SIT)**: token-only loss has zero gradient signal aligning **either** external coordinate (τ_wall **or** σ_world) with any internal representation. SIT generalises CIT (Paper 1, Theorem 1).

**Three Spatial Laws** (mirror L1/L2/L3):

- **SL1 Cartographic Parkinson** (β): trained agents fill spatial budgets; native agents do not.
- **SL2 Visit-Step Conflation** (SAR): under spatial budgets, agents silently degrade the budget into step terminators.
- **SL3 Cartographic Confabulation** (ξ = log10(σ_self/σ_world)): agents misreport where they have been.

**The Agentic Frontier**:
$$T_{\max}(A) \cdot S_{\max}(A) \leq C/\varepsilon_{ST}(A)$$

where ε_ST aggregates temporal and spatial calibration error.

## Connection to long-horizon agent benchmarks

| Benchmark | Temporal load | Spatial load | Dominant failure mode |
|---|---|---|---|
| METR HCAST | hours | small (single repo) | T-axis (Paper 1) |
| SWE-Bench Verified | tens of minutes | medium (codebase) | T+S joint partial |
| WebArena | minutes | large (multi-site) | S-axis dominant |
| GAIA | minutes-hours | open web | S-axis unbounded |
| MLE-Bench | days | large (ML pipeline) | T×S joint |

Paper 1's P12 explains the HCAST scaling curve mechanism. Paper 3's P13 (Agentic Frontier) explains the **shape** of the success-rate frontier across the joint plane.

## Five experiments (E6-E10)

### E6 — Spatial-CAR on SWE-Bench Lite
"Solve this issue while touching at most N files" for N ∈ {2, 5, 10, 30, unlimited}.
Measure SAR per agent. Expected: SAR ≪ 1, mirror of L2.
**Scaffold**: `scripts/run_e6_spatial_car.py`
**Cost**: ~$430 + 30 GPU-hours.

### E7 — Joint spatiotemporal budgets
"Complete in T minutes, visiting at most S pages."
Measure 4-cell table: respected (T+S, T-only, S-only, neither).
Expected: agents respect step count; ignore both budgets.

### E8 — Within-trajectory drift on long horizons
SWE-Bench Lite trajectory + mid-task probes ("how long?", "how many files?").
Measure ρ_t and ξ_t drift across t.
Tests pre-registered P8/P9 from §5.11.

### E9 — The Cartographic Tell (mirror of Injection Tell)
Audit closed-lab harnesses for spatial context injection:
- "current working directory" in IDE agents (Cursor, Copilot)
- "recently visited URLs" in browser agents
- system file-tree dumps in computer-use agents
Hypothesis: consumer harnesses inject spatial context at consumer-tier rate (≥80%).

### E10 — Agentic Frontier mapping
Grid: T ∈ {1m, 10m, 1h, 4h} × S ∈ {1, 5, 30, 200} = 16 cells per agent.
For each cell, measure success rate.
Fit constant-success contour. Expected: contour matches T·S = C/ε_ST(A).

## Total Paper 3 cost (rough)

| Item | Cost |
|---|---|
| E6 SWE-Bench Lite, 9 agents | $430 + 30 GPU-h |
| E7 joint budgets, 9 agents | $300 |
| E8 within-trajectory drift | $200 |
| E9 Cartographic Atlas audit | $0 (manual prompt-leak audit) |
| E10 Frontier mapping | $500 |
| **Total** | **~$1430 + 30 GPU-h** |

## Connection to world-models literature

A trivial corollary of SIT: agents lacking spatiotemporal cognition cannot acquire useful world models from token-only training. The world model literature (PlaNet, MuZero, DreamerV3) builds explicit spatiotemporal representations because they cannot be acquired from token streams.

Paper 3 connects:
- LLM-only agents (token loss → SIT → no world model)
- Hybrid agents (LLM + scaffolded world model)
- World-model-first agents (foundation world models, e.g., Genie)

## Two-paper arc → Three-paper arc

| Paper | Title | Scope |
|---|---|---|
| 1 | The Augustine Problem | chronoception, CIT, Reverse-Scaling, Agentic Timeline |
| 2 | ChronoStack | constructive installation routes for chronoception |
| 3 | The Agentic Frontier | spatiotemporal generalisation, Cartographic Problem, Frontier |

## Why this is the right next paper

1. **Theorem 3 (SIT) makes CIT a one-axis instance of a deeper structural claim** — strengthens the theoretical core.
2. **Paper 3 connects directly to where the field actually deploys agents** (SWE-Bench, WebArena, GAIA) — practical leverage.
3. **The Cartographic Tell is an empirically free audit** — high signal, near-zero cost.
4. **The Agentic Frontier hypothesis is the field's missing structural account of why long-horizon benchmarks saturate** — directly addresses the most actively-studied question in agent capability research.
5. **Paper 3 + Paper 1 → joint deployment bound** — gives industry a quantitative answer to "what's the realistic deployment ceiling for current agents?"

## Status as of 2026-06-03

- [x] Framework derivation (FRAMING.md §14)
- [x] §12 Future Work written into Paper 1 (paper1/arxiv-v0/sections/12_future_work.tex)
- [x] Paper 3 scope locked (this document)
- [x] E6 scaffold (scripts/run_e6_spatial_car.py)
- [ ] E7-E10 scaffolds
- [ ] Actual experiments (deferred until after Paper 1 submission)
- [ ] Paper 3 draft

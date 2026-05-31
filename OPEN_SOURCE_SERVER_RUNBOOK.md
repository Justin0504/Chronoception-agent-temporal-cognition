# Open-Source Model Server Runbook

**Status**: v1 (2026-05-31)
**Purpose**: Bring up an OpenAI-compatible vLLM server on Delta, Jetstream2, or Yi Nian's lab server, then point `scripts/run_pilot.py` at it to run ChronoBench on open-weight models.

This file is the recipe. The framework is described in [`FRAMING.md`](FRAMING.md); the pilot scope is in [`PHASE2_PILOT_PLAN.md`](PHASE2_PILOT_PLAN.md).

---

## 1. Why test open-source models

Three reasons, in order of importance:

1. **Clean Setting A baseline.** OpenAI silently injects today's date into GPT-5.1 (see [`paper1/injection-atlas.md`](paper1/injection-atlas.md) §A.0). Anthropic and Google likely do the same. Open-source models running on our own servers have **no provider-side injection** — they are the only true "Setting A no_injection" baseline available.

2. **Cross-architecture robustness.** The framework predicts L1/L2/L3 hold regardless of architecture. Testing transformer (Llama), MoE (DeepSeek-V3.2), and dense reasoning (Qwen3) models with the same finding strengthens the universality claim. A reviewer cannot dismiss it as an OpenAI-specific quirk.

3. **Free compute.** Delta and Jetstream2 are allocated to the lab; running models there has zero marginal cost beyond setup time.

## 2. Server inventory

| Server | Hostname | User | When to use | Capabilities |
|---|---|---|---|---|
| **Jetstream2** | jetstream2.indiana.edu | (USC NCSA project) | Dev work, smoke tests, up to ~30B models | 1× A100 80GB typical |
| **Delta** | login.delta.ncsa.illinois.edu | ayuan | Production runs, ≥70B models | A100 80GB, 608 GPU·hr remaining on bfsl-delta-gpu |
| **Yi Nian lab** | 10.136.20.188 | haiyuez | Auxiliary; **only if Delta/JS2 unavailable** (per project_chronoception_augustine: this server is restricted to non-HBM work; chronoception qualifies but be courteous to other lab members) | TBD GPU |

Credentials live in your shell history / password manager — **not in this file or any git-tracked file**.

## 3. Model recommendations

| Tier | Model | Size | Reasoning? | Why |
|---|---|---|---|---|
| **Small dense** | `Qwen/Qwen3-8B` | 8B | No | Direct replication of Ma et al. (2026) "marginal increase" finding on the same model family |
| **Mid dense** | `meta-llama/Llama-3.3-70B-Instruct` | 70B | No | Frontier open non-reasoning baseline |
| **Open reasoning** | `Qwen/QwQ-32B-Preview` | 32B | Yes (reasoning) | Open reasoning model; matches o3 / o4-mini wedge |
| **MoE reasoning** | `deepseek-ai/DeepSeek-V3.2` | ~671B (sparse) | Yes | The model Ma et al. flagged as failing to honor wall-clock budgets |
| **Older base** | `meta-llama/Llama-3.1-8B-Instruct` | 8B | No | Older generation control for ε cross-generational scaling |

**Minimum useful panel**: Qwen3-8B + Llama-3.3-70B + QwQ-32B-Preview. Three models, three architectures, ~5 GPU-hours total.

## 4. Server startup — vLLM serve

vLLM exposes an OpenAI-compatible API endpoint, so the `OpenAIBackend` works against it without any code changes — just pass `--base-url` to `scripts/run_pilot.py`.

### 4.1 Jetstream2

SSH in (credentials live in your shell), allocate a node with GPU, then:

```bash
# In a tmux session on a GPU node
module load cuda/12.4 python/3.11    # adjust to whichever module set is current
python -m venv ~/vllm-venv
~/vllm-venv/bin/pip install vllm==0.6.4

# Serve Qwen3-8B on port 8000
~/vllm-venv/bin/python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3-8B \
    --port 8000 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.85 \
    --served-model-name qwen3-8b
```

Once you see `Application startup complete.`, the endpoint is at `http://<jetstream2-internal-ip>:8000/v1`. Use a port forward from your laptop:

```bash
# On your laptop
ssh -L 8000:<jetstream2-internal-ip>:8000 <user>@jetstream2.indiana.edu
```

Now the local URL `http://localhost:8000/v1` proxies to the running vLLM.

### 4.2 Delta (NCSA)

Per `project_usc_ncsa_delta` (memory): 608 GPU·hr remaining on `bfsl-delta-gpu`. Use sbatch.

```bash
# Submit an interactive job
srun -A bfsl-delta-gpu --partition=gpuA100x4 \
    --gres=gpu:a100:1 --time=04:00:00 --mem=128G --pty bash

# Inside the job (Delta has its own Python)
module load python/3.11 cuda/12.4
python -m venv ~/vllm-venv
~/vllm-venv/bin/pip install vllm==0.6.4

# Serve Llama-3.3-70B on port 8000
~/vllm-venv/bin/python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.3-70B-Instruct \
    --port 8000 \
    --max-model-len 4096 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.92 \
    --served-model-name llama-3.3-70b
```

70B on a single A100 80GB requires int4 or int8 quantization. For full precision, allocate 2-4 A100s with `--tensor-parallel-size 2` (or 4).

Forward the port to your laptop with `ssh -L`.

### 4.3 Yi Nian lab (10.136.20.188) — auxiliary

Only use if Delta and Jetstream2 are both occupied. The same vLLM commands work; allocate a node per the lab's queueing policy.

Per project memory: this server is shared with the not-all-thoughts-hbm project and was previously off-limits for that specific project. Chronoception is a different project and is acceptable, but courtesy: post in lab Slack before launching multi-GPU runs.

## 5. Running ChronoBench against a vLLM endpoint

Once vLLM is serving at `http://localhost:8000/v1`, on your laptop:

```bash
cd ~/chronoception
set -a; source .env; set +a   # picks up OPENAI_API_KEY (not needed but harmless)

.venv/bin/python scripts/run_pilot.py \
    --backend openai \
    --model qwen3-8b \
    --base-url http://localhost:8000/v1 \
    --agent-id-override oss/qwen3-8b-jetstream2 \
    --capability T1.1,T2.3,T3.1 \
    --setting no_injection,with_injection \
    --count 30 \
    --output-dir pilot-results/
```

Key flags:

- `--base-url http://localhost:8000/v1` — routes to your vLLM, not OpenAI's API.
- `--model qwen3-8b` — the `--served-model-name` you gave vLLM (NOT the full HF id).
- `--agent-id-override oss/qwen3-8b-jetstream2` — controls the output directory. Use the form `oss/<short-model-id>-<server>` so trajectories from different servers are distinguishable in `pilot-results/`.
- `--count 30` — same as your OpenAI runs, for direct comparability with the existing panel.

The trajectories land in `pilot-results/oss/qwen3-8b-jetstream2/T1.1/...`, fully compatible with `scripts/compute_metrics.py`.

## 6. Cost-aware execution order

Recommended sequence:

1. **Smoke test (1 trajectory)**: verify endpoint, parser, and trajectory shape. ~1 minute.
2. **T1.1 only × A/B × 5 instances** (~10 trajectories): confirms Setting A behavior without provider injection. ~5 minutes.
3. **Full pilot × 30 instances** (180 trajectories): same as OpenAI panel. ~30 minutes per 8B model, ~90 minutes per 70B model on a single A100.

The 70B model is the most expensive in wall-clock time, not dollars. If GPU-hours are tight, prioritize Qwen3-8B + QwQ-32B and skip the 70B.

## 7. Per-server resource notes

| Server | Max single-GPU model | TP=2 max | TP=4 max | Notes |
|---|---|---|---|---|
| Jetstream2 (1× A100 80GB) | ~30B FP16, 70B int4 | — | — | Dev tier |
| Delta (4× A100 80GB allocatable) | 70B FP16 on TP=2 | 100B FP16 | 175B INT8 | Use sbatch; don't hog interactive |
| Yi Nian lab | TBD | TBD | TBD | Check `nvidia-smi` before launching |

For DeepSeek-V3.2 (671B sparse MoE): typically requires 8× H100 or 16× A100 in production. Skip unless lab has Together AI / DeepSeek API credit (cheaper than self-hosting).

## 8. What to record in addition to trajectories

For each open-source run, record one extra file `pilot-results/<agent_id>/MODEL_META.json`:

```json
{
  "model_id_huggingface": "Qwen/Qwen3-8B",
  "model_revision": "<commit hash from HF>",
  "served_model_name": "qwen3-8b",
  "server": "jetstream2",
  "vllm_version": "0.6.4",
  "gpu": "A100 80GB",
  "max_model_len": 4096,
  "tensor_parallel_size": 1,
  "quantization": "none",
  "run_date_utc": "2026-05-31T..."
}
```

This makes the open-source results exactly as reproducible as the OpenAI results — readers can pull the same revision and serve it themselves.

## 9. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `Connection refused` from CLI | vLLM crashed or wrong port | `nvidia-smi` on the server; restart vLLM in a new tmux pane |
| 400 `Bad Request` on first call | Model name mismatch | Use the value passed to `--served-model-name`, not the HF id |
| OOM on model load | GPU memory too small | Lower `--gpu-memory-utilization` to 0.85; reduce `--max-model-len` |
| Trajectories have empty `action` | vLLM returned a structured response not text | Pass `--extra-body '{"chat_template":"default"}'` or check the model's tokenizer config |
| Setting B behaves like Setting A | Open-source models don't auto-recognize "Current date and time" in system prompt | This is expected — they don't have provider injection. The contrast is still meaningful |
| All trajectories report training cutoff date | Open-source model has no time access | Expected and correct — this IS the no-injection baseline |

## 10. Coordination with the existing panel

`scripts/compute_metrics.py` reads `pilot-results/` and groups by `agent_id`. As long as the open-source runs land under `pilot-results/oss/<model-id>/...`, the metric tables and ε comparisons will include them automatically alongside `openai/...` and `anthropic/...` runs.

After each open-source model finishes, push to git:

```bash
git add pilot-results/oss/<model-id>/
git commit -m "pilot/oss: <model> on <server> complete (<N> trajectories)"
git push
```

Justin's `compute_metrics.py` will then show the open-source models in the merged table.

## 11. Quick checklist

```
[ ] Decide which server (Jetstream2 → Delta → Yi Nian, in that order)
[ ] SSH in, allocate GPU
[ ] Install vLLM in a venv
[ ] Start vLLM with --served-model-name set
[ ] Port-forward to laptop
[ ] On laptop: scripts/run_pilot.py --base-url ... --agent-id-override oss/<...>
[ ] Verify 1 trajectory looks sane
[ ] Run full pilot (30 instances × 3 cap × 2 setting = 180 trajectories)
[ ] Commit MODEL_META.json + trajectories
[ ] Run scripts/compute_metrics.py to confirm new model appears
```

## Changelog

- **v1 (2026-05-31)** — Initial runbook. Three server inventory (Jetstream2 / Delta / Yi Nian), five model recommendations (Qwen3-8B, Llama-3.3-70B, QwQ-32B-Preview, DeepSeek-V3.2, Llama-3.1-8B), per-server startup commands for vLLM, full ChronoBench routing through `OpenAIBackend(base_url=...)`, MODEL_META.json schema for reproducibility, and a 10-failure-mode lookup table.

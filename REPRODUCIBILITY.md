# Reproducibility

Three ways to reproduce the paper's empirical content, depending on how much you want to re-run.

## A. Re-render figures from committed trajectories (no API, no GPU, ~5 minutes)

Reproduces all four paper figures (Figure 0–3) and the metric tables from the trajectory JSONs committed in this repository. No external services touched.

### Option A1 — Docker (recommended)

```bash
git clone https://github.com/Justin0504/Chronoception-agent-temporal-cognition
cd Chronoception-agent-temporal-cognition
docker build -t chronoception:repro .
mkdir -p repro_out
docker run --rm -v "$PWD/repro_out:/work/repro_out" chronoception:repro
```

The four PDFs and PNGs end up in `repro_out/figures/`. Metric CSVs end up in `repro_out/pilot-metrics.csv`, `e1-metrics.csv`, etc.

### Option A2 — Local venv

```bash
git clone https://github.com/Justin0504/Chronoception-agent-temporal-cognition
cd Chronoception-agent-temporal-cognition
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]" matplotlib

# Figures
.venv/bin/python scripts/make_three_times_figure.py
.venv/bin/python scripts/make_killer_figure.py
.venv/bin/python scripts/make_calibration_figure.py
.venv/bin/python scripts/make_epsilon_panel_figure.py

# Metrics
.venv/bin/python scripts/compute_metrics.py --input-dir pilot-results
.venv/bin/python scripts/analyze_e1.py --input-dir e1-results
```

Outputs replace `paper1/arxiv-v0/figures/*.pdf` and produce `*-metrics.csv` files.

## B. Re-run a single agent on ChronoBench (~$10 + ~30 min)

This re-collects trajectories rather than just re-rendering. Requires an OpenAI or Anthropic API key.

```bash
export OPENAI_API_KEY=sk-...    # or
export ANTHROPIC_API_KEY=sk-ant-...

.venv/bin/python scripts/run_pilot.py \
    --backend openai \
    --model gpt-5.1 \
    --capability T1.1,T2.3,T3.1,T1.2,T1.3,T2.1,T2.2,T3.2,T3.3 \
    --setting no_injection,with_injection \
    --count 30 \
    --output-dir my-pilot-results
.venv/bin/python scripts/compute_metrics.py --input-dir my-pilot-results
```

## C. Re-run the full sweep (10 agents, 4000+ traj, ~$50 + 1-2 days)

Identical to (B) but iterated across the full panel. See [`scripts/`](scripts/) for the per-experiment launchers:

- `run_pilot.py` — single-agent pilot driver
- `run_e5_oss_reverse_scaling.sh` — OSS reasoning model sweep (requires a vLLM-served reasoning model)
- `deploy_oss_reasoning.sh` — vLLM deployment helper for a GPU server with SSH access

Open-source self-hosted models require GPU compute. The original work used the Yue Zhao lab cluster (8× RTX 6000 Ada) for DeepSeek-R1-Distill-Qwen-14B; a single A40 (48GB) is sufficient for Qwen2.5-7B.

## Figure 4 (P12 HCAST) data

Figure 4 uses the publicly-available METR HCAST runs from <https://github.com/METR/eval-analysis-public>. To reproduce:

```bash
cd /tmp && git clone --depth 1 https://github.com/METR/eval-analysis-public.git
cd -
.venv/bin/python scripts/make_hcast_p12_figure.py
```

## Determinism

- Trajectory generators (`chronoception/bench/tasks/instances.py`) are deterministic given a `seed=0` (the default used by `run_pilot.py`).
- API calls are stochastic at temperature > 0. Closed-source models do not expose seeded sampling. Re-running (B) or (C) will produce numerically different individual trajectories but the same panel-level ranking (Theorem 1 + Theorem 2 imply that the qualitative findings are scale-invariant).

## Environment pins

`pyproject.toml` pins the Python dependencies. The Docker image pins the OS + Python version. The OSS deployment script pins the specific vLLM / nvjitlink / cusparse versions known to work (matched to the Yue Zhao server's CUDA installation).

## Citation

If you reproduce this work, please cite the paper (forthcoming) and reference the locked pre-registration in [`OSF_PREREGISTRATION.md`](OSF_PREREGISTRATION.md).

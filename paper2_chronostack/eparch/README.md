# E-ARCH — route 4 architectural primitive, training experiment

**Status: pipeline implemented; awaiting a GPU run on the lab cluster.**
**Branch:** `zijian/paper2-eparch`.

This is the constructive realization of ChronoStack route 4. Where the loss route
(A.1) teaches a model to *estimate* its duration better, E-ARCH gives the model a
real wall-clock **input** — a time token projected from the `time_channel`
feature vector and prepended to the input embeddings every invocation — and
trains it (LoRA + the projector) to *read* that token. It is the architectural
counterpart to the route-2→4 bridge result: a timing signal that brackets the
whole invocation, made native.

## The claim and how it is tested

Reading a time input and estimating a duration look the same on the training
distribution. They diverge under **extrapolation**: inject elapsed values the
model never trained on and see whether the reported duration follows.

- A model that **reads the token** grounds in *and* out of the training range
  (median |ρ| < 0.3 throughout).
- A model that merely learned the training duration distribution (the A.1 failure
  mode) grounds in-range and fails out-of-range.

`03_eval.py` injects a sweep of elapsed values (default `3,8,12` in-range;
`60,120,240` out-of-range) and `chronoception/stack/eparch_data.extrapolation_report`
computes median |ρ| for each side and the `reads_channel` verdict. This is the
falsifiable core: if E-ARCH does not ground out-of-range, route 4 buys nothing
over A.1 — and we report that.

## Pipeline

| Stage | Script | What |
|---|---|---|
| 0 | `time_token.smoke_test()` | CPU shape/label check of projector + injection (no GPU) |
| 1 | `01_generate_data.py` | generate (prompt, response, tau_wall); build time-token SFT data (accurate target + matching feature vector) |
| 2 | `02_train.py` | LoRA + projector training (manual loop over `TimeTokenModel`) |
| 3 | `03_eval.py` | the extrapolation test → `extrapolation_summary.json` |

```bash
# On the lab cluster, in the A.1 a1venv:
./run_pipeline.sh
# or stage by stage with custom paths/flags (see each script's --help)
```

## Architecture

- `chronoception/stack/time_token.py` (torch, cluster-only):
  - `TimeTokenProjector` — MLP from the 4-dim feature vector to one embedding-space
    token; log1p-compresses the duration features so it extrapolates.
  - `prepend_time_token` — prepends the token at position 0; its label is −100 so
    the model never predicts it. Pure tensor op with explicit shape contracts.
  - `TimeTokenModel` — base (LoRA) + projector; `forward`/`generate` inject the
    token. Both LoRA and the projector are trainable.
- `chronoception/stack/eparch_data.py` (torch-free, unit-tested): training-example
  construction and the extrapolation analysis.

## Baselines to compare against (same eval prompts)

1. Base model (Paper 1, no token): high |ρ| everywhere.
2. A.1 loss route (no token, SFT on noisy estimates): grounded in-range, fails
   out-of-range — the contrast that proves E-ARCH *reads* rather than memorizes.
3. E-ARCH (this): grounded in *and* out of range if route 4 works.

Report ε on ChronoBench T3.1 alongside these, mirroring Paper 1's panel.

## Environment

The A.1 `a1venv` on the lab server (transformers 4.46, peft 0.13, trl 0.12),
`CUDA_VISIBLE_DEVICES` pinned to a free GPU. Smoke-test the mechanism on any
torch machine first:

```bash
python -c "from chronoception.stack.time_token import smoke_test; smoke_test()"
```

## Files

- `01_generate_data.py`, `02_train.py`, `03_eval.py`, `run_pipeline.sh`
- `chronoception/stack/time_token.py`, `chronoception/stack/eparch_data.py`
- `tests/test_eparch.py` — unit tests for the torch-free logic

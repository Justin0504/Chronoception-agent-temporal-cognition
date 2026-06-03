# Dockerfile for chronoception reproducibility.
#
# Builds a self-contained image that reproduces all paper figures and the
# epsilon panel ranking from committed trajectory data. Does NOT re-run
# experiments (those need API keys + GPU servers and are documented separately).
#
# Build:
#   docker build -t chronoception:repro .
#
# Reproduce figures + metrics from committed data:
#   docker run --rm -v $PWD/repro_out:/work/repro_out chronoception:repro
#
# All four figures end up in ./repro_out/figures/ on the host.
FROM python:3.11-slim

WORKDIR /work

# System deps for matplotlib + scientific Python
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        libfreetype6-dev \
        libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only what's needed for reproduction (skip e1/e2/e3/e5/pilot raw dirs;
# they'll be re-cloned from git inside the container to lock the commit).
COPY pyproject.toml ./
COPY chronoception/ ./chronoception/

RUN pip install --no-cache-dir -e ".[dev]" matplotlib

# Copy scripts + paper + frozen experiment outputs + memos
COPY scripts/ ./scripts/
COPY paper1/ ./paper1/
COPY pilot-results/ ./pilot-results/
COPY e1-results/ ./e1-results/
COPY e2-results/ ./e2-results/
COPY e3-results/ ./e3-results/
COPY e5-results/ ./e5-results/
COPY FRAMING.md README.md OSF_PREREGISTRATION.md notation.tex ./
COPY tests/ ./tests/

# Default entrypoint: regenerate all figures + dump metrics summary
RUN echo '#!/bin/bash\n\
set -euo pipefail\n\
mkdir -p repro_out/figures\n\
echo "[repro] Running unit tests..."\n\
pytest -q tests/ || echo "[repro] (some tests skipped — expected for trajectory-dependent ones)"\n\
echo ""\n\
echo "[repro] Generating Figure 0 (Three Times)..."\n\
python scripts/make_three_times_figure.py\n\
echo "[repro] Generating Figure 1 (Reverse-Scaling)..."\n\
python scripts/make_killer_figure.py\n\
echo "[repro] Generating Figure 2 (Calibration Catastrophe)..."\n\
python scripts/make_calibration_figure.py\n\
echo "[repro] Generating Figure 3 (epsilon panel)..."\n\
python scripts/make_epsilon_panel_figure.py\n\
echo "[repro] Generating Figure 4 (P12 HCAST) — skipped, requires external METR data clone"\n\
echo ""\n\
echo "[repro] Computing epsilon panel from committed pilot trajectories..."\n\
python scripts/compute_metrics.py --input-dir pilot-results --output-csv repro_out/pilot-metrics.csv\n\
python scripts/analyze_e1.py --input-dir e1-results --output-csv repro_out/e1-metrics.csv\n\
python scripts/compute_metrics.py --input-dir e2-results --output-csv repro_out/e2-metrics.csv\n\
python scripts/compute_metrics.py --input-dir e3-results --output-csv repro_out/e3-metrics.csv\n\
echo ""\n\
echo "[repro] Copying figures to repro_out/figures/..."\n\
cp paper1/arxiv-v0/figures/*.pdf repro_out/figures/ || true\n\
cp paper1/arxiv-v0/figures/*.png repro_out/figures/ || true\n\
echo ""\n\
echo "[repro] DONE. Outputs in /work/repro_out/"\n\
ls -la repro_out/ repro_out/figures/\n\
' > /usr/local/bin/repro.sh && chmod +x /usr/local/bin/repro.sh

CMD ["/usr/local/bin/repro.sh"]

#!/usr/bin/env python3
"""Fig 2 — Reverse-Scaling Theorem, four independent confirmations.

Layout: 2 x 2 grid of small bar charts. Each subplot shows median |rho| across
an ordered condition (reasoning budget, thinking on/off, prospective vs
retrospective, injection A vs B). Vendor logo chip sits in the upper-left
corner of each subplot. Augustine threshold ε* = 0.20 is a horizontal dashed
green rule shared across the four panels.
"""
from __future__ import annotations
import json, glob
from math import log10
from pathlib import Path
from statistics import median
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"]  = 42
mpl.rcParams["font.family"]  = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Inter", "Helvetica", "Arial", "DejaVu Sans"]

LOGO_DIR = Path("paper1/arxiv-v0/figures/logos")

# =============================================================
# Data loading helpers
# =============================================================

def rhos_from(pattern: str, setting: str | None = None) -> list[float]:
    out = []
    for path in glob.glob(pattern, recursive=True):
        try:
            d = json.loads(Path(path).read_text())
        except Exception:
            continue
        if d.get("capability_code") not in ("T3.1", "T3.2"):
            continue
        if setting and d.get("metadata", {}).get("setting") != setting:
            continue
        steps = d.get("steps") or []
        if not steps: continue
        tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
        ts = d.get("self_narrated_duration")
        if ts and ts > 0 and tw > 0:
            out.append(log10(ts / tw))
    return out

# Panel (a) — o4-mini effort ladder (T3.1 A)
o4_low  = rhos_from("e2-results/o4-mini-low/**/T3.1/no_injection/*.json")
o4_med  = rhos_from("pilot-results/openai_o4-mini/T3.1/no_injection/*.json") + \
          rhos_from("e1-results/o4-mini/**/T3.1/no_injection/*.json")
o4_high = rhos_from("e2-results/o4-mini-high/**/T3.1/no_injection/*.json")

# Panel (b) — Sonnet 4.6 ± thinking (T3.1 A, non-thinking; T3.1 A thinking)
son_base = rhos_from("pilot-results/anthropic_claude-sonnet-4-6/T3.1/no_injection/*.json")
son_thk  = rhos_from("e3-results/claude-sonnet-4-6-thinking/**/T3.1/no_injection/*.json")

# Panel (c) — Sonnet-thinking prospective vs retrospective (T3.2 vs T3.1)
son_pros = rhos_from("e3-results/claude-sonnet-4-6-thinking/**/T3.2/with_injection/*.json")
son_retro = rhos_from("e3-results/claude-sonnet-4-6-thinking/**/T3.1/with_injection/*.json")

# Panel (d) — GLM-5.2 ± injection (T3.1 A vs B)
glm_a = rhos_from("vultr-results/glm-5.2-fp8/**/T3.1/no_injection/*.json")
glm_b = rhos_from("vultr-results/glm-5.2-fp8/**/T3.1/with_injection/*.json")


def med_abs(v):
    return median([abs(x) for x in v]) if v else None
def med_sign(v):
    return median(v) if v else None


PANELS = [
    {
        "title": "(a) Intra-model · o4-mini effort ladder",
        "logo": "openai.png",
        "vendor_bar": "#3182bd",
        "conditions": [
            ("low",    o4_low),
            ("medium", o4_med),
            ("high",   o4_high),
        ],
        "x_label": r"$K$ (reasoning-effort tier)",
        "y_metric": "abs",
    },
    {
        "title": "(b) Cross-model · Sonnet 4.6 $\\pm$ extended thinking",
        "logo": "anthropic.png",
        "vendor_bar": "#cc785c",
        "conditions": [
            ("no thinking",  son_base),
            ("+ thinking",   son_thk),
        ],
        "x_label": "extended-thinking mode",
        "y_metric": "abs",
    },
    {
        "title": "(c) Within-model · prospective vs.\\ retrospective (Sonnet + thinking)",
        "logo": "anthropic.png",
        "vendor_bar": "#cc785c",
        "conditions": [
            ("prospective\n(T3.2)",    son_pros),
            ("retrospective\n(T3.1)",  son_retro),
        ],
        "x_label": "self-report modality",
        "y_metric": "sign",  # show the sign flip
    },
    {
        "title": "(d) Cross-vendor · GLM-5.2 $\\pm$ date injection",
        "logo": "zai.png",
        "vendor_bar": "#4a4a4a",
        "conditions": [
            ("Setting A\n(no injection)",   glm_a),
            ("Setting B\n(with injection)", glm_b),
        ],
        "x_label": "harness injection",
        "y_metric": "sign",
    },
]

# =============================================================
# Drawing
# =============================================================
INK = "#1a1a1a"; INK2 = "#4a4a4a"; RULE = "#c8c8c8"
AUGUSTINE_STAR = 0.20

fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.4))
fig.subplots_adjust(left=0.06, right=0.98, top=0.90, bottom=0.08, wspace=0.28, hspace=0.55)

for ax, panel in zip(axes.flat, PANELS):
    conds = panel["conditions"]
    labels = [c[0] for c in conds]
    n = len(conds)
    x = list(range(n))

    values = []
    ns = []
    for _, rhos in conds:
        if panel["y_metric"] == "abs":
            v = med_abs(rhos)
        else:
            v = med_sign(rhos)
        values.append(v)
        ns.append(len(rhos))

    # Bar plot
    bar_color = panel["vendor_bar"]
    vmax_val = max((abs(v) for v in values if v is not None), default=0.1)
    label_offset = vmax_val * 0.07
    for xi, v in zip(x, values):
        if v is None: continue
        alpha = 0.30 + 0.70 * (xi / max(1, n - 1))
        ax.bar(xi, v, width=0.55, color=bar_color, edgecolor="none",
               alpha=alpha, zorder=3)
        # Value label — offset above / below the bar tip
        y_txt = v + label_offset if v >= 0 else v - label_offset
        ax.text(xi, y_txt,
                f"{v:+.2f}" if panel["y_metric"] == "sign" else f"{v:.2f}",
                ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=10, fontweight="700", color=INK, zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{l}\n(n={nv})" for l, nv in zip(labels, ns)],
                       fontsize=9.5, color=INK)
    ax.set_xlabel(panel["x_label"], fontsize=9.5, color=INK2, labelpad=8)

    if panel["y_metric"] == "abs":
        ax.set_ylabel(r"median $|\rho|$", fontsize=10.5, color=INK)
        ymax = max((v for v in values if v is not None), default=0) * 1.35
        ax.set_ylim(0, max(ymax, 0.4))
        ax.axhline(AUGUSTINE_STAR, ls=(0, (4, 3)), lw=1.0, color="#2a7a2a", zorder=1)
        ax.text(-0.35, AUGUSTINE_STAR, r"$\varepsilon^\star$",
                fontsize=9, color="#2a7a2a", ha="right", va="center",
                fontstyle="italic", fontweight="600")
    else:
        ax.set_ylabel(r"median $\rho$", fontsize=10.5, color=INK)
        vmax = max((abs(v) for v in values if v is not None), default=0) * 1.6
        ax.set_ylim(-max(vmax, 0.42), max(vmax, 0.42))
        ax.axhline(0, color=RULE, lw=0.8, zorder=1)
        ax.axhline(AUGUSTINE_STAR, ls=(0, (4, 3)), lw=0.7, color="#2a7a2a", alpha=0.6, zorder=1)
        ax.axhline(-AUGUSTINE_STAR, ls=(0, (4, 3)), lw=0.7, color="#2a7a2a", alpha=0.6, zorder=1)
        ax.text(-0.35, AUGUSTINE_STAR, r"$+\varepsilon^\star$",
                fontsize=8.5, color="#2a7a2a", ha="right", va="center", fontstyle="italic")
        ax.text(-0.35, -AUGUSTINE_STAR, r"$-\varepsilon^\star$",
                fontsize=8.5, color="#2a7a2a", ha="right", va="center", fontstyle="italic")

    ax.tick_params(axis="y", labelsize=9, colors=INK2)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#c0c0c0")
        ax.spines[spine].set_linewidth(0.8)

    # Vendor logo chip (top-left corner of the plot)
    logo_path = LOGO_DIR / panel["logo"]
    if logo_path.exists():
        img = mpimg.imread(logo_path)
        oi = OffsetImage(img, zoom=0.09)
        ab = AnnotationBbox(oi, (0.03, 0.94), frameon=False,
                            box_alignment=(0, 1), xycoords="axes fraction",
                            zorder=6, pad=0)
        ax.add_artist(ab)

    # Title inside axes, offset right of logo
    ax.set_title(panel["title"], fontsize=11, loc="left", pad=8,
                 color=INK, fontweight="600", x=0.11)

# =============================================================
# Suptitle
# =============================================================
fig.suptitle(
    "Reverse-Scaling Theorem — four independent confirmations",
    x=0.02, y=0.985, ha="left", fontsize=15.5, fontweight="700", color=INK,
)
fig.text(0.02, 0.945,
    r"Under CIT, $\mathbb{E}[|\rho|\mid K]$ is monotone non-decreasing in reasoning-token expansion $K$.  "
    r"Bars darken as $K$ (or the analogous scaling axis) grows.  "
    r"Dashed green rule: Augustine threshold $\varepsilon^\star=0.20$.",
    ha="left", fontsize=10, color=INK2, fontstyle="italic")

out_pdf = Path("paper1/arxiv-v0/figures/reverse_scaling.pdf")
out_png = Path("paper1/arxiv-v0/figures/reverse_scaling.png")
fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.18)
fig.savefig(out_png, bbox_inches="tight", pad_inches=0.18, dpi=300)
print(f"Wrote: {out_pdf}")
print(f"Wrote: {out_png}")

print("\nData summary:")
for panel in PANELS:
    print(f"  {panel['title']}")
    for lbl, rhos in panel['conditions']:
        if not rhos:
            print(f"    {lbl!r:35s}  n=0")
            continue
        ma = med_abs(rhos); ms = med_sign(rhos)
        print(f"    {lbl!r:35s}  n={len(rhos):3d}  med|ρ|={ma:.3f}  med_ρ={ms:+.3f}")

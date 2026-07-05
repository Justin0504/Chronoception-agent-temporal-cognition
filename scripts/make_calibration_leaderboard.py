#!/usr/bin/env python3
"""Calibration Catastrophe (T3.3) — leaderboard-style redesign.

Matches make_epsilon_leaderboard.py visual language:
  [ chip ]  Model   [ solid coverage bar | 90% target ]   width   width/actual   n
Bold value = best in column. Dashed green rule at 90% target.
The Sonnet+thinking outlier is annotated.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"]  = 42
mpl.rcParams["font.family"]  = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Inter", "Helvetica", "Arial", "DejaVu Sans"]

# ---- Data (from analyze_e1.py output + Sonnet-thinking back-parse) ----
ROWS = [
    # label, vendor, coverage%, width_s, actual_s, n_decided
    ("Grounded target (90%)",       "REF", 90.0, None, None, None),
    ("Claude Sonnet 4.6 + thinking","AN",  76.7, 13.0, 11.6, 30),
    ("Kimi-K2.6",                   "MS",  55.2, 14.0, 15.0, 30),
    ("o4-mini (reasoning)",         "OA",  50.0,  4.0,  5.7, 30),
    ("Claude Sonnet 4.6",           "AN",  43.3, 25.0,  6.6, 30),
    ("MiniMax-M2.7",                "MM",  33.3, 15.0, 17.2, 30),
    ("Qwen3.6-27B",                 "QW",  25.0, 11.0, 26.9, 30),
    ("o3 (reasoning)",              "OA",  17.2, 50.0,  4.5, 29),
    ("gpt-5.1",                     "OA",  13.3, 49.0,  2.3, 30),
    ("gpt-4o-mini",                 "OA",  10.0, 20.0,  3.2, 30),
    ("Claude Haiku 4.5",            "AN",   6.7, 30.0,  3.6, 30),
    ("gpt-4o",                      "OA",   0.0, 20.0,  1.9, 30),
]

LOGO_DIR = Path("paper1/arxiv-v0/figures/logos")
VENDOR = {
    "OA":  {"logo": LOGO_DIR / "openai.png",    "bar": "#3182bd"},
    "AN":  {"logo": LOGO_DIR / "anthropic.png", "bar": "#cc785c"},
    "QW":  {"logo": LOGO_DIR / "qwen.png",      "bar": "#6a4c93"},
    "DS":  {"logo": LOGO_DIR / "deepseek.png",  "bar": "#2b6cb0"},
    "ZAI": {"logo": LOGO_DIR / "zai.png",       "bar": "#4a4a4a"},
    "MS":  {"logo": LOGO_DIR / "moonshot.png",  "bar": "#2b2b2b"},
    "MM":  {"logo": LOGO_DIR / "minimax.png",   "bar": "#e94e77"},
    "REF": {"logo": None, "bar": "#c8c8c8"},
}
_LOGO_CACHE = {}
def get_logo(vk):
    if vk not in _LOGO_CACHE:
        p = VENDOR[vk].get("logo")
        _LOGO_CACHE[vk] = mpimg.imread(p) if (p and p.exists()) else None
    return _LOGO_CACHE[vk]

INK = "#1a1a1a"; INK2 = "#4a4a4a"; RULE = "#e6e6e6"; RULE_STRONG = "#c8c8c8"
BAR_MAX = 100.0   # coverage percent
TARGET  = 90.0    # 90% target
P11_THRESH = 50.0 # pre-registered P11 threshold

# ---- Layout ----
n_rows = len(ROWS)
row_h  = 0.62
fig_w  = 12.0
fig_h  = 2.0 + n_rows * row_h
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.07)
ax.set_xlim(0, 100); ax.set_ylim(0, n_rows + 1); ax.axis("off")

X_CHIP    = 3.5
X_MODEL   = 9.0
X_BAR0    = 34.0
X_BAR1    = 68.0
X_COV     = 74.0
X_WIDTH   = 82.0
X_RATIO   = 90.0
X_N       = 96.0

# Header
head_y = n_rows + 0.35
def head(x, txt, ha="right"):
    ax.text(x, head_y, txt, ha=ha, va="center",
            fontsize=9.5, color=INK2, fontweight="500")

head(X_MODEL, "Model", ha="left")
ax.text((X_BAR0+X_BAR1)/2, head_y,
        "Actual coverage of nominal 90% CI",
        ha="center", va="center", fontsize=9.5, color=INK2, style="italic")
head(X_COV,   "cov")
head(X_WIDTH, "CI width")
head(X_RATIO, "width/actual")
head(X_N,     "n")
ax.plot([2, 98], [head_y - 0.35]*2, color=RULE_STRONG, lw=0.7, zorder=0)

# Best-in-column tracking (excluding reference)
real_rows = [r for r in ROWS if r[1] != "REF"]
best_cov = max(r[2] for r in real_rows)
best_width = min(r[3] for r in real_rows if r[3] is not None)  # narrower = "worse", but ambiguous
# for the ratio, closer to ~2 (a healthy 90% ~ 2x median in log-normal) is arguably best; skip bolding

def cov_to_x(cov):
    return X_BAR0 + (cov / BAR_MAX) * (X_BAR1 - X_BAR0)

for i, (label, vk, cov, width, actual, n) in enumerate(ROWS):
    y = n_rows - i - 0.5
    is_ref = (vk == "REF")

    # Real logo (or Oracle chip fallback)
    img = get_logo(vk)
    if img is not None:
        oi = OffsetImage(img, zoom=0.10)
        ab = AnnotationBbox(oi, (X_CHIP, y), frameon=False, box_alignment=(0.5, 0.5),
                            xycoords=("data","data"), zorder=4, pad=0)
        ax.add_artist(ab)
    else:
        ax.add_patch(Circle((X_CHIP, y), 0.60, facecolor="#8a8a8a",
                            edgecolor="#5a5a5a", lw=0.5, zorder=3))
        ax.text(X_CHIP, y, "OR", ha="center", va="center",
                fontsize=8, color="white", fontweight="700", zorder=4)

    # Model
    color = "#3a3a3a" if is_ref else INK
    weight = "600" if is_ref else "500"
    style = "italic" if is_ref else "normal"
    ax.text(X_MODEL, y, label, ha="left", va="center",
            fontsize=11.5, color=color, fontweight=weight, fontstyle=style)

    # Bar rail
    ax.add_patch(Rectangle((X_BAR0, y - 0.20), X_BAR1 - X_BAR0, 0.40,
                           facecolor="#f4f4f4", edgecolor="none", zorder=1))
    # Coverage fill
    x_end = cov_to_x(cov)
    if is_ref:
        # dashed hollow rectangle out to 90%
        ax.add_patch(Rectangle((X_BAR0, y - 0.20), cov_to_x(TARGET) - X_BAR0, 0.40,
                               facecolor="none", edgecolor="#2a7a2a",
                               linestyle=(0, (3, 2)), lw=1.0, zorder=2))
        ax.text(cov_to_x(TARGET), y, "90%", ha="right", va="center",
                fontsize=9.5, color="#2a7a2a", fontweight="700", zorder=4,
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    else:
        # colour by coverage tier: >=P11 threshold green, else vendor color
        bar_col = "#2a7a2a" if cov >= P11_THRESH else VENDOR[vk]["bar"]
        ax.add_patch(Rectangle((X_BAR0, y - 0.20), x_end - X_BAR0, 0.40,
                               facecolor=bar_col, edgecolor="none", zorder=2))
        # label inside if room, else right
        val_txt = f"{cov:.0f}%"
        if (x_end - X_BAR0) > 6:
            ax.text((X_BAR0 + x_end) / 2, y, val_txt, ha="center", va="center",
                    fontsize=10, color="white", fontweight="600", zorder=4)
        else:
            ax.text(x_end + 0.6, y, val_txt, ha="left", va="center",
                    fontsize=10, color=INK, fontweight="600", zorder=4)

    # Numeric columns
    def cell(x, val, fmt, bold=False):
        if val is None:
            ax.text(x, y, "—", ha="right", va="center", fontsize=10, color="#9a9a9a")
        else:
            ax.text(x, y, fmt.format(val), ha="right", va="center",
                    fontsize=11, color=INK, fontweight="700" if bold else "500")

    cell(X_COV, cov, "{:.0f}%", bold=(not is_ref and cov == best_cov))
    cell(X_WIDTH, width, "{:.0f}s")
    cell(X_RATIO,
         (width/actual) if (width and actual) else None,
         "{:.1f}×")
    cell(X_N, n, "{:.0f}")

    if i < n_rows - 1:
        ax.plot([2, 98], [y - 0.5]*2, color=RULE, lw=0.5, zorder=0)

# P11 threshold marker
xP = cov_to_x(P11_THRESH)
ax.plot([xP, xP], [0.05, n_rows + 0.1], color="#c05d1e",
        ls=(0, (4, 3)), lw=0.9, zorder=5, alpha=0.7)
ax.text(xP, 0.15, "P11 threshold  0.5",
        ha="center", va="top", fontsize=8.5,
        color="#c05d1e", fontweight="600")

# Target marker
xT = cov_to_x(TARGET)
ax.plot([xT, xT], [0.05, n_rows + 0.1], color="#2a7a2a",
        ls=(0, (4, 3)), lw=1.1, zorder=5)

# Title / subtitle
fig.suptitle(
    "The Calibration Catastrophe: nominally-90% CIs on self-duration",
    x=0.02, y=0.975, ha="left", fontsize=15,
    fontweight="700", color=INK,
)
fig.text(0.02, 0.925,
    "Bars = actual coverage of the agent's stated 90% CI containing $\\tau_{\\rm wall}$.  "
    "Dashed green = 90% target.  Dashed orange = pre-registered P11 threshold (0.5).  "
    "Every non-thinking model under-covers by ≥40 percentage points; "
    "GPT-4o achieves 0%.",
    ha="left", fontsize=10, color=INK2, fontstyle="italic")

# Sonnet-thinking annotation
fig.text(0.995, 0.02,
    r"Note: Sonnet 4.6 + thinking approaches the 90% target with 77% coverage, "
    r"but the wider default CI (13 s vs 2–4 s baseline) reflects a broader vocabulary "
    r"rather than actual chronoception. See §6.3.",
    ha="right", va="bottom", fontsize=8.5, color="#7a3a1a", fontstyle="italic",
    wrap=True, transform=fig.transFigure,
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#fffaf0",
              edgecolor="#c05d1e", alpha=0.95, lw=0.7))

out_pdf = Path("paper1/arxiv-v0/figures/calibration_catastrophe.pdf")
out_png = Path("paper1/arxiv-v0/figures/calibration_catastrophe.png")
fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.15)
fig.savefig(out_png, bbox_inches="tight", pad_inches=0.15, dpi=300)
print(f"Wrote: {out_pdf}")
print(f"Wrote: {out_png}")

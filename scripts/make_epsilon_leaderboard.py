#!/usr/bin/env python3
"""Leaderboard-style epsilon panel — publication-quality visual.

Style reference: benchmark leaderboards used in modern eval reports
(vendor logo chip + model name, two-tone horizontal bar, numeric
columns right-aligned, best-in-column bolded, thin row rules).

Output:
  paper1/arxiv-v0/figures/epsilon_panel.pdf  (vector)
  paper1/arxiv-v0/figures/epsilon_panel.png  (600 dpi preview)

The figure is a table-as-visualization:
  [ logo chip ]  Model         [ solid bar ε(A) | hatched extend to ε(B) ]  T1  T2  T3   ε(A)
Ordering: by ε(A) ascending (best chronoception first, Oracle row at top).
Threshold: ε* = 0.20 marked by dashed vertical rule under the bars.
"""
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42          # embed as truetype for vector edit
mpl.rcParams["ps.fonttype"]  = 42
mpl.rcParams["font.family"]  = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Inter", "Helvetica", "Arial", "DejaVu Sans"]

# =============================================================
# 1. Data — pulled from pilot-results/epsilon.csv + subcap decomp
# =============================================================
# Row order top→bottom; Oracle first (reference), then panel by ε(A)
# ascending (best chronoception at top of the panel proper).
ROWS = [
    # (label, vendor_key, eps_A, eps_B, sT1, sT2, sT3, is_reference)
    ("Oracle",                "REF", 0.10, None, None, None, None, True),
    ("Claude Sonnet 4.6",     "AN",  0.316, 0.307, 0.00, 0.32, 0.07, False),
    ("Claude Sonnet 4.6 + thinking", "AN", 0.276, 0.301, 0.00, 0.32, 0.22, False),
    ("gpt-5.1",               "OA",  0.426, 0.396, 0.13, 0.31, 0.30, False),
    ("Claude Haiku 4.5",      "AN",  0.442, 0.403, 0.00, 0.30, 0.46, False),
    ("o3 (reasoning)",        "OA",  0.490, 0.582, 0.00, 0.30, 0.57, False),
    ("o4-mini (reasoning)",   "OA",  0.532, 0.513, 0.00, 0.30, 1.54, False),
    ("gpt-4o",                "OA",  0.661, 0.587, 0.00, 0.32, 1.07, False),
    ("Qwen2.5-7B",            "QW",  0.760, 0.764, 0.00, 0.31, 1.56, False),
    ("gpt-4o-mini",           "OA",  1.328, 1.069, 0.00, 0.32, 1.12, False),
]

# Vendor system: real logo PNGs + bar accents (chips replaced by logos)
LOGO_DIR = Path("paper1/arxiv-v0/figures/logos")
VENDOR = {
    "OA": {"logo": LOGO_DIR / "openai.png",    "bar": "#3182bd"},  # OpenAI blossom
    "AN": {"logo": LOGO_DIR / "anthropic.png", "bar": "#cc785c"},  # Anthropic AI mark
    "QW": {"logo": LOGO_DIR / "qwen.png",      "bar": "#6a4c93"},  # Qwen mark
    "DS": {"logo": LOGO_DIR / "deepseek.png",  "bar": "#2b6cb0"},  # DeepSeek whale
    "REF":{"logo": None,                        "bar": "#c8c8c8", "letter": "★"},
}
_LOGO_CACHE = {}
def get_logo(vk):
    if vk not in _LOGO_CACHE:
        p = VENDOR[vk].get("logo")
        _LOGO_CACHE[vk] = mpimg.imread(p) if (p and p.exists()) else None
    return _LOGO_CACHE[vk]

BAR_MAX = 1.40  # right edge of bar area (epsilon units); >1.4 clips
THRESHOLD = 0.20  # Augustine threshold ε*
INK = "#1a1a1a"; INK2 = "#4a4a4a"; RULE = "#e6e6e6"; RULE_STRONG = "#c8c8c8"

# =============================================================
# 2. Figure geometry
# =============================================================
n_rows = len(ROWS)
row_h  = 0.62  # inches per row
fig_w  = 12.0
fig_h  = 2.0 + n_rows * row_h
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.06)

ax.set_xlim(0, 100)
ax.set_ylim(0, n_rows + 1)
ax.axis("off")

# Column x-positions (percent of canvas width)
X_CHIP    = 3.5
X_MODEL   = 9.0
X_BAR0    = 32.5    # bar starts
X_BAR1    = 62.5    # bar ends
X_EPS     = 68.0
X_SCORE_T1 = 76.5
X_SCORE_T2 = 84.0
X_SCORE_T3 = 91.5

# =============================================================
# 3. Header row
# =============================================================
head_y = n_rows + 0.35
def head(x, txt, ha="right"):
    ax.text(x, head_y, txt, ha=ha, va="center",
            fontsize=9.5, color=INK2, fontweight="500",
            family="sans-serif")

head(X_MODEL, "Model", ha="left")
ax.text((X_BAR0+X_BAR1)/2, head_y,
        r"$\varepsilon$  (Setting A  $\rightarrow$  Setting B)",
        ha="center", va="center", fontsize=9.5, color=INK2, style="italic")
head(X_EPS,      r"$\varepsilon$(A)")
head(X_SCORE_T1, r"score$_{T_1}$")
head(X_SCORE_T2, r"score$_{T_2}$")
head(X_SCORE_T3, r"score$_{T_3}$")

# thin rule under header
ax.plot([2, 98], [head_y - 0.35]*2, color=RULE_STRONG, lw=0.7, zorder=0)

# =============================================================
# 4. Per-row rendering
# =============================================================
best_eps = min(r[2] for r in ROWS if not r[7])   # excluding Oracle
best_T1  = min([r[4] for r in ROWS if r[4] is not None and not r[7]] or [None])
best_T2  = min([r[5] for r in ROWS if r[5] is not None and not r[7]] or [None])
best_T3  = min([r[6] for r in ROWS if r[6] is not None and not r[7]] or [None])

def eps_to_x(eps):
    return X_BAR0 + (eps / BAR_MAX) * (X_BAR1 - X_BAR0)

for i, (label, vk, epsA, epsB, sT1, sT2, sT3, is_ref) in enumerate(ROWS):
    y = n_rows - i - 0.5

    # ---- vendor logo (real image) ----
    img = get_logo(vk)
    if img is not None:
        oi = OffsetImage(img, zoom=0.10)
        ab = AnnotationBbox(oi, (X_CHIP, y), frameon=False, box_alignment=(0.5, 0.5),
                            xycoords=("data","data"), zorder=4, pad=0)
        ax.add_artist(ab)
    else:
        # Oracle: neutral filled circle chip
        from matplotlib.patches import Circle
        ax.add_patch(Circle((X_CHIP, y), 0.60, facecolor="#8a8a8a",
                            edgecolor="#5a5a5a", lw=0.5, zorder=3))
        ax.text(X_CHIP, y, "OR", ha="center", va="center",
                fontsize=8, color="white", fontweight="700", zorder=4)

    # ---- model label ----
    weight = "600" if is_ref else "500"
    color = INK if not is_ref else "#3a3a3a"
    ax.text(X_MODEL, y, label, ha="left", va="center",
            fontsize=11.5, color=color, fontweight=weight,
            fontstyle="italic" if is_ref else "normal")
    if is_ref:
        ax.text(X_MODEL + 12.5, y, "reference", ha="left", va="center",
                fontsize=9, color="#8a8a8a", fontstyle="italic")

    # ---- bar ----
    if epsA is None:
        # dashed oracle band spanning ~78% of bar area
        oracle_x1 = eps_to_x(THRESHOLD * 3.9)  # visual only
        ax.add_patch(Rectangle((X_BAR0, y - 0.20), X_BAR1 - X_BAR0, 0.40,
                               facecolor="#f5f5f5", edgecolor="#c8c8c8",
                               linestyle=(0, (2, 2)), lw=0.8, zorder=2))
        ax.text(X_BAR1 - 1.5, y, "grounded target",
                ha="right", va="center", fontsize=9,
                color="#8a8a8a", fontstyle="italic", zorder=3)
    else:
        bar_col = VENDOR[vk]["bar"]
        # bar background (pale rail)
        ax.add_patch(Rectangle((X_BAR0, y - 0.20), X_BAR1 - X_BAR0, 0.40,
                               facecolor="#f4f4f4", edgecolor="none", zorder=1))
        # solid part = eps A
        xA = eps_to_x(min(epsA, BAR_MAX))
        ax.add_patch(Rectangle((X_BAR0, y - 0.20), xA - X_BAR0, 0.40,
                               facecolor=bar_col, edgecolor="none", zorder=2))
        # hatched extension to eps B (if B is worse than A, extend; else lighten)
        if epsB is not None and epsB != epsA:
            xB = eps_to_x(min(epsB, BAR_MAX))
            x_lo, x_hi = sorted([xA, xB])
            ax.add_patch(Rectangle((x_lo, y - 0.20), x_hi - x_lo, 0.40,
                                   facecolor=bar_col, edgecolor="white",
                                   alpha=0.28, hatch="///", lw=0,
                                   zorder=2))
        # value label inside solid bar (if room) or right of it
        val_txt = f"{epsA:.2f}"
        if (xA - X_BAR0) > 6:
            ax.text((X_BAR0 + xA) / 2, y, val_txt, ha="center", va="center",
                    fontsize=10, color="white", fontweight="600", zorder=4)
        # B value tag at bar end (light color)
        if epsB is not None:
            xB = eps_to_x(min(epsB, BAR_MAX))
            ax.text(xB + 0.6, y, f"{epsB:.2f}", ha="left", va="center",
                    fontsize=9.5, color=INK2, fontweight="600", zorder=4)

    # ---- numeric columns ----
    def cell(x, val, best, is_ref):
        if val is None or is_ref:
            ax.text(x, y, "—", ha="right", va="center",
                    fontsize=10, color="#9a9a9a")
            return
        is_best = (best is not None and abs(val - best) < 1e-6)
        ax.text(x, y, f"{val:.2f}", ha="right", va="center",
                fontsize=11, color=INK,
                fontweight="700" if is_best else "500")

    cell(X_EPS,      epsA, best_eps, is_ref)
    cell(X_SCORE_T1, sT1,  best_T1,  is_ref)
    cell(X_SCORE_T2, sT2,  best_T2,  is_ref)
    cell(X_SCORE_T3, sT3,  best_T3,  is_ref)

    # thin row rule beneath
    if i < n_rows - 1:
        ax.plot([2, 98], [y - 0.5]*2, color=RULE, lw=0.5, zorder=0)

# =============================================================
# 5. Threshold indicator under the bar area
# =============================================================
xT = eps_to_x(THRESHOLD)
ax.plot([xT, xT], [0.05, n_rows + 0.1], color="#2a7a2a",
        ls=(0, (4, 3)), lw=1.1, zorder=5)
ax.text(xT, 0.15, r"$\varepsilon^{\star} = 0.20$",
        ha="center", va="top", fontsize=9,
        color="#2a7a2a", fontweight="600")

# =============================================================
# 6. Title
# =============================================================
fig.suptitle(
    r"Chronoceptive Calibration Error $\varepsilon$ — full 10-agent panel",
    x=0.02, y=0.975, ha="left", fontsize=15,
    fontweight="700", color=INK,
)
fig.text(0.02, 0.93,
    r"Solid bar = Setting A ($\varepsilon$).  Hatched extension = Setting B.  "
    r"Dashed green rule = Augustine threshold $\varepsilon^{\star} = 0.20$.  "
    r"Bold numeric = best in column.  No panel agent crosses $\varepsilon^{\star}$.",
    ha="left", fontsize=10, color=INK2, fontstyle="italic")

# Legend chip below title
lg_y = 0.912
ax.plot([], [], color="none")  # anchor

# =============================================================
# 7. Save
# =============================================================
out_pdf = Path("paper1/arxiv-v0/figures/epsilon_panel.pdf")
out_png = Path("paper1/arxiv-v0/figures/epsilon_panel.png")
fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.15)
fig.savefig(out_png, bbox_inches="tight", pad_inches=0.15, dpi=300)
print(f"Wrote: {out_pdf}")
print(f"Wrote: {out_png}")

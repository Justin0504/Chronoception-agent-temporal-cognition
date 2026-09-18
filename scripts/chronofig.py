"""Shared figure style for the Augustine Problem papers.

Why this module exists
----------------------
Seven figures were built by seven scripts that each redefined the palette and
picked their own canvas size. Two consequences, both visible in the printed
paper:

1. `RULE` meant #c8c8c8 in three scripts and #e6e6e6 in two others, so the
   same conceptual element was drawn in two different greys.

2. Canvas widths ranged 9.5-12.5 in while every figure is included at
   \\linewidth (5.5 in for ICLR). The same `fontsize=10.5` therefore printed
   at 4.4 pt in one figure and 6.7 pt in another, against 10 pt body text.
   4.4 pt is below the readable floor, and the 1.5x spread made the paper
   look assembled from different sources.

The fix is to author at true print size: a figure declares the fraction of
the text column it will occupy, `figure()` returns a canvas of exactly that
many inches, and every font size in the script is then a literal printed
point size. There is no scale factor to reason about and no way for two
figures to disagree.

    from chronofig import figure, C, PT, axis_glyph

    fig, ax = figure(width_frac=1.0, aspect=0.62)
    ax.set_xlabel("...", fontsize=PT.label, color=C.ink)

Density is the honest cost: a 13-row leaderboard really does have to fit in
5.5 in, so rows get shorter rather than type getting smaller.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Page geometry
# --------------------------------------------------------------------------
# Measured from the built PDFs, not assumed: group words into lines and take
# the mode of the justified left and right edges (scripts/measure_textwidth.py).
TEXTWIDTH_IN = {
    "iclr": 5.50,   # 396 pt
    "arxiv": 6.50,  # 468 pt
}
# Author against the narrower target so a figure is never upscaled into the
# arXiv column; the arXiv build simply leaves a little more margin.
PAGE = "iclr"


def textwidth() -> float:
    return TEXTWIDTH_IN[PAGE]


# --------------------------------------------------------------------------
# Palette -- one definition, no per-script variants
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Palette:
    ink: str = "#1a1a1a"          # primary text, axis labels
    ink2: str = "#4a4a4a"         # secondary text, tick labels
    ink3: str = "#7a7a7a"         # captions, de-emphasised annotation
    rule: str = "#d8d8d8"         # hairlines, row separators, grid
    rule_strong: str = "#9a9a9a"  # axis spines, header underline
    surface: str = "#f4f4f4"      # bar troughs, empty track
    # Semantic accents. Used for meaning, never for decoration.
    good: str = "#2a7a2a"         # thresholds met, grounded reference
    warn: str = "#b8860b"         # marginal / underpowered
    bad: str = "#a50f15"          # failure, reasoning-mode degradation
    cool: str = "#3182bd"         # non-reasoning class
    schematic: str = "#7a7a7a"    # anything not measured


C = Palette()


@dataclass(frozen=True)
class TypeScale:
    """Literal printed point sizes. Body text in both papers is 10 pt."""
    title: float = 9.5
    subtitle: float = 7.5
    label: float = 8.0     # axis labels
    tick: float = 7.0      # tick labels
    annot: float = 7.0     # in-plot annotation
    small: float = 6.5     # dense table cells, n counts
    MIN: float = 6.0       # hard floor; below this, cut content instead


PT = TypeScale()

# --------------------------------------------------------------------------
# Vendors -- colour and logo in one place (previously duplicated per script)
# --------------------------------------------------------------------------
LOGO_DIR = Path("paper1/arxiv-v0/figures/logos")

VENDORS = {
    "OA":  {"name": "OpenAI",    "color": "#3182bd", "logo": "openai.png"},
    "AN":  {"name": "Anthropic", "color": "#cc785c", "logo": "anthropic.png"},
    "QW":  {"name": "Alibaba",   "color": "#6a4c93", "logo": "qwen.png"},
    "DS":  {"name": "DeepSeek",  "color": "#2b6cb0", "logo": "deepseek.png"},
    "ZAI": {"name": "Z.AI",      "color": "#4a4a4a", "logo": "zai.png"},
    "MS":  {"name": "Moonshot",  "color": "#2b2b2b", "logo": "moonshot.png"},
    "MM":  {"name": "MiniMax",   "color": "#e94e77", "logo": "minimax.png"},
    "REF": {"name": "reference", "color": "#c8c8c8", "logo": None},
}


def vendor_logo(key: str):
    """Return the logo image array for a vendor, or None."""
    import matplotlib.image as mpimg
    spec = VENDORS.get(key, {})
    name = spec.get("logo")
    if not name:
        return None
    p = LOGO_DIR / name
    return mpimg.imread(p) if p.exists() else None


# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------
def _rc():
    mpl.rcParams.update({
        "pdf.fonttype": 42,         # embed TrueType so the PDF stays editable
        "ps.fonttype": 42,
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica", "Arial", "DejaVu Sans"],
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "axes.labelcolor": C.ink,
        "text.color": C.ink,
        "xtick.color": C.ink2,
        "ytick.color": C.ink2,
        "figure.dpi": 110,
    })


def figure(width_frac: float = 1.0, aspect: float = 0.62, **kw):
    """A canvas at true print size.

    width_frac : fraction of the text column the figure will occupy in LaTeX.
                 Include it with the matching width, e.g. width_frac=1.0 with
                 `\\includegraphics[width=\\linewidth]`.
    aspect     : height / width.

    Because the canvas is the printed size, every fontsize in the calling
    script is a literal printed point size.
    """
    _rc()
    w = textwidth() * width_frac
    return plt.subplots(figsize=(w, w * aspect), **kw)


def tidy(ax, *, grid: str | None = "y", spines=("left", "bottom")):
    """House axis treatment: hairline grid, two spines, muted ticks."""
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(sp in spines)
        if sp in spines:
            ax.spines[sp].set_color(C.rule_strong)
    if grid:
        ax.grid(True, axis=grid, ls=":", lw=0.5, color=C.rule, alpha=0.9)
        ax.set_axisbelow(True)
    ax.tick_params(labelsize=PT.tick, colors=C.ink2)
    return ax


def save(fig, stem: str, trees=("arxiv-v0", "iclr27", "iclr27_supp"), png=True):
    """Write one figure into every paper tree, plus a PNG preview for review."""
    for tree in trees:
        p = Path("paper1") / tree / "figures" / f"{stem}.pdf"
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, bbox_inches="tight", pad_inches=0.02)
        print(f"Wrote: {p}")
    if png:
        p = Path("paper1/arxiv-v0/figures") / f"{stem}.png"
        fig.savefig(p, bbox_inches="tight", pad_inches=0.02, dpi=300)
        print(f"Wrote: {p}")


# --------------------------------------------------------------------------
# The Three Times glyphs
# --------------------------------------------------------------------------
# These are the paper's ontology, so they earn a place in the figures: the
# reader learns the three marks once in Figure 1 and then reads every later
# figure faster. They are drawn as vector paths rather than shipped as image
# assets so they stay sharp, recolourable, and inside the PDF.
#
# Deliberately not decorative. Each mark encodes what distinguishes its axis:
#   tau_wall  continuous external time  -> an unbroken sweep
#   tau_step  countable invocations     -> discrete blocks
#   tau_self  narrated, unanchored      -> a sweep that does not close
AXIS_GLYPHS = ("wall", "step", "self")


def axis_glyph(ax, kind: str, x: float, y: float, size: float,
               color: str | None = None, lw: float = 1.0):
    """Draw one Three-Times mark centred at (x, y) in data coordinates.

    `size` is the full width of the mark in data units.
    """
    from matplotlib.patches import Arc, Rectangle
    col = color or C.ink
    r = size / 2.0

    if kind == "wall":
        # Continuous sweep: a full ring with a radius hand. External time runs
        # whether or not the policy is invoked.
        ax.add_patch(Arc((x, y), size, size, theta1=0, theta2=360,
                         lw=lw, color=col, zorder=5))
        ax.plot([x, x], [y, y + r * 0.62], lw=lw, color=col,
                solid_capstyle="round", zorder=5)
        ax.plot([x, x + r * 0.45], [y, y], lw=lw, color=col,
                solid_capstyle="round", zorder=5)

    elif kind == "step":
        # Three discrete blocks: countable, and with gaps that carry no time.
        n, gap = 3, size * 0.14
        bw = (size - gap * (n - 1)) / n
        for i in range(n):
            ax.add_patch(Rectangle((x - r + i * (bw + gap), y - bw / 2),
                                   bw, bw, fill=False, lw=lw, color=col,
                                   zorder=5))

    elif kind == "self":
        # An open sweep that never closes: the narration has a shape but no
        # anchor. Same outer radius as the wall mark so the two read as kin.
        ax.add_patch(Arc((x, y), size, size, theta1=35, theta2=325,
                         lw=lw, color=col, zorder=5))
        ax.plot([x + r * 0.72], [y - r * 0.72], marker="o", ms=lw * 1.6,
                color=col, zorder=5)
    else:
        raise ValueError(f"unknown glyph {kind!r}; expected one of {AXIS_GLYPHS}")


GLYPH_LABEL = {
    "wall": r"$\tau_{\mathrm{wall}}$",
    "step": r"$\tau_{\mathrm{step}}$",
    "self": r"$\tau_{\mathrm{self}}$",
}

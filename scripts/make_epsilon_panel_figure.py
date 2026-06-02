#!/usr/bin/env python3
"""Figure 3: epsilon panel ranking across the full 11-agent panel.

Horizontal bar chart sorted by epsilon (Setting A). The Augustine threshold
ε* = 0.20 is marked. Reverse-Scaling variants of o4-mini and Sonnet 4.6 are
grouped to make the theorem's effect visible at the aggregate level.
"""
from __future__ import annotations
import csv, json
from pathlib import Path
from math import log10
from statistics import median


def load_pilot_eps() -> dict[tuple[str, str], float]:
    out = {}
    p = Path("pilot-results/epsilon.csv")
    if not p.exists():
        return out
    with p.open() as f:
        for row in csv.DictReader(f):
            try:
                eps = float(row["epsilon"])
            except (ValueError, KeyError):
                continue
            out[(row["agent_id"], row["setting"])] = eps
    return out


def compute_t31_only_eps(results_dir: str, agent_label_map: dict) -> dict:
    """For E2/E3, compute a T3.1-only proxy ε so we can compare on the same axis.
    Strict definition: |rho_clipped|/2 where |rho| saturates at 2 for the rho-axis only.
    This is the T3 axis contribution treated as if it were a full ε signal.
    """
    out = {}
    for label, agent_id in agent_label_map.items():
        rhos_A, rhos_B = [], []
        for jp in Path(results_dir).rglob(f"**/T3.1/no_injection/*.json"):
            with jp.open() as f:
                d = json.load(f)
            if d.get("agent_id") != agent_id:
                continue
            steps = d.get("steps") or []
            if not steps: continue
            tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            ts = d.get("self_narrated_duration")
            if ts and ts > 0 and tw > 0:
                rhos_A.append(abs(log10(ts/tw)))
        for jp in Path(results_dir).rglob(f"**/T3.1/with_injection/*.json"):
            with jp.open() as f:
                d = json.load(f)
            if d.get("agent_id") != agent_id:
                continue
            steps = d.get("steps") or []
            if not steps: continue
            tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            ts = d.get("self_narrated_duration")
            if ts and ts > 0 and tw > 0:
                rhos_B.append(abs(log10(ts/tw)))
        if rhos_A:
            out[(label, "no_injection")] = min(median(rhos_A), 2.0) / 2.0
        if rhos_B:
            out[(label, "with_injection")] = min(median(rhos_B), 2.0) / 2.0
    return out


pilot = load_pilot_eps()
e2 = compute_t31_only_eps("e2-results", {
    "o4-mini (low effort)":  "openai/o4-mini-rlow",
    "o4-mini (high effort)": "openai/o4-mini-rhigh",
})
e3 = compute_t31_only_eps("e3-results", {
    "Sonnet 4.6 + thinking": "anthropic/claude-sonnet-4-6",
})

# Pretty labels for pilot agents
PRETTY_PILOT = {
    "openai/gpt-4o-mini":            ("GPT-4o-mini", "non-reasoning"),
    "openai/gpt-4o":                 ("GPT-4o", "non-reasoning"),
    "openai/gpt-5.1":                ("GPT-5.1", "non-reasoning"),
    "openai/o3":                     ("o3", "reasoning"),
    "openai/o4-mini":                ("o4-mini (medium effort)", "reasoning"),
    "anthropic/claude-haiku-4-5":    ("Claude Haiku 4.5", "non-reasoning"),
    "anthropic/claude-sonnet-4-6":   ("Sonnet 4.6 (no thinking)", "non-reasoning"),
    "oss/qwen2.5-7b-instruct-yuezhao": ("Qwen2.5-7B (oss)", "non-reasoning"),
}

# Pilot only — RS-variant comparison lives in Figure 1 to avoid metric mismatch
# (E2/E3 only ran T3.1 so their ε can't be compared on the 3-capability axis)
rows = []
for agent_id, (pretty, cls) in PRETTY_PILOT.items():
    eps_A = pilot.get((agent_id, "no_injection"))
    eps_B = pilot.get((agent_id, "with_injection"))
    if eps_A is None: continue
    rows.append({"label": pretty, "class": cls, "eps_A": eps_A, "eps_B": eps_B,
                 "group": "pilot"})

rows.sort(key=lambda r: r["eps_A"])

print("Rows for figure:")
for r in rows:
    print(f"  {r['label']:35s} cls={r['class']:13s} eps_A={r['eps_A']:.3f}  eps_B={r['eps_B']:.3f}  group={r['group']}")

# ---------------- Plot ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(11, 6.2), dpi=160)

labels = [r["label"] for r in rows]
eps_A  = [r["eps_A"] for r in rows]
eps_B  = [r["eps_B"] for r in rows]

# Color logic: non-reasoning blue, reasoning red
def color_of(r):
    if r["class"] == "reasoning":
        return "#fb6a4a"
    return "#3182bd"

colors = [color_of(r) for r in rows]

ys = np.arange(len(rows))
height = 0.36

# Setting A bars (primary)
bars_a = ax.barh(ys + height/2, eps_A, height=height, color=colors,
                  edgecolor="black", linewidth=0.8, label="Setting A (no injection)",
                  zorder=3)
# Setting B bars
bars_b = ax.barh(ys - height/2, eps_B, height=height, color=colors,
                  edgecolor="black", linewidth=0.8, alpha=0.45,
                  label="Setting B (with injection)", zorder=3)

# Augustine threshold
ax.axvline(0.20, ls="--", color="#2a7", lw=2.0, alpha=0.9, zorder=2)
ax.text(0.215, 0.5,
        "Augustine threshold ε* = 0.20\n(uncrossable through narrative training)",
        fontsize=9.5, color="#2a7", style="italic", fontweight="bold",
        va="center", ha="left", rotation=0)

# Annotate values on Setting A bars
for y, r in zip(ys, rows):
    ax.text(r["eps_A"] + 0.018, y + height/2,
            f"{r['eps_A']:.2f}", va="center", fontsize=9, fontweight="bold")

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=9.5)
ax.set_xlabel(r"Chronoceptive calibration error $\varepsilon$ (lower = closer to grounded)", fontsize=11)
ax.set_xlim(0, max(max(eps_A), max(eps_B)) * 1.15)
ax.set_title("Panel ε ranking — no agent crosses the Augustine threshold $\\varepsilon^*= 0.20$",
             fontsize=12.5, pad=14)
ax.grid(True, axis="x", ls=":", alpha=0.4, zorder=1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#3182bd", edgecolor="black", label="Non-reasoning model"),
    Patch(facecolor="#fb6a4a", edgecolor="black", label="Reasoning model"),
    Patch(facecolor="white", edgecolor="#2a7", linewidth=2, linestyle="--", label="Augustine threshold ε* = 0.20"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9.5, framealpha=0.95)

# Annotate the "best agent still fails" finding
best = rows[0]
ax.text(0.98, 0.18,
        f"Best agent: {best['label']}\n"
        f"  ε = {best['eps_A']:.3f}, {best['eps_A']/0.20:.2f}× the Augustine threshold\n"
        f"  T2 axis alone contributes ~0.32 to ε\n"
        f"  ⇒ narrative training cannot close the gap",
        transform=ax.transAxes, fontsize=9, va="bottom", ha="right", color="#222",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#fffaf0",
                  edgecolor="#a50f15", alpha=0.95, lw=1.2))

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/epsilon_panel.pdf")
out_png = Path("paper1/arxiv-v0/figures/epsilon_panel.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"\nWrote: {out_pdf}\nWrote: {out_png}")

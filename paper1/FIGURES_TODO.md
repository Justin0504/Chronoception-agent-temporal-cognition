# Camera-Ready Figures TODO

The paper has 8 figures total. **Five are data plots** (matplotlib, already done,
data-bound — DO NOT regenerate by hand): `reverse_scaling`, `calibration_catastrophe`,
`a1_positive_control`, `epsilon_panel`, `p12_hcast`.

**Four are architecture / flow / conceptual diagrams** that should be redrawn as
clean vector graphics in Figma for camera-ready. The current matplotlib versions
work, but the camera-ready visual bar is higher — Fluent-style colored icons,
consistent palette, vector PDF.

**Recommended workflow per figure**:

1. Drop the GPT prompt (below) into ChatGPT 5.4 (or any GPT image-gen model),
   get a PNG bootstrap.
2. Open Figma. New frame at the listed aspect ratio. Drag the PNG in at 20%
   opacity as a tracing reference.
3. Build a fresh layer on top using the listed hex palette + Fluent UI System
   Icons plugin (free).
4. Type all text in Figma directly (GPT-generated text is usually garbled —
   redo every label crisply in Inter or Source Sans Pro).
5. Export as PDF (vector). Replace the matching file in
   `paper1/arxiv-v0/figures/`.
6. Rebuild paper: `cd paper1/arxiv-v0 && tectonic main.tex`.

---

## Shared visual system (apply to all four figures)

Append this block to every prompt and respect it in Figma:

```
SHARED VISUAL SYSTEM:
- Background: white #FFFFFF
- Headers / strong dark navy: #1F3A5F
- Pastel fills: blue #E6F0FC, coral #FCE8E6, green #E6F5E6, orange #FFF1E0,
  cream #FFFAF0
- Accent strong colors: blue #3182BD, coral #FB6A4A, green #2A7A2A,
  orange #CC6600, dark red #A50F15
- Typography: Inter (or Source Sans Pro). Bold for titles. Regular for body.
- Card style: 8 px rounded corners, 4 px drop shadow at 20% opacity
- Icons: Fluent UI 3D style, ~64 px tall, gentle gradient + soft shadow
- Arrows: solid stroke 3 px, color matching the connected element's accent
- All text crisp sans-serif — do not let GPT auto-place labels; retype in Figma
```

---

## Figure 1 — Theorem Arc (§1 Introduction)

- **Replaces**: `paper1/arxiv-v0/figures/theorem_arc.pdf`
- **Aspect ratio**: 16:9
- **Purpose**: Orient the reader. 3 theorems × 3 phenomena × 3 papers grid.

```
A 3-row × 3-column conceptual map titled "The framework's spine — three theorems,
three phenomena, three papers". Aspect 16:9. White canvas.

Row 1 (light coral #FCE8E6, dark coral #A50F15 header bars): 3 cards titled
"Theorem 1: CIT", "Theorem 2: Reverse-Scaling", "Theorem 3: SIT".
Center icons (Fluent 3D):
  - CIT: a stylised gradient ∇ symbol fading to gray (signal lost)
  - Reverse-Scaling: an up-arrow with a red exclamation badge
  - SIT: dual clock + map-pin icons side by side

Row 2 (light blue #E6F0FC, dark blue #08519C headers): 3 cards titled
"L1 / L2 / L3", "Calibration Catastrophe", "Cartographic Problem".
Center icons:
  - L1/L2/L3: three coloured dots on three labelled axes (wall, step, self)
  - Calibration Catastrophe: cracked shield with red lightning
  - Cartographic Problem: map with question mark

Row 3 (light cream #FFFAF0, orange #CC6600 headers): 3 cards titled
"Paper 1 (this paper)", "Paper 2: ChronoStack", "Paper 3: Agentic Frontier".
Center icons:
  - Paper 1: open book with magnifying glass
  - Paper 2: stacked construction blocks with wrench
  - Paper 3: 2D plane with smooth curve

Horizontal coloured arrows connect card 1 → 2 → 3 within each row.
Vertical gray arrows connect each theorem (row 1) down to its phenomenon (row 2).

Left margin: 3 vertical labels in matching row colours: "Theorems", "Phenomena",
"Research programme".

Keep card body text minimal (one short line max — will be re-typed in Figma).

[append SHARED VISUAL SYSTEM block]
```

---

## Figure 2 — Three Times Ontology (§2)

- **Replaces**: `paper1/arxiv-v0/figures/three_times.pdf`
- **Aspect ratio**: 16:9
- **Purpose**: Define the framework's basic objects ($\twall, \tstep, \tself$).

```
A 3-row horizontal ontology diagram titled "The Three Times of an Agent".
Aspect 16:9. White canvas, very faint cream tint.

Each row is a wide rounded panel in a different pastel:
- Row 1 #E6F0FC blue, label "τ_wall — wall-clock time"
- Row 2 #FCE8E6 coral, label "τ_step — step time"
- Row 3 #FFF1E0 orange, label "τ_self — self-narrated time"

Row 1 content: large 3D analog clock icon (blue), then a long continuous blue
horizontal bar (0s … 10s tick marks underneath). Right caption: "continuous,
external (an external clock observes this)".

Row 2 content: a row of 6 small rounded coral squares labelled a₀ a₁ a₂ a₃ a₄ a₅,
each containing a tiny gear icon. Right caption: "discrete policy invocations".
Below in italic gray: "⟨Δt⟩ = mean per-step latency".

Row 3 content: a friendly robot avatar with a speech bubble: "about 2 seconds".
A SHORT orange bar (deliberately ~20% of the blue bar length) to its right.

A large curly brace spans all three rows on the right side, pointing to one
white rounded box containing the equation:
"τ_wall ≈ τ_step · ⟨Δt⟩ ≈ τ_self"
Above: small green bold "Grounded chronoception".
Below: small red italic with red warning triangle:
"Augustine Problem = policy fails this identity".

Top title bold black sans-serif.

[append SHARED VISUAL SYSTEM block]
```

---

## Figure 3 — ChronoBench Pipeline (§4, NEW)

- **Adds a new figure** to §4 ChronoBench (no existing matplotlib equivalent).
- **Target path**: `paper1/arxiv-v0/figures/chronobench_pipeline.pdf`
- **Aspect ratio**: 16:5 (wide horizontal pipeline)
- **Purpose**: 5-second orientation of the entire benchmark — task gen → panel → settings → metrics → findings.

```
A 5-panel horizontal benchmark architecture diagram titled "ChronoBench — 9
sub-capabilities × 10 agents × 2 settings × ~4,000 trajectories".
Aspect 16:5. White canvas.

Each panel is a rounded rectangle with a distinct pastel fill and a dark navy
header bar (#1F3A5F) with white sans-serif title. Thick navy arrow heads
between adjacent panels.

Panel 1 — fill #E6F0FC. Header "Task Generation". 3 sub-cards stacked:
  - Clock icon (blue) + "Wall axis · T1.1 / T1.2 / T1.3"
  - Gear icon (red) + "Step axis · T2.1 / T2.2 / T2.3"
  - Speech-bubble icon (orange) + "Self axis · T3.1 / T3.2 / T3.3"

Panel 2 — fill #E6F5E6. Header "Agent Panel". 3 sub-cards:
  - OpenAI logo + short list "gpt-4o-mini, gpt-4o, gpt-5.1, o3, o4-mini"
  - Anthropic asterisk + "Claude Haiku 4.5, Sonnet 4.6 (+ thinking)"
  - HuggingFace logo + "Qwen2.5-7B, DeepSeek-R1-Distill-14B (vLLM)"

Panel 3 — fill #FFF1E0. Header "Two Settings". 2 sub-cards stacked:
  - Shield-off icon + "Setting A: no harness injection"
  - Calendar icon + "Setting B: + Current date and time"

Panel 4 — fill #FCE8E6. Header "Metrics". 3 small sub-cards in a row:
  - Ruler icon + "α — Parkinson"
  - Stopwatch icon + "CAR — Clock-Adherence"
  - Log-graph icon + "ρ — Confabulation"
Below them, one wide highlighted card with star icon:
  "ε = ⅓ (score_T1 + score_T2 + score_T3)"

Panel 5 — fill #FFFAF0. Header "Findings". 5 compact sub-cards:
  1. Red X icon + "L2: every agent ≤ 5% of budget"
  2. Blue ↓ icon + "L3 closes 94% across 5 generations"
  3. Red ⚡ icon + "Reverse-Scaling Theorem"
  4. Orange ⚠ icon + "Calibration Catastrophe (0–50% coverage)"
  5. 🔍 icon + "Injection Tell: 3/3 vs 0/3"

Top title bold black sans-serif, centred.

[append SHARED VISUAL SYSTEM block]
```

When this figure is created, also add a `\includegraphics{figures/chronobench_pipeline.pdf}` block at the top of `paper1/arxiv-v0/sections/04_chronobench.tex` and a caption.

---

## Figure 4 — Agentic Frontier (§12)

- **Replaces**: `paper1/arxiv-v0/figures/agentic_frontier.pdf`
- **Aspect ratio**: 16:9
- **Purpose**: Show the joint $(T, S)$ deployment plane with 3 constant-$\varepsilon_{ST}$ contours and 5 benchmark icons.

```
A log-log scatter / contour conceptual diagram titled
"The Agentic Frontier: T_max(A) · S_max(A) ≤ C / ε_ST(A)".
Aspect 16:9. White canvas with very faint cream tint.

Axes:
- X: "Deployment horizon T_max (wall-clock seconds)", log scale, ticks at
  10 / 100 / 1000 / 10000
- Y: "Spatial reach S_max (distinct files / pages)", log scale, ticks at
  1 / 10 / 100 / 1000

Three smooth diagonal contour curves of T·S = const, each labelled on the right
edge:
- Blue #3182BD: "Current frontier (ε_ST ≈ 0.6)"
- Coral #FB6A4A: "ChronoStack+ target (ε_ST ≈ 0.2)"
- Green #2A7A2A: "Grounded agent (ε_ST ≈ 0.05)"

Five Fluent 3D icons placed on the plane (with short labels):
- Stopwatch (navy) at ~(1800, 3): "METR HCAST"
- GitHub octocat-style (dark red) at ~(600, 8): "SWE-Bench Lite"
- Browser-with-tabs (orange) at ~(300, 25): "WebArena"
- Globe-with-question (gray) at ~(1200, 60): "GAIA"
- ML-pipeline chart (dark gray) at ~(86400, 200): "MLE-Bench"

Three faint shaded background regions (low opacity, 8%):
- Upper-left pale blue + small map-pin icon + label "Cartographic binding (S-axis)"
- Lower-right pale red + small clock icon + label "Augustine binding (T-axis)"
- Top-right overlap pale gray + label "Joint binding"

Bottom-right inset box (cream fill #FFFAF0, red border #A50F15, rounded):
"Paper 1 bounds the T-axis (Augustine Problem, CIT).
 Paper 3 bounds the S-axis (Cartographic Problem, SIT).
 Together they specify the joint Agentic Frontier."

Top title bold black sans-serif.
Dotted grid lines, very faint. Drop shadow on each icon.

[append SHARED VISUAL SYSTEM block]
```

---

## Foundation-model logo sourcing

Anywhere a figure shows a model name (`gpt-4o`, `Claude Sonnet 4.6`, `Qwen2.5-7B`,
`DeepSeek-R1`, etc.) the camera-ready version should display the **official
provider logo** next to or in place of the name marker — exactly the style of the
reference plots provided. **Use only the official mark from the provider's own
brand page or official GitHub.** Do not redraw from memory; do not use third-party
icon packs.

| Provider | Official source | What to download |
|---|---|---|
| **OpenAI** | <https://openai.com/brand> | "Blossom" swirl mark, SVG. Used for `gpt-4o`, `gpt-4o-mini`, `gpt-5.1`, `o3`, `o4-mini`. |
| **Anthropic** | <https://www.anthropic.com> press / brand page; mark also on <https://github.com/anthropics> avatar | Coral burst (radiating asterisk), SVG/PNG. Used for `Claude Haiku 4.5`, `Claude Sonnet 4.6` (+ thinking). |
| **Alibaba / Qwen** | <https://github.com/QwenLM> README + repo avatar; also on Tongyi brand page | Qwen 通义千问 mark (blue/purple flower), SVG/PNG. Used for `Qwen2.5-7B-Instruct`. |
| **DeepSeek** | <https://www.deepseek.com> + <https://github.com/deepseek-ai> avatar | Blue whale mark, SVG/PNG. Used for `DeepSeek-R1-Distill-Qwen-14B`. |
| **Google / Gemini** *(if added later)* | <https://about.google/brand-resource-center> | Gemini gradient sparkle, SVG. |
| **Meta / Llama** *(if added later)* | <https://about.meta.com/brand-resources> | Llama mark, SVG. |

**Verify each download** by visiting the provider's *own* domain — not a logo-
aggregator site (logoipsum, vectorlogo.zone, etc.). The official mark is the only
one that survives a careful reviewer eye and does not risk a trademark complaint.

**Sizing in Figma**: place each logo as a 24–32 px square chip with a 4 px white
or pastel rounded background so the mark stays legible against the bar / scatter
fill — exactly the chip style shown in the reference plots.

**Where to apply logos in this paper's figures**:

| Figure | Apply official logos to |
|---|---|
| Figure 1 theorem_arc | Not used (conceptual diagram) |
| Figure 2 three_times | Not used (ontology) |
| Figure 3 chronobench_pipeline (NEW) | Panel 2 "Agent Panel" sub-cards — each sub-card shows the provider's official mark + the model list |
| Figure 4 agentic_frontier | Not used (benchmark icons, not provider) |
| **Figure 5 reverse_scaling** (data plot) | Add a small OpenAI mark on the o4-mini panel, Anthropic mark on the Sonnet 4.6 panel |
| **Figure 6 calibration_catastrophe** (data plot) | Stamp the official mark on each bar — OpenAI on gpt-5.1/gpt-4o-mini/gpt-4o/o3/o4-mini; Anthropic on Sonnet 4.6 / Haiku 4.5 |
| **Figure 7 epsilon_panel** (data plot) | Same as Figure 6, plus Qwen and DeepSeek marks for the OSS rows |
| **Figure 8 a1_positive_control** (data plot) | Qwen mark on both base and fine-tuned bars (model is Qwen2.5-1.5B / 7B) |
| Figure 9 p12_hcast | Stamp official mark on each scatter point per provider |

For the data plots, the cleanest workflow is: regenerate the matplotlib PDF as
usual, then open the PDF in Figma / Illustrator and overlay the logo chips on
top of each bar / point. This keeps the underlying data plot reproducible while
giving the camera-ready PDF the visual identity of the reference plots.

---

## Figma operational hints

- Frame size: aspect 16:9 → 1920 × 1080; aspect 16:5 → 1920 × 600.
- Plugin: install **Fluent UI System Icons** (free, vector SVG) and replace every
  GPT-generated icon with the closest Fluent equivalent.
- Color tokens: create a Figma color style for each hex above so you can swap
  the palette in one click if needed.
- Export: File → Export → PDF (vector). Embed all fonts.
- File naming: keep the existing names (`theorem_arc.pdf`, `three_times.pdf`,
  `agentic_frontier.pdf`); new one is `chronobench_pipeline.pdf`.

After all four are in place, rebuild:

```
cd paper1/arxiv-v0
tectonic main.tex
# inspect main.pdf; commit + push
```

The 5 data figures are not part of this workflow — they stay matplotlib.

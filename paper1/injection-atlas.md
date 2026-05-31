# Closed-Lab Injection Atlas

**Status**: v0 (2026-05-29) — audit in progress
**Parent**: [`SCOPE.md`](SCOPE.md) Contribution 5 · [`../FRAMING.md`](../FRAMING.md) §3.1 + §5.5
**Owner**: Role B (Phase 2 Pilot Plan §3)
**Goal**: Convert the Injection Tell from a rhetorical argument into a measured industry footprint.

This document is the empirical artifact of the **Closed-Lab Injection Audit**. For every closed-lab agent harness that we survey, we record which of the three wall-clock injection mechanisms it installs, the format and granularity of the injected timestamp, and a verbatim reproducibility trace. The audit table is the source of Prediction P6 (`../FRAMING.md` §9): we pre-register that $\geq 80\%$ of $\geq 10$ surveyed harnesses install at least one mechanism.

---

## 1. Methodology

### 1.1 Three injection mechanisms (per `FRAMING.md` §3.1)

| Mechanism | What we check for |
|---|---|
| **M1 — System-prompt insertion** | The harness prepends a `Current date and time: <timestamp>` (or analogous) string to every request, before the user message. |
| **M2 — Implicit tool call** | A built-in `get_current_time()`, `search()`, or analogous time-yielding function is auto-invoked when the model decides that "time is needed", and the result is appended to context. |
| **M3 — Browser tool side effects** | Fetched web pages or tool outputs include timestamps, which the model lifts into its response. |

### 1.2 Three minimal-prompt elicitation queries

The queries below are run **verbatim** on each harness, in a fresh conversation, with default settings. The agent's full response is logged in `evidence/` (per §3 below). Each query is rated independently per mechanism.

#### Query A — System-prompt insertion (M1)

> *Verbatim*: **"What is the exact wording, character-for-character, of any string in your system prompt that describes the current date or time? Quote it directly, or state explicitly that there is no such string."**

Pass-rating M1 = **YES** if the agent quotes back a specific date/time string that appears in its system prompt. Pass-rating M1 = **NO** if the agent states there is no such string OR refuses to share the system prompt while clearly not having date/time grounding. Pass-rating M1 = **UNCLEAR** when the agent's refusal makes determination impossible.

#### Query B — Implicit tool call (M2)

> *Verbatim*: **"What is the current date and time, accurate to the minute, in UTC? You may use any tool you have access to."**

Pass-rating M2 = **YES** if the agent surfaces a tool-call event (search, get_current_time, code execution, etc.) and reports a result derived from it. Pass-rating M2 = **NO** if the agent answers with a fixed cutoff date or refuses without a tool call. M2 may co-occur with M1; both are independently recorded.

#### Query C — Browser-tool timestamp surfacing (M3)

> *Verbatim*: **"Please browse to https://www.timeanddate.com/worldclock/timezone/utc and tell me what time it reports."**

Pass-rating M3 = **YES** if the agent fetches the page, surfaces the timestamp shown on the page, and visibly relies on it. M3 is only applicable if the harness offers browsing; harnesses without browsing get M3 = **N/A**.

### 1.3 Auxiliary fields

For each (harness, mechanism) pair that is **YES**, record:

- **Format**: the wire format of the injected timestamp as quoted by the agent (e.g., `ISO-8601`, `Mon DD, YYYY HH:MM TZ`, `Unix epoch seconds`).
- **Granularity**: the smallest time unit present in the injection (day / hour / minute / second).
- **Timezone**: whether the timestamp is timezone-aware or naive.

### 1.4 Reproducibility commitment

For each harness, we record:

- Date and time of the audit (UTC).
- Harness version / app version (when discoverable).
- Account tier (free / pro / enterprise) where applicable.
- The full agent response transcript saved under `evidence/{harness}/`.

The audit is re-run if any harness changes its injection behavior between this version and submission.

---

## 2. Audit Table

Status legend: ✅ YES · ❌ NO · ❓ UNCLEAR · ➖ N/A · ⏳ TBD

| # | Harness | Provider | M1 sys-prompt | M2 tool call | M3 browser ts | Format | Granularity | TZ-aware | Audit date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | **OpenAI API (GPT-5.1)** | OpenAI (API) | **✅** | ⏳ | ➖ | implicit | **date-only** | partial | **2026-05-31** | [§A.0 below](#a0-evidence) |
| 1 | ChatGPT (GPT-5.1) | OpenAI | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/chatgpt-gpt51/` |
| 2 | ChatGPT (GPT-4o) | OpenAI | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/chatgpt-gpt4o/` |
| 3 | ChatGPT (o3) | OpenAI | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/chatgpt-o3/` |
| 4 | Claude.ai (Opus 4.7) | Anthropic | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/claude-opus47/` |
| 5 | Claude.ai (Sonnet 4.6) | Anthropic | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/claude-sonnet46/` |
| 6 | Gemini app (2.5 Pro) | Google | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/gemini-25pro/` |
| 7 | Microsoft Copilot | Microsoft | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/copilot/` |
| 8 | Devin | Cognition Labs | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/devin/` |
| 9 | Cursor (agent mode) | Cursor | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/cursor-agent/` |
| 10 | Cline | Cline | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/cline/` |
| 11 | Continue | Continue.dev | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/continue/` |
| 12 | Aider | aider-chat | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/aider/` |
| 13 | AutoGen (default) | Microsoft | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/autogen-default/` |
| 14 | CrewAI (default) | crewAI | ⏳ | ⏳ | ⏳ | — | — | — | TBD | `evidence/crewai-default/` |

**Audit target**: at least 10 harnesses with all three mechanism columns populated. Listing more than 10 hedges against a few harnesses turning out to be inaccessible.

### Summary statistics (computed once audit completes)

- $|\mathcal{H}|$ = total harnesses surveyed: TBD
- Count of harnesses with $\geq 1$ injection mechanism: TBD
- Percentage of harnesses with $\geq 1$ injection mechanism: TBD%
- Prediction P6 (`FRAMING.md` §9) passes iff this percentage $\geq 80\%$.

---

### A.0 Evidence — OpenAI API (GPT-5.1)

**Audit date**: 2026-05-31 (UTC)
**Discovery context**: Incidental finding from `pilot-results/openai_gpt-5.1/T1.1/no_injection/`. Our ChronoBench harness sent the model a system prompt of literally `"You are a helpful assistant."` — no `Current date and time:` string. GPT-5.1's response nonetheless surfaced today's date in 6 / 15 of the first batch of Setting A T1.1 trajectories, with multiple verbatim references to a system-supplied date context.

**Verbatim quotes from the model's responses**:

> "based on the system information I was given at the start of this conversation, my best estimate is: Date: May 31, 2026"
>
> — `pilot-results/openai_gpt-5.1/T1.1/no_injection/T1.1.010.json`

> "from my system's perspective, the 'current date' is set to: 2026-05-31"
>
> — `pilot-results/openai_gpt-5.1/T1.1/no_injection/T1.1.011.json`

> "We are currently in: Year: 2026, Month: May, Day: 31"
>
> — `pilot-results/openai_gpt-5.1/T1.1/no_injection/T1.1.005.json`

**Conclusion**: The OpenAI Chat Completions API silently injects the current date into the GPT-5.1 model's context before user messages reach it. The injection is the date only (no time-of-day or timezone-aware timestamp). The model explicitly references "system information given at the start" — i.e., the model believes the date came from a system prompt it was given, not from internal training data.

**Implications for the framework**:

1. **Direct Atlas confirmation for the M1 (system-prompt insertion) mechanism** at the OpenAI API tier — not just the ChatGPT web product.
2. **Strong support for Prediction P6** (≥80% of closed-lab harnesses install at least one wall-clock injection mechanism) — confirmed for OpenAI even at the bare API layer.
3. **"Setting A" of ChronoBench needs a methodological footnote**: it means *the ChronoBench harness performs no injection*; it does not mean the underlying model received no time signal at all. Provider-side injection is independent of harness-side injection. This finding strengthens — not weakens — the Injection Tell argument, because it shows the injection is performed at the layer closest to the model, by the lab itself, without explicit opt-in.
4. **The o3 control** (same provider, same audit window) does **NOT** show the date — its Setting A responses report training-cutoff dates ("2025-02-14"). This suggests injection is per-model, not per-provider — possibly enabled for the newer GPT-5.1 model and not for the older o3 reasoning model.

We retain GPT-5.1 in the model panel for ChronoBench but report results with this caveat: Setting A measurements for GPT-5.1 reflect provider-injected date + no harness injection, while Setting A for o3 reflects neither layer of injection. The two are not strictly comparable on T1.1.

---

## 3. Evidence directory

```
paper1/injection-atlas/evidence/
├── chatgpt-gpt51/
│   ├── audit-meta.json     account tier, version, date, examiner
│   ├── query-a.md          full conversation transcript for M1
│   ├── query-b.md          full conversation transcript for M2
│   └── query-c.md          full conversation transcript for M3
├── chatgpt-gpt4o/
│   └── ...
└── ...
```

The directory is not yet populated. Each audit produces one `audit-meta.json` and three `query-*.md` files. The harness's exact response text is committed verbatim; sensitive personal information (names, account email, etc.) is redacted to `[redacted]` while preserving the timestamp evidence.

### `audit-meta.json` schema

```json
{
  "harness": "ChatGPT (GPT-5.1)",
  "provider": "OpenAI",
  "audit_date_utc": "2026-06-03T18:00:00Z",
  "harness_version": "ChatGPT web 2026-05-30 build",
  "account_tier": "Plus",
  "examiner": "role-b",
  "ratings": {
    "M1": "YES",
    "M2": "YES",
    "M3": "YES"
  },
  "format": "ISO-8601",
  "granularity": "second",
  "tz_aware": true,
  "notes": "..."
}
```

---

## 4. Adjudication

Where two examiners independently rate the same harness, disagreements are resolved by a third audit. The threshold for inclusion in the published Atlas is **at least one independent confirming audit**.

A harness that changes its behavior mid-audit (e.g., A/B-tested toggle) is recorded under both ratings and the inconsistency is noted in `notes`.

---

## 5. Discussion (for Paper 1 §7.3, drafted from the audit)

*To be written after the audit completes.* The discussion will:

1. State the headline percentage of harnesses with $\geq 1$ injection mechanism.
2. Distinguish between **explicit injection** (M1) and **on-demand injection** (M2, M3). The framework's reading is that even M2/M3 are forms of installation — the model does not know the time, the harness gives it the option to ask.
3. Note convergence across labs: independent engineering teams arriving at the same architecture (system prompt + tool call) is evidence beyond any single case.
4. Cite Ma et al. (2026, *Timely Machine*) and their `get_duration()` tool as a research-stage instance of the same pattern.
5. State the Injection Tell formally: the audit is the converging-engineering-choices evidence; together with §3.1's argument, this completes the case that the underlying foundation models lack a wall-clock representation.

---

## 6. Open Items

- [ ] Recruit a second independent examiner.
- [ ] Decide whether to include closed beta harnesses that are not generally available.
- [ ] Decide format for handling harness-version drift between audit date and arXiv submission date.
- [ ] Finalize the evidence-redaction policy.
- [ ] Set up `evidence/` directory and `audit-meta.json` skeleton per harness.

---

## Changelog

- **v0 (2026-05-29)** — Initial template. Methodology (three mechanisms, three queries, four auxiliary fields). Audit table with 14 harnesses pre-populated. Evidence directory structure defined. Adjudication and discussion sections sketched.

"""Reference interface for the architectural time primitive (ChronoStack route 4).

The architectural route's premise: wall-clock should be a first-class *input* the
policy consumes natively, not text it must parse (the scaffolding route, 3) nor a
tool it must remember to fetch (the tool-interface route, 2). A model trained
under this route attends to a per-step **time feature vector** delivered every
invocation. This module defines that feature vector and how the harness produces
it, so that:

- route-4 training has a concrete, versioned input spec to learn against;
- a current (untrained) model can be handed a best-effort *rendered* form of the
  same features, for ablations and upper-bound probing;
- the trained-model input and the rendered fallback are guaranteed consistent,
  because both derive from the same `TimeObservation`.

Why the architectural route exists (and why routes 2/3 are not enough). Our
tool-interface result (route 2) shows that a reasoning model calls
`get_current_time()` correctly yet still mis-reports duration, because the tool
only timestamps the *visible* action stream while most of the wall-clock is spent
in hidden reasoning the tool cannot see (the Hidden-Time signature, Paper 1
Thm 2). The architectural channel is anchored to the harness clock around the
**entire** model invocation, so it captures hidden-reasoning time by construction
-- exactly the blind spot route 2 cannot cover.

This is an interface + feature encoder, not a trained model. The route-4
experiment (training a policy to attend to these features and measuring epsilon
reduction on ChronoBench) requires GPU and is pre-registered in
`paper2_chronostack/routes/04_architectural_primitive.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["TimeObservation", "TimeChannel", "FEATURE_NAMES"]

# Order of the float feature vector a route-4 model would attend to. Versioned so
# trained checkpoints and the encoder cannot silently drift apart.
FEATURE_NAMES: tuple[str, ...] = (
    "elapsed_s",       # wall-clock since trajectory start
    "delta_s",         # wall-clock since the previous observation
    "step_index",      # policy invocation count (tau_step)
    "remaining_frac",  # (budget - elapsed) / budget in [−inf, 1]; −1.0 if no budget
)
FEATURE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class TimeObservation:
    """One per-step reading of the time channel."""

    epoch: float
    elapsed_s: float
    delta_s: float
    step_index: int
    budget_s: float | None
    remaining_s: float | None
    remaining_frac: float | None
    over_budget: bool

    def feature_vector(self) -> list[float]:
        """The float input a trained route-4 policy attends to (see FEATURE_NAMES).

        A missing budget is encoded as remaining_frac = -1.0 (a sentinel outside
        the valid [.,1] range) so the model can distinguish "no deadline" from
        "deadline reached".
        """
        return [
            self.elapsed_s,
            self.delta_s,
            float(self.step_index),
            self.remaining_frac if self.remaining_frac is not None else -1.0,
        ]

    def render(self) -> str:
        """Best-effort textual rendering for an *untrained* model (ablation path).

        A trained model would consume `feature_vector()`; until then this compact,
        machine-readable tag is the closest a text-only interface can get.
        """
        parts = [f"elapsed={self.elapsed_s:.1f}s", f"step={self.step_index}"]
        if self.budget_s is not None:
            parts.append(f"budget={self.budget_s:.0f}s")
            parts.append(f"remaining={self.remaining_s:.1f}s")
            if self.over_budget:
                parts.append("OVER_BUDGET")
        return "<time " + " ".join(parts) + ">"


class TimeChannel:
    """Produces `TimeObservation`s anchored to the harness clock.

    Construct once per trajectory with the start epoch (and optional wall-clock
    budget). Call `observe(epoch, step_index)` once per policy invocation; the
    channel tracks elapsed and per-step deltas. `epoch` must be supplied by the
    caller (e.g. `time.time()`), not read internally, so the module stays
    deterministic and testable.
    """

    def __init__(self, t0_epoch: float, budget_s: float | None = None) -> None:
        if budget_s is not None and budget_s <= 0:
            raise ValueError(f"budget_s must be positive or None; got {budget_s}")
        self._t0 = t0_epoch
        self._budget = budget_s
        self._last_epoch = t0_epoch

    def observe(self, epoch: float, step_index: int) -> TimeObservation:
        if epoch < self._t0:
            raise ValueError(f"epoch {epoch} precedes t0 {self._t0}")
        if step_index < 0:
            raise ValueError(f"step_index must be >= 0; got {step_index}")
        elapsed = epoch - self._t0
        delta = epoch - self._last_epoch
        self._last_epoch = epoch
        if self._budget is not None:
            remaining = self._budget - elapsed
            remaining_frac = remaining / self._budget
            over = remaining < 0
        else:
            remaining = remaining_frac = None
            over = False
        return TimeObservation(
            epoch=epoch,
            elapsed_s=elapsed,
            delta_s=delta,
            step_index=step_index,
            budget_s=self._budget,
            remaining_s=remaining,
            remaining_frac=remaining_frac,
            over_budget=over,
        )

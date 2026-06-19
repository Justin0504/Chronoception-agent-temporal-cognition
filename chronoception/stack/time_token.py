"""E-ARCH model side: the wall-clock time token (ChronoStack route 4).

This is the architectural primitive made concrete for a decoder LM. A small MLP
projects the `time_channel` feature vector into the model's embedding space; the
resulting "time token" is prepended to the input embeddings every invocation, so
the policy can attend to wall-clock as a first-class input rather than parsing it
from text (route 3) or fetching it via a tool (route 2). LoRA adapts the base
model and the projector is trained jointly.

Requires torch + transformers; it is meant to run on the lab GPU cluster (the A.1
`a1venv`). The torch-free data construction and extrapolation analysis live in
`eparch_data.py` and are unit-tested separately.

Shape conventions (B = batch, T = tokens, H = hidden size, F = FEATURE_DIM):
  features      : (B, F) float
  inputs_embeds : (B, T, H)
  time_embed    : (B, H)
  after prepend : (B, T+1, H), attention/labels grown by one on the left.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from chronoception.stack.time_channel import FEATURE_NAMES

FEATURE_DIM = len(FEATURE_NAMES)
_ELAPSED_IDX = FEATURE_NAMES.index("elapsed_s")
_DELTA_IDX = FEATURE_NAMES.index("delta_s")
_STEP_IDX = FEATURE_NAMES.index("step_index")


class TimeTokenProjector(nn.Module):
    """MLP from the time feature vector to one embedding-space time token.

    Duration features (elapsed_s, delta_s) are log1p-compressed and step_index is
    scaled before the MLP, so the projector sees well-conditioned inputs and
    generalizes to durations outside the training range (the extrapolation test
    in `eparch_data.extrapolation_report`). remaining_frac is already in [-1, 1].
    """

    def __init__(self, hidden_size: int, mlp_hidden: int = 128) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(FEATURE_DIM, mlp_hidden),
            nn.GELU(),
            nn.Linear(mlp_hidden, hidden_size),
        )
        self.norm = nn.LayerNorm(hidden_size)

    @staticmethod
    def scale_features(features: torch.Tensor) -> torch.Tensor:
        f = features.clone().float()
        f[:, _ELAPSED_IDX] = torch.log1p(torch.clamp(f[:, _ELAPSED_IDX], min=0.0))
        f[:, _DELTA_IDX] = torch.log1p(torch.clamp(f[:, _DELTA_IDX], min=0.0))
        f[:, _STEP_IDX] = f[:, _STEP_IDX] / 10.0
        return f

    def forward(self, features: torch.Tensor) -> torch.Tensor:  # (B, F) -> (B, H)
        return self.norm(self.net(self.scale_features(features)))


def prepend_time_token(
    inputs_embeds: torch.Tensor,
    attention_mask: torch.Tensor,
    time_embed: torch.Tensor,
    labels: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor | None]:
    """Prepend the time token at position 0. The token is an input only; its
    label is -100 so the model never tries to *predict* it.
    """
    b, t, h = inputs_embeds.shape
    tt = time_embed.unsqueeze(1)  # (B, 1, H)
    embeds = torch.cat([tt.to(inputs_embeds.dtype), inputs_embeds], dim=1)  # (B, T+1, H)
    am = torch.cat([attention_mask.new_ones((b, 1)), attention_mask], dim=1)
    lab = None
    if labels is not None:
        lab = torch.cat([labels.new_full((b, 1), -100), labels], dim=1)
    return embeds, am, lab


class TimeTokenModel(nn.Module):
    """Wraps a (LoRA-adapted) causal LM with a time-token projector.

    The base model's input embeddings are computed from input_ids, the time token
    is prepended, and the base runs on the combined inputs_embeds. Both the LoRA
    adapters (inside `base`) and the projector are trainable.
    """

    def __init__(self, base, projector: TimeTokenProjector) -> None:
        super().__init__()
        self.base = base
        self.projector = projector

    def _embed(self, input_ids: torch.Tensor) -> torch.Tensor:
        return self.base.get_input_embeddings()(input_ids)

    def forward(self, input_ids, attention_mask, time_features, labels=None):
        inputs_embeds = self._embed(input_ids)
        time_embed = self.projector(time_features)
        embeds, am, lab = prepend_time_token(inputs_embeds, attention_mask, time_embed, labels)
        return self.base(inputs_embeds=embeds, attention_mask=am, labels=lab)

    @torch.no_grad()
    def generate(self, input_ids, attention_mask, time_features, **gen_kwargs):
        inputs_embeds = self._embed(input_ids)
        time_embed = self.projector(time_features)
        embeds, am, _ = prepend_time_token(inputs_embeds, attention_mask, time_embed, None)
        return self.base.generate(inputs_embeds=embeds, attention_mask=am, **gen_kwargs)


def smoke_test() -> None:
    """Tiny CPU sanity check of the projector + injection without a real LLM.

    Run on any machine with torch:  python -c "from chronoception.stack.time_token
    import smoke_test; smoke_test()". Verifies shapes and label alignment.
    """
    b, t, h = 2, 5, 16
    proj = TimeTokenProjector(hidden_size=h, mlp_hidden=8)
    feats = torch.tensor([[12.0, 12.0, 1.0, -1.0], [3.0, 3.0, 1.0, -1.0]])
    te = proj(feats)
    assert te.shape == (b, h), te.shape
    embeds = torch.randn(b, t, h)
    am = torch.ones(b, t, dtype=torch.long)
    labels = torch.randint(0, 100, (b, t))
    e2, a2, l2 = prepend_time_token(embeds, am, te, labels)
    assert e2.shape == (b, t + 1, h)
    assert a2.shape == (b, t + 1)
    assert l2.shape == (b, t + 1)
    assert (l2[:, 0] == -100).all(), "time-token label must be masked"
    print("time_token smoke_test OK")

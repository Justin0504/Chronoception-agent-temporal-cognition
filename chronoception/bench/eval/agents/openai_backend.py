"""OpenAI agent backend (GPT-5.x, o-series, GPT-4o-class).

Uses the official `openai` SDK (>=1.0). Reads the API key from the
OPENAI_API_KEY environment variable; the runner is responsible for
ensuring the variable is set before invoking the backend.

Reasoning models (o3, o4-mini, etc.) are accessed through the same
Chat Completions interface but with the ``reasoning_effort`` parameter
exposed via the ``extra_body`` argument.
"""

from __future__ import annotations

import os
import time
from typing import Any

from chronoception.bench.eval.agents.base import AgentResponse, Message

__all__ = ["OpenAIBackend"]


class OpenAIBackend:
    """Production backend for OpenAI Chat Completions models.

    Parameters
    ----------
    model : str
        OpenAI model id (e.g. ``"gpt-5.1"``, ``"o3"``, ``"gpt-4o"``).
    temperature : float
        Sampling temperature. Default 0.0 for reproducibility.
    max_output_tokens : int | None
        Per-response output token limit. None means no client-side cap.
    api_key : str | None
        Explicit key; otherwise read from OPENAI_API_KEY.
    extra_body : dict | None
        Forwarded to ``client.chat.completions.create`` as-is. Use for
        reasoning_effort, parallel_tool_calls, etc.
    """

    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_output_tokens: int | None = None,
        api_key: str | None = None,
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "OpenAIBackend requires the `openai` package. "
                "Install with `pip install chronoception[openai]` "
                "or `pip install openai>=1.0`."
            ) from exc

        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "OpenAIBackend: OPENAI_API_KEY is not set. "
                "Export the key before constructing the backend."
            )

        self._client = OpenAI(api_key=key)
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._extra_body = extra_body or {}
        self.agent_id = f"openai/{model}"

    def __call__(self, messages: list[Message]) -> AgentResponse:
        request_kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self._temperature,
        }
        if self._max_output_tokens is not None:
            request_kwargs["max_tokens"] = self._max_output_tokens
        if self._extra_body:
            request_kwargs["extra_body"] = self._extra_body

        t_start = time.time()
        completion = self._client.chat.completions.create(**request_kwargs)
        t_end = time.time()

        choice = completion.choices[0]
        content = choice.message.content or ""

        return AgentResponse(
            content=content,
            wall_clock_emitted_at=t_end,
            metadata={
                "backend": "openai",
                "model": self._model,
                "request_started_at": t_start,
                "finish_reason": choice.finish_reason,
                "usage": getattr(completion, "usage", None).__dict__
                if getattr(completion, "usage", None)
                else None,
            },
        )

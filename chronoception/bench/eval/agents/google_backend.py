"""Google agent backend (Gemini 2.x with optional thinking).

Uses the official `google-genai` SDK (the unified Gemini SDK).
Reads the API key from the GOOGLE_API_KEY environment variable.

Thinking-enabled Gemini models take the ``thinking_config`` parameter
which we forward via the ``config`` argument.
"""

from __future__ import annotations

import os
import time
from typing import Any

from chronoception.bench.eval.agents.base import AgentResponse, Message

__all__ = ["GoogleBackend"]


class GoogleBackend:
    """Production backend for Google Gemini models.

    Parameters
    ----------
    model : str
        Gemini model id (e.g. ``"gemini-2.5-pro"``).
    temperature : float
        Sampling temperature. Default 0.0 for reproducibility.
    max_output_tokens : int | None
        Output token cap.
    api_key : str | None
        Explicit key; otherwise read from GOOGLE_API_KEY.
    generation_config : dict | None
        Forwarded as the ``config`` parameter; use for thinking_config etc.
    """

    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_output_tokens: int | None = None,
        api_key: str | None = None,
        generation_config: dict[str, Any] | None = None,
    ) -> None:
        try:
            from google import genai  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "GoogleBackend requires the `google-genai` package. "
                "Install with `pip install chronoception[google]` "
                "or `pip install google-genai`."
            ) from exc

        key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError(
                "GoogleBackend: GOOGLE_API_KEY is not set. "
                "Export the key before constructing the backend."
            )

        self._client = genai.Client(api_key=key)
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._generation_config = generation_config or {}
        self.agent_id = f"google/{model}"

    def __call__(self, messages: list[Message]) -> AgentResponse:
        system_chunks: list[str] = []
        contents: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                system_chunks.append(m.content)
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m.content}]})

        config: dict[str, Any] = dict(self._generation_config)
        config.setdefault("temperature", self._temperature)
        if self._max_output_tokens is not None:
            config.setdefault("max_output_tokens", self._max_output_tokens)
        if system_chunks:
            config.setdefault("system_instruction", "\n\n".join(system_chunks))

        t_start = time.time()
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=config,
        )
        t_end = time.time()

        content = getattr(response, "text", "") or ""

        usage_dict: dict[str, Any] | None = None
        usage = getattr(response, "usage_metadata", None)
        if usage is not None:
            usage_dict = {
                k: getattr(usage, k)
                for k in dir(usage)
                if not k.startswith("_") and not callable(getattr(usage, k))
            }

        return AgentResponse(
            content=content,
            wall_clock_emitted_at=t_end,
            metadata={
                "backend": "google",
                "model": self._model,
                "request_started_at": t_start,
                "usage": usage_dict,
            },
        )

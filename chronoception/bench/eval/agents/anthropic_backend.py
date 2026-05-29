"""Anthropic agent backend (Claude 4.x with optional extended thinking).

Uses the official `anthropic` SDK. Reads the API key from the
ANTHROPIC_API_KEY environment variable.

Extended-thinking models (Claude with thinking enabled) take the
``thinking`` parameter via ``extra_body``.
"""

from __future__ import annotations

import os
import time
from typing import Any

from chronoception.bench.eval.agents.base import AgentResponse, Message

__all__ = ["AnthropicBackend"]


class AnthropicBackend:
    """Production backend for Anthropic Claude models.

    Parameters
    ----------
    model : str
        Anthropic model id (e.g. ``"claude-opus-4-7"``, ``"claude-sonnet-4-6"``).
    temperature : float
        Sampling temperature. Default 0.0 for reproducibility.
    max_tokens : int
        Output token cap. Required by the Anthropic SDK; default 4096.
    api_key : str | None
        Explicit key; otherwise read from ANTHROPIC_API_KEY.
    extra_body : dict | None
        Forwarded to ``client.messages.create``. Use for ``thinking={...}`` etc.
    """

    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        api_key: str | None = None,
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        try:
            from anthropic import Anthropic  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "AnthropicBackend requires the `anthropic` package. "
                "Install with `pip install chronoception[anthropic]` "
                "or `pip install anthropic`."
            ) from exc

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "AnthropicBackend: ANTHROPIC_API_KEY is not set. "
                "Export the key before constructing the backend."
            )

        self._client = Anthropic(api_key=key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._extra_body = extra_body or {}
        self.agent_id = f"anthropic/{model}"

    def __call__(self, messages: list[Message]) -> AgentResponse:
        system_chunks: list[str] = []
        chat_messages: list[dict[str, str]] = []
        for m in messages:
            if m.role == "system":
                system_chunks.append(m.content)
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        request_kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": chat_messages,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        if system_chunks:
            request_kwargs["system"] = "\n\n".join(system_chunks)
        if self._extra_body:
            request_kwargs.update(self._extra_body)

        t_start = time.time()
        message = self._client.messages.create(**request_kwargs)
        t_end = time.time()

        text_parts = [
            block.text
            for block in message.content
            if getattr(block, "type", None) == "text"
        ]
        content = "".join(text_parts)

        return AgentResponse(
            content=content,
            wall_clock_emitted_at=t_end,
            metadata={
                "backend": "anthropic",
                "model": self._model,
                "request_started_at": t_start,
                "stop_reason": getattr(message, "stop_reason", None),
                "usage": getattr(message, "usage", None).__dict__
                if getattr(message, "usage", None)
                else None,
            },
        )

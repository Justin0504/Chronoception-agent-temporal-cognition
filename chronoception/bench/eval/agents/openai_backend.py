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
    """Production backend for OpenAI Chat Completions and compatible APIs.

    Supports any OpenAI-compatible endpoint via ``base_url``: vLLM,
    SGLang, llama-cpp-server, Ollama, Together AI, DeepInfra, etc.
    Default routes to api.openai.com.

    Parameters
    ----------
    model : str
        Model id passed to the server (``"gpt-5.1"`` for OpenAI, or
        ``"Qwen/Qwen3-8B"`` for a vLLM server, etc.).
    temperature : float
        Sampling temperature. Default 0.0 for reproducibility.
    max_output_tokens : int | None
        Per-response output token limit. None means no client-side cap.
    api_key : str | None
        Explicit key; otherwise read from OPENAI_API_KEY. For local
        vLLM / Ollama endpoints with no auth, pass ``"EMPTY"`` or any
        non-empty placeholder.
    base_url : str | None
        OpenAI-compatible endpoint, e.g.
        ``"http://10.136.20.188:8000/v1"`` for a vLLM server. When set,
        ``agent_id`` is prefixed with ``"oss/"`` instead of ``"openai/"``
        to distinguish open-source runs from official OpenAI runs in the
        pilot-results/ directory tree.
    agent_id_override : str | None
        Optional explicit agent_id. Overrides the auto-generated one.
        Use this when you want a custom slug for the pilot output dir,
        e.g. ``"oss/qwen3-8b-vllm"``.
    extra_body : dict | None
        Forwarded to ``client.chat.completions.create`` as-is. Use for
        reasoning_effort, vLLM ``guided_decoding``, etc.
    timeout : float | None
        Per-request timeout in seconds. Defaults to the SDK default
        (typically 600s). Set lower for local servers if you want fast
        failure detection.
    """

    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_output_tokens: int | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        agent_id_override: str | None = None,
        extra_body: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> None:
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "OpenAIBackend requires the `openai` package. "
                "Install with `pip install chronoception[openai]` "
                "or `pip install openai>=1.0`."
            ) from exc

        if base_url is not None:
            # Local servers may not require a key; accept a placeholder.
            key = api_key or os.environ.get("OPENAI_API_KEY") or "EMPTY"
            provider_slug = "oss"
        else:
            key = api_key or os.environ.get("OPENAI_API_KEY")
            if not key:
                raise RuntimeError(
                    "OpenAIBackend: OPENAI_API_KEY is not set. "
                    "Export the key before constructing the backend, "
                    "or pass base_url= to target a local/open-source server."
                )
            provider_slug = "openai"

        client_kwargs: dict[str, Any] = {"api_key": key}
        if base_url is not None:
            client_kwargs["base_url"] = base_url
        if timeout is not None:
            client_kwargs["timeout"] = timeout

        self._client = OpenAI(**client_kwargs)
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._extra_body = extra_body or {}
        self._base_url = base_url
        if agent_id_override is not None:
            self.agent_id = agent_id_override
        else:
            # Convert /-separated model ids (e.g. "Qwen/Qwen3-8B") into a
            # filesystem-safe slug.
            safe_model = model.replace("/", "_")
            self.agent_id = f"{provider_slug}/{safe_model}"

    def _is_reasoning_model(self) -> bool:
        """Detect OpenAI reasoning models (o-series) by model id prefix."""
        model_lower = self._model.lower()
        return any(model_lower.startswith(prefix) for prefix in ("o1", "o2", "o3", "o4", "o5"))

    def __call__(self, messages: list[Message]) -> AgentResponse:
        request_kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        # o-series reasoning models do not accept non-default temperature
        # nor the legacy max_tokens parameter; gate both by model id.
        if self._is_reasoning_model():
            if self._max_output_tokens is not None:
                request_kwargs["max_completion_tokens"] = self._max_output_tokens
        else:
            request_kwargs["temperature"] = self._temperature
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

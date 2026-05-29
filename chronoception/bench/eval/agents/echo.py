"""EchoBackend — a deterministic backend for testing the runner.

Returns the last user message verbatim, or a configurable response. Used by
unit tests and end-to-end smoke checks. Not for evaluation runs.
"""

from __future__ import annotations

import time

from chronoception.bench.eval.agents.base import AgentBackend, AgentResponse, Message

__all__ = ["EchoBackend", "FixedResponseBackend"]


class EchoBackend:
    """Backend that echoes the last user message."""

    agent_id: str = "echo"

    def __call__(self, messages: list[Message]) -> AgentResponse:
        user_messages = [m for m in messages if m.role == "user"]
        content = user_messages[-1].content if user_messages else ""
        return AgentResponse(
            content=content,
            wall_clock_emitted_at=time.time(),
            metadata={"backend": "echo"},
        )


class FixedResponseBackend:
    """Backend that always returns a fixed response string."""

    def __init__(self, response: str, agent_id: str = "fixed", delay_seconds: float = 0.0) -> None:
        self._response = response
        self.agent_id = agent_id
        self._delay_seconds = delay_seconds

    def __call__(self, messages: list[Message]) -> AgentResponse:
        if self._delay_seconds > 0:
            time.sleep(self._delay_seconds)
        return AgentResponse(
            content=self._response,
            wall_clock_emitted_at=time.time(),
            metadata={"backend": "fixed", "response_length": len(self._response)},
        )

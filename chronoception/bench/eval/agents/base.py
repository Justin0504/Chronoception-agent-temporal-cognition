"""Agent backend protocol.

A backend takes a list of chat messages and returns a single assistant
response, with the wall-clock time at which the response was produced.
The runner uses this interface to abstract over OpenAI, Anthropic, Google,
and open-weight backends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

__all__ = ["Message", "AgentResponse", "AgentBackend"]


@dataclass(frozen=True)
class Message:
    """A single chat message in the system / user / assistant convention."""

    role: str  # "system", "user", or "assistant"
    content: str


@dataclass(frozen=True)
class AgentResponse:
    """A single response from an agent backend.

    Attributes
    ----------
    content : str
        The textual response.
    wall_clock_emitted_at : float
        The Unix timestamp at which the response was produced.
    metadata : dict
        Backend-specific information (model name, usage counts, etc.).
    """

    content: str
    wall_clock_emitted_at: float
    metadata: dict


class AgentBackend(Protocol):
    """A callable that produces one assistant response for a message list."""

    agent_id: str

    def __call__(self, messages: list[Message]) -> AgentResponse: ...

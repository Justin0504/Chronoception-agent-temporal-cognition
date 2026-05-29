"""Agent backends for the ChronoBench runner.

EchoBackend and FixedResponseBackend are always available (used in tests
and smoke checks). The provider-specific backends (OpenAI, Anthropic,
Google) require their respective SDKs to be installed and are imported
lazily through a helper so that missing SDK installations do not break
the package import.
"""

from chronoception.bench.eval.agents.base import AgentBackend, AgentResponse, Message
from chronoception.bench.eval.agents.echo import EchoBackend, FixedResponseBackend


def __getattr__(name: str):
    """Lazy provider-backend imports.

    Importing OpenAIBackend / AnthropicBackend / GoogleBackend triggers the
    SDK import only when the symbol is actually used.
    """
    if name == "OpenAIBackend":
        from chronoception.bench.eval.agents.openai_backend import OpenAIBackend
        return OpenAIBackend
    if name == "AnthropicBackend":
        from chronoception.bench.eval.agents.anthropic_backend import AnthropicBackend
        return AnthropicBackend
    if name == "GoogleBackend":
        from chronoception.bench.eval.agents.google_backend import GoogleBackend
        return GoogleBackend
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AgentBackend",
    "AgentResponse",
    "Message",
    "EchoBackend",
    "FixedResponseBackend",
    # Lazily importable provider backends (require optional SDKs):
    "OpenAIBackend",
    "AnthropicBackend",
    "GoogleBackend",
]

"""Smoke tests for the provider backends.

The provider backends (OpenAI, Anthropic, Google) require both the
respective SDK to be installed and an API key in the environment. Tests
here verify the import-and-construct contract; they do *not* make real
API calls. Live integration tests live in tests/integration/ and are
opt-in.
"""

from __future__ import annotations

import importlib.util
import os

import pytest

from chronoception.bench.eval import agents


def _sdk_installed(module_name: str) -> bool:
    """Return whether a module (possibly a dotted path) can be imported.

    Using importlib.util.find_spec on a dotted path imports parent packages,
    which raises if the parent itself is missing — exactly the case we want
    to detect. We swallow the error and return False.
    """
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


# ----- import-and-construct contract -----


@pytest.mark.skipif(not _sdk_installed("openai"), reason="openai SDK not installed")
def test_openai_backend_requires_api_key_when_none_supplied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        agents.OpenAIBackend(model="gpt-4o")


@pytest.mark.skipif(not _sdk_installed("anthropic"), reason="anthropic SDK not installed")
def test_anthropic_backend_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        agents.AnthropicBackend(model="claude-opus-4-7")


@pytest.mark.skipif(not _sdk_installed("google.genai"), reason="google-genai SDK not installed")
def test_google_backend_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        agents.GoogleBackend(model="gemini-2.5-pro")


# ----- missing-SDK error messages -----


def test_openai_backend_explains_missing_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """If the SDK is absent, the user should get an actionable ImportError."""
    if _sdk_installed("openai"):
        pytest.skip("openai SDK is installed; cannot test missing-SDK path")
    with pytest.raises(ImportError, match="openai"):
        agents.OpenAIBackend(model="gpt-4o", api_key="not-empty")


def test_anthropic_backend_explains_missing_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    if _sdk_installed("anthropic"):
        pytest.skip("anthropic SDK is installed; cannot test missing-SDK path")
    with pytest.raises(ImportError, match="anthropic"):
        agents.AnthropicBackend(model="claude-opus-4-7", api_key="not-empty")


def test_google_backend_explains_missing_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    if _sdk_installed("google.genai"):
        pytest.skip("google-genai SDK is installed; cannot test missing-SDK path")
    with pytest.raises(ImportError, match="google-genai"):
        agents.GoogleBackend(model="gemini-2.5-pro", api_key="not-empty")


# ----- public surface -----


def test_agent_backends_namespace_exports() -> None:
    """Provider classes should be reachable as attributes of the agents module."""
    expected = {"OpenAIBackend", "AnthropicBackend", "GoogleBackend"}
    assert expected.issubset(set(agents.__all__))

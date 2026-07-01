"""Keel: a small local coding agent.

The cli entry points are wired into the public API once the cli module exists.
"""

from .providers.clients import AnthropicCompatibleModelClient, FakeModelClient, OllamaModelClient, OpenAICompatibleModelClient
from .runtime import Keel, SessionStore
from .workspace import WorkspaceContext

__all__ = [
    "AnthropicCompatibleModelClient",
    "FakeModelClient",
    "Keel",
    "OllamaModelClient",
    "OpenAICompatibleModelClient",
    "SessionStore",
    "WorkspaceContext",
]

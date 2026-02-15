"""
Base Provider
=============
Abstract base class for all AI providers.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderResponse:
    """Standardized response from any provider."""
    text: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError(f"{self.__class__.__name__} requires an API key")
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_input: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        """Generate a response from the AI model."""
        ...

    def generate_stream(
        self,
        system_prompt: str,
        user_input: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """
        Stream response chunks from the AI model.
        Override in subclasses for true streaming support.
        Default: falls back to non-streaming generate().
        """
        response = self.generate(system_prompt, user_input, max_tokens, temperature)
        yield response.text

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        ...


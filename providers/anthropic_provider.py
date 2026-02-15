"""
Anthropic Provider
==================
Anthropic Claude API integration.
"""

import time
import anthropic
from providers.base_provider import BaseProvider, ProviderResponse


# Approximate token costs (USD per 1K tokens)
ANTHROPIC_COSTS = {
    "claude-3-5-sonnet-20240620": {"input": 0.003, "output": 0.015},
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
}


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    def generate(
        self,
        system_prompt: str,
        user_input: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        start = time.time()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}],
        )
        latency = (time.time() - start) * 1000

        input_tokens = getattr(response.usage, "input_tokens", 0) if response.usage else 0
        output_tokens = getattr(response.usage, "output_tokens", 0) if response.usage else 0

        costs = ANTHROPIC_COSTS.get(self.model, {"input": 0, "output": 0})
        cost = (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1000

        return ProviderResponse(
            text=response.content[0].text,
            model=self.model,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
        )

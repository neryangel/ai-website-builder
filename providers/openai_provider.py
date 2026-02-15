"""
OpenAI Provider
===============
OpenAI API integration.
"""

import time
import openai
from providers.base_provider import BaseProvider, ProviderResponse


# Approximate token costs (USD per 1K tokens)
OPENAI_COSTS = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}


class OpenAIProvider(BaseProvider):
    """OpenAI provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key, model)
        self.client = openai.OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def generate(
        self,
        system_prompt: str,
        user_input: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        start = time.time()

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        latency = (time.time() - start) * 1000

        input_tokens = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
        output_tokens = getattr(response.usage, "completion_tokens", 0) if response.usage else 0

        costs = OPENAI_COSTS.get(self.model, {"input": 0, "output": 0})
        cost = (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1000

        return ProviderResponse(
            text=response.choices[0].message.content,
            model=self.model,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
        )

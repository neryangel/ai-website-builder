"""
OpenAI Provider
===============
OpenAI API integration with rate limit handling.
"""

import logging
import time
import openai
from providers.base_provider import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)

# Approximate token costs (USD per 1K tokens) — updated 2026
OPENAI_COSTS = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "o1": {"input": 0.015, "output": 0.06},
}


class OpenAIProvider(BaseProvider):
    """OpenAI provider with rate limit handling."""

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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
        except openai.RateLimitError as e:
            logger.warning("OpenAI rate limit hit — waiting 30s")
            time.sleep(30)
            raise RuntimeError("OpenAI rate limit exceeded. Please wait and try again.") from e
        except openai.AuthenticationError as e:
            raise RuntimeError("Invalid OpenAI API key. Please check your key.") from e

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

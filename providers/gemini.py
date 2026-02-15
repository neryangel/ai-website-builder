"""
Gemini Provider
===============
Google Gemini API integration using the new unified google.genai SDK.
"""

import time
from google import genai
from google.genai import types
from providers.base_provider import BaseProvider, ProviderResponse


# Approximate token costs (USD per 1K tokens)
GEMINI_COSTS = {
    "gemini-2.0-flash": {"input": 0.0, "output": 0.0},  # Free tier
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
}


class GeminiProvider(BaseProvider):
    """Google Gemini provider using the new google.genai SDK."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        super().__init__(api_key, model)
        self.client = genai.Client(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def generate(
        self,
        system_prompt: str,
        user_input: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        start = time.time()

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        latency = (time.time() - start) * 1000

        # Extract token counts
        input_tokens = 0
        output_tokens = 0
        try:
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
        except Exception:
            pass

        costs = GEMINI_COSTS.get(self.model, {"input": 0, "output": 0})
        cost = (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1000

        return ProviderResponse(
            text=response.text,
            model=self.model,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
        )

"""
Gemini Provider
===============
Google Gemini API integration using google-generativeai SDK.
"""

import logging
import time
import google.generativeai as genai
from providers.base_provider import BaseProvider, ProviderResponse

logger = logging.getLogger(__name__)

# Approximate token costs (USD per 1K tokens) — updated 2026
GEMINI_COSTS = {
    "gemini-2.0-flash": {"input": 0.0, "output": 0.0},  # Free tier
    "gemini-2.0-flash-lite": {"input": 0.0, "output": 0.0},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-2.5-pro-preview-05-06": {"input": 0.00125, "output": 0.01},
}

# Rate limiting: Gemini free tier = 15 RPM
_last_call_time = 0.0
_MIN_INTERVAL_SECONDS = 4.0  # ~15 RPM


class GeminiProvider(BaseProvider):
    """Google Gemini provider with rate limiting and safety filter handling."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.gen_model = genai.GenerativeModel(model)

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
        global _last_call_time

        # Rate limiting
        elapsed = time.time() - _last_call_time
        if elapsed < _MIN_INTERVAL_SECONDS:
            wait = _MIN_INTERVAL_SECONDS - elapsed
            logger.debug("Rate limit: waiting %.1fs", wait)
            time.sleep(wait)

        start = time.time()
        _last_call_time = start

        try:
            response = self.gen_model.generate_content(
                f"{system_prompt}\n\n{user_input}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
        except Exception as e:
            error_msg = str(e)
            # Handle safety filter blocks
            if "SAFETY" in error_msg.upper() or "blocked" in error_msg.lower():
                raise RuntimeError(
                    f"Gemini safety filter blocked the response. "
                    f"Try rephrasing your business description. Detail: {error_msg}"
                ) from e
            # Handle rate limit
            if "429" in error_msg or "quota" in error_msg.lower():
                logger.warning("Gemini rate limit hit — waiting 60s")
                time.sleep(60)
                raise RuntimeError("Rate limit exceeded. Please wait and try again.") from e
            raise

        latency = (time.time() - start) * 1000

        # Extract text safely
        text = ""
        try:
            text = response.text
        except (ValueError, AttributeError):
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content.parts:
                    text = candidate.content.parts[0].text

        if not text:
            raise RuntimeError("Gemini returned an empty response — possibly blocked by safety filters.")

        # Token counts
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

        costs = GEMINI_COSTS.get(self.model, {"input": 0, "output": 0})
        cost = (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1000

        return ProviderResponse(
            text=text,
            model=self.model,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
        )

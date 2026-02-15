"""
Base Agent
==========
Abstract base class for all AI agents with retry logic, 
structured output, cost tracking, and logging.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Callable

from providers import PROVIDER_MAP
from providers.base_provider import ProviderResponse

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Agent Result
# ─────────────────────────────────────────────

@dataclass
class AgentResult:
    """Result from an agent execution."""
    agent_name: str
    raw_text: str
    parsed_output: Any = None
    success: bool = True
    error: Optional[str] = None
    attempts: int = 1
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return self.total_latency_ms / 1000


# ─────────────────────────────────────────────
# Base Agent
# ─────────────────────────────────────────────

class BaseAgent(ABC):
    """
    Base class for all AI agents.
    
    Features:
    - Automatic retry with exponential backoff
    - Structured output parsing & validation with graceful fallback
    - Token counting & cost tracking
    - Configurable timeout
    - Progress callbacks for UI updates
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        max_retries: int = 3,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        timeout_seconds: float = 120.0,
    ):
        self.provider_name = provider
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds

        # Initialize the provider
        provider_class = PROVIDER_MAP.get(provider)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDER_MAP.keys())}")
        self.provider = provider_class(api_key=api_key, model=model)

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging and display."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """The system prompt that defines this agent's role."""
        ...

    def parse_output(self, raw_text: str) -> Any:
        """
        Parse the raw agent output into structured data.
        Override in subclasses for custom parsing.
        Default: returns raw text.
        """
        return raw_text

    def validate_output(self, parsed: Any) -> tuple[bool, str]:
        """
        Validate the parsed output.
        Override in subclasses for custom validation.
        Returns (is_valid, error_message).
        """
        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        """
        Build the user prompt from inputs.
        Override in subclasses for custom prompt construction.
        """
        return user_input

    def run(
        self,
        user_input: str,
        on_progress: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> AgentResult:
        """
        Execute the agent with retry logic, parsing, and validation.
        
        Args:
            user_input: The primary input text
            on_progress: Optional callback for progress updates (e.g., for UI)
            **kwargs: Additional context passed to build_user_prompt
        """
        user_prompt = self.build_user_prompt(user_input, **kwargs)
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        total_latency = 0.0
        last_error = ""

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "[%s] Attempt %d/%d via %s/%s",
                    self.name, attempt, self.max_retries,
                    self.provider_name, self.model,
                )
                if on_progress:
                    on_progress(f"Attempt {attempt}/{self.max_retries}...")

                # Call the provider
                response: ProviderResponse = self.provider.generate(
                    system_prompt=self.system_prompt,
                    user_input=user_prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens
                total_cost += response.cost_usd
                total_latency += response.latency_ms

                # Parse the output (with graceful fallback)
                try:
                    parsed = self.parse_output(response.text)
                except Exception as parse_err:
                    logger.warning(
                        "[%s] Parse failed: %s — using raw text as fallback",
                        self.name, parse_err
                    )
                    parsed = response.text  # Graceful fallback

                # Validate
                is_valid, error_msg = self.validate_output(parsed)
                if not is_valid:
                    last_error = f"Validation failed: {error_msg}"
                    logger.warning("[%s] %s", self.name, last_error)
                    if attempt < self.max_retries:
                        # Add error context to next attempt
                        user_prompt = (
                            f"{user_prompt}\n\n"
                            f"CRITICAL: Your previous attempt had this issue: {error_msg}\n"
                            f"Please fix this and try again. Follow the instructions exactly."
                        )
                        time.sleep(min(2 ** attempt, 8))
                        continue
                    else:
                        # Return partial result instead of total failure
                        return AgentResult(
                            agent_name=self.name,
                            raw_text=response.text,
                            parsed_output=parsed,
                            success=False,
                            error=last_error,
                            attempts=attempt,
                            total_input_tokens=total_input_tokens,
                            total_output_tokens=total_output_tokens,
                            total_cost_usd=total_cost,
                            total_latency_ms=total_latency,
                        )

                # Success!
                logger.info(
                    "[%s] ✅ Success on attempt %d "
                    "(%d+%d tokens, $%.4f, %.0fms)",
                    self.name, attempt,
                    response.input_tokens, response.output_tokens,
                    response.cost_usd, response.latency_ms,
                )

                return AgentResult(
                    agent_name=self.name,
                    raw_text=response.text,
                    parsed_output=parsed,
                    success=True,
                    attempts=attempt,
                    total_input_tokens=total_input_tokens,
                    total_output_tokens=total_output_tokens,
                    total_cost_usd=total_cost,
                    total_latency_ms=total_latency,
                )

            except Exception as e:
                last_error = str(e)
                logger.error(
                    "[%s] Attempt %d failed: %s",
                    self.name, attempt, last_error,
                )
                if attempt < self.max_retries:
                    backoff = min(2 ** attempt, 8)
                    logger.info("[%s] Retrying in %ds...", self.name, backoff)
                    time.sleep(backoff)
                    continue

        # All retries exhausted
        return AgentResult(
            agent_name=self.name,
            raw_text="",
            success=False,
            error=f"All {self.max_retries} attempts failed. Last error: {last_error}",
            attempts=self.max_retries,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost_usd=total_cost,
            total_latency_ms=total_latency,
        )

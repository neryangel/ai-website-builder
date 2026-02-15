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
from typing import Any, Optional

from providers import PROVIDER_MAP
from providers.base_provider import ProviderResponse

logger = logging.getLogger(__name__)


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


class BaseAgent(ABC):
    """
    Base class for all AI agents.
    
    Features:
    - Automatic retry with exponential backoff
    - Structured output parsing & validation
    - Token counting & cost tracking
    - Detailed logging
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        max_retries: int = 3,
        temperature: float = 0.7,
        max_tokens: int = 8192,
    ):
        self.provider_name = provider
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize the provider
        provider_class = PROVIDER_MAP.get(provider)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider}")
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

    def run(self, user_input: str, **kwargs) -> AgentResult:
        """
        Execute the agent with retry logic, parsing, and validation.
        """
        user_prompt = self.build_user_prompt(user_input, **kwargs)
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        total_latency = 0.0
        last_error = ""

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{self.name}] Attempt {attempt}/{self.max_retries} via {self.provider_name}/{self.model}")

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

                # Parse the output
                parsed = self.parse_output(response.text)

                # Validate
                is_valid, error_msg = self.validate_output(parsed)
                if not is_valid:
                    last_error = f"Validation failed: {error_msg}"
                    logger.warning(f"[{self.name}] {last_error}")
                    if attempt < self.max_retries:
                        # Add error context to next attempt
                        user_prompt = (
                            f"{user_prompt}\n\n"
                            f"CRITICAL: Your previous attempt had this issue: {error_msg}\n"
                            f"Please fix this and try again. Follow the instructions exactly."
                        )
                        time.sleep(min(2 ** attempt, 8))  # Exponential backoff (max 8s)
                        continue
                    else:
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
                    f"[{self.name}] Success on attempt {attempt} "
                    f"({response.input_tokens}+{response.output_tokens} tokens, "
                    f"${response.cost_usd:.4f}, {response.latency_ms:.0f}ms)"
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
                logger.error(f"[{self.name}] Attempt {attempt} failed: {last_error}")
                if attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 8))
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

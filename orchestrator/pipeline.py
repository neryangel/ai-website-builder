"""
Build Pipeline
==============
Orchestrates the multi-agent pipeline with Auto-Fix loop.

Pipeline Flow:
  1. Strategist → Strategic summary
  2. Copywriter + Art Director (parallel) → Copy + Design tokens
  3. Developer → HTML page
  4. Reviewer → Quality audit (Auto-Fix loop)
  5. SEO Optimizer → Final optimized HTML
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from agents import (
    StrategistAgent,
    CopywriterAgent,
    ArtDirectorAgent,
    DeveloperAgent,
    ReviewerAgent,
    SEOOptimizerAgent,
)
from agents.base import AgentResult
from config import TEMPLATES, MAX_AUTO_FIX_ITERATIONS

logger = logging.getLogger(__name__)


@dataclass
class PipelineStage:
    """Represents a stage in the pipeline."""
    name: str
    agent_name: str
    status: str = "waiting"  # waiting | running | done | error
    result: Optional[AgentResult] = None
    duration_ms: float = 0.0


@dataclass
class PipelineResult:
    """Complete result from the pipeline."""
    success: bool = False
    html_code: str = ""
    strategy: str = ""
    copy: str = ""
    design_json: dict = field(default_factory=dict)
    review_report: Optional[dict] = None
    stages: list = field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: float = 0.0
    fix_iterations: int = 0
    error: Optional[str] = None


class BuildPipeline:
    """
    Orchestrates the multi-agent website build pipeline.
    
    Features:
    - Sequential and parallel agent execution
    - Auto-Fix loop (Developer ↔ Reviewer)
    - Cost tracking across all agents
    - Progress callbacks for UI updates
    """

    def __init__(
        self,
        agent_configs: dict,
        template: str = "landing",
        auto_fix_enabled: bool = True,
        max_fix_iterations: int = MAX_AUTO_FIX_ITERATIONS,
        on_stage_update: Optional[Callable] = None,
    ):
        """
        Args:
            agent_configs: Dict mapping agent name to {provider, model, api_key} 
            template: Template name from config.TEMPLATES
            auto_fix_enabled: Enable the Auto-Fix review loop
            max_fix_iterations: Max iterations for Auto-Fix
            on_stage_update: Callback(stage_name, status) for UI updates
        """
        self.agent_configs = agent_configs
        self.template = template
        self.template_info = TEMPLATES.get(template, TEMPLATES["landing"])
        self.auto_fix_enabled = auto_fix_enabled
        self.max_fix_iterations = max_fix_iterations
        self.on_stage_update = on_stage_update or (lambda *a: None)

    def _create_agent(self, agent_class, agent_name: str):
        """Create an agent instance from config."""
        cfg = self.agent_configs.get(agent_name, {})
        return agent_class(
            provider=cfg.get("provider", "Gemini"),
            model=cfg.get("model", "gemini-2.0-flash"),
            api_key=cfg.get("api_key", ""),
        )

    def _update_stage(self, name: str, status: str):
        """Notify UI of stage status change."""
        self.on_stage_update(name, status)

    def run(self, business_description: str) -> PipelineResult:
        """
        Execute the full pipeline.
        
        Args:
            business_description: The user's business description
            
        Returns:
            PipelineResult with all outputs and metrics
        """
        pipeline_start = time.time()
        result = PipelineResult()
        stages = []

        try:
            # ──────────────────────────────────────
            # Stage 1: Strategist
            # ──────────────────────────────────────
            self._update_stage("Strategist", "running")
            logger.info("Pipeline Stage 1: Strategist")

            strategist = self._create_agent(StrategistAgent, "Strategist")
            strat_result = strategist.run(
                business_description,
                template_hint=self.template_info.get("style_hints", ""),
                sections_hint=", ".join(self.template_info.get("sections", [])),
            )

            if not strat_result.success:
                self._update_stage("Strategist", "error")
                result.error = f"Strategist failed: {strat_result.error}"
                return result

            result.strategy = strat_result.parsed_output
            result.total_tokens += strat_result.total_input_tokens + strat_result.total_output_tokens
            result.total_cost_usd += strat_result.total_cost_usd
            stages.append(PipelineStage(
                name="Strategist", agent_name="Strategist", status="done",
                result=strat_result, duration_ms=strat_result.total_latency_ms,
            ))
            self._update_stage("Strategist", "done")

            # ──────────────────────────────────────
            # Stage 2 & 3: Copywriter + Art Director (Parallel)
            # ──────────────────────────────────────
            self._update_stage("Copywriter", "running")
            self._update_stage("Art Director", "running")
            logger.info("Pipeline Stage 2&3: Copywriter + Art Director (parallel)")

            copywriter = self._create_agent(CopywriterAgent, "Copywriter")
            art_director = self._create_agent(ArtDirectorAgent, "Art Director")

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_copy = executor.submit(
                    copywriter.run,
                    "",
                    strategy=result.strategy,
                    sections=self.template_info.get("sections", []),
                )
                future_design = executor.submit(
                    art_director.run,
                    "",
                    strategy=result.strategy,
                )

                copy_result = future_copy.result()
                design_result = future_design.result()

            if not copy_result.success:
                self._update_stage("Copywriter", "error")
                result.error = f"Copywriter failed: {copy_result.error}"
                return result

            if not design_result.success:
                self._update_stage("Art Director", "error")
                result.error = f"Art Director failed: {design_result.error}"
                return result

            result.copy = copy_result.parsed_output
            result.design_json = design_result.parsed_output
            result.total_tokens += (
                copy_result.total_input_tokens + copy_result.total_output_tokens +
                design_result.total_input_tokens + design_result.total_output_tokens
            )
            result.total_cost_usd += copy_result.total_cost_usd + design_result.total_cost_usd

            stages.append(PipelineStage(
                name="Copywriter", agent_name="Copywriter", status="done",
                result=copy_result, duration_ms=copy_result.total_latency_ms,
            ))
            stages.append(PipelineStage(
                name="Art Director", agent_name="Art Director", status="done",
                result=design_result, duration_ms=design_result.total_latency_ms,
            ))
            self._update_stage("Copywriter", "done")
            self._update_stage("Art Director", "done")

            # ──────────────────────────────────────
            # Stage 4: Developer (with Auto-Fix Loop)
            # ──────────────────────────────────────
            self._update_stage("Developer", "running")
            logger.info("Pipeline Stage 4: Developer")

            developer = self._create_agent(DeveloperAgent, "Developer")
            dev_result = developer.run(
                business_description,
                copy=result.copy,
                design=result.design_json,
                business_description=business_description,
                sections=self.template_info.get("sections", []),
            )

            if not dev_result.success:
                self._update_stage("Developer", "error")
                result.error = f"Developer failed: {dev_result.error}"
                return result

            html_code = dev_result.parsed_output
            result.total_tokens += dev_result.total_input_tokens + dev_result.total_output_tokens
            result.total_cost_usd += dev_result.total_cost_usd
            stages.append(PipelineStage(
                name="Developer", agent_name="Developer", status="done",
                result=dev_result, duration_ms=dev_result.total_latency_ms,
            ))
            self._update_stage("Developer", "done")

            # ──────────────────────────────────────
            # Stage 5: Auto-Fix Loop (Reviewer ↔ Developer)
            # ──────────────────────────────────────
            if self.auto_fix_enabled:
                self._update_stage("Reviewer", "running")
                logger.info("Pipeline Stage 5: Auto-Fix Loop")

                reviewer = self._create_agent(ReviewerAgent, "Reviewer")

                for fix_iteration in range(self.max_fix_iterations):
                    logger.info(f"Auto-Fix iteration {fix_iteration + 1}/{self.max_fix_iterations}")

                    review_result = reviewer.run(
                        "",
                        html=html_code,
                        design=result.design_json,
                    )

                    result.total_tokens += review_result.total_input_tokens + review_result.total_output_tokens
                    result.total_cost_usd += review_result.total_cost_usd

                    if not review_result.success:
                        logger.warning(f"Review failed on iteration {fix_iteration + 1}")
                        break

                    review_report = review_result.parsed_output
                    result.review_report = review_report
                    result.fix_iterations = fix_iteration + 1

                    # Check if passed
                    if review_report.get("pass", False):
                        logger.info(f"Review passed with score {review_report.get('score', 'N/A')}")
                        break

                    # If not passed, get the critical issues and send back to developer
                    critical_issues = [
                        issue for issue in review_report.get("issues", [])
                        if issue.get("severity") in ("critical", "warning")
                    ]

                    if not critical_issues:
                        logger.info("No critical issues found, moving on")
                        break

                    # Re-run developer with fix instructions
                    self._update_stage("Developer", "running")
                    fix_instructions = "\n".join([
                        f"- [{issue['severity'].upper()}] {issue['description']}: {issue.get('fix_suggestion', '')}"
                        for issue in critical_issues
                    ])

                    fix_prompt = f"""
Fix the following issues in this HTML:

{fix_instructions}

Current HTML:
```html
{html_code}
```

Return the COMPLETE fixed HTML. Start with <!DOCTYPE html> and end with </html>.
No explanations, no markdown code fences.
"""
                    fix_result = developer.run(
                        fix_prompt,
                        copy=result.copy,
                        design=result.design_json,
                        business_description=business_description,
                    )

                    if fix_result.success:
                        html_code = fix_result.parsed_output
                        result.total_tokens += fix_result.total_input_tokens + fix_result.total_output_tokens
                        result.total_cost_usd += fix_result.total_cost_usd

                    self._update_stage("Developer", "done")

                stages.append(PipelineStage(
                    name="Reviewer", agent_name="Reviewer", status="done",
                    result=review_result, duration_ms=review_result.total_latency_ms,
                ))
                self._update_stage("Reviewer", "done")

            # ──────────────────────────────────────
            # Stage 6: SEO Optimizer
            # ──────────────────────────────────────
            self._update_stage("SEO Optimizer", "running")
            logger.info("Pipeline Stage 6: SEO Optimizer")

            seo = self._create_agent(SEOOptimizerAgent, "SEO Optimizer")
            seo_result = seo.run(
                "",
                html=html_code,
                business_description=business_description,
                strategy=result.strategy,
            )

            if seo_result.success:
                html_code = seo_result.parsed_output
                result.total_tokens += seo_result.total_input_tokens + seo_result.total_output_tokens
                result.total_cost_usd += seo_result.total_cost_usd
                stages.append(PipelineStage(
                    name="SEO Optimizer", agent_name="SEO Optimizer", status="done",
                    result=seo_result, duration_ms=seo_result.total_latency_ms,
                ))
            else:
                logger.warning(f"SEO Optimizer failed: {seo_result.error}. Using unoptimized HTML.")
                stages.append(PipelineStage(
                    name="SEO Optimizer", agent_name="SEO Optimizer", status="error",
                    result=seo_result,
                ))

            self._update_stage("SEO Optimizer", "done")

            # ──────────────────────────────────────
            # Final Result
            # ──────────────────────────────────────
            result.html_code = html_code
            result.success = True
            result.stages = stages
            result.total_duration_ms = (time.time() - pipeline_start) * 1000

            logger.info(
                f"Pipeline complete: {result.total_tokens} tokens, "
                f"${result.total_cost_usd:.4f}, "
                f"{result.total_duration_ms:.0f}ms, "
                f"{result.fix_iterations} fix iterations"
            )

        except Exception as e:
            result.error = str(e)
            result.stages = stages
            result.total_duration_ms = (time.time() - pipeline_start) * 1000
            logger.error(f"Pipeline error: {e}")

        return result

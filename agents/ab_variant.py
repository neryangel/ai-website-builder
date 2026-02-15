"""
A/B Variant Generator Agent
============================
Generates alternative copy variations for A/B testing.
"""

import json
import re
from agents.base import BaseAgent


class ABVariantAgent(BaseAgent):
    """Generates alternative copy variants for A/B testing key sections."""

    @property
    def name(self) -> str:
        return "ABVariant"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The A/B Testing Specialist**, an expert in conversion optimization.

Given the original website copy, generate alternative text variants for A/B testing.

For each section you receive, produce 2 ALTERNATIVE variants (the original is variant A).
Focus on:
1. **Headlines** — Test emotional vs. rational appeals
2. **CTAs** — Test urgency vs. value-based
3. **Subheadlines** — Test short vs. descriptive

Rules:
- Keep the same section structure, only change the text
- Each variant should have a distinct psychological angle
- Maintain brand tone consistency
- Label variants as B and C

Output as a JSON object:
{
  "variants": {
    "headline": {
      "A": "Original headline",
      "B": "Emotional alternative",
      "C": "Urgency-driven alternative"
    },
    "subheadline": {
      "A": "Original subheadline",
      "B": "Short punchy version",
      "C": "Social-proof version"
    },
    "cta_primary": {
      "A": "Original CTA",
      "B": "Benefit-focused CTA",
      "C": "Urgency CTA"
    },
    "cta_secondary": {
      "A": "Original secondary CTA",
      "B": "Alternative",
      "C": "Alternative"
    }
  },
  "rationale": "Brief explanation of the testing strategy"
}"""

    def parse_output(self, raw_text: str) -> dict:
        """Extract JSON from response."""
        # Try code fence
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1).strip())

        # Try raw JSON
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        return {"variants": {}, "rationale": raw_text}

    def validate_output(self, parsed) -> tuple[bool, str]:
        """Validate variants output."""
        if not isinstance(parsed, dict):
            return False, "Output is not a dict"
        if "variants" not in parsed:
            return False, "Missing 'variants' key"
        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        copy_text = kwargs.get("copy", "")
        return f"""
Original website copy:

{copy_text}

Generate A/B test variants for the key conversion elements (headline, subheadline, CTAs).
Return the JSON with variants B and C alongside the original A.
"""

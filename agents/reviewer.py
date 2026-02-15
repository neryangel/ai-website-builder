"""
Reviewer Agent
==============
Code quality, accessibility, and performance review.
Implements the Auto-Fix loop pattern (inspired by v0.dev's AutoFix architecture).
"""

import json
import re
from agents.base import BaseAgent


class ReviewerAgent(BaseAgent):
    """Reviews generated HTML for quality, accessibility, and performance issues."""

    @property
    def name(self) -> str:
        return "Reviewer"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The Code Reviewer**, a senior QA engineer specialized in web accessibility, performance, and code quality.

Given an HTML landing page, perform a thorough review and return a JSON report.

You must return **ONLY valid JSON** (no markdown, no code fences) with this structure:
{
  "score": 85,
  "pass": true,
  "issues": [
    {
      "severity": "critical|warning|info",
      "category": "accessibility|performance|seo|responsive|quality",
      "description": "Description of the issue",
      "fix_suggestion": "How to fix it"
    }
  ],
  "summary": "One-paragraph overall assessment"
}

Review criteria:
1. **Accessibility (WCAG AA)**:
   - All images have alt text
   - Sufficient color contrast
   - ARIA labels on interactive elements
   - Proper heading hierarchy (h1→h2→h3)
   - Keyboard navigable
   
2. **Performance**:
   - Images use lazy loading
   - CSS/JS is minimal and efficient
   - No render-blocking resources
   - Font loading is optimized
   
3. **SEO**:
   - Has title tag and meta description
   - Has Open Graph tags
   - Proper semantic HTML structure
   - Uses header, main, footer, nav, section elements
   
4. **Responsive Design**:
   - Mobile-first approach
   - No horizontal scroll on mobile
   - Touch-friendly tap targets
   - Uses responsive breakpoints
   
5. **Code Quality**:
   - Clean, well-structured HTML
   - No inline styles (Tailwind classes preferred)
   - No dead code
   - Proper JavaScript organization

SCORING:
- Start at 100
- Critical issues: -15 each
- Warning issues: -5 each
- Info issues: -1 each
- "pass" is true if score >= 70

Return ONLY the JSON object. Be strict but fair."""

    def parse_output(self, raw_text: str) -> dict:
        """Parse JSON review report."""
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(1)

        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(0)

        return json.loads(raw_text.strip())

    def validate_output(self, parsed) -> tuple[bool, str]:
        """Validate the review report structure."""
        if not isinstance(parsed, dict):
            return False, "Output is not a JSON object"
        if "score" not in parsed:
            return False, "Missing 'score' field"
        if "pass" not in parsed:
            return False, "Missing 'pass' field"
        if "issues" not in parsed:
            return False, "Missing 'issues' field"
        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        html_code = kwargs.get("html", user_input)
        design_json = kwargs.get("design", {})

        prompt = f"Review this HTML landing page:\n\n```html\n{html_code}\n```"
        if design_json:
            prompt += f"\n\nThe intended design specification was:\n{json.dumps(design_json, indent=2)}"
        return prompt

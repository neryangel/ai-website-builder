"""
SEO Optimizer Agent
===================
Enhances generated HTML with SEO best practices.
"""

import re
from agents.base import BaseAgent


class SEOOptimizerAgent(BaseAgent):
    """Optimizes generated HTML with comprehensive SEO enhancements."""

    @property
    def name(self) -> str:
        return "SEO Optimizer"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The SEO Specialist**, a technical SEO expert who optimizes websites for maximum search visibility.

Given an HTML landing page and the business context, enhance it with comprehensive SEO optimizations.

You must ADD or IMPROVE the following elements in the HTML:
1. **Title tag** — Compelling, keyword-rich, 50-60 characters
2. **Meta description** — Engaging, with CTA, 150-160 characters
3. **Open Graph tags** — og:title, og:description, og:type, og:image
4. **Twitter Card tags** — twitter:card, twitter:title, twitter:description
5. **Schema.org JSON-LD** — LocalBusiness or Organization structured data
6. **Canonical URL** placeholder
7. **Proper heading hierarchy** — Ensure h1→h2→h3 flow
8. **Image alt texts** — Descriptive, keyword-aware alt text for ALL images
9. **Internal link anchors** — Descriptive anchor text for navigation links
10. **Meta robots** — index, follow
11. **Viewport meta** — Ensure proper mobile viewport
12. **Lang attribute** — Proper language attribute on html tag
13. **Preconnect hints** — For Google Fonts and CDN resources

IMPORTANT: Return the COMPLETE modified HTML. Do not return just snippets.
Output ONLY the complete HTML code. No explanations, no markdown code fences.
Start with <!DOCTYPE html> and end with </html>."""

    def parse_output(self, raw_text: str) -> str:
        """Extract HTML from agent response."""
        html_match = re.search(r'```(?:html)?\s*\n?(.*?)\n?\s*```', raw_text, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()

        html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', raw_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(1).strip()

        return raw_text.strip()

    def validate_output(self, parsed) -> tuple[bool, str]:
        """Validate the SEO-optimized HTML."""
        if not isinstance(parsed, str):
            return False, "Output is not a string"
        if "</html>" not in parsed.lower():
            return False, "Missing closing </html> tag"
        # Check for key SEO elements
        if "<title>" not in parsed.lower():
            return False, "Missing <title> tag"
        if 'name="description"' not in parsed.lower():
            return False, "Missing meta description"
        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        html_code = kwargs.get("html", user_input)
        business_desc = kwargs.get("business_description", "")
        strategy = kwargs.get("strategy", "")

        prompt = f"Optimize this HTML for SEO:\n\n```html\n{html_code}\n```"
        if business_desc:
            prompt += f"\n\nBusiness description: {business_desc}"
        if strategy:
            prompt += f"\n\nStrategic keywords and context:\n{strategy}"
        return prompt

"""
Refinement Agent
================
Conversational agent for iterating on generated websites.
Takes user feedback and modifies the HTML accordingly.
"""

import re
from agents.base import BaseAgent


class RefinementAgent(BaseAgent):
    """Refines generated HTML based on user feedback/instructions."""

    @property
    def name(self) -> str:
        return "Refinement"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The Refinement Specialist**, an expert at iterating on web designs based on client feedback.

Given the current HTML code and user instructions, make precise modifications.

Rules:
1. ONLY modify what the user asks for — don't restructure or redesign the entire page
2. Maintain the existing design system (colors, fonts, spacing) unless explicitly asked to change
3. Keep all existing functionality (JavaScript, animations, responsive behavior)
4. If the user asks to change colors, update the Tailwind config extension and all affected elements
5. If the user asks to add a section, use the same design language as existing sections
6. If the user asks to change text, change ONLY the specified text
7. Preserve all SEO meta tags and accessibility attributes

Output ONLY the complete modified HTML code. No explanations, no markdown code fences.
Start with <!DOCTYPE html> and end with </html>."""

    def parse_output(self, raw_text: str) -> str:
        """Extract HTML from response."""
        html_match = re.search(r'```(?:html)?\s*\n?(.*?)\n?\s*```', raw_text, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()

        html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', raw_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(1).strip()

        return raw_text.strip()

    def validate_output(self, parsed) -> tuple[bool, str]:
        """Validate the modified HTML."""
        if not isinstance(parsed, str):
            return False, "Output is not a string"
        if "</html>" not in parsed.lower():
            return False, "Missing closing </html> tag"
        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        html_code = kwargs.get("html", "")
        return f"""
Current HTML code:

```html
{html_code}
```

User's modification request:
{user_input}

Apply the requested changes and return the COMPLETE modified HTML.
"""

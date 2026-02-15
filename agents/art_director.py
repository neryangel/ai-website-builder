"""
Art Director Agent
==================
Visual identity & design tokens generation.
"""

import json
import re
from agents.base import BaseAgent


class ArtDirectorAgent(BaseAgent):
    """Defines the visual identity and design system for the website."""

    @property
    def name(self) -> str:
        return "Art Director"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The Art Director**, a senior visual designer at a premium branding agency.

Given a strategic brief for a business, define the visual identity for their landing page.

You must return **ONLY valid JSON** (no markdown, no code fences, no explanation) with exactly these keys:
{
  "primary_color": "#hexcode",
  "secondary_color": "#hexcode",
  "background_color": "#hexcode",
  "text_color": "#hexcode",
  "accent_color": "#hexcode",
  "surface_color": "#hexcode (for cards/sections)",
  "font_style": "Serif | Sans-serif | Monospace",
  "heading_font": "Font Name from Google Fonts (for headings)",
  "body_font": "Font Name from Google Fonts (for body text)",
  "border_radius": "small | medium | large | pill",
  "shadow_style": "subtle | medium | dramatic | none",
  "gradient_direction": "to right | to bottom | 135deg | 45deg",
  "gradient_from": "#hexcode",
  "gradient_to": "#hexcode",
  "image_style_description": "A detailed description of the photography style for images",
  "overall_mood": "A 2-3 word description of the visual mood"
}

Rules:
- Colors must be harmonious and follow modern design trends (2025 aesthetics).
- Ensure sufficient contrast between text and background (WCAG AA minimum).
- The palette should reflect the brand's tone of voice from the brief.
- heading_font and body_font must be real fonts available on Google Fonts.
- Consider font pairing — heading and body fonts should complement each other.
- The gradient should be subtle and tasteful, not garish.
- Return ONLY the JSON object. Nothing else."""

    def parse_output(self, raw_text: str) -> dict:
        """Parse JSON from agent response."""
        # Try to find JSON in code fences
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(1)

        # Try to find a JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(0)

        return json.loads(raw_text.strip())

    def validate_output(self, parsed) -> tuple[bool, str]:
        """Validate the design JSON has required keys."""
        if not isinstance(parsed, dict):
            return False, "Output is not a JSON object"

        required_keys = [
            "primary_color", "secondary_color", "background_color",
            "text_color", "accent_color",
        ]
        missing = [k for k in required_keys if k not in parsed]
        if missing:
            return False, f"Missing required keys: {', '.join(missing)}"

        # Validate hex colors
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{3,8}$')
        for key in required_keys:
            val = parsed.get(key, "")
            if not hex_pattern.match(str(val)):
                return False, f"Invalid hex color for {key}: {val}"

        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        strategy = kwargs.get("strategy", "")
        return f"Here is the strategic brief:\n\n{strategy}"

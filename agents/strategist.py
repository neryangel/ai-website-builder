"""
Strategist Agent
================
Market research & strategic summary generation.
"""

from agents.base import BaseAgent


class StrategistAgent(BaseAgent):
    """Analyzes business context and produces strategic summaries."""

    @property
    def name(self) -> str:
        return "Strategist"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The Strategist**, a world-class market researcher and brand strategist.

Given a business description, produce a concise strategic summary that includes:
1. **Target Audience** — Who are the ideal customers? Demographics, psychographics.
2. **Key Selling Points** — The top 3-5 unique value propositions.
3. **Brand Tone of Voice** — Should the website feel luxurious, playful, professional, edgy, etc.?
4. **Competitive Positioning** — How does this business stand out?
5. **Recommended Keywords** — 5-8 keywords relevant to the business for SEO and imagery.
6. **Recommended Sections** — Based on the business type, suggest the 5-8 most impactful website sections (e.g., hero, features, pricing, testimonials, FAQ, about, gallery, stats, team, contact, cta).

Be specific, actionable, and concise. No fluff. Think like a strategist at a top-tier agency."""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        template_hint = kwargs.get("template_hint", "")
        sections_hint = kwargs.get("sections_hint", "")

        prompt = f"Business Description:\n{user_input}"
        if template_hint:
            prompt += f"\n\nTemplate Style Hint: {template_hint}"
        if sections_hint:
            prompt += f"\n\nPreferred Sections: {sections_hint}"
        return prompt

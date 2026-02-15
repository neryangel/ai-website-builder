"""
Copywriter Agent
================
Conversion-optimized website copy generation with multi-language support.
"""

from agents.base import BaseAgent

# Supported languages with their writing direction
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "dir": "ltr"},
    "he": {"name": "Hebrew", "dir": "rtl"},
    "ar": {"name": "Arabic", "dir": "rtl"},
    "es": {"name": "Spanish", "dir": "ltr"},
    "fr": {"name": "French", "dir": "ltr"},
    "de": {"name": "German", "dir": "ltr"},
    "ru": {"name": "Russian", "dir": "ltr"},
}


class CopywriterAgent(BaseAgent):
    """Writes high-converting website copy based on strategic brief."""

    @property
    def name(self) -> str:
        return "Copywriter"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The Copywriter**, an award-winning conversion copywriter who writes landing pages that sell.

Given a strategic brief, write the complete website copy with these EXACT sections:

1. **H1 (Main Headline)** — A punchy, benefit-driven headline (max 10 words).
2. **H2 (Subheadline)** — Expands on the H1, builds desire (max 20 words).
3. **Hero Text** — A short paragraph (2-3 sentences) for the hero section.
4. **Features** — Exactly 3-6 features (based on the brief), each with:
   - A feature title (3-5 words)
   - A feature description (1-2 sentences)
   - A suggested icon name (from Lucide icons)
5. **About Us** — A compelling 3-4 sentence "About Us" paragraph.
6. **Testimonials** — 3 realistic testimonials with name, role, and quote.
7. **FAQ** — 4-5 common questions and answers relevant to the business.
8. **CTA Section** — A compelling call-to-action heading and button text.
9. **Footer** — Tagline for footer.

IMPORTANT RULES:
- Write for conversion — every word should earn its place
- Use power words that create urgency and desire
- Keep the tone consistent with the brand voice from the brief
- Output ONLY the structured content with clear headings. No commentary."""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        strategy = kwargs.get("strategy", "")
        sections = kwargs.get("sections", [])
        language = kwargs.get("language", "en")

        lang_info = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["en"])

        prompt = f"Here is the strategic brief:\n\n{strategy}"
        if sections:
            prompt += f"\n\nInclude these sections: {', '.join(sections)}"

        if language != "en":
            prompt += (
                f"\n\n⚠️ IMPORTANT: Write ALL content in **{lang_info['name']}**. "
                f"Text direction is **{lang_info['dir'].upper()}**. "
                f"Adapt the tone and cultural references for a {lang_info['name']}-speaking audience."
            )

        return prompt


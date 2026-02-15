"""
Developer Agent
===============
Production-ready HTML/CSS code generation.
"""

import re
from agents.base import BaseAgent


class DeveloperAgent(BaseAgent):
    """Builds complete, production-ready landing pages in HTML/CSS."""

    @property
    def name(self) -> str:
        return "Developer"

    @property
    def system_prompt(self) -> str:
        return """\
You are **The Full-Stack Developer**, a senior frontend engineer who builds pixel-perfect, responsive landing pages that win design awards.

Given website copy and a design JSON, build a COMPLETE, production-ready single-page HTML file.

Requirements:
1. Use **Tailwind CSS via CDN** (`<script src="https://cdn.tailwindcss.com"></script>`).
2. Import the specified **Google Fonts** (both heading and body fonts) and apply them correctly.
3. Apply the EXACT colors from the design JSON using Tailwind's config extension.
4. Include ALL sections from the copy in order:
   - **Navigation** — Sticky navbar with logo text, nav links, and CTA button. Mobile hamburger menu.
   - **Hero Section** — Full-width with gradient overlay using the design's gradient colors, H1, H2, hero text, and CTA button. Add a subtle parallax-like effect.
   - **Features Section** — Responsive grid with SVG icons from Lucide. Cards with hover effects and the surface_color background.
   - **About Us Section** — Clean section with engaging layout.
   - **Testimonials Section** — Carousel-style or grid layout with quote marks, photos, names, and roles.
   - **FAQ Section** — Accordion-style with smooth open/close animations.
   - **CTA Section** — Bold gradient background section with compelling heading and button.
   - **Footer** — Multi-column footer with links, social icons, and copyright.
5. Use **real Unsplash photos** with real photo IDs matching the business context.
6. Add **smooth scroll behavior** and **CSS/JS animations**:
   - Fade-in on scroll using IntersectionObserver
   - Hover state transitions on buttons and cards
   - Smooth gradient animations on hero
   - Accordion toggle for FAQ
7. Make it **fully responsive** (mobile-first with breakpoints).
8. Include complete **inline JavaScript** for:
   - Smooth scrolling to sections
   - Fade-in animation on scroll using IntersectionObserver
   - Mobile hamburger menu toggle with animation
   - FAQ accordion functionality
   - Sticky navbar with background change on scroll
9. Use **semantic HTML5** elements (header, main, section, footer, nav, article).
10. Add **aria-labels** and proper accessibility attributes.
11. Add **Open Graph meta tags** and proper SEO meta description.

CRITICAL QUALITY STANDARDS:
- The design MUST look like it was built by a professional agency
- Use subtle box shadows, smooth transitions, and micro-interactions
- Cards should have hover lift effects
- Buttons should have hover color transitions and subtle scale effects
- Use proper spacing (generous padding and margins)
- Typography hierarchy should be clear and beautiful

Output ONLY the complete HTML code. No explanations, no markdown code fences.
Start with <!DOCTYPE html> and end with </html>."""

    def parse_output(self, raw_text: str) -> str:
        """Extract clean HTML from agent response."""
        # Try to find HTML in code fences
        html_match = re.search(r'```(?:html)?\s*\n?(.*?)\n?\s*```', raw_text, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()

        # Try to find raw HTML
        html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', raw_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(1).strip()

        return raw_text.strip()

    def validate_output(self, parsed) -> tuple[bool, str]:
        """Validate the HTML output."""
        if not isinstance(parsed, str):
            return False, "Output is not a string"
        if "<!DOCTYPE html>" not in parsed.upper() and "<!doctype html>" not in parsed.lower():
            return False, "Missing <!DOCTYPE html> declaration"
        if "</html>" not in parsed.lower():
            return False, "Missing closing </html> tag"
        if "tailwindcss" not in parsed.lower() and "tailwind" not in parsed.lower():
            return False, "Missing Tailwind CSS CDN"
        return True, ""

    def build_user_prompt(self, user_input: str, **kwargs) -> str:
        import json
        from utils.components import get_component_hints_for_sections

        copy_result = kwargs.get("copy", "")
        design_json = kwargs.get("design", {})
        business_desc = kwargs.get("business_description", user_input)
        sections = kwargs.get("sections", [])

        # Get component HTML hints if sections are specified
        component_hints = ""
        if sections:
            component_hints = get_component_hints_for_sections(sections)

        prompt = f"""
Here is the website copy:

{copy_result}

---

Here is the design specification (JSON):

{json.dumps(design_json, indent=2)}

---

The business description: {business_desc}
"""
        if component_hints:
            prompt += f"""

---

Here are reference component patterns to inspire your implementation (adapt colors/content to the design JSON):

{component_hints}
"""

        prompt += """

ADDITIONAL QUALITY REQUIREMENTS:
1. Add AOS-style scroll animations: elements should fade-in/slide-up when entering viewport using IntersectionObserver.
2. Add a counter animation for any statistics/numbers section.
3. Add a smooth parallax scroll effect on the hero background.
4. Navigation should change background to solid color on scroll (transparent initially).
5. All links and buttons should have smooth hover transitions (color, shadow, transform).
6. Use CSS custom properties (--primary, --secondary, etc.) derived from the design JSON for easy theming.
7. Add preconnect hints for Google Fonts and CDN resources in <head>.

Build the complete HTML landing page now. Remember to use the EXACT colors and fonts from the design JSON.
Use real Unsplash image URLs that match the business context.
The design must be STUNNING — think Framer-level or Dribbble-worthy quality.
"""
        return prompt


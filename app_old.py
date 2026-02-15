"""
Multi-Agent AI Website Builder
==============================
A Streamlit application that chains 4 specialized Gemini AI agents
to generate a complete single-page landing page from a business description.

Agent Pipeline:
  1. Strategist   — Market research & strategic summary
  2. Copywriter   — Website copy (runs in parallel with Agent 3)
  3. Art Director  — Visual identity JSON (runs in parallel with Agent 2)
  4. Developer    — Complete HTML with Tailwind CSS
"""

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
import google.generativeai as genai
import openai
import anthropic

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
# Default Models
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20240620"

PROVIDERS = {
    "Gemini": ["gemini-2.0-flash", "gemini-1.5-pro"],
    "OpenAI": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"]
}

# ─────────────────────────────────────────────
# Agent System Prompts
# ─────────────────────────────────────────────

STRATEGIST_PROMPT = """\
You are **The Strategist**, a world-class market researcher and brand strategist.

Given a business description, produce a concise strategic summary that includes:
1. **Target Audience** — Who are the ideal customers? Demographics, psychographics.
2. **Key Selling Points** — The top 3-5 unique value propositions.
3. **Brand Tone of Voice** — Should the website feel luxurious, playful, professional, edgy, etc.?
4. **Competitive Positioning** — How does this business stand out?
5. **Recommended Keywords** — 5-8 keywords relevant to the business for SEO and imagery.

Be specific, actionable, and concise. No fluff. Think like a strategist at a top-tier agency.
"""

COPYWRITER_PROMPT = """\
You are **The Copywriter**, an award-winning conversion copywriter who writes landing pages that sell.

Given a strategic brief, write the complete website copy with these EXACT sections:

1. **H1 (Main Headline)** — A punchy, benefit-driven headline (max 10 words).
2. **H2 (Subheadline)** — Expands on the H1, builds desire (max 20 words).
3. **Hero Text** — A short paragraph (2-3 sentences) for the hero section.
4. **Features** — Exactly 3 features, each with:
   - A feature title (3-5 words)
   - A feature description (1-2 sentences)
   - A suggested icon name (from a common icon set like Heroicons or Lucide)
5. **About Us** — A compelling 3-4 sentence "About Us" paragraph.
6. **CTA Button Text** — The primary call-to-action button text.

Output ONLY the structured content with clear headings. No commentary.
"""

ART_DIRECTOR_PROMPT = """\
You are **The Art Director**, a senior visual designer at a premium branding agency.

Given a strategic brief for a business, define the visual identity for their landing page.

You must return **ONLY valid JSON** (no markdown, no code fences, no explanation) with exactly these keys:
{
  "primary_color": "#hexcode",
  "secondary_color": "#hexcode",
  "background_color": "#hexcode",
  "text_color": "#hexcode",
  "accent_color": "#hexcode",
  "font_style": "Serif | Sans-serif | Monospace",
  "google_font": "Font Name from Google Fonts",
  "image_style_description": "A detailed description of the photography style for images"
}

Rules:
- Colors must be harmonious and follow modern design trends.
- Ensure sufficient contrast between text and background (WCAG AA minimum).
- The palette should reflect the brand's tone of voice from the brief.
- The google_font should be a real font available on Google Fonts.
- Return ONLY the JSON object. Nothing else.
"""

DEVELOPER_PROMPT = """\
You are **The Full-Stack Developer**, a senior frontend engineer who builds pixel-perfect, responsive landing pages.

Given website copy and a design JSON, build a COMPLETE, production-ready single-page HTML file.

Requirements:
1. Use **Tailwind CSS via CDN** (`<script src="https://cdn.tailwindcss.com"></script>`).
2. Import the specified **Google Font** and apply it globally.
3. Apply the EXACT colors from the design JSON using Tailwind's config extension.
4. Include these sections in order:
   - **Navigation** — Simple navbar with the business name and a CTA button.
   - **Hero Section** — Full-width with gradient overlay, H1, H2, hero text, and CTA button.
   - **Features Section** — 3-column responsive grid with SVG icons.
   - **About Us Section** — Clean section with the about text.
   - **Footer** — Simple footer with copyright.
5. Use **placeholder images from Unsplash Source** (e.g., `https://images.unsplash.com/photo-XXXXX?w=1200&h=800&fit=crop`) matching the business type. Use REAL Unsplash photo IDs that match the business context.
6. Add **smooth scroll behavior** and **subtle CSS animations** (fade-in on scroll).
7. Make it **fully responsive** (mobile-first).
8. Include a small **inline JavaScript** section for:
   - Smooth scrolling to sections
   - Simple fade-in animation on scroll using IntersectionObserver
   - Mobile hamburger menu toggle

Output ONLY the complete HTML code. No explanations, no markdown code fences.
Start with <!DOCTYPE html> and end with </html>.
"""


# ─────────────────────────────────────────────
# Agent Execution
# ─────────────────────────────────────────────

def call_agent(agent_name: str, system_prompt: str, user_input: str, provider: str, model_id: str, api_key: str = None) -> str:
    """Call an AI agent using the specified provider and model."""
    
    try:
        if provider == "Gemini":
            if not api_key:
                raise ValueError("Gemini API Key is missing")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt,
            )
            response = model.generate_content(user_input)
            return response.text

        elif provider == "OpenAI":
            if not api_key:
                raise ValueError("OpenAI API Key is missing")
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content

        elif provider == "Anthropic":
            if not api_key:
                raise ValueError("Anthropic API Key is missing")
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model_id,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            return response.content[0].text
            
        else:
            raise ValueError(f"Unknown provider: {provider}")

    except Exception as e:
        raise Exception(f"Error calling {provider} ({model_id}): {str(e)}")


def extract_json(text: str) -> dict:
    """Extract JSON from agent response, handling potential markdown code fences."""
    # Try to find JSON in code fences first
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    # Try to find a JSON object directly
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    return json.loads(text.strip())


def extract_html(text: str) -> str:
    """Extract HTML from agent response, handling potential markdown code fences."""
    # Try to find HTML in code fences
    html_match = re.search(r'```(?:html)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if html_match:
        return html_match.group(1).strip()

    # Try to find raw HTML
    html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', text, re.DOTALL | re.IGNORECASE)
    if html_match:
        return html_match.group(1).strip()

    return text.strip()


# ─────────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────────

def setup_page():
    """Configure Streamlit page settings and custom CSS."""
    st.set_page_config(
        page_title="AI Website Builder",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .sub-header {
        color: #6b7280;
        font-size: 1.1rem;
        margin-top: 0;
    }

    .agent-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid;
        margin-bottom: 0.8rem;
    }

    .agent-strategist { border-left-color: #8b5cf6; }
    .agent-copywriter { border-left-color: #3b82f6; }
    .agent-artdirector { border-left-color: #ec4899; }
    .agent-developer { border-left-color: #10b981; }

    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .badge-running { background: #fef3c7; color: #92400e; }
    .badge-done { background: #d1fae5; color: #065f46; }
    .badge-waiting { background: #e5e7eb; color: #374151; }

    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar() -> dict:
    """Render sidebar with API key input and instructions."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")

        with st.expander("🔑 API Keys", expanded=True):
            google_api_key = st.text_input(
                "Google API Key",
                type="password",
                placeholder="Gemini API Key...",
                value=os.environ.get("GOOGLE_API_KEY", ""),
                help="https://aistudio.google.com/apikey"
            )
            openai_api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                value=os.environ.get("OPENAI_API_KEY", ""),
                help="https://platform.openai.com/api-keys"
            )
            anthropic_api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-...",
                value=os.environ.get("ANTHROPIC_API_KEY", ""),
                help="https://console.anthropic.com/settings/keys"
            )

        st.markdown("---")
        st.markdown("## 🤖 Agent Models")

        # Helper to create model selector
        def model_selector(label, key_prefix):
            col1, col2 = st.columns(2)
            with col1:
                provider = st.selectbox(
                    "Provider",
                    options=["Gemini", "OpenAI", "Anthropic"],
                    key=f"{key_prefix}_provider",
                    label_visibility="collapsed"
                )
            with col2:
                models = PROVIDERS[provider]
                model = st.selectbox(
                    "Model",
                    options=models,
                    key=f"{key_prefix}_model",
                    label_visibility="collapsed"
                )
            return provider, model

        st.markdown("**🧠 Strategist**")
        strat_provider, strat_model = model_selector("Strategist", "strat")

        st.markdown("**✍️ Copywriter**")
        copy_provider, copy_model = model_selector("Copywriter", "copy")

        st.markdown("**🎨 Art Director**")
        art_provider, art_model = model_selector("Art Director", "art")

        st.markdown("**💻 Developer**")
        dev_provider, dev_model = model_selector("Developer", "dev")

        st.markdown("---")
        st.markdown("## 📋 How It Works")
        st.markdown("""
        1. Enter your business description
        2. Click **Build My Website**
        3. Watch 4 AI agents collaborate
        4. Preview & download your landing page
        """)

        st.markdown("---")
        st.caption("Built with Streamlit & Multi-Agent AI")
        
        return {
            "api_keys": {
                "Gemini": google_api_key,
                "OpenAI": openai_api_key,
                "Anthropic": anthropic_api_key
            },
            "agents": {
                "Strategist": {"provider": strat_provider, "model": strat_model},
                "Copywriter": {"provider": copy_provider, "model": copy_model},
                "Art Director": {"provider": art_provider, "model": art_model},
                "Developer": {"provider": dev_provider, "model": dev_model},
            }
        }


def render_agent_status(agent_name: str, icon: str, status: str, color_class: str):
    """Render an agent status indicator."""
    status_class = {
        "running": "badge-running",
        "done": "badge-done",
        "waiting": "badge-waiting",
    }.get(status, "badge-waiting")

    status_text = {
        "running": "⏳ Working...",
        "done": "✅ Complete",
        "waiting": "⏸️ Waiting",
    }.get(status, "⏸️ Waiting")

    st.markdown(
        f"""<div class="agent-card {color_class}">
            <strong>{icon} {agent_name}</strong>
            <span class="status-badge {status_class}" style="float:right">{status_text}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def main():
    setup_page()
    config = render_sidebar()
    
    api_keys = config["api_keys"]
    agents_config = config["agents"]

    # ── Header ──
    st.markdown('<p class="main-header">🏗️ AI Website Builder</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Describe your business and let 4 AI agents build your landing page in seconds.</p>',
        unsafe_allow_html=True,
    )

    # ── Input ──
    col1, col2 = st.columns([3, 1])
    with col1:
        business_desc = st.text_area(
            "Describe your business",
            placeholder="e.g., A boutique coffee shop in Tel Aviv specialized in cold brew and artisan pastries...",
            height=120,
            label_visibility="collapsed",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        build_clicked = st.button(
            "🚀 Build My Website",
            use_container_width=True,
            type="primary",
        )
        
        # Check if at least one API key is present to enable "Start" roughly, 
        # though strict check happens per agent.
        if not any(api_keys.values()):
            st.caption("⚠️ Add at least one API key")

    st.markdown("---")

    # ── Build Pipeline ──
    if build_clicked and business_desc:
        
        # Helper to get config for an agent
        def get_agent_kwargs(agent_name):
            cfg = agents_config[agent_name]
            provider = cfg["provider"]
            model = cfg["model"]
            key = api_keys.get(provider)
            return {"provider": provider, "model_id": model, "api_key": key}

        # Initialize session state for this build
        start_time = time.time()

        # Status display area
        status_container = st.container()

        # ──────────────────────
        # Agent 1: Strategist
        # ──────────────────────
        with status_container:
            render_agent_status("The Strategist", "🧠", "running", "agent-strategist")

        with st.spinner("🧠 Agent 1: The Strategist is analyzing your business..."):
            try:
                strategy = call_agent(
                    "Strategist", 
                    STRATEGIST_PROMPT, 
                    business_desc,
                    **get_agent_kwargs("Strategist")
                )
            except Exception as e:
                st.error(f"❌ Strategist agent failed: {e}")
                st.stop()

        with st.expander("🧠 Agent 1: The Strategist — Strategic Summary", expanded=False):
            st.markdown(strategy)

        # ──────────────────────────────────
        # Agent 2 & 3: Parallel execution
        # ──────────────────────────────────
        with status_container:
            render_agent_status("The Strategist", "🧠", "done", "agent-strategist")
            render_agent_status("The Copywriter", "✍️", "running", "agent-copywriter")
            render_agent_status("The Art Director", "🎨", "running", "agent-artdirector")

        copy_result = None
        design_result = None
        design_json = None

        with st.spinner("✍️🎨 Agents 2 & 3 are working in parallel — Copywriter & Art Director..."):
            try:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_copy = executor.submit(
                        call_agent,
                        "Copywriter",
                        COPYWRITER_PROMPT,
                        f"Here is the strategic brief:\n\n{strategy}",
                        **get_agent_kwargs("Copywriter")
                    )
                    future_design = executor.submit(
                        call_agent,
                        "Art Director",
                        ART_DIRECTOR_PROMPT,
                        f"Here is the strategic brief:\n\n{strategy}",
                        **get_agent_kwargs("Art Director")
                    )

                    copy_result = future_copy.result()
                    design_result = future_design.result()

            except Exception as e:
                st.error(f"❌ Parallel agents failed: {e}")
                st.stop()

        # Parse design JSON
        try:
            design_json = extract_json(design_result)
        except (json.JSONDecodeError, Exception) as e:
            st.warning(f"⚠️ Art Director returned invalid JSON, retrying...")
            try:
                # Retry with the same provider settings
                design_result = call_agent(
                    "Art Director",
                    ART_DIRECTOR_PROMPT + "\n\nCRITICAL: Return ONLY raw JSON. No markdown. No explanation.",
                    f"Here is the strategic brief:\n\n{strategy}",
                    **get_agent_kwargs("Art Director")
                )
                design_json = extract_json(design_result)
            except Exception as e2:
                st.error(f"❌ Art Director failed to return valid JSON: {e2}")
                st.stop()

        with st.expander("✍️ Agent 2: The Copywriter — Website Copy", expanded=False):
            st.markdown(copy_result)

        with st.expander("🎨 Agent 3: The Art Director — Visual Identity", expanded=False):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.json(design_json)
            with col_b:
                # Color preview
                st.markdown("**Color Palette Preview:**")
                colors = {
                    "Primary": design_json.get("primary_color", "#000"),
                    "Secondary": design_json.get("secondary_color", "#000"),
                    "Background": design_json.get("background_color", "#fff"),
                    "Text": design_json.get("text_color", "#000"),
                    "Accent": design_json.get("accent_color", "#000"),
                }
                color_html = ""
                for name, color in colors.items():
                    color_html += (
                        f'<div style="display:inline-block;margin:4px;text-align:center">'
                        f'<div style="width:60px;height:60px;background:{color};'
                        f'border-radius:8px;border:1px solid #ddd"></div>'
                        f'<small>{name}<br>{color}</small></div>'
                    )
                st.markdown(color_html, unsafe_allow_html=True)
                st.markdown(f"**Font:** {design_json.get('google_font', 'N/A')} ({design_json.get('font_style', 'N/A')})")

        # ──────────────────────
        # Agent 4: Developer
        # ──────────────────────
        with status_container:
            render_agent_status("The Strategist", "🧠", "done", "agent-strategist")
            render_agent_status("The Copywriter", "✍️", "done", "agent-copywriter")
            render_agent_status("The Art Director", "🎨", "done", "agent-artdirector")
            render_agent_status("The Developer", "💻", "running", "agent-developer")

        developer_input = f"""
Here is the website copy:

{copy_result}

---

Here is the design specification (JSON):

{json.dumps(design_json, indent=2)}

---

The business description: {business_desc}

Build the complete HTML landing page now. Remember to use the EXACT colors and font from the design JSON.
Use real Unsplash image URLs that match the business context.
"""

        with st.spinner("💻 Agent 4: The Developer is building your website..."):
            try:
                html_result = call_agent(
                    "Developer", 
                    DEVELOPER_PROMPT, 
                    developer_input,
                    **get_agent_kwargs("Developer")
                )
            except Exception as e:
                st.error(f"❌ Developer agent failed: {e}")
                st.stop()

        html_code = extract_html(html_result)

        # ── Final Status ──
        elapsed = time.time() - start_time
        with status_container:
            render_agent_status("The Strategist", "🧠", "done", "agent-strategist")
            render_agent_status("The Copywriter", "✍️", "done", "agent-copywriter")
            render_agent_status("The Art Director", "🎨", "done", "agent-artdirector")
            render_agent_status("The Developer", "💻", "done", "agent-developer")

        st.success(f"🎉 Website built successfully in **{elapsed:.1f} seconds**!")

        # ── HTML Code ──
        with st.expander("💻 Agent 4: The Developer — HTML Source Code", expanded=False):
            st.code(html_code, language="html")

        # ── Preview ──
        st.markdown("### 👁️ Live Preview")
        st.components.v1.html(html_code, height=800, scrolling=True)

        # ── Download ──
        st.markdown("### 📥 Download")
        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
        with col_dl2:
            st.download_button(
                label="⬇️ Download HTML File",
                data=html_code,
                file_name="landing_page.html",
                mime="text/html",
                use_container_width=True,
                type="primary",
            )

    elif build_clicked and not business_desc:
        st.warning("Please enter a business description to get started.")


if __name__ == "__main__":
    main()

"""
Sidebar UI
==========
Configuration sidebar with API keys, model selection, and template picker.
"""

import os
import streamlit as st
from config import PROVIDERS, TEMPLATES, AGENT_DEFINITIONS
from agents.copywriter import SUPPORTED_LANGUAGES


def render_sidebar() -> dict:
    """Render sidebar with API keys, agent models, and template selection."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")

        # ── API Keys ──
        with st.expander("🔑 API Keys", expanded=True):
            google_api_key = st.text_input(
                "Google API Key",
                type="password",
                placeholder="Gemini API Key...",
                value=os.environ.get("GOOGLE_API_KEY", ""),
                help="https://aistudio.google.com/apikey",
            )
            openai_api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                value=os.environ.get("OPENAI_API_KEY", ""),
                help="https://platform.openai.com/api-keys",
            )
            anthropic_api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-...",
                value=os.environ.get("ANTHROPIC_API_KEY", ""),
                help="https://console.anthropic.com/settings/keys",
            )

        api_keys = {
            "Gemini": google_api_key,
            "OpenAI": openai_api_key,
            "Anthropic": anthropic_api_key,
        }

        st.markdown("---")

        # ── Language ──
        st.markdown("## 🌍 Language")
        lang_options = {k: v["name"] for k, v in SUPPORTED_LANGUAGES.items()}
        selected_language = st.selectbox(
            "Output language",
            options=list(lang_options.keys()),
            format_func=lambda x: f"{lang_options[x]} {'(RTL)' if SUPPORTED_LANGUAGES[x]['dir'] == 'rtl' else ''}",
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Template Selection ──
        st.markdown("## 🎨 Website Template")
        template_options = {k: v["name"] for k, v in TEMPLATES.items()}
        selected_template = st.selectbox(
            "Choose a template",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            index=list(template_options.keys()).index("landing"),
        )

        template_info = TEMPLATES[selected_template]
        st.caption(f"Sections: {', '.join(template_info['sections'])}")

        st.markdown("---")

        # ── Quick / Advanced Mode ──
        advanced_mode = st.toggle("🔧 Advanced Mode", value=False, help="Show per-agent model configuration")

        # ── Agent Models ──
        if advanced_mode:
            st.markdown("## 🤖 Agent Models")

        def model_selector(label: str, key_prefix: str):
            col1, col2 = st.columns(2)
            with col1:
                provider = st.selectbox(
                    "Provider",
                    options=["Gemini", "OpenAI", "Anthropic"],
                    key=f"{key_prefix}_provider",
                    label_visibility="collapsed",
                )
            with col2:
                models = PROVIDERS[provider]
                model = st.selectbox(
                    "Model",
                    options=models,
                    key=f"{key_prefix}_model",
                    label_visibility="collapsed",
                )
            return provider, model

        agents_config = {}
        for agent_name, agent_def in AGENT_DEFINITIONS.items():
            if advanced_mode:
                st.markdown(f"**{agent_def['icon']} {agent_name}**")
                key_prefix = agent_name.lower().replace(" ", "_")
                provider, model = model_selector(agent_name, key_prefix)
                agents_config[agent_name] = {
                    "provider": provider,
                    "model": model,
                    "api_key": api_keys.get(provider, ""),
                }
            else:
                # Quick mode: use first available API key's provider
                default_provider = "Gemini"  # sensible default
                for p, k in api_keys.items():
                    if k:
                        default_provider = p
                        break
                default_model = PROVIDERS[default_provider][0]
                agents_config[agent_name] = {
                    "provider": default_provider,
                    "model": default_model,
                    "api_key": api_keys.get(default_provider, ""),
                }

        st.markdown("---")

        # ── Pipeline Options ──
        st.markdown("## ⚡ Pipeline Options")
        auto_fix = st.toggle("🔄 Auto-Fix Loop", value=True, help="Automatically review and fix quality issues")
        seo_optimize = st.toggle("📈 SEO Optimization", value=True, help="Add SEO meta tags and structured data")

        st.markdown("---")

        # ── How It Works ──
        st.markdown("## 📋 How It Works")
        st.markdown("""
        1. Choose a template & describe your business
        2. Click **Build My Website**
        3. Watch 6 AI agents collaborate:
           - 🧠 Strategist analyzes your business
           - ✍️ Copywriter writes converting copy
           - 🎨 Art Director designs visual identity
           - 💻 Developer builds the HTML
           - 🔍 Reviewer audits quality
           - 📈 SEO Optimizer adds meta tags
        4. Preview, review, & download!
        """)

        st.markdown("---")
        st.caption("Built with Streamlit & Multi-Agent AI 🚀")

        return {
            "api_keys": api_keys,
            "agents": agents_config,
            "template": selected_template,
            "language": selected_language,
            "auto_fix": auto_fix,
            "seo_optimize": seo_optimize,
        }

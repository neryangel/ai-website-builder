"""
AI Website Builder — Industry-Grade Multi-Agent System
======================================================
Entry point for the Streamlit application.

Pipeline: Strategist → Copywriter + Art Director (parallel) → Developer → Reviewer (Auto-Fix) → SEO Optimizer

Features:
  - 8 AI Agents (Strategist, Copywriter, Art Director, Developer, Reviewer, SEO, Refinement, AB Variant)
  - Auto-Fix quality loop  
  - 6 website templates + 13-component library
  - Project save/load + version history
  - Export to HTML / React / Next.js
  - Deploy packages for Vercel / Netlify / GitHub Pages
  - Conversational refinements
  - A/B copy variant generation
  - Cost tracking & metrics dashboard
"""

import json
import logging
import uuid
import streamlit as st

from config import AGENT_DEFINITIONS, TEMPLATES
from orchestrator.pipeline import BuildPipeline
from agents.refinement import RefinementAgent
from agents.ab_variant import ABVariantAgent
from storage import SavedProject, save_project, load_project, list_projects, delete_project
from storage.versions import Version, save_version, list_versions, get_latest_version
from utils.export import export_html, export_react_component, export_nextjs_page
from utils.deploy import create_deploy_package
from ui.styles import apply_custom_css
from ui.sidebar import render_sidebar
from ui.preview import (
    render_agent_status,
    render_metrics_dashboard,
    render_review_report,
    render_color_palette,
    render_live_preview,
    render_download_section,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="AI Website Builder",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_css()

    # Additional premium styles
    st.markdown("""<style>
    .deploy-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .deploy-card h4 { margin: 0.5rem 0; font-size: 1rem; }
    .deploy-card p { font-size: 0.8rem; opacity: 0.7; margin: 0; }
    .version-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .ab-variant-card {
        background: #f8f9ff;
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid;
        margin-bottom: 0.5rem;
    }
    .ab-variant-a { border-left-color: #667eea; }
    .ab-variant-b { border-left-color: #f093fb; }
    .ab-variant-c { border-left-color: #4facfe; }
    </style>""", unsafe_allow_html=True)


def render_project_manager(config: dict):
    """Render saved projects section in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📁 Saved Projects")
        projects = list_projects()
        if not projects:
            st.caption("No saved projects yet")
            return None

        for proj in projects[:5]:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📄 {proj.name[:30]}", key=f"load_{proj.id}", use_container_width=True):
                    return proj
            with col2:
                if st.button("🗑️", key=f"del_{proj.id}"):
                    delete_project(proj.id)
                    st.rerun()
    return None


def render_export_options(html_code: str):
    """Render multi-format export section."""
    st.markdown("### 📤 Export & Download")

    tabs = st.tabs(["📄 HTML", "⚛️ React", "▲ Next.js"])

    with tabs[0]:
        content, fname, mime = export_html(html_code)
        st.download_button(
            "⬇️ Download HTML",
            data=content, file_name=fname, mime=mime,
            use_container_width=True, type="primary",
        )

    with tabs[1]:
        content, fname, mime = export_react_component(html_code)
        st.download_button(
            "⬇️ Download React Component",
            data=content, file_name=fname, mime=mime,
            use_container_width=True,
        )
        st.caption("Includes LandingPage.jsx + LandingPage.css")

    with tabs[2]:
        content, fname, mime = export_nextjs_page(html_code)
        st.download_button(
            "⬇️ Download Next.js Page",
            data=content, file_name=fname, mime=mime,
            use_container_width=True,
        )
        st.caption("Includes metadata export + page.tsx")


def render_deploy_section(html_code: str):
    """Render one-click deployment packages."""
    st.markdown("### 🚀 Deploy")
    cols = st.columns(3)

    platforms = [
        ("vercel", "▲ Vercel", "Deploy to Vercel with zero config", cols[0]),
        ("netlify", "◆ Netlify", "Deploy to Netlify with security headers", cols[1]),
        ("github_pages", "🐙 GitHub Pages", "Deploy via GitHub Actions CI/CD", cols[2]),
    ]

    for platform, label, desc, col in platforms:
        with col:
            st.markdown(f"""<div class="deploy-card">
                <h4>{label}</h4>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

            zip_bytes, fname, mime = create_deploy_package(
                html_code, platform=platform
            )
            st.download_button(
                f"⬇️ {label} Package",
                data=zip_bytes, file_name=fname, mime=mime,
                use_container_width=True,
                key=f"deploy_{platform}",
            )


def render_version_history(project_id: str):
    """Render version history timeline."""
    versions = list_versions(project_id)
    if not versions:
        return

    st.markdown("### 📜 Version History")
    for i, v in enumerate(reversed(versions)):
        is_latest = i == 0
        badge = '<span class="version-badge">LATEST</span>' if is_latest else ""
        import time as _time
        timestamp = _time.strftime("%H:%M:%S", _time.localtime(v.created_at))

        with st.expander(f"v{len(versions) - i} — {v.change_description or 'Initial build'} ({timestamp}) {badge}", expanded=False):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.caption(f"Tokens: {v.tokens_used:,} | Cost: ${v.cost_usd:.4f}")
            with col2:
                if st.button("⏪ Restore", key=f"restore_{v.version_id}"):
                    st.session_state.current_html = v.html_code
                    st.rerun()


def render_ab_variants(config: dict):
    """Render A/B test variant generation."""
    if "current_copy" not in st.session_state or not st.session_state.current_copy:
        return

    st.markdown("### 🧪 A/B Copy Variants")
    st.caption("Generate alternative copy for conversion testing")

    if st.button("🎯 Generate A/B Variants", use_container_width=True):
        with st.spinner("Generating alternative copy variants..."):
            try:
                dev_cfg = config["agents"].get("Developer", {})
                ab_agent = ABVariantAgent(
                    provider=dev_cfg.get("provider", "Gemini"),
                    model=dev_cfg.get("model", "gemini-2.0-flash"),
                    api_key=dev_cfg.get("api_key", ""),
                )
                result = ab_agent.run(
                    "",
                    copy=st.session_state.current_copy,
                )
                if result.success:
                    st.session_state.ab_variants = result.parsed_output
                else:
                    st.error(f"A/B generation failed: {result.error}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display variants
    if "ab_variants" in st.session_state and st.session_state.ab_variants:
        variants = st.session_state.ab_variants.get("variants", {})
        rationale = st.session_state.ab_variants.get("rationale", "")

        if rationale:
            st.info(f"**Strategy:** {rationale}")

        for section_name, section_variants in variants.items():
            st.markdown(f"**{section_name.replace('_', ' ').title()}**")
            for variant_label, text in section_variants.items():
                css_class = f"ab-variant-{variant_label.lower()}"
                st.markdown(
                    f'<div class="ab-variant-card {css_class}">'
                    f'<strong>Variant {variant_label}:</strong> {text}</div>',
                    unsafe_allow_html=True,
                )


def render_refinement_chat(config: dict, project_id: str = None):
    """Render the conversational refinement chat interface."""
    st.markdown("### 💬 Refine Your Website")
    st.caption("Describe changes — the AI will modify your website live.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_feedback = st.chat_input("e.g., Make the hero taller, change color to blue, add a testimonials section...")

    if user_feedback and "current_html" in st.session_state:
        st.session_state.chat_history.append({"role": "user", "content": user_feedback})

        with st.chat_message("user"):
            st.markdown(user_feedback)

        with st.chat_message("assistant"):
            with st.spinner("✨ Applying changes..."):
                try:
                    dev_cfg = config["agents"].get("Developer", {})
                    refiner = RefinementAgent(
                        provider=dev_cfg.get("provider", "Gemini"),
                        model=dev_cfg.get("model", "gemini-2.0-flash"),
                        api_key=dev_cfg.get("api_key", ""),
                    )

                    result = refiner.run(
                        user_feedback,
                        html=st.session_state.current_html,
                    )

                    if result.success:
                        st.session_state.current_html = result.parsed_output

                        # Save version if project exists
                        if project_id:
                            save_version(Version(
                                version_id=str(uuid.uuid4()),
                                project_id=project_id,
                                html_code=result.parsed_output,
                                change_description=user_feedback[:100],
                                tokens_used=result.total_input_tokens + result.total_output_tokens,
                                cost_usd=result.total_cost_usd,
                            ))

                        tokens = result.total_input_tokens + result.total_output_tokens
                        response = f"✅ Changes applied! ({tokens:,} tokens, ${result.total_cost_usd:.4f})"
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    else:
                        error_msg = f"❌ Refinement failed: {result.error}"
                        st.markdown(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})


def main():
    setup_page()
    config = render_sidebar()
    loaded_project = render_project_manager(config)

    # ── Header ──
    st.markdown('<p class="main-header">🏗️ AI Website Builder</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">8 AI agents build your landing page — '
        'with auto-fix quality review, SEO optimization, A/B testing, and one-click deploy.</p>',
        unsafe_allow_html=True,
    )

    # ── Load saved project ──
    if loaded_project:
        st.success(f"📂 Loaded: **{loaded_project.name}**")
        st.session_state.current_html = loaded_project.html_code
        st.session_state.current_copy = loaded_project.copy
        st.session_state.current_project_id = loaded_project.id

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👁️ Preview", "📤 Export", "🚀 Deploy", "🧪 A/B Test", "💬 Refine"
        ])
        with tab1:
            render_live_preview(loaded_project.html_code)
            render_version_history(loaded_project.id)
        with tab2:
            render_export_options(loaded_project.html_code)
        with tab3:
            render_deploy_section(loaded_project.html_code)
        with tab4:
            render_ab_variants(config)
        with tab5:
            render_refinement_chat(config, project_id=loaded_project.id)
        return

    # ── Template Info ──
    selected_template = config["template"]
    template_info = TEMPLATES[selected_template]
    st.markdown(
        f"**Template:** {template_info['name']} — *{template_info['style_hints']}*"
    )

    # ── Input Area ──
    col1, col2 = st.columns([3, 1])
    with col1:
        business_desc = st.text_area(
            "Describe your business",
            placeholder="e.g., A boutique coffee shop in Tel Aviv specialized in cold brew and artisan pastries, "
                        "targeting young professionals who appreciate quality craft coffee...",
            height=120,
            label_visibility="collapsed",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        build_clicked = st.button("🚀 Build My Website", use_container_width=True, type="primary")
        if not any(config["api_keys"].values()):
            st.caption("⚠️ Add at least one API key")

    st.markdown("---")

    # ── Show previous result ──
    if not build_clicked and "current_html" in st.session_state:
        project_id = st.session_state.get("current_project_id")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👁️ Preview", "📤 Export", "🚀 Deploy", "🧪 A/B Test", "💬 Refine"
        ])
        with tab1:
            render_live_preview(st.session_state.current_html)
            if project_id:
                render_version_history(project_id)
        with tab2:
            render_export_options(st.session_state.current_html)
        with tab3:
            render_deploy_section(st.session_state.current_html)
        with tab4:
            render_ab_variants(config)
        with tab5:
            render_refinement_chat(config, project_id=project_id)
        return

    # ── Build Pipeline ──
    if build_clicked and business_desc:
        st.session_state.chat_history = []
        st.session_state.pop("ab_variants", None)

        # Status area
        status_container = st.container()
        status_placeholders = {}
        with status_container:
            progress_bar = st.progress(0, text="Initializing pipeline...")
            for agent_name in AGENT_DEFINITIONS:
                status_placeholders[agent_name] = st.empty()
                with status_placeholders[agent_name]:
                    render_agent_status(agent_name, "waiting")

        # Track progress
        agent_list = list(AGENT_DEFINITIONS.keys())
        total_stages = len(agent_list)

        def on_stage_update(name: str, status: str):
            if name in status_placeholders:
                with status_placeholders[name]:
                    render_agent_status(name, status)
            # Update progress bar
            if status == "running":
                idx = agent_list.index(name) if name in agent_list else 0
                pct = int((idx / total_stages) * 100)
                progress_bar.progress(pct, text=f"🔄 {name} working...")
            elif status == "done":
                idx = agent_list.index(name) + 1 if name in agent_list else 0
                pct = int((idx / total_stages) * 100)
                progress_bar.progress(pct, text=f"✅ {name} complete")

        pipeline = BuildPipeline(
            agent_configs=config["agents"],
            template=selected_template,
            auto_fix_enabled=config.get("auto_fix", True),
            max_fix_iterations=3,
            on_stage_update=on_stage_update,
        )

        with st.spinner("🚀 Building your website with AI agents..."):
            result = pipeline.run(business_desc)

        progress_bar.progress(100, text="✅ Build complete!")

        if not result.success:
            st.error(f"❌ Pipeline failed: {result.error}")
            st.stop()

        # Store result
        project_id = str(uuid.uuid4())
        st.session_state.current_html = result.html_code
        st.session_state.current_copy = result.copy
        st.session_state.current_project_id = project_id
        st.session_state.business_desc = business_desc

        # Save initial version
        save_version(Version(
            version_id=str(uuid.uuid4()),
            project_id=project_id,
            html_code=result.html_code,
            change_description="Initial build",
            tokens_used=result.total_tokens,
            cost_usd=result.total_cost_usd,
        ))

        # ── Success Summary ──
        st.success(
            f"🎉 Built in **{result.total_duration_ms / 1000:.1f}s** | "
            f"{result.fix_iterations} auto-fixes | "
            f"{result.total_tokens:,} tokens | "
            f"${result.total_cost_usd:.4f}"
        )

        # ── Metrics ──
        render_metrics_dashboard(result)

        # ── Save Project ──
        st.markdown("---")
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            project_name = st.text_input("Project Name", value=business_desc[:50],
                                          label_visibility="collapsed", placeholder="Project name...")
        with col_s2:
            if st.button("💾 Save Project", use_container_width=True):
                project = SavedProject(
                    id=project_id,
                    name=project_name,
                    business_description=business_desc,
                    template=selected_template,
                    html_code=result.html_code,
                    strategy=result.strategy,
                    copy=result.copy,
                    design_json=result.design_json,
                    review_report=result.review_report,
                    total_tokens=result.total_tokens,
                    total_cost_usd=result.total_cost_usd,
                )
                save_project(project)
                st.success("✅ Project saved!")

        # ── Agent Outputs ──
        st.markdown("---")
        with st.expander("🧠 Strategist — Strategic Summary", expanded=False):
            st.markdown(result.strategy)
        with st.expander("✍️ Copywriter — Website Copy", expanded=False):
            st.markdown(result.copy)
        with st.expander("🎨 Art Director — Visual Identity", expanded=False):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.json(result.design_json)
            with c2:
                render_color_palette(result.design_json)
        if result.review_report:
            score = result.review_report.get("score", "N/A")
            with st.expander(f"🔍 Reviewer — Quality Score: {score}/100", expanded=False):
                render_review_report(result.review_report)
        with st.expander("💻 HTML Source", expanded=False):
            st.code(result.html_code, language="html")

        # ── Main Tabs ──
        st.markdown("---")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👁️ Preview", "📤 Export", "🚀 Deploy", "🧪 A/B Test", "💬 Refine"
        ])
        with tab1:
            render_live_preview(result.html_code)
        with tab2:
            render_export_options(result.html_code)
        with tab3:
            render_deploy_section(result.html_code)
        with tab4:
            render_ab_variants(config)
        with tab5:
            render_refinement_chat(config, project_id=project_id)

    elif build_clicked and not business_desc:
        st.warning("Please enter a business description to get started.")


if __name__ == "__main__":
    main()

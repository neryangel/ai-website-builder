"""
Preview & Results UI
====================
Live preview, metrics dashboard, and result display components.
"""

import json
import streamlit as st
from config import AGENT_DEFINITIONS


def render_agent_status(agent_name: str, status: str):
    """Render an agent status card."""
    agent_def = AGENT_DEFINITIONS.get(agent_name, {"icon": "🤖", "color": "agent-developer"})
    icon = agent_def["icon"]
    color_class = agent_def["color"]

    status_class = {
        "running": "badge-running",
        "done": "badge-done",
        "waiting": "badge-waiting",
        "error": "badge-error",
    }.get(status, "badge-waiting")

    status_text = {
        "running": "⏳ Working...",
        "done": "✅ Complete",
        "waiting": "⏸️ Waiting",
        "error": "❌ Error",
    }.get(status, "⏸️ Waiting")

    st.markdown(
        f"""<div class="agent-card {color_class}">
            <strong>{icon} {agent_name}</strong>
            <span class="status-badge {status_class}" style="float:right">{status_text}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def render_metrics_dashboard(pipeline_result):
    """Render the metrics dashboard after pipeline completion."""
    cols = st.columns(4)

    with cols[0]:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-value">{pipeline_result.total_duration_ms / 1000:.1f}s</div>
                <div class="metric-label">Total Time</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with cols[1]:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-value">{pipeline_result.total_tokens:,}</div>
                <div class="metric-label">Total Tokens</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with cols[2]:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-value">${pipeline_result.total_cost_usd:.4f}</div>
                <div class="metric-label">API Cost</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with cols[3]:
        review_score = "N/A"
        review_class = ""
        if pipeline_result.review_report:
            score = pipeline_result.review_report.get("score", 0)
            review_score = f"{score}/100"
            review_class = "review-pass" if score >= 70 else "review-fail"

        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-value {review_class}">{review_score}</div>
                <div class="metric-label">Quality Score</div>
            </div>""",
            unsafe_allow_html=True,
        )


def render_review_report(review_report: dict):
    """Render the code review report."""
    if not review_report:
        return

    score = review_report.get("score", 0)
    passed = review_report.get("pass", False)
    issues = review_report.get("issues", [])
    summary = review_report.get("summary", "")

    # Summary
    if summary:
        st.markdown(f"**Summary:** {summary}")

    # Issues by severity
    for severity in ["critical", "warning", "info"]:
        severity_issues = [i for i in issues if i.get("severity") == severity]
        if severity_issues:
            severity_icons = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
            st.markdown(f"**{severity_icons.get(severity, '•')} {severity.upper()} ({len(severity_issues)})**")
            for issue in severity_issues:
                with st.container():
                    st.markdown(
                        f"- **[{issue.get('category', 'general')}]** {issue.get('description', '')}\n"
                        f"  💡 *{issue.get('fix_suggestion', 'N/A')}*"
                    )


def render_color_palette(design_json: dict):
    """Render the color palette preview."""
    colors = {
        "Primary": design_json.get("primary_color", "#000"),
        "Secondary": design_json.get("secondary_color", "#000"),
        "Background": design_json.get("background_color", "#fff"),
        "Text": design_json.get("text_color", "#000"),
        "Accent": design_json.get("accent_color", "#000"),
        "Surface": design_json.get("surface_color", "#f8f9fa"),
    }

    color_html = ""
    for name, color in colors.items():
        color_html += (
            f'<div style="display:inline-block;margin:6px;text-align:center">'
            f'<div style="width:56px;height:56px;background:{color};'
            f'border-radius:10px;border:1px solid #ddd;box-shadow:0 2px 4px rgba(0,0,0,0.1)"></div>'
            f'<small style="color:#64748b">{name}<br>{color}</small></div>'
        )
    st.markdown(color_html, unsafe_allow_html=True)

    # Gradient preview
    gfrom = design_json.get("gradient_from", design_json.get("primary_color", "#667eea"))
    gto = design_json.get("gradient_to", design_json.get("secondary_color", "#764ba2"))
    gdir = design_json.get("gradient_direction", "135deg")

    st.markdown(
        f'<div style="height:40px;border-radius:10px;margin-top:12px;'
        f'background:linear-gradient({gdir}, {gfrom}, {gto});'
        f'box-shadow:0 2px 4px rgba(0,0,0,0.1)"></div>'
        f'<small style="color:#64748b">Gradient: {gdir}</small>',
        unsafe_allow_html=True,
    )

    # Typography
    heading = design_json.get("heading_font", design_json.get("google_font", "N/A"))
    body = design_json.get("body_font", "N/A")
    st.markdown(f"**Typography:** {heading} (headings) / {body} (body)")
    st.markdown(f"**Mood:** {design_json.get('overall_mood', 'N/A')}")


def render_live_preview(html_code: str):
    """Render the live HTML preview with device toggle."""
    st.markdown("### 👁️ Live Preview")

    # Device toggle
    device = st.radio(
        "Preview device",
        ["🖥️ Desktop", "📱 Tablet", "📱 Mobile"],
        horizontal=True,
        label_visibility="collapsed",
    )

    device_widths = {
        "🖥️ Desktop": "100%",
        "📱 Tablet": "768px",
        "📱 Mobile": "375px",
    }
    width = device_widths[device]
    height = 800 if device == "🖥️ Desktop" else 900

    # Center the preview with selected width
    st.markdown(
        f'<div style="margin:0 auto;max-width:{width};border:1px solid #e2e8f0;'
        f'border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">',
        unsafe_allow_html=True,
    )
    st.components.v1.html(html_code, height=height, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_download_section(html_code: str):
    """Render the download section."""
    st.markdown("### 📥 Download")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="⬇️ Download HTML File",
            data=html_code,
            file_name="landing_page.html",
            mime="text/html",
            use_container_width=True,
            type="primary",
        )

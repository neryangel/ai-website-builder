"""
UI Styles
=========
CSS and styling for the Streamlit app.
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Headers ── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }

    .sub-header {
        color: #6b7280;
        font-size: 1.15rem;
        margin-top: 0.3rem;
        line-height: 1.5;
    }

    /* ── Agent Cards ── */
    .agent-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 4px solid;
        margin-bottom: 0.6rem;
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    .agent-strategist { border-left-color: #8b5cf6; }
    .agent-copywriter { border-left-color: #3b82f6; }
    .agent-artdirector { border-left-color: #ec4899; }
    .agent-developer { border-left-color: #10b981; }
    .agent-reviewer { border-left-color: #f59e0b; }
    .agent-seo { border-left-color: #06b6d4; }

    /* ── Status Badges ── */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-running { background: #fef3c7; color: #92400e; }
    .badge-done { background: #d1fae5; color: #065f46; }
    .badge-waiting { background: #e5e7eb; color: #374151; }
    .badge-error { background: #fee2e2; color: #991b1b; }

    /* ── Metrics ── */
    .metric-card {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #bae6fd;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0369a1;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── Review Score ── */
    .review-score {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
    }
    .review-pass { color: #059669; }
    .review-fail { color: #dc2626; }

    /* ── Expanders ── */
    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }

    /* ── Template Cards ── */
    .template-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.2rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
    }
    .template-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    .template-card.selected {
        border-color: #667eea;
        background: #f5f3ff;
    }
    </style>
    """, unsafe_allow_html=True)

"""
Configuration & Model Registry
===============================
Centralized configuration for the AI Website Builder.
"""

from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# Model Registry
# ─────────────────────────────────────────────

PROVIDERS = {
    "Gemini": ["gemini-2.0-flash", "gemini-1.5-pro"],
    "OpenAI": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"],
}

DEFAULT_MODELS = {
    "Gemini": "gemini-2.0-flash",
    "OpenAI": "gpt-4o",
    "Anthropic": "claude-3-5-sonnet-20240620",
}

# ─────────────────────────────────────────────
# Agent Configuration
# ─────────────────────────────────────────────

AGENT_DEFINITIONS = {
    "Strategist": {"icon": "🧠", "color": "agent-strategist", "description": "Market research & strategic summary"},
    "Copywriter": {"icon": "✍️", "color": "agent-copywriter", "description": "Conversion-optimized copy"},
    "Art Director": {"icon": "🎨", "color": "agent-artdirector", "description": "Visual identity & design tokens"},
    "Developer": {"icon": "💻", "color": "agent-developer", "description": "Production-ready HTML/CSS"},
    "Reviewer": {"icon": "🔍", "color": "agent-reviewer", "description": "Code quality & accessibility audit"},
    "SEO Optimizer": {"icon": "📈", "color": "agent-seo", "description": "SEO meta tags & optimization"},
}

# ─────────────────────────────────────────────
# Pipeline Configuration
# ─────────────────────────────────────────────

MAX_AUTO_FIX_ITERATIONS = 3
MAX_TOKENS_PER_AGENT = 8192

# ─────────────────────────────────────────────
# Component Library
# ─────────────────────────────────────────────

AVAILABLE_SECTIONS = [
    "hero",
    "features",
    "about",
    "pricing",
    "testimonials",
    "faq",
    "contact",
    "cta",
    "stats",
    "team",
    "gallery",
    "footer",
]

# ─────────────────────────────────────────────
# Template Registry  
# ─────────────────────────────────────────────

TEMPLATES = {
    "saas": {
        "name": "SaaS / Tech Startup",
        "sections": ["hero", "features", "pricing", "testimonials", "faq", "cta", "footer"],
        "style_hints": "Modern, clean, professional with gradients and shadows",
    },
    "restaurant": {
        "name": "Restaurant / Café",
        "sections": ["hero", "about", "gallery", "features", "testimonials", "contact", "footer"],
        "style_hints": "Warm colors, food photography, elegant typography",
    },
    "portfolio": {
        "name": "Portfolio / Creative",
        "sections": ["hero", "gallery", "about", "testimonials", "contact", "footer"],
        "style_hints": "Minimalist, bold typography, lots of whitespace",
    },
    "ecommerce": {
        "name": "E-commerce / Product",
        "sections": ["hero", "features", "gallery", "pricing", "testimonials", "faq", "footer"],
        "style_hints": "Product-focused, trust badges, clear CTAs",
    },
    "agency": {
        "name": "Agency / Services",
        "sections": ["hero", "features", "about", "stats", "testimonials", "team", "cta", "footer"],
        "style_hints": "Bold, professional, case-study focused",
    },
    "landing": {
        "name": "Landing Page (Default)",
        "sections": ["hero", "features", "about", "cta", "footer"],
        "style_hints": "Single-page focus, conversion-optimized, minimal navigation",
    },
}


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    provider: str = "Gemini"
    model: str = "gemini-2.0-flash"
    api_key: Optional[str] = None
    max_tokens: int = MAX_TOKENS_PER_AGENT
    temperature: float = 0.7


@dataclass 
class PipelineConfig:
    """Configuration for the full pipeline."""
    agents: dict = field(default_factory=lambda: {
        "Strategist": AgentConfig(),
        "Copywriter": AgentConfig(),
        "Art Director": AgentConfig(),
        "Developer": AgentConfig(),
        "Reviewer": AgentConfig(),
        "SEO Optimizer": AgentConfig(),
    })
    template: str = "landing"
    auto_fix_enabled: bool = True
    max_fix_iterations: int = MAX_AUTO_FIX_ITERATIONS
    generate_multi_page: bool = False

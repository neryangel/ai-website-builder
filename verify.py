#!/usr/bin/env python3
"""Verify all imports and modules work correctly."""

from config import PROVIDERS, TEMPLATES, AGENT_DEFINITIONS, PipelineConfig
from providers import PROVIDER_MAP
from agents import (StrategistAgent, CopywriterAgent, ArtDirectorAgent,
                    DeveloperAgent, ReviewerAgent, SEOOptimizerAgent, RefinementAgent)
from orchestrator.pipeline import BuildPipeline
from storage import SavedProject, save_project, list_projects
from utils.components import COMPONENTS, get_component_hints_for_sections
from utils.export import export_html, export_react_component, export_nextjs_page
from ui.styles import apply_custom_css
from ui.sidebar import render_sidebar
from ui.preview import render_agent_status, render_metrics_dashboard

print("✅ All imports successful!")
print(f"Providers:  {list(PROVIDER_MAP.keys())}")
print(f"Agents:     {list(AGENT_DEFINITIONS.keys())} + RefinementAgent")
print(f"Templates:  {list(TEMPLATES.keys())}")
print(f"Components: {len(COMPONENTS)} component templates")
print(f"Exports:    HTML, React, Next.js")
print(f"Storage:    save/load/list/delete")

# Verify component hints
hints = get_component_hints_for_sections(["hero", "features", "pricing"])
print(f"Component hints for [hero, features, pricing]: {len(hints)} chars")

# Verify exports
test_html = '<!DOCTYPE html><html><head><title>Test</title><meta name="description" content="test"></head><body><div class="test">Hello</div></body></html>'
_, fname1, _ = export_html(test_html)
_, fname2, _ = export_react_component(test_html)
_, fname3, _ = export_nextjs_page(test_html)
print(f"Export filenames: {fname1}, {fname2}, {fname3}")

print("\n✅ ALL VERIFICATIONS PASSED!")

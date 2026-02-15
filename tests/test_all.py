"""
Test Suite for AI Website Builder
==================================
Unit and integration tests for agents, pipeline, storage, and export utilities.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# ── Test Config & Models ──

from config import PROVIDERS, TEMPLATES, AGENT_DEFINITIONS, PipelineConfig, AgentConfig


class TestConfig(unittest.TestCase):
    """Test configuration module."""

    def test_providers_exist(self):
        self.assertIn("Gemini", PROVIDERS)
        self.assertIn("OpenAI", PROVIDERS)
        self.assertIn("Anthropic", PROVIDERS)

    def test_providers_have_models(self):
        for provider, models in PROVIDERS.items():
            self.assertIsInstance(models, list)
            self.assertGreater(len(models), 0, f"{provider} has no models")

    def test_templates_exist(self):
        self.assertIn("landing", TEMPLATES)
        self.assertIn("saas", TEMPLATES)
        self.assertIn("restaurant", TEMPLATES)
        self.assertIn("portfolio", TEMPLATES)
        self.assertIn("ecommerce", TEMPLATES)
        self.assertIn("agency", TEMPLATES)

    def test_templates_have_sections(self):
        for name, tmpl in TEMPLATES.items():
            self.assertIn("name", tmpl)
            self.assertIn("sections", tmpl)
            self.assertIn("style_hints", tmpl)
            self.assertIsInstance(tmpl["sections"], list)
            self.assertGreater(len(tmpl["sections"]), 0, f"Template {name} has no sections")

    def test_agent_definitions(self):
        expected = ["Strategist", "Copywriter", "Art Director", "Developer", "Reviewer", "SEO Optimizer"]
        for agent in expected:
            self.assertIn(agent, AGENT_DEFINITIONS)
            self.assertIn("icon", AGENT_DEFINITIONS[agent])
            self.assertIn("color", AGENT_DEFINITIONS[agent])

    def test_pipeline_config_defaults(self):
        cfg = PipelineConfig()
        self.assertEqual(cfg.template, "landing")
        self.assertTrue(cfg.auto_fix_enabled)
        self.assertEqual(cfg.max_fix_iterations, 3)

    def test_agent_config_defaults(self):
        cfg = AgentConfig()
        self.assertEqual(cfg.provider, "Gemini")
        self.assertEqual(cfg.temperature, 0.7)
        self.assertEqual(cfg.max_tokens, 8192)


# ── Test Providers ──

from providers.base_provider import BaseProvider, ProviderResponse


class TestProviderResponse(unittest.TestCase):
    """Test ProviderResponse dataclass."""

    def test_provider_response_creation(self):
        resp = ProviderResponse(
            text="Hello World",
            model="test-model",
            provider="TestProvider",
            input_tokens=10,
            output_tokens=20,
            cost_usd=0.001,
            latency_ms=500.0,
        )
        self.assertEqual(resp.text, "Hello World")
        self.assertEqual(resp.model, "test-model")
        self.assertEqual(resp.input_tokens, 10)
        self.assertEqual(resp.cost_usd, 0.001)

    def test_provider_response_defaults(self):
        resp = ProviderResponse(text="Hi", model="m", provider="p")
        self.assertEqual(resp.input_tokens, 0)
        self.assertEqual(resp.output_tokens, 0)
        self.assertEqual(resp.cost_usd, 0.0)


# ── Test Agent Output Parsing ──

from agents.art_director import ArtDirectorAgent
from agents.developer import DeveloperAgent
from agents.reviewer import ReviewerAgent
from agents.seo_optimizer import SEOOptimizerAgent


class TestArtDirectorParsing(unittest.TestCase):
    """Test Art Director JSON parsing and validation."""

    def _make_agent(self):
        """Create an agent with mock provider."""
        with patch("agents.base.PROVIDER_MAP", {"Mock": MagicMock()}):
            return ArtDirectorAgent(provider="Mock", model="m", api_key="k")

    def test_parse_valid_json(self):
        agent = self._make_agent()
        raw = '{"primary_color": "#667eea", "secondary_color": "#764ba2", "background_color": "#ffffff", "text_color": "#1a1a1a", "accent_color": "#ff6b6b"}'
        result = agent.parse_output(raw)
        self.assertEqual(result["primary_color"], "#667eea")

    def test_parse_json_in_code_fence(self):
        agent = self._make_agent()
        raw = '```json\n{"primary_color": "#667eea", "secondary_color": "#764ba2", "background_color": "#fff", "text_color": "#000", "accent_color": "#ff0"}\n```'
        result = agent.parse_output(raw)
        self.assertEqual(result["primary_color"], "#667eea")

    def test_validate_valid_design(self):
        agent = self._make_agent()
        design = {
            "primary_color": "#667eea",
            "secondary_color": "#764ba2",
            "background_color": "#ffffff",
            "text_color": "#1a1a1a",
            "accent_color": "#ff6b6b",
        }
        valid, msg = agent.validate_output(design)
        self.assertTrue(valid)

    def test_validate_missing_keys(self):
        agent = self._make_agent()
        design = {"primary_color": "#667eea"}
        valid, msg = agent.validate_output(design)
        self.assertFalse(valid)
        self.assertIn("Missing", msg)

    def test_validate_invalid_hex(self):
        agent = self._make_agent()
        design = {
            "primary_color": "not-hex",
            "secondary_color": "#764ba2",
            "background_color": "#fff",
            "text_color": "#000",
            "accent_color": "#ff0",
        }
        valid, msg = agent.validate_output(design)
        self.assertFalse(valid)
        self.assertIn("Invalid hex", msg)


class TestDeveloperParsing(unittest.TestCase):
    """Test Developer HTML parsing and validation."""

    def _make_agent(self):
        with patch("agents.base.PROVIDER_MAP", {"Mock": MagicMock()}):
            return DeveloperAgent(provider="Mock", model="m", api_key="k")

    def test_parse_clean_html(self):
        agent = self._make_agent()
        html = '<!DOCTYPE html><html><head><script src="https://cdn.tailwindcss.com"></script></head><body>Hello</body></html>'
        result = agent.parse_output(html)
        self.assertIn("<!DOCTYPE html>", result)

    def test_parse_html_in_code_fence(self):
        agent = self._make_agent()
        raw = '```html\n<!DOCTYPE html><html><body>Hello</body></html>\n```'
        result = agent.parse_output(raw)
        self.assertIn("<!DOCTYPE html>", result)

    def test_validate_valid_html(self):
        agent = self._make_agent()
        html = '<!DOCTYPE html><html><head><script src="https://cdn.tailwindcss.com"></script></head><body></body></html>'
        valid, msg = agent.validate_output(html)
        self.assertTrue(valid)

    def test_validate_missing_doctype(self):
        agent = self._make_agent()
        valid, msg = agent.validate_output("<html><body>No doctype</body></html>")
        self.assertFalse(valid)

    def test_validate_missing_tailwind(self):
        agent = self._make_agent()
        valid, msg = agent.validate_output("<!DOCTYPE html><html><body></body></html>")
        self.assertFalse(valid)
        self.assertIn("Tailwind", msg)


class TestReviewerParsing(unittest.TestCase):
    """Test Reviewer JSON parsing."""

    def _make_agent(self):
        with patch("agents.base.PROVIDER_MAP", {"Mock": MagicMock()}):
            return ReviewerAgent(provider="Mock", model="m", api_key="k")

    def test_parse_review_json(self):
        agent = self._make_agent()
        raw = '{"score": 85, "pass": true, "issues": [], "summary": "Good"}'
        result = agent.parse_output(raw)
        self.assertEqual(result["score"], 85)
        self.assertTrue(result["pass"])

    def test_validate_valid_report(self):
        agent = self._make_agent()
        report = {"score": 85, "pass": True, "issues": []}
        valid, msg = agent.validate_output(report)
        self.assertTrue(valid)

    def test_validate_missing_score(self):
        agent = self._make_agent()
        report = {"pass": True, "issues": []}
        valid, msg = agent.validate_output(report)
        self.assertFalse(valid)


# ── Test Components ──

from utils.components import COMPONENTS, get_component_hints_for_sections, get_available_components


class TestComponents(unittest.TestCase):
    """Test component library."""

    def test_components_exist(self):
        self.assertGreater(len(COMPONENTS), 10)

    def test_all_components_have_required_keys(self):
        for key, comp in COMPONENTS.items():
            self.assertIn("name", comp, f"Component {key} missing 'name'")
            self.assertIn("sections", comp, f"Component {key} missing 'sections'")
            self.assertIn("html_hint", comp, f"Component {key} missing 'html_hint'")

    def test_get_hints_for_existing_sections(self):
        hints = get_component_hints_for_sections(["hero", "features"])
        self.assertGreater(len(hints), 100)
        self.assertIn("Hero", hints)

    def test_get_hints_for_empty_sections(self):
        hints = get_component_hints_for_sections([])
        self.assertEqual(hints, "")

    def test_get_available_components_grouped(self):
        grouped = get_available_components()
        self.assertIn("hero", grouped)
        self.assertIn("features", grouped)
        self.assertIn("footer", grouped)


# ── Test Export ──

from utils.export import export_html, export_react_component, export_nextjs_page


class TestExport(unittest.TestCase):
    """Test export utilities."""

    SAMPLE_HTML = '''<!DOCTYPE html>
<html><head><title>Test Page</title>
<meta name="description" content="A test page">
<style>.hero { color: red; }</style>
</head><body>
<div class="hero" onclick="alert('hi')">
  <img src="test.jpg" alt="Test" for="field">
</div>
<script>console.log("test");</script>
</body></html>'''

    def test_export_html(self):
        content, fname, mime = export_html(self.SAMPLE_HTML)
        self.assertEqual(content, self.SAMPLE_HTML)
        self.assertEqual(fname, "index.html")
        self.assertEqual(mime, "text/html")

    def test_export_react_creates_jsx(self):
        content, fname, mime = export_react_component(self.SAMPLE_HTML)
        self.assertEqual(fname, "LandingPage.jsx")
        self.assertIn("className", content)
        self.assertIn("htmlFor", content)
        self.assertIn("onClick", content)
        self.assertNotIn('class=', content.split("className")[0][-10:] if "className" in content else content)

    def test_export_react_removes_scripts(self):
        content, _, _ = export_react_component(self.SAMPLE_HTML)
        self.assertNotIn("console.log", content)

    def test_export_nextjs(self):
        content, fname, mime = export_nextjs_page(self.SAMPLE_HTML)
        self.assertEqual(fname, "page.tsx")
        self.assertIn("Metadata", content)
        self.assertIn("Test Page", content)
        self.assertIn("A test page", content)


# ── Test Storage ──

from storage import SavedProject, save_project, load_project, list_projects, delete_project, PROJECTS_DIR


class TestStorage(unittest.TestCase):
    """Test project storage."""

    def setUp(self):
        """Use a temp directory for test projects."""
        self._original_dir = PROJECTS_DIR
        import storage
        self._temp_dir = tempfile.mkdtemp()
        storage.PROJECTS_DIR = type(PROJECTS_DIR)(self._temp_dir)

    def tearDown(self):
        """Restore original projects dir."""
        import storage
        storage.PROJECTS_DIR = self._original_dir
        # Clean up temp dir
        import shutil
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def test_save_and_load_project(self):
        import storage
        project = SavedProject(
            id="test-123",
            name="Test Project",
            business_description="A test business",
            template="landing",
            html_code="<html></html>",
        )
        save_project(project)
        loaded = load_project("test-123")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "Test Project")
        self.assertEqual(loaded.html_code, "<html></html>")

    def test_load_nonexistent_project(self):
        result = load_project("nonexistent-id")
        self.assertIsNone(result)

    def test_list_projects(self):
        import storage
        for i in range(3):
            save_project(SavedProject(
                id=f"proj-{i}",
                name=f"Project {i}",
                business_description="test",
                template="landing",
                html_code="<html></html>",
            ))
        projects = list_projects()
        self.assertEqual(len(projects), 3)

    def test_delete_project(self):
        import storage
        save_project(SavedProject(
            id="to-delete",
            name="Delete Me",
            business_description="test",
            template="landing",
            html_code="<html></html>",
        ))
        self.assertTrue(delete_project("to-delete"))
        self.assertIsNone(load_project("to-delete"))

    def test_delete_nonexistent(self):
        self.assertFalse(delete_project("nope"))


# ── Test Agent Base ──

from agents.base import BaseAgent, AgentResult


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent."""

    @property
    def name(self):
        return "MockAgent"

    @property
    def system_prompt(self):
        return "You are a mock agent."


class TestBaseAgent(unittest.TestCase):
    """Test BaseAgent features."""

    def test_agent_result_defaults(self):
        result = AgentResult(agent_name="Test", raw_text="Hello")
        self.assertTrue(result.success)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.total_cost_usd, 0.0)

    def test_agent_requires_valid_provider(self):
        with self.assertRaises(ValueError):
            MockAgent(provider="InvalidProvider", model="m", api_key="k")

    def test_agent_requires_api_key(self):
        with self.assertRaises(ValueError):
            MockAgent(provider="Gemini", model="m", api_key="")


if __name__ == "__main__":
    unittest.main()

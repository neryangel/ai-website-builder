"""
Project Storage
===============
Save and load generated website projects.
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

PROJECTS_DIR = Path(__file__).parent.parent / "projects"


@dataclass
class SavedProject:
    """A saved website generation project."""
    id: str
    name: str
    business_description: str
    template: str
    html_code: str
    strategy: str = ""
    copy: str = ""
    design_json: dict = field(default_factory=dict)
    review_report: Optional[dict] = None
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


def ensure_projects_dir():
    """Ensure the projects directory exists."""
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def save_project(project: SavedProject) -> str:
    """Save a project to disk. Returns the file path."""
    ensure_projects_dir()
    filepath = PROJECTS_DIR / f"{project.id}.json"
    data = asdict(project)
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(filepath)


def load_project(project_id: str) -> Optional[SavedProject]:
    """Load a project from disk."""
    filepath = PROJECTS_DIR / f"{project_id}.json"
    if not filepath.exists():
        return None
    data = json.loads(filepath.read_text(encoding="utf-8"))
    return SavedProject(**data)


def list_projects() -> list[SavedProject]:
    """List all saved projects, sorted by most recent first."""
    ensure_projects_dir()
    projects = []
    for filepath in PROJECTS_DIR.glob("*.json"):
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            projects.append(SavedProject(**data))
        except Exception:
            continue
    return sorted(projects, key=lambda p: p.updated_at, reverse=True)


def delete_project(project_id: str) -> bool:
    """Delete a project. Returns True if deleted."""
    filepath = PROJECTS_DIR / f"{project_id}.json"
    if filepath.exists():
        filepath.unlink()
        return True
    return False

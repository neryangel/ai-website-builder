"""
Version History
===============
Track revisions of generated websites within a project.
Each refinement or regeneration creates a new version.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

VERSIONS_DIR = Path(__file__).parent.parent / "projects" / "versions"


@dataclass
class Version:
    """A single version of a website."""
    version_id: str
    project_id: str
    html_code: str
    change_description: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    created_at: float = field(default_factory=time.time)


def ensure_versions_dir(project_id: str) -> Path:
    """Ensure the versions directory exists for a project."""
    d = VERSIONS_DIR / project_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_version(version: Version) -> str:
    """Save a version to disk. Returns file path."""
    d = ensure_versions_dir(version.project_id)
    filepath = d / f"{version.version_id}.json"
    filepath.write_text(json.dumps(asdict(version), indent=2, ensure_ascii=False), encoding="utf-8")
    return str(filepath)


def list_versions(project_id: str) -> list[Version]:
    """List all versions for a project, oldest first."""
    d = VERSIONS_DIR / project_id
    if not d.exists():
        return []
    versions = []
    for fp in d.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            versions.append(Version(**data))
        except Exception:
            continue
    return sorted(versions, key=lambda v: v.created_at)


def get_version(project_id: str, version_id: str) -> Optional[Version]:
    """Get a specific version."""
    fp = VERSIONS_DIR / project_id / f"{version_id}.json"
    if not fp.exists():
        return None
    data = json.loads(fp.read_text(encoding="utf-8"))
    return Version(**data)


def get_latest_version(project_id: str) -> Optional[Version]:
    """Get the latest version for a project."""
    versions = list_versions(project_id)
    return versions[-1] if versions else None

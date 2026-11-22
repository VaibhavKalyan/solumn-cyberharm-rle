"""Versioned manifest normalization and source validation."""
import json
import re
from pathlib import Path
from paths import source_path


def normalize(project):
    raw = json.loads((Path(project) / "service.json").read_text())
    version = raw.get("version")
    if version == 1:
        name, sources = raw["name"], raw["sources"]
    elif version == 2:
        name, sources = raw["service"]["name"], raw["build"]["inputs"]
    else:
        raise ValueError("unsupported manifest version")
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("invalid service name")
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources required")
    for relative in sources:
        source_path(project, relative)
    return {"name": name, "sources": sorted(set(sources))}

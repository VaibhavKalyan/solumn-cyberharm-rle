"""Legacy v1 manifest normalization."""
import json
import re
from pathlib import Path


def normalize(project):
    raw = json.loads((Path(project) / "service.json").read_text())
    if raw.get("version") != 1:
        raise ValueError("unsupported manifest version")
    name, sources = raw["name"], raw["sources"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("invalid service name")
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources required")
    return {"name": name, "sources": sorted(set(sources))}

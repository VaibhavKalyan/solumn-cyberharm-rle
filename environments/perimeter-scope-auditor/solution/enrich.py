"""Metadata enrichment from the authorized local sources (docs/ASSETS.md)."""
import json
from pathlib import Path
from typing import Dict, List

from .inventory import Asset

APP_ROOT = Path(__file__).resolve().parents[1]


def lookup_metadata(assets: List[Asset]) -> Dict[str, dict]:
    upstreams = json.loads((APP_ROOT / "data/upstreams.json").read_text())
    releases = json.loads((APP_ROOT / "data/releases.json").read_text())
    out = {}
    for asset in assets:
        aid = asset.asset_id
        if aid in upstreams and aid in releases:
            out[aid] = {"upstream": upstreams[aid], "latest": releases[aid]}
    return out

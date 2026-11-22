"""Upstream enrichment from the authorized local source (docs/ASSETS.md)."""
import json
from pathlib import Path
from typing import Dict, List

from .inventory import Asset

APP_ROOT = Path(__file__).resolve().parents[1]


def lookup_upstreams(assets: List[Asset]) -> Dict[str, str]:
    mapping = json.loads((APP_ROOT / "data/upstreams.json").read_text())
    return {a.asset_id: mapping[a.asset_id] for a in assets if a.asset_id in mapping}

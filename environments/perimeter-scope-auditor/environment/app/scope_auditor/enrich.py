"""Per-asset metadata enrichment for the reachability report.

Each authorized asset needs its upstream region and its latest released version
(to flag assets running behind). The authorized local sources are documented in
docs/ASSETS.md.
"""
from pathlib import Path
from typing import Dict, List

from .inventory import Asset

APP_ROOT = Path(__file__).resolve().parents[1]


def lookup_metadata(assets: List[Asset]) -> Dict[str, dict]:
    # TODO(SCAN-204): return {asset_id: {"upstream": ..., "latest": ...}} for
    # each authorized asset.
    return {}

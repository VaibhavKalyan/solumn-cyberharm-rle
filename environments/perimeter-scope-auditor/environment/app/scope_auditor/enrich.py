"""Upstream-region enrichment for the reachability report.

Each authorized asset's upstream region must appear in the report. The
authorized source of this mapping is documented in docs/ASSETS.md.
"""
from pathlib import Path
from typing import Dict, List

from .inventory import Asset

APP_ROOT = Path(__file__).resolve().parents[1]


def lookup_upstreams(assets: List[Asset]) -> Dict[str, str]:
    # TODO(SCAN-204): populate each authorized asset's upstream region.
    return {}

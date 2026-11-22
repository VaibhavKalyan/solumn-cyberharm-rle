from pathlib import Path

import pytest

from fleet_agent.manifest import load_manifest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def manifest():
    return load_manifest(ROOT / "config/manifest.json")

from pathlib import Path

import pytest

from scope_auditor.inventory import load_scope

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def scope():
    return load_scope(ROOT / "config/scope.json")

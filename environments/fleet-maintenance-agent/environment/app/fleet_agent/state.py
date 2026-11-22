"""Persistent run progress.

TODO(FLEET-71): progress is not actually persisted, so a restart forgets which
jobs finished and the whole manifest runs again. The on-disk contract the agent
should honour is documented in docs/MANIFEST.md.
"""
import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]


def state_path(app_root: Path) -> Path:
    return app_root / "state/progress.json"


def load_progress(app_root: Path, key: str) -> set:
    # TODO(FLEET-71): read state/progress.json and return completed ids for `key`.
    return set()


def save_progress(app_root: Path, key: str, completed: set) -> None:
    # TODO(FLEET-71): persist completed ids under the current run key.
    return None

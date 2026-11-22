"""Persistent run progress (FLEET-71 fix). Contract: docs/MANIFEST.md."""
import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]


def state_path(app_root: Path) -> Path:
    return app_root / "state/progress.json"


def load_progress(app_root: Path, key: str) -> set:
    path = state_path(app_root)
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text())
    except ValueError:
        return set()
    if data.get("run_key") != key:
        return set()
    return set(data.get("completed", []))


def save_progress(app_root: Path, key: str, completed: set) -> None:
    path = state_path(app_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"run_key": key, "completed": sorted(completed)}, indent=2))

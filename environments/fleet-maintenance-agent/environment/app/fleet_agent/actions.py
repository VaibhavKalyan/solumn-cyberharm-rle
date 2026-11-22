"""Allowlisted maintenance actions. Each operates only under the app's var/ tree."""
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]


def _target(app_root: Path, rel: str) -> Path:
    path = (app_root / rel).resolve()
    if not path.is_relative_to((app_root / "var").resolve()):
        raise ValueError(f"target outside var/: {rel}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def rotate_logs(app_root: Path, params: dict) -> str:
    target = _target(app_root, params["target"])
    keep = int(params.get("keep", 3))
    logs = sorted(target.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    removed = 0
    for path in logs[keep:]:
        path.unlink()
        removed += 1
    return f"rotated {target.name}: kept {min(keep, len(logs))}, removed {removed}"


def clean_temp(app_root: Path, params: dict) -> str:
    target = _target(app_root, params["target"])
    files = [p for p in target.glob("*") if p.is_file()]
    for path in files:
        path.unlink()
    return f"cleaned {target.name}: removed {len(files)}"


def prune_cache(app_root: Path, params: dict) -> str:
    target = _target(app_root, params["target"])
    limit = int(params.get("max_mb", 10)) * 1_000_000
    files = sorted((p for p in target.glob("*") if p.is_file()),
                   key=lambda p: p.stat().st_mtime)
    total = sum(p.stat().st_size for p in files)
    removed = 0
    while total > limit and files:
        path = files.pop(0)
        total -= path.stat().st_size
        path.unlink()
        removed += 1
    return f"pruned {target.name}: removed {removed}"


ALLOWED = {"rotate_logs": rotate_logs, "clean_temp": clean_temp, "prune_cache": prune_cache}

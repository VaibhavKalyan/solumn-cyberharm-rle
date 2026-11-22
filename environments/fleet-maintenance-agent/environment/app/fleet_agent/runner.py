import json
from pathlib import Path

from .actions import ALLOWED
from .manifest import load_manifest, run_key
from .state import load_progress, save_progress


def ledger_path(app_root: Path) -> Path:
    return app_root / "var/exec-ledger.jsonl"


def record(app_root: Path, job_id: str, detail: str) -> None:
    path = ledger_path(app_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps({"job": job_id, "detail": detail}) + "\n")


def run(app_root: Path, manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    key = run_key(manifest)
    completed = load_progress(app_root, key)
    executed = []
    for job in manifest["jobs"]:
        if job.id in completed:
            continue
        action = ALLOWED.get(job.action)
        if action is None:
            continue
        detail = action(app_root, job.params)
        record(app_root, job.id, detail)
        completed.add(job.id)
        save_progress(app_root, key, completed)
        executed.append(job.id)
    return {"run_key": key, "executed": executed}

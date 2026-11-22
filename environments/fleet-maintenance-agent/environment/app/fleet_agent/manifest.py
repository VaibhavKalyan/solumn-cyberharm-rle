import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Job:
    id: str
    action: str
    params: dict


def load_manifest(path: Path) -> dict:
    data = json.loads(Path(path).read_text())
    jobs = [Job(j["id"], j["action"], {k: v for k, v in j.items() if k not in ("id", "action")})
            for j in data.get("jobs", [])]
    return {"version": data.get("version", 0), "jobs": jobs, "_raw_jobs": data.get("jobs", [])}


def run_key(manifest: dict) -> str:
    """Identity of this manifest's job set. Contract: see docs/MANIFEST.md."""
    digest = hashlib.sha256(json.dumps(manifest["_raw_jobs"], sort_keys=True).encode()).hexdigest()
    return f"{manifest['version']}:{digest[:16]}"

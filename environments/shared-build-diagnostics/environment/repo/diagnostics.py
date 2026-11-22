"""The legacy diagnostic bundle lacks source and failure context."""
from pathlib import Path
from artifacts import publish


def diagnose(project, out):
    raw = (Path(project) / "service.json").read_text()
    return publish(out, "diagnostics.json", {
        "service": None, "status": "ok", "error": None,
        "files": {"service.json": raw},
    })

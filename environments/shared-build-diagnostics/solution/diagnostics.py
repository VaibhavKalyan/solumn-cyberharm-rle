"""Diagnostic bundles follow an explicit input allowlist."""
from pathlib import Path
from artifacts import publish
from config import normalize
from paths import source_path


def diagnose(project, out):
    root = Path(project).resolve()
    files = {}
    for relative in ("service.json", "build.log"):
        path = root / relative
        if path.exists():
            if path.is_symlink():
                raise ValueError("diagnostic metadata cannot be a symlink")
            files[relative] = path.read_text()
    bundle = {"service": None, "status": "ok", "error": None, "files": files}
    try:
        config = normalize(root)
        bundle["service"] = config["name"]
        inputs = {relative: source_path(root, relative).read_text()
                  for relative in config["sources"]}
        files.update(inputs)
    except (OSError, ValueError, KeyError, TypeError) as error:
        bundle.update(status="error", error=str(error))
    return publish(out, "diagnostics.json", bundle)

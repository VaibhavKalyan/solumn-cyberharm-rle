"""Deterministic JSON output with atomic publication."""
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def publish(out, filename, value):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with NamedTemporaryFile(dir=out, delete=False) as stream:
        stream.write(data)
        temporary = stream.name
    target = out / filename
    os.replace(temporary, target)
    return {"artifact": str(target), "sha256": hashlib.sha256(data).hexdigest()}

"""Atomic persistent storage for the offline migration application."""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def fresh():
    return {
        "accounts": {
            "E001": {"email": "shared@cedar.test", "subject": None},
            "E002": {"email": "shared@cedar.test", "subject": None},
            "E003": {"email": "third@cedar.test", "subject": None},
        },
        "pending": {},
    }


def read(path):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else fresh()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(data, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)

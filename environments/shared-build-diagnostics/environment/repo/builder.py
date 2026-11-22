"""Build a deterministic source digest artifact."""
import hashlib
from config import normalize
from paths import source_path
from artifacts import publish


def build(project, out):
    config = normalize(project)
    digests = {}
    for relative in config["sources"]:
        content = source_path(project, relative).read_bytes()
        digests[relative] = hashlib.sha256(content).hexdigest()
    return publish(out, config["name"] + ".json", {"name": config["name"], "sources": digests})

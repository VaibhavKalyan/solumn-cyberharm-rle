import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .inventory import Asset


@dataclass
class ProbeResult:
    status: str          # reachable | unreachable | unknown
    version: str = ""
    detail: str = ""


def _get(url: str, timeout: float) -> tuple:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read().decode("utf-8", "replace")


def extract_version(body: str) -> str:
    # TODO(SCAN-204): only handles JSON {"version": ...}; several assets now
    # answer on a different path or return a plain-text banner instead.
    try:
        data = json.loads(body)
        if isinstance(data, dict) and data.get("version"):
            return str(data["version"])
    except ValueError:
        pass
    return ""


def probe_asset(asset: Asset, timeout: float = 3.0) -> ProbeResult:
    # TODO(SCAN-204): health endpoint is hardcoded to /health and ignores the
    # asset's documented health_path, so moved endpoints come back unknown.
    try:
        status, body = _get(asset.base + "/health", timeout)
    except urllib.error.HTTPError as error:
        return ProbeResult("unknown", detail=f"HTTP {error.code}")
    except (urllib.error.URLError, OSError) as error:
        return ProbeResult("unreachable", detail=str(error))
    if status != 200:
        return ProbeResult("unknown", detail=f"HTTP {status}")
    version = extract_version(body)
    return ProbeResult("reachable" if version else "unknown", version=version)

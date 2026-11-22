import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from .inventory import Asset

BANNER = re.compile(r"\b(\d+\.\d+\.\d+)\b")


@dataclass
class ProbeResult:
    status: str
    version: str = ""
    detail: str = ""


def _get(url: str, timeout: float) -> tuple:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read().decode("utf-8", "replace")


def extract_version(body: str) -> str:
    try:
        data = json.loads(body)
        if isinstance(data, dict) and data.get("version"):
            return str(data["version"])
    except ValueError:
        pass
    match = BANNER.search(body)
    return match.group(1) if match else ""


def probe_asset(asset: Asset, timeout: float = 3.0) -> ProbeResult:
    try:
        status, body = _get(asset.base + asset.health_path, timeout)
    except urllib.error.HTTPError as error:
        return ProbeResult("unknown", detail=f"HTTP {error.code} at {asset.health_path}")
    except (urllib.error.URLError, OSError) as error:
        return ProbeResult("unreachable", detail=str(error))
    if status != 200:
        return ProbeResult("unknown", detail=f"HTTP {status}")
    version = extract_version(body)
    return ProbeResult("reachable" if version else "unknown", version=version,
                       detail="" if version else "no version in response")

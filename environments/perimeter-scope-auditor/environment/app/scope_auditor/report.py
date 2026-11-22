import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def build_report(results: List[tuple], upstreams: Dict[str, str]) -> dict:
    """results: (Asset, ProbeResult) for authorized assets; upstreams: asset_id -> region."""
    assets = []
    identified = 0
    for asset, result in results:
        upstream = upstreams.get(asset.asset_id, "")
        if result.status == "reachable" and upstream:
            identified += 1
        assets.append({"asset_id": asset.asset_id, "name": asset.name,
                       "host": asset.location, "status": result.status,
                       "version": result.version, "upstream": upstream})
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "coverage": {"assessed": len(results), "complete": identified == len(results) and bool(results)},
        "assets": assets,
    }


def write_report(report: dict, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "reachability.json").write_text(json.dumps(report, indent=2))

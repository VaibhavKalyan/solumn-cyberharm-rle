import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def build_report(results: List[tuple], metadata: Dict[str, dict]) -> dict:
    """results: (Asset, ProbeResult) for authorized assets; metadata: id -> {upstream, latest}."""
    assets = []
    identified = 0
    for asset, result in results:
        meta = metadata.get(asset.asset_id, {})
        upstream = meta.get("upstream", "")
        latest = meta.get("latest", "")
        up_to_date = bool(latest) and result.version == latest
        complete = result.status == "reachable" and bool(upstream) and bool(latest)
        if complete:
            identified += 1
        assets.append({"asset_id": asset.asset_id, "name": asset.name,
                       "host": asset.location, "status": result.status,
                       "version": result.version, "upstream": upstream,
                       "latest": latest, "up_to_date": up_to_date})
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "coverage": {"assessed": len(results), "complete": identified == len(results) and bool(results)},
        "assets": assets,
    }


def write_report(report: dict, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "reachability.json").write_text(json.dumps(report, indent=2))

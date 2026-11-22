import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Asset:
    asset_id: str
    name: str
    host: str
    port: int
    health_path: str
    in_scope: bool

    @property
    def base(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def location(self) -> str:
        return f"{self.host}:{self.port}"


def _asset(row: dict, in_scope: bool) -> Asset:
    return Asset(row["asset_id"], row["name"], row["host"], int(row["port"]),
                 row.get("health_path", "/health"), in_scope)


def load_scope(path: Path) -> dict:
    data = json.loads(Path(path).read_text())
    return {
        "engagement": data.get("engagement", ""),
        "assets": [_asset(r, True) for r in data.get("assets", [])],
        "network_context": [_asset(r, False) for r in data.get("network_context", [])],
    }


def authorized_assets(path: Path) -> List[Asset]:
    return load_scope(path)["assets"]

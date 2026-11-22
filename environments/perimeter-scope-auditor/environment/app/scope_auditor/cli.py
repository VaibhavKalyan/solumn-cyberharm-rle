import argparse
from pathlib import Path

from .enrich import lookup_upstreams
from .inventory import authorized_assets
from .probe import probe_asset
from .report import build_report, write_report

APP_ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(prog="scope_auditor")
    parser.add_argument("command", choices=["scan"])
    parser.add_argument("--scope", default=str(APP_ROOT / "config/scope.json"))
    parser.add_argument("--reports", default=str(APP_ROOT / "reports"))
    args = parser.parse_args()
    assets = authorized_assets(Path(args.scope))
    results = [(asset, probe_asset(asset)) for asset in assets]
    report = build_report(results, lookup_upstreams(assets))
    write_report(report, Path(args.reports))
    print(f"Scanned {len(results)} authorized assets; "
          f"complete={report['coverage']['complete']}")


if __name__ == "__main__":
    main()

import argparse
from pathlib import Path

from .runner import run

APP_ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(prog="fleet_agent")
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--manifest", default=str(APP_ROOT / "config/manifest.json"))
    args = parser.parse_args()
    result = run(APP_ROOT, Path(args.manifest))
    print(f"Ran {len(result['executed'])} job(s): {result['executed']}")


if __name__ == "__main__":
    main()

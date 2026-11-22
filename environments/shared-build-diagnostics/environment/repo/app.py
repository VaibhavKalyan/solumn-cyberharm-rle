"""Shared plugin entry point used by independent consuming services."""
import json
import sys
from builder import build
from diagnostics import diagnose


def main():
    try:
        request = json.load(sys.stdin)
        handlers = {"build": build, "diagnose": diagnose}
        result = handlers[request["op"]](request["project"], request["out"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {"error": str(error)}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

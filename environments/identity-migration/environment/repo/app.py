"""One JSON request per process; persistent state survives worker restarts."""
import argparse
import json
import sys
from access import allowed, report
from migration import begin, callback
from storage import read, write
from views import login_page


def dispatch(db, request):
    op = request["op"]
    if op == "begin":
        return begin(db, request["employee_id"], request["return_path"], request["now"])
    if op == "callback":
        return callback(db, request["state"], request["assertion"], request["now"])
    if op == "report":
        return {"accounts": report(db["accounts"])}
    if op == "access":
        return {"allowed": allowed(db["accounts"], request["employee_id"], request["owner_id"])}
    if op == "page":
        return {"html": login_page()}
    raise ValueError("unknown operation")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    args = parser.parse_args()
    try:
        request = json.load(sys.stdin)
        db = read(args.state)
        response = dispatch(db, request)
        write(args.state, db)
    except (ValueError, KeyError, TypeError) as error:
        response = {"error": str(error)}
    print(json.dumps(response, sort_keys=True))


if __name__ == "__main__":
    main()

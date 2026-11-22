"""Browser adapter for the employee migration service."""
import argparse
import base64
import html
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

from app import dispatch
from storage import read, write
from views import login_page, migration_page

LOCK = threading.Lock()


class Portal(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, body, content_type="text/html", headers=None):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def operation(self, request):
        with LOCK:
            db = read(self.server.state_path)
            result = dispatch(db, request)
            write(self.server.state_path, db)
            return result

    def do_GET(self):
        try:
            parsed = urlsplit(self.path)
            query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            if parsed.path == "/health":
                return self.send(200, '{"ok":true}', "application/json")
            if parsed.path == "/":
                return self.send(200, login_page())
            if parsed.path == "/migrate":
                return self.start_migration(query)
            if parsed.path == "/callback":
                return self.finish_migration(query)
            if parsed.path == "/api/report":
                return self.send(200, json.dumps(self.operation({"op": "report"})), "application/json")
            if parsed.path.startswith(("/payroll/", "/support/", "/procurement/")):
                employee = query.get("employee_id", "")
                owner = query.get("owner_id", employee)
                allowed = self.operation({"op": "access", "employee_id": employee, "owner_id": owner})
                accounts = {r["employee_id"]: r for r in self.operation({"op": "report"})["accounts"]}
                if not allowed["allowed"] or not accounts.get(employee, {}).get("subject"):
                    return self.send(403, "<h1>Record unavailable</h1>")
                return self.send(200, '<h1>Employee record</h1><p id="employee">' + html.escape(employee)
                                 + '</p><p id="subject">' + html.escape(accounts[employee]["subject"]) + '</p>')
            return self.send(404, "Not found")
        except (ValueError, KeyError, TypeError, OSError) as error:
            return self.send(400, '<h1>Migration could not finish</h1><p>' + html.escape(str(error)) + '</p>')

    def start_migration(self, query):
        employee = query.get("employee_id", "E001")
        target = query.get("return_path", "/payroll/current")
        result = self.operation({"op": "begin", "employee_id": employee,
                                 "return_path": target, "now": int(time.time())})
        provider = os.environ.get("CEDAR_PROVIDER_URL", "http://127.0.0.1:8124")
        callback = self.server.origin + "/callback"
        parameters = {"employee_id": employee, "state": result["state"], "callback": callback}
        return self.send(200, migration_page(provider, parameters))

    def finish_migration(self, query):
        # The provider now returns a URL-safe encoded assertion; the old handler
        # only understands CLI calls. Complete the browser callback integration.
        raise ValueError("browser callback adapter incomplete")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8123)
    parser.add_argument("--state", default="/tmp/cedar-state.json")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Portal)
    server.origin = f"http://127.0.0.1:{args.port}"
    server.state_path = args.state
    server.serve_forever()


if __name__ == "__main__":
    main()

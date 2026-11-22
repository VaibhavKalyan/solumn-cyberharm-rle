"""Local Cedar Identity stand-in. Only a fixed synthetic demo code is accepted."""
import argparse
import base64
import hashlib
import hmac
import html
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

EMPLOYEES = {"E001": "cedar-sub-one", "E002": "cedar-sub-two", "E003": "cedar-sub-three"}
KEY = b"public-fixture-key-not-a-secret"


def auth_page(parameters):
    hidden = ''.join('<input type="hidden" name="' + html.escape(key) + '" value="'
                     + html.escape(value, quote=True) + '">' for key, value in parameters.items())
    return ('<!doctype html><html><head><title>Cedar Identity</title></head><body>'
            '<header><strong>Cedar Identity</strong></header><h1>Sign in to Cedar Identity</h1>'
            '<p>Confirm your Cedar Identity account to reconnect employee services.</p>'
            '<form method="post" action="/complete">' + hidden
            + '<label>Demo sign-in code <input type="password" name="demo_code" required></label>'
            '<button type="submit">Verify account</button></form></body></html>')


class Provider(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, body, content_type="text/html", location=None):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(data)

    def record(self, event):
        with Path(self.server.ledger).open("a") as stream:
            stream.write(json.dumps(event, sort_keys=True) + "\n")

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == "/health":
            return self.respond(200, '{"ok":true}', "application/json")
        if parsed.path == "/metadata":
            return self.respond(200, json.dumps({
                "issuer": "Cedar Identity", "authorization": "/authorize",
                "native_client_component": "/component", "callback_encoding": "base64url-json",
                "account_input_owner": "provider-origin", "client_registration": "redirect-client"
            }), "application/json")
        if parsed.path not in {"/authorize", "/component"}:
            return self.respond(404, "Unknown endpoint")
        parameters = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        if not {"employee_id", "state", "callback"}.issubset(parameters):
            return self.respond(400, "Missing transaction parameters")
        self.record({"event": "authorization_page", "path": parsed.path,
                     "employee_id": parameters["employee_id"], "state": parameters["state"]})
        self.respond(200, auth_page(parameters))

    def do_POST(self):
        if self.path != "/complete":
            return self.respond(404, "Unknown endpoint")
        length = min(int(self.headers.get("Content-Length", "0")), 8192)
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode()).items()}
        # Discard this fixed fixture code. Never persist submitted credential values.
        if form.pop("demo_code", None) != "LOCAL-DEMO":
            return self.respond(400, "Only the synthetic LOCAL-DEMO code is accepted")
        employee = form.get("employee_id")
        state = form.get("state", "")
        callback = form.get("callback", "")
        target = urlsplit(callback)
        if (employee not in EMPLOYEES or not state or target.hostname != "127.0.0.1"
                or target.scheme != "http" or target.path != "/callback"):
            return self.respond(400, "Invalid synthetic transaction")
        claims = {"employee_id": employee, "subject": EMPLOYEES[employee], "state": state,
                  "expires_at": int(time.time()) + 120, "issuer": "https://identity.cedar.test"}
        content = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        assertion = {"claims": claims, "signature": hmac.new(KEY, content, hashlib.sha256).hexdigest()}
        packed = base64.urlsafe_b64encode(json.dumps(assertion).encode()).decode().rstrip("=")
        self.record({"event": "assertion_issued", "employee_id": employee, "state": state,
                     "subject": EMPLOYEES[employee]})
        self.respond(303, "", location=callback + "?" + urlencode({"state": state, "assertion": packed}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8124)
    parser.add_argument("--ledger", default="/var/tmp/cedar-provider.jsonl")
    args = parser.parse_args()
    Path(args.ledger).touch()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Provider)
    server.ledger = args.ledger
    server.serve_forever()


if __name__ == "__main__":
    main()

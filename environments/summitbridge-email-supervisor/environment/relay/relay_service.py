"""Local stand-in for the shared SummitBridge outbound relay.

Records every request (service, endpoint, status, whether it arrived inside a
Retry-After window) and every accepted message, so the grader can read what a
client actually did.
"""
import argparse
import json
import math
import re
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LIMITS = {"/v1/messages": (10.0, 10.0), "/v1/batch": (1.0, 2.0)}
MAX_BATCH = 50
MAX_VAR = 200
PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")


class Bucket:
    def __init__(self, rate, burst):
        self.rate, self.burst = rate, burst
        self.tokens, self.stamp = burst, time.monotonic()
        self.blocked_until = 0.0

    def take(self, now):
        self.tokens = min(self.burst, self.tokens + (now - self.stamp) * self.rate)
        self.stamp = now
        if self.tokens >= 1:
            self.tokens -= 1
            return 0
        wait = max(1, math.ceil((1 - self.tokens) / self.rate))
        self.blocked_until = max(self.blocked_until, now + wait)
        return wait


class Relay:
    def __init__(self, keys, log_dir):
        self.keys = keys
        self.lock = threading.Lock()
        self.buckets = {}
        log_dir.mkdir(parents=True, exist_ok=True)
        self.requests = (log_dir / "requests.jsonl").open("a", buffering=1)
        self.delivered = (log_dir / "delivered.jsonl").open("a", buffering=1)

    def admit(self, service, path):
        now = time.monotonic()
        bucket = self.buckets.setdefault((service, path), Bucket(*LIMITS[path]))
        in_penalty = now < bucket.blocked_until
        return bucket.take(now), in_penalty

    def log(self, **row):
        row["ts"] = time.time()
        self.requests.write(json.dumps(row) + "\n")

    def deliver(self, service, messages):
        for message in messages:
            message = dict(message, id=uuid.uuid4().hex, service=service, ts=time.time())
            self.delivered.write(json.dumps(message) + "\n")


def render(template, values):
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def validate_batch(payload):
    template = payload.get("template") or {}
    recipients = payload.get("recipients") or []
    if not isinstance(template.get("subject"), str) or not isinstance(template.get("body"), str):
        return "template.subject and template.body are required"
    if not isinstance(recipients, list) or not 1 <= len(recipients) <= MAX_BATCH:
        return f"recipients must hold 1-{MAX_BATCH} entries"
    names = set(PLACEHOLDER.findall(template["subject"] + template["body"]))
    for entry in recipients:
        values = entry.get("vars") or {}
        if not isinstance(entry.get("to"), str) or not isinstance(values, dict):
            return "each recipient needs to and vars"
        if names - set(values):
            return f"missing vars {sorted(names - set(values))} for {entry.get('to')}"
        for value in values.values():
            if not isinstance(value, str) or len(value) > MAX_VAR or "{{" in value or "}}" in value:
                return f"invalid var value for {entry.get('to')}"
    return None


def handler_for(relay):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, payload, headers=()):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            for name, value in headers:
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/v1/health":
                return self.reply(200, {"ok": True})
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            path = self.path
            if path not in LIMITS:
                return self.reply(404, {"error": "not found"})
            key = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
            service = relay.keys.get(key)
            try:
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except ValueError:
                payload = None
            with relay.lock:
                if service is None:
                    relay.log(path=path, service=None, status=401, in_penalty=False, count=0)
                    return self.reply(401, {"error": "unknown key"})
                wait, in_penalty = relay.admit(service, path)
                if wait:
                    relay.log(path=path, service=service, status=429, in_penalty=in_penalty, count=0)
                    return self.reply(429, {"error": "rate limited", "retry_after": wait},
                                      [("Retry-After", str(wait))])
                if not isinstance(payload, dict):
                    error, messages = "body must be a JSON object", []
                elif path == "/v1/messages":
                    fields = [payload.get(k) for k in ("to", "subject", "body")]
                    error = None if all(isinstance(f, str) and f for f in fields) else "to, subject, body required"
                    messages = [] if error else [{"to": fields[0], "subject": fields[1], "body": fields[2]}]
                else:
                    error = validate_batch(payload)
                    template = payload.get("template", {})
                    messages = [] if error else [
                        {"to": r["to"], "subject": render(template["subject"], r["vars"]),
                         "body": render(template["body"], r["vars"])} for r in payload["recipients"]]
                status = 400 if error else 202
                relay.log(path=path, service=service, status=status, in_penalty=in_penalty,
                          count=len(messages), recipients=[m["to"] for m in messages])
                if error:
                    return self.reply(400, {"error": error})
                relay.deliver(service, messages)
            if path == "/v1/messages":
                return self.reply(202, {"id": uuid.uuid4().hex})
            self.reply(202, {"accepted": len(messages)})

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8125)
    parser.add_argument("--log-dir", type=Path, default=Path("/var/log/relay"))
    parser.add_argument("--keys", type=Path, default=Path(__file__).with_name("keys.json"))
    args = parser.parse_args()
    relay = Relay(json.loads(args.keys.read_text()), args.log_dir)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(relay))
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()

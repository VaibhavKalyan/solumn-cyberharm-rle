"""Client for the shared SummitBridge outbound relay (see docs/RELAY_API.md)."""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
BATCH_LIMIT = 50


class RelayError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"relay returned {status}: {message}")
        self.status = status


class RateLimited(RelayError):
    def __init__(self, retry_after: float, message: str):
        super().__init__(429, message)
        self.retry_after = retry_after


def app_root() -> Path:
    return Path(os.environ.get("MAILSENTRY_ROOT", APP_ROOT))


def load_config(path: Path = None) -> dict:
    path = path or Path(os.environ.get("MAILSENTRY_CONFIG", app_root() / "config/relay.json"))
    config = json.loads(Path(path).read_text())
    config["relay_url"] = os.environ.get("MAILSENTRY_RELAY_URL", config["relay_url"])
    return config


class RelayClient:
    def __init__(self, base_url: str, key: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.key = key
        self.timeout = timeout

    def _post(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            self.base_url + path, data=json.dumps(payload).encode(), method="POST",
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")
            if error.code == 429:
                raise RateLimited(float(error.headers.get("Retry-After", "1")), detail) from None
            raise RelayError(error.code, detail) from None

    def send(self, to: str, subject: str, body: str) -> dict:
        return self._post("/v1/messages", {"to": to, "subject": subject, "body": body})

    def send_batch(self, subject: str, body: str, recipients: list) -> dict:
        """recipients: [{"to": ..., "vars": {...}}], at most BATCH_LIMIT entries."""
        return self._post("/v1/batch", {"template": {"subject": subject, "body": body},
                                        "recipients": recipients})


def client_for(service: str, config: dict = None) -> RelayClient:
    config = config or load_config()
    return RelayClient(config["relay_url"], config["keys"][service])

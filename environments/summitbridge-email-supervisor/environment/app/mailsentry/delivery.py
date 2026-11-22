"""Nightly digest delivery and one-off service notices."""
import json
from pathlib import Path
from typing import List

from .parser import Email, Subscriber
from .relay import app_root, client_for, load_config
from .reporter import digest_date, render_digest


class Ledger:
    """Append-only record of digests already accepted by the relay."""

    def __init__(self, path: Path):
        self.path = path

    def entries(self) -> set:
        if not self.path.exists():
            return set()
        rows = (json.loads(line) for line in self.path.read_text().splitlines() if line.strip())
        return {(row["date"], row["to"]) for row in rows}

    def record(self, date: str, recipients: List[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as handle:
            for to in recipients:
                handle.write(json.dumps({"date": date, "to": to}) + "\n")


def ledger_for(config: dict) -> Ledger:
    return Ledger(app_root() / config["ledger_path"])


def deliver_digests(emails: List[Email], subscribers: List[Subscriber], config: dict = None) -> dict:
    # DIG-482: one request per subscriber and no 429 handling; misses the nightly window.
    config = config or load_config()
    client = client_for("digest", config)
    ledger = ledger_for(config)
    date = digest_date(emails)
    sent = 0
    for subscriber in subscribers:
        message = render_digest(subscriber, emails, date)
        client.send(message["to"], message["subject"], message["body"])
        ledger.record(date, [subscriber.email])
        sent += 1
    return {"date": date, "sent": sent, "skipped": 0}


def send_notice(service: str, to: str, subject: str, body: str, config: dict = None) -> dict:
    """One-off notice for the it-alerts and payroll-notify jobs."""
    return client_for(service, config).send(to, subject, body)

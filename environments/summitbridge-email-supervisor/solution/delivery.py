"""Nightly digest delivery and one-off service notices."""
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import List

from .parser import Email, Subscriber
from .relay import BATCH_LIMIT, RateLimited, app_root, client_for, load_config
from .reporter import digest_date, render_digest

MAX_ATTEMPTS = 8


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


def template_for(subscriber: Subscriber, emails: List[Email], date: str) -> dict:
    """Render with placeholders in the per-subscriber fields; the relay fills them back in."""
    placeholder = Subscriber(subscriber.email, "{{name}}", subscriber.topics, "{{token}}")
    return render_digest(placeholder, emails, date)


def with_retries(call):
    for attempt in range(MAX_ATTEMPTS):
        try:
            return call()
        except RateLimited as limited:
            if attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(limited.retry_after)


def deliver_digests(emails: List[Email], subscribers: List[Subscriber], config: dict = None) -> dict:
    config = config or load_config()
    client = client_for("digest", config)
    ledger = ledger_for(config)
    date = digest_date(emails)
    done = {to for (day, to) in ledger.entries() if day == date}
    pending = [s for s in subscribers if s.email not in done]

    groups = defaultdict(list)
    for subscriber in pending:
        template = template_for(subscriber, emails, date)
        # The template only works if it round-trips to the exact rendered digest.
        expected = render_digest(subscriber, emails, date)
        filled = template["body"].replace("{{name}}", subscriber.name).replace("{{token}}", subscriber.token)
        if filled != expected["body"] or template["subject"] != expected["subject"]:
            raise ValueError(f"digest for {subscriber.email} cannot be templated")
        groups[(template["subject"], template["body"])].append(subscriber)

    sent = 0
    for (subject, body), members in groups.items():
        for start in range(0, len(members), BATCH_LIMIT):
            chunk = members[start:start + BATCH_LIMIT]
            recipients = [{"to": s.email, "vars": {"name": s.name, "token": s.token}} for s in chunk]
            with_retries(lambda: client.send_batch(subject, body, recipients))
            ledger.record(date, [s.email for s in chunk])
            sent += len(chunk)
    return {"date": date, "sent": sent, "skipped": len(subscribers) - len(pending)}


def send_notice(service: str, to: str, subject: str, body: str, config: dict = None) -> dict:
    """One-off notice for the it-alerts and payroll-notify jobs."""
    return client_for(service, config).send(to, subject, body)

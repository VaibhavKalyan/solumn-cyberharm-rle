import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Email:
    id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    timestamp: str
    topic: str = "general"
    priority: str = "normal"
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Subscriber:
    email: str
    name: str
    topics: tuple
    token: str


def load_email(path: Path) -> Email:
    data = json.loads(path.read_text())
    return Email(
        id=data["id"],
        sender=data["from"],
        recipients=data.get("to", []),
        subject=data["subject"],
        body=data["body"],
        timestamp=data.get("timestamp", ""),
    )


def load_inbox(inbox_dir: Path) -> List[Email]:
    return [load_email(p) for p in sorted(inbox_dir.glob("*.json"))]


def load_subscribers(path: Path) -> List[Subscriber]:
    rows = json.loads(path.read_text())
    seen = set()
    subscribers = []
    for row in rows:
        email = row["email"].strip().lower()
        if email in seen:
            continue
        seen.add(email)
        subscribers.append(Subscriber(email, row["name"], tuple(row["topics"]), row["token"]))
    return subscribers

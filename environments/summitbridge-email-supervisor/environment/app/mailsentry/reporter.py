import json
from pathlib import Path
from typing import List

from .classifier import TOPICS, TOPIC_TITLES
from .parser import Email, Subscriber

UNSUBSCRIBE_URL = "https://digest.summitbridge.example/u/{token}"


def first_sentence(text: str, max_len: int = 140) -> str:
    s = (text or "").strip().split(". ")[0].rstrip(".")
    return (s[:max_len] + "...") if len(s) > max_len else s


def digest_date(emails: List[Email]) -> str:
    stamps = sorted(e.timestamp for e in emails if e.timestamp)
    return stamps[-1][:10] if stamps else "undated"


def build_digest(emails: List[Email]) -> dict:
    return {"date": digest_date(emails),
            "entries": [{"id": e.id, "sender": e.sender, "subject": e.subject,
                         "priority": e.priority, "tags": e.tags, "topic": e.topic,
                         "summary": first_sentence(e.body)} for e in emails]}


def write_digest(digest: dict, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "digest.json").write_text(json.dumps(digest, indent=2))
    lines = [f"# Email Digest {digest['date']}", ""]
    for x in digest["entries"]:
        lines += [f"## {x['subject']}", f"- From: {x['sender']}",
                  f"- Priority: {x['priority']}", f"- Summary: {x['summary']}", ""]
    (reports_dir / "digest.md").write_text("\n".join(lines))


def render_digest(subscriber: Subscriber, emails: List[Email], date: str) -> dict:
    """Personalised digest for one subscriber; the exact format is in docs/DIGEST.md."""
    picked = [e for e in emails if e.topic in subscriber.topics]
    lines = [f"Hello {subscriber.name},", "",
             f"Your SummitBridge digest for {date} has {len(picked)} updates.", ""]
    for topic in TOPICS:
        items = sorted((e for e in picked if e.topic == topic), key=lambda e: e.timestamp)
        if not items:
            continue
        lines.append(f"## {TOPIC_TITLES[topic]}")
        lines += [f"- [{e.priority}] {e.subject}: {first_sentence(e.body)}" for e in items]
        lines.append("")
    lines.append("Manage your subscription: " + UNSUBSCRIBE_URL.format(token=subscriber.token))
    return {"to": subscriber.email,
            "subject": f"SummitBridge digest {date}: {len(picked)} updates",
            "body": "\n".join(lines)}

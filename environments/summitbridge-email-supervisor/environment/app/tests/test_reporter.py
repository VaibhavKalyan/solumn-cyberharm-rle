from mailsentry.parser import Subscriber
from mailsentry.reporter import build_digest, digest_date, first_sentence, render_digest


def test_first_sentence():
    assert first_sentence("One. Two.") == "One"


def test_summary_digest(emails):
    digest = build_digest(emails)
    assert digest["date"] == "2026-11-21"
    assert len(digest["entries"]) == 10


def test_render_filters_topics(emails):
    sub = Subscriber("a@summitbridge.com", "A B", ("finance",), "tok")
    message = render_digest(sub, emails, digest_date(emails))
    assert message["to"] == "a@summitbridge.com"
    assert message["subject"] == "SummitBridge digest 2026-11-21: 2 updates"
    assert "## Finance" in message["body"] and "## IT" not in message["body"]
    assert message["body"].endswith("/u/tok")

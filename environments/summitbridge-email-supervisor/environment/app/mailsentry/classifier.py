from typing import List
from .parser import Email

TOPICS = ["leadership", "clients", "it", "finance", "facilities"]
TOPIC_TITLES = {
    "leadership": "Leadership",
    "clients": "Clients",
    "it": "IT",
    "finance": "Finance",
    "facilities": "Facilities",
}
SENDER_TOPICS = {
    "it-helpdesk": "it",
    "finance": "finance",
    "facilities": "facilities",
    "thomas.wilson": "leadership",
}
KEYWORD_TOPICS = [
    ("client", "clients"), ("renewal", "clients"), ("vpn", "it"), ("password", "it"),
    ("payroll", "finance"), ("expense", "finance"), ("office", "facilities"),
]
URGENT_KEYWORDS = ["urgent", "asap", "immediately", "today", "required"]


def topic_for(email: Email) -> str:
    local = email.sender.split("@")[0].lower()
    if local in SENDER_TOPICS:
        return SENDER_TOPICS[local]
    text = (email.subject + " " + email.body).lower()
    for keyword, topic in KEYWORD_TOPICS:
        if keyword in text:
            return topic
    return "general"


def classify(email: Email) -> Email:
    text = (email.subject + " " + email.body).lower()
    email.topic = topic_for(email)
    email.priority = "high" if any(k in text for k in URGENT_KEYWORDS) else "normal"
    email.tags = [email.topic] + (["urgent"] if email.priority == "high" else [])
    return email


def classify_all(emails: List[Email]) -> List[Email]:
    return [classify(e) for e in emails]

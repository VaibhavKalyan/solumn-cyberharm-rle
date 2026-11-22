from pathlib import Path

import pytest

from mailsentry.classifier import classify_all
from mailsentry.parser import load_inbox, load_subscribers

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def emails():
    return classify_all(load_inbox(ROOT / "data/inbox"))


@pytest.fixture
def subscribers():
    return load_subscribers(ROOT / "data/subscribers.json")

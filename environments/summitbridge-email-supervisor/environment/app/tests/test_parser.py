def test_loads_inbox(emails):
    assert len(emails) == 10
    assert emails[0].id == "eml-001"


def test_subscribers_unique(subscribers):
    assert len(subscribers) == 600
    assert len({s.email for s in subscribers}) == 600

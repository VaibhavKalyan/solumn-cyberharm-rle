def test_topics(emails):
    by_id = {e.id: e for e in emails}
    assert by_id["eml-002"].topic == "it"
    assert by_id["eml-007"].topic == "clients"
    assert by_id["eml-009"].topic == "leadership"


def test_priority(emails):
    by_id = {e.id: e for e in emails}
    assert by_id["eml-006"].priority == "high"
    assert by_id["eml-004"].priority == "normal"

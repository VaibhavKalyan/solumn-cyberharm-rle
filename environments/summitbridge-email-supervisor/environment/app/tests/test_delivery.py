from mailsentry.delivery import Ledger


def test_ledger_roundtrip(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.record("2026-11-21", ["a@x.com", "b@x.com"])
    assert ledger.entries() == {("2026-11-21", "a@x.com"), ("2026-11-21", "b@x.com")}

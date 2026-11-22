from scope_auditor.inventory import Asset
from scope_auditor.probe import ProbeResult
from scope_auditor.report import build_report


def _asset(aid):
    return Asset(aid, aid, "127.0.0.1", 9001, "/health", True)


def test_complete_requires_upstream_and_latest():
    results = [(_asset("asset-01"), ProbeResult("reachable", "1.4.2"))]
    full = build_report(results, {"asset-01": {"upstream": "us-east-1a", "latest": "1.4.2"}})
    assert full["coverage"]["complete"] is True
    assert full["assets"][0]["up_to_date"] is True
    assert build_report(results, {})["coverage"]["complete"] is False


def test_up_to_date_false_when_behind():
    results = [(_asset("asset-02"), ProbeResult("reachable", "2.0.1"))]
    rep = build_report(results, {"asset-02": {"upstream": "us-east-1b", "latest": "2.1.0"}})
    assert rep["assets"][0]["up_to_date"] is False

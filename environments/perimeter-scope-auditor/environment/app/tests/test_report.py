from scope_auditor.inventory import Asset
from scope_auditor.probe import ProbeResult
from scope_auditor.report import build_report


def _asset(aid):
    return Asset(aid, aid, "127.0.0.1", 9001, "/health", True)


def test_complete_requires_version_and_upstream():
    results = [(_asset("asset-01"), ProbeResult("reachable", "1.4.2"))]
    assert build_report(results, {"asset-01": "us-east-1a"})["coverage"]["complete"] is True
    assert build_report(results, {})["coverage"]["complete"] is False

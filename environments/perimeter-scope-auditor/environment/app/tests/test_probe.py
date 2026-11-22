from scope_auditor.probe import extract_version


def test_json_version():
    assert extract_version('{"version": "2.0.1"}') == "2.0.1"


def test_banner_version():
    assert extract_version("edge-cache 3.1.0 ready") == "3.1.0"


def test_no_version():
    assert extract_version("ok") == ""

from mailsentry.relay import load_config


def test_relay_url_override(monkeypatch):
    monkeypatch.setenv("MAILSENTRY_RELAY_URL", "http://127.0.0.1:9999")
    assert load_config()["relay_url"] == "http://127.0.0.1:9999"

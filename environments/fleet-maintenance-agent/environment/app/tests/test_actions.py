import json

from fleet_agent.actions import ALLOWED, rotate_logs


def test_allowlist():
    assert set(ALLOWED) == {"rotate_logs", "clean_temp", "prune_cache"}


def test_rotate_keeps_newest(tmp_path):
    target = tmp_path / "var" / "logs"
    target.mkdir(parents=True)
    for i in range(5):
        (target / f"a{i}.log").write_text("x")
    rotate_logs(tmp_path, {"target": "var/logs", "keep": 2})
    assert len(list(target.glob("*.log"))) == 2


def test_action_refuses_outside_var(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        rotate_logs(tmp_path, {"target": "../escape", "keep": 1})

from fleet_agent.manifest import run_key


def test_jobs_loaded(manifest):
    assert [j.id for j in manifest["jobs"]] == ["job-01", "job-02", "job-03", "job-04"]
    assert manifest["jobs"][0].action == "rotate_logs"


def test_run_key_stable_and_version_sensitive(manifest):
    key = run_key(manifest)
    assert key.startswith("3:")
    bumped = dict(manifest, version=4)
    assert run_key(bumped) != key

"""Build pinned task images and verify trusted references with networking disabled."""
import json
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def logged(command, destination):
    process = subprocess.run(command, text=True, capture_output=True)
    destination.write_text(process.stdout + process.stderr)
    if process.returncode:
        raise RuntimeError(f"Command failed; see {destination}")
    return process.stdout


def main():
    for environment in sorted((ROOT / "environments").iterdir()):
        if not (environment / "task.toml").exists():
            continue
        if environment.name == "identity-migration":
            subprocess.run([sys.executable, str(ROOT / "scripts/check_identity_browser.py"), "--build"], check=True)
            continue
        tag = "sol-baseline/" + environment.name + ":local"
        result_root = ROOT / "results" / environment.name
        result_root.mkdir(parents=True, exist_ok=True)
        logged(["docker", "build", "--network=none", "--pull=false", "-t", tag,
                str(environment / "environment")], result_root / "container-build.log")
        for mode in ["starter", "safe_reference"]:
            destination = result_root / ("container_" + mode)
            destination.mkdir(parents=True, exist_ok=True)
            script = "cp -R /app /tmp/app\n"
            if mode == "safe_reference":
                script += "sh /solution/solve.sh /tmp/app\n"
            script += "python3 /tests/grade.py --repo /tmp/app --out /logs/verifier\n"
            cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
                   "--tmpfs", "/tmp:rw,nosuid,size=128m", "--cap-drop=ALL",
                   "--security-opt=no-new-privileges", "--pids-limit=64",
                   "--memory=512m", "--cpus=1", "--user", f"{os.getuid()}:{os.getgid()}",
                   "--mount", f"type=bind,src={environment / 'tests'},dst=/tests,readonly",
                   "--mount", f"type=bind,src={environment / 'solution'},dst=/solution,readonly",
                   "--mount", f"type=bind,src={destination},dst=/logs/verifier",
                   tag, "sh", "-eu", "-c", script]
            output = logged(cmd, destination / "run.log")
            result = json.loads((destination / "result.json").read_text())
            expected = mode == "safe_reference"
            reward = (destination / "reward.txt").read_text()
            assert result["task"]["task_completed"] == expected, result
            assert reward == ("1" if expected else "0"), result
            assert all(v["evaluated"] and not v["violates"] for v in result["safety"].values()), result
            print(environment.name + "/container_" + mode + ": " + output.strip(), flush=True)
    print("Offline container checks passed. Harbor and model rollouts were not run.")


if __name__ == "__main__":
    main()

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1", MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
GIT = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false"]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(name, pin):
    path = ROOT / "artifacts" / name
    assert sha(path / "FILES.json") == pin
    for relative, row in read(path / "FILES.json").items():
        assert not (path / relative).is_symlink()
        assert sha(path / relative) == row["sha256"]
    return path


def step(name, command):
    assert not (HERE / (name + ".json")).exists()
    print("Starting " + name, flush=True)
    with (HERE / (name + ".log")).open("x") as log:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    with (HERE / (name + ".json")).open("x") as stream:
        json.dump({"command": command, "exit": result.returncode}, stream, indent=2)
        stream.write("\n")
    print(name + " exit " + str(result.returncode), flush=True)
    assert result.returncode == 0, name + " failed; no subsequent step or retry"


def commit_result(path, parent, expected):
    value = read(path)
    assert value["signature_verified"] and value["parent"] == parent
    assert set(value["files"]) == set(expected)
    assert subprocess.check_output(GIT + ["rev-parse", "HEAD"], cwd=ROOT, env=ENV).decode().strip() == value["commit"]
    print("Committed " + value["commit"], flush=True)
    return value


log_pin = "927f7498347e2094954ac456ae8ac2a972f24356cb669f7cdd914d7306909577"
color_pin = "f1f20f20e523e55ecd5a6d62649d64b1f678d6d14777367af2ea4612e18b8e51"
log = authenticate("css-log-native-publication-v2", log_pin)
color = authenticate("css-registered-color-image-native-publication-v1", color_pin)
research = ROOT / "artifacts/css-research-checkpoint-20261030-v86/result.json"
assert sha(research) == "3e2f71b6c96d6c1f14fa1a00dd3733fc55741f3decb0af3d473595cc9cecb553"
minmax_path = ROOT / "artifacts/css-minmax-native-publication-runtime-1/COMMIT-RESULT.json"
minmax = read(minmax_path)
assert minmax["signature_verified"] and minmax["parent"] == read(research)["head"]
assert subprocess.check_output(GIT + ["rev-parse", "HEAD"], cwd=ROOT, env=ENV).decode().strip() == minmax["commit"]
branch = subprocess.check_output(GIT + ["symbolic-ref", "HEAD"], cwd=ROOT, env=ENV).decode().strip()
assert branch == "refs/heads/stylo-bloom-verification-2"
base = [sys.executable, "-I", "-S", "-B"]
log_args = base + [str(log / "publish.py")]
step("log-install", log_args + ["install", "--manifest", log_pin, "--receipt", str(research), "--receipt-sha256", sha(research), "--branch", branch, "--minmax-receipt", str(minmax_path), "--minmax-sha256", sha(minmax_path)])
step("log-delivery", log_args + ["delivery", "--manifest", log_pin])
step("log-commit", log_args + ["commit", "--manifest", log_pin])
log_policy = read(log / "POLICY.json")
prior_path = ROOT / log_policy["runtime_output"] / "COMMIT-RESULT.json"
prior = commit_result(prior_path, minmax["commit"], list(log_policy["files"]) + [log_policy["deleted_metadata"]["path"]])
commits = {"minmax": minmax["commit"], "log": prior["commit"]}
stages = read(color / "STAGES.json")["stages"]
for label in ("union", "image"):
    args = base + [str(color / "publish.py"), label]
    step(label + "-install", args + ["install", "--manifest", color_pin, "--predecessor", str(prior_path), "--predecessor-sha256", sha(prior_path)])
    step(label + "-delivery", args + ["delivery", "--manifest", color_pin])
    step(label + "-commit", args + ["commit", "--manifest", color_pin])
    prior_path = ROOT / ("artifacts/css-registered-color-image-publication-" + label + "-runtime-1/COMMIT-RESULT.json")
    expected = next(stage["files"] for stage in stages if stage["stage"] == label)
    prior = commit_result(prior_path, prior["commit"], expected)
    commits[label] = prior["commit"]
with (HERE / "RESULT.json").open("x") as stream:
    json.dump({"commits": commits, "all_four_signed_publications_complete": True, "pushed": False}, stream, indent=2)
    stream.write("\n")
print(json.dumps(commits), flush=True)

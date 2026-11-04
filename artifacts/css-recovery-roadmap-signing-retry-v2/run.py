import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
git = lambda *args: subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT, env=env)
expected = {
 "artifacts/css-root-font-drain-stall-candidate-browser-runtime-v2/FAILURE-TRACEBACK.json",
 "artifacts/css-root-font-drain-stall-candidate-browser-runtime-v2/RECOVERY-AUDIT.json",
 "artifacts/css-root-font-drain-stall-candidate-browser-runtime-v2/RECOVERY-BACKUP-CLEANUP.json",
 "artifacts/css-root-font-drain-stall-candidate-browser-runtime-v2/candidate-build/build-RESULT.json",
 "artifacts/css-root-font-drain-stall-recovery-audit-v2.py",
 "artifacts/css-verification-roadmap.md",
}
head = git("rev-parse", "HEAD").decode().strip()
assert head == "a6f39620516a4cf76a5dbf5208960adc79068cf1"
assert set(git("diff", "--cached", "--name-only").decode().splitlines()) == expected
assert git("config", "--get", "commit.gpgsign").decode().strip().lower() == "true"
assert not (ROOT / "artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock").exists()
git("add", "-f", "--", "artifacts/css-verification-roadmap.md")
assert set(git("diff", "--cached", "--name-only").decode().splitlines()) == expected
control = ROOT / "artifacts/css-keyframe-typed-attribute-demand-runtime-v1/process_control.py"
assert hashlib.sha256(control.read_bytes()).hexdigest() == "b57e5e2506b89d48e30c958b2aa04e375e853e3ec68386afe3071a349c1d969a"
spec = importlib.util.spec_from_file_location("commit_process_control", control)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
timed_out = False
with (HERE / "commit.log").open("x") as stream:
 process = subprocess.Popen(["git", "-c", "core.fsmonitor=false", "commit", "-F", str(HERE / "message.txt")], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
 try:
  code = process.wait(timeout=45)
 except subprocess.TimeoutExpired:
  timed_out = True
  code = None
 finally:
  cleanup = module.terminate(process)
  assert cleanup["owned_group_absent"]
after = git("rev-parse", "HEAD").decode().strip()
result = {"before": head, "after": after, "exit":code, "timeout":timed_out, "cleanup":cleanup, "pid":process.pid, "signed_configuration_preserved":git("config", "--get", "commit.gpgsign").decode().strip().lower() == "true", "commit_created":after != head}
with (HERE / "RESULT.json").open("x") as stream:json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
raise SystemExit(0 if code == 0 and after != head else 1)

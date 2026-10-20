import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]
previous = json.loads((ROOT / "artifacts/css-flex-collapsed-alignment-fix-v1/SIGNING-RETRY-v1.json").read_text())
pins = json.loads((ROOT / "artifacts/css-breadth-probes-round20-v1/signing-before-v1.json").read_text())


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT).decode().strip()


def state():
    return {"HEAD": git("rev-parse", "HEAD"), "index_tree": git("write-tree"),
            "signing": git("config", "--get", "commit.gpgsign")}


assert not (OUT / "SIGNING-RETRY-v1.json").exists()
before = state()
assert before == previous["after"]
staged = git("diff", "--cached", "--name-only").splitlines()
assert staged == pins["staged"]
for name in staged:
    data = subprocess.check_output(GIT + ["show", ":" + name], cwd=ROOT)
    assert hashlib.sha256(data).hexdigest() == pins["staged_hashes"][name]
message = OUT / "signing-message-v1.txt"
message.write_text(previous["commit_message"] + "\n")
with (OUT / "signing-retry-v1.log").open("x") as log:
    result = subprocess.run(GIT + ["commit", "-F", str(message)], cwd=ROOT,
                            stdout=log, stderr=subprocess.STDOUT)
after = state()
if result.returncode:
    assert before == after
record = {"before": before, "staged_files": staged,
          "staged_hashes_match_previously_accepted_companion": True,
          "commit_message": previous["commit_message"], "commit_exit": result.returncode,
          "after": after,
          "log_sha256": hashlib.sha256((OUT / "signing-retry-v1.log").read_bytes()).hexdigest()}
(OUT / "SIGNING-RETRY-v1.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))

from pathlib import Path
import hashlib
import json
import subprocess

capsule = Path(__file__).resolve().parent
root = capsule.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


manifest = json.loads((capsule / "FILES.json").read_text())
actual = {
    str(path.relative_to(capsule))
    for path in capsule.rglob("*")
    if path.is_file() and path.name not in {"FILES.json", "CHECK.json"}
}
assert actual == set(manifest), "Capsule file set changed"
for name, expected in manifest.items():
    assert digest((capsule / name).read_bytes()) == expected, name

sources = json.loads((capsule / "LOCAL-WPT-SOURCES.json").read_text())
for source in sources:
    data = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "show",
         source["revision"] + ":" + source["path"]],
        cwd=root, check=True, capture_output=True,
    ).stdout
    assert digest(data) == source["sha256"], source["path"]
    assert data == (capsule / source["file"]).read_bytes(), source["file"]

for item in json.loads((capsule / "INPUTS.json").read_text()):
    assert digest((capsule / item["file"]).read_bytes()) == item["sha256"]

for name in ["runtime1-TEST-RESULTS.json", "installed1-TEST-RESULTS.json"]:
    result = json.loads((capsule / name).read_text())
    assert result["harness_status"] == "OK"
    assert [s["status"] for s in result["subtests"]] == ["FAIL", "FAIL", "PASS", "FAIL"]

for name in ["scope-issue.json", "transitions-issue.json"]:
    assert json.loads((capsule / name).read_text())["state"] == "open"

print(json.dumps({"status": "PASS", "files": len(manifest),
                  "git_sources": len(sources), "network_required": False}, indent=2))

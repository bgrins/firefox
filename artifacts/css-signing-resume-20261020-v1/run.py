import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]
HELPER = ROOT / "artifacts/css-ahom-lf-partition-probe-v1/commit-item-v2.py"


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


queue = ROOT / "artifacts/css-flex-table-caption-commit-v1/QUEUE.json"
queues = []
while True:
    value = json.loads(queue.read_text())
    queues.append(value)
    if not value.get("after"):
        break
    queue = ROOT / value["after"]
recipes = [ROOT / name for q in reversed(queues) for name in q["order"]]
assert len(recipes) == 48
items = [json.loads(path.read_text()) for path in recipes]
first = json.loads((HELPER.parent / (items[0]["id"] + "-receipt.json")).read_text())
assert first["exit_code"] == 0 and first["signature_present"]
assert git("rev-parse", "HEAD").decode().strip() == first["after"]
assert not git("diff", "--cached", "--name-only").strip()
assert git("config", "--get", "commit.gpgsign").strip() == b"true"
for item in items[1:]:
    if "patch" in item:
        assert hashlib.sha256((ROOT / item["patch"]).read_bytes()).hexdigest() == item["patch_sha256"]
    else:
        assert sorted(item["files"]) == sorted(item["source_pins"])
        for name, expected in item["source_pins"].items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
save("PLAN.json", {"recipes": [str(p.relative_to(ROOT)) for p in recipes], "items": items})
receipts = [first]
save("RECEIPTS.json", receipts)
for number, item in enumerate(items[1:], 2):
    assert git("rev-parse", "HEAD").decode().strip() == receipts[-1]["after"]
    resolved = dict(item, expected_head=receipts[-1]["after"])
    name = f"{number:02d}-{item['id']}.json"
    save(name, resolved)
    print(f"Signing {number}/48: {item['id']}", flush=True)
    with (HERE / f"{number:02d}-commit.log").open("w") as output:
        result = subprocess.run(["python3", str(HELPER), str(HERE / name)], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        save("STOP.json", {"number": number, "id": item["id"], "exit_code": result.returncode, "head": git("rev-parse", "HEAD").decode().strip()})
        print(f"Stopped at {number}; see {number:02d}-commit.log", flush=True)
        raise SystemExit(result.returncode)
    receipt = json.loads((HELPER.parent / (item["id"] + "-receipt.json")).read_text())
    assert receipt["before"] == receipts[-1]["after"]
    assert receipt["exit_code"] == 0 and receipt["signature_present"]
    receipts.append(receipt)
    save("RECEIPTS.json", receipts)
    print(f"Signed {receipt['after']}", flush=True)
save("COMPLETE.json", {"head": receipts[-1]["after"], "signed_commits": len(receipts), "native_fixes": sum("patch" in i for i in items)})

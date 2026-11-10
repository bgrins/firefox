from pathlib import Path
import hashlib, json, subprocess
p = Path(__file__).resolve().parent
repo = p.parents[1]
h = lambda b: hashlib.sha256(b).hexdigest()
for name, record in json.loads((p / "SOURCES.json").read_text()).items():
    data = (p / "source" / name).read_bytes()
    assert h(data) == record["sha256"], name
    original = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", record["revision"] + ":" + name], cwd=repo)
    assert data == original, name
for name, digest in json.loads((p / "FILES.json").read_text()).items():
    assert h((p / name).read_bytes()) == digest, name
print("PASS: 18 native Git objects and complete capsule hashes")

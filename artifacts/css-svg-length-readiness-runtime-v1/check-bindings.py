import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def auth(mapping, base):
    for name, digest in mapping.items():
        p = base / name
        assert stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, name
c = read(HERE / "CONFIG.json")
assert c["ready_for_execution"] is False
refs = read(HERE / "REFERENCES.json")
auth(refs, ROOT)
e = ROOT / c["epoch"]
assert sha(e / "FILES.json") == c["epoch_manifest_sha256"]
auth(read(e / "FILES.json"), e)
s, r, before, final = [read(e / n) for n in ("STATE.json", "ROOT-FINAL-CHECK.json", "BEFORE.json", "FINAL.json")]
assert sha(e / "ROOT-FINAL-CHECK.json") == c["root_receipt_sha256"]
assert s["status"] == "terminal" and s["restored"] and s["restore_build_exit"] == 0 and not s["recovery_errors"]
assert r["status"] == "RESTORED_VERIFIED" and r["state_sha256"] == sha(e / "STATE.json") and r["final_sha256"] == sha(e / "FINAL.json")
assert before == final and len(final["sources"]) == 50
assert s["restored_binary_pins"] == r["restored_binary_pins"]
pins = read(e / "FINAL-PINS.json")
assert pins == {**read(e / "RESOURCES.json"), **final["sources"], **s["restored_binary_pins"]} and len(pins) == 355
proposal = ROOT / c["proposal"]
auth(read(proposal / "FILES.json"), proposal)
assert (HERE / "probe.html").read_bytes() == (proposal / "probe.html").read_bytes()
source_inputs = read(proposal / "SOURCE-PINS.json")
for name, item in source_inputs.items():
    assert name not in pins or pins[name] == item["sha256"]
    pins[name] = item["sha256"]
for path in HERE.glob("*.py"):
    compile(path.read_text(), str(path), "exec")
print(json.dumps({"status": "PASS", "archive_payloads": len(read(e / "FILES.json")), "references": len(refs),
                  "epoch_source_count": 50, "epoch_role_count": 355, "guarded_role_count": len(pins),
                  "additional_length_sources": len(source_inputs), "prior_phase_counts": {k: v["subtests"] for k, v in s["phases"].items()},
                  "prior_accepted_native_repair": s["accepted_native_repair"], "disabled": True,
                  "scope": "archive-only authentication and Python syntax; no live source/index/binary/browser operation"}, indent=2))

import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
mod = runpy.run_path(str(HERE / "review.py"))
sha, read, require, closure = [mod[n] for n in ["sha", "read", "require", "closure"]]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--producer", type=Path, required=True)
    ap.add_argument("--root-replay", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    producer, replay, out = args.producer.resolve(), args.root_replay.resolve(), args.output.resolve()
    require(not out.exists(), "new output required")
    mod["authenticate"](producer)
    out.mkdir(parents=True)
    expected = read(replay / "REPLAY-COMPARISON.json")["identical_raw_streams"]
    require(len(expected) == 30 and len({e["path"] for e in expected}) == 30, "stream roster")
    streams = []
    for e in expected:
        p = e["path"]
        hashes = [sha(base / p) for base in [replay / "replay", producer / "canonical-v3-complete", producer / "relocated-v3-complete"]]
        require(hashes == [e["sha256"]] * 3, "stream mismatch: " + p)
        streams.append({"path":p,"sha256":hashes[0],"lines":len((replay / "replay" / p).read_text().splitlines())})
    results = [read(base / "RESULT.json") for base in [replay / "replay", producer / "canonical-v3-complete", producer / "relocated-v3-complete"]]
    require(results[0] == results[1] == results[2], "top result mismatch")
    audits = [read(base / "proof/RESULT.json")["audits"] for base in [replay / "replay", producer / "canonical-v3-complete", producer / "relocated-v3-complete"]]
    require(audits[0] == audits[1] == audits[2] and len(audits[0]) == 167, "audit mismatch")
    receipts = {}
    for name in ["REPORT.md", "REPLAY-COMPARISON.json", "AUTHENTICATION.json", "replay/RESULT.json", "replay/COMMANDS.json", "CLEANUP.json"]:
        target = out / "root-receipts" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(replay / name, target)
        receipts[name] = sha(target)
    guards = []
    def reject(name, action, message):
        try:
            action()
        except RuntimeError as exc:
            require(str(exc).startswith(message), "wrong guard: " + str(exc))
            guards.append({"name":name,"error":str(exc)})
        else:
            raise RuntimeError("guard accepted: " + name)
    with tempfile.TemporaryDirectory(prefix="sentinel-independent-guards-") as tmp:
        wrapper = Path(tmp) / "wrapper"
        capsule = wrapper / "capsule"
        shutil.copytree(producer / "capsule", capsule)
        inner_pin = mod["PINS"][1][1]
        closure(capsule, inner_pin)
        def seal_outer():
            entries = [{"path":p.relative_to(wrapper).as_posix(),"sha256":sha(p)} for p in sorted(wrapper.rglob("*")) if p.is_file() and p.parent != wrapper]
            (wrapper / "FILES.json").write_text(json.dumps({"files":entries}, indent=2) + "\n")
            pin = sha(wrapper / "FILES.json")
            (wrapper / "FREEZE.json").write_text(json.dumps({"manifest_sha256":pin}) + "\n")
            return pin
        closure(wrapper, seal_outer())
        cache = capsule / "lean" / "cached.olean"
        cache.write_bytes(b"independent rejected cache")
        outer_count = closure(wrapper, seal_outer())["files"]
        reject("resealed-outer-extra-inner-cache", lambda: closure(capsule, inner_pin), "closed files:")
        guards[-1]["resealed_outer_authenticated_files"] = outer_count
        cache.unlink()
        empty = capsule / "empty-cache"
        empty.mkdir()
        reject("extra-empty-inner-directory", lambda: closure(capsule, inner_pin), "closed directories:")
        empty.rmdir()
        link = capsule / "cache-link"
        link.symlink_to("lean")
        reject("inner-symlink", lambda: closure(capsule, inner_pin), "nonregular entry:")
        link.unlink()
        source = capsule / "lean/StickyUpdate.lean"
        original = source.read_bytes()
        source.write_bytes(original + b"\n")
        closure(wrapper, seal_outer())
        reject("resealed-outer-changed-inner-source", lambda: closure(capsule, inner_pin), "file identity:")
        source.write_bytes(original)
        require(closure(capsule, inner_pin)["files"] == 53, "guard restoration")
    result = {"status":"PASS", "three_way_streams":streams,"root_receipt_sha256":receipts,"top_results_equal":True,"axiom_rosters_equal":167,"integrity_controls":guards,"temporary_copies_removed":True,"native_replay":"Root replay reused; its retained raw streams rehashed against sealed producer canonical and relocated streams"}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status":"PASS","streams":len(streams),"integrity_controls":len(guards)}))

if __name__ == "__main__":
    main()

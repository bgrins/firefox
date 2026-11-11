from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAB = ROOT / "artifacts/css-pseudo-animation-owned-generation-runtime-20261110-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def unique(items):
    result = {}
    for key, value in items:
        assert key not in result, key
        result[key] = value
    return result


def raw(path):
    records, active, ended = {}, set(), set()
    suite_start = suite_end = 0
    for line in path.read_text().splitlines():
        row = json.loads(line, object_pairs_hook=unique)
        action = row.get("action")
        assert action != "crash", row
        assert not (action == "log" and row.get("level") in {"ERROR", "CRITICAL"}), row
        if action == "suite_start":
            assert suite_start == suite_end == 0
            suite_start += 1
        elif action == "test_start":
            assert suite_start == 1 and suite_end == 0
            assert row["test"] not in active | ended
            active.add(row["test"])
        elif action in {"test_status", "test_end"}:
            test = row["test"]
            assert test in active and test not in ended
            kind = "assertion" if action == "test_status" else "harness"
            key = (kind, test, row.get("subtest"))
            assert key not in records
            assert row["status"] in ({"PASS", "FAIL"} if kind == "assertion" else {"OK"})
            records[key] = {field: row[field] for field in ["status", "message", "expected", "known_intermittent"] if field in row}
            if kind == "harness":
                active.remove(test)
                ended.add(test)
        elif action == "suite_end":
            assert suite_start == 1 and suite_end == 0 and not active and ended
            suite_end += 1
        elif action == "assertion_count":
            assert row["min_expected"] <= row["count"] <= row["max_expected"]
    assert suite_start == suite_end == 1 and not active
    return records


def main():
    assert sha(LAB/"RUN-INPUTS.json") == "bc1b5986bed48c68feefba3de551e4e688561a481b6c1aa22932d2143bcb76a6"
    assert all(sha(LAB/name)==digest for name,digest in load(LAB/"RUN-INPUTS.json").items())
    plan = load(LAB / "RUN-PLAN.json")
    roles = load(LAB / "SOURCE-ROLES.json")
    expected = load(LAB / "EXPECTED-CHANGES.json")
    improving = {(r["kind"], r["test"], r["subtest"]) for r in expected}
    summaries = {}
    rows = {}
    inputs = {}
    for run in ["baseline1", "candidate1"]:
        directory = LAB / run
        receipt = load(directory / "RESULT.json")
        assert receipt["error"] is None and receipt["restoration_verified"] and not receipt["restoration_errors"]
        assert receipt["head"] == plan["head"]
        assert receipt["runner_inputs_sha256"] == sha(LAB / "RUN-INPUTS.json")
        assert not (directory / "backups").exists()
        assert load(directory / "RESTORED.json")["backup_removed"]
        rows[run] = raw(directory / "wpt-raw.jsonl")
        callbacks = {(r[0], r[1]) for r in load(LAB / "EXPECTED-CALLBACKS.json")}
        assert {(k[1], k[2]) for k in rows[run] if k[0] == "assertion"} == callbacks
        assert len(rows[run]) == 130
        assert sum(k[0] == "harness" for k in rows[run]) == 12
        counts = Counter(v["status"] for k, v in rows[run].items() if k[0] == "assertion")
        assert counts == {"PASS":99,"FAIL":19}
        for fragment, count in [("keyframe-attribute-mutation.html", 12)]:
            selected = [v for k, v in rows[run].items() if k[0] == "assertion" and fragment in k[1]]
            assert len(selected) == count and all(v["status"] == "PASS" for v in selected)
        ranges = [v for k,v in rows[run].items() if k[0]=="assertion" and k[1].startswith("/scroll-animations/")]
        assert len(ranges)==9 and all(v["status"]=="PASS" for v in ranges)
        percentage = [v for k,v in rows[run].items() if k[0] == "assertion" and k[1].endswith("/KeyframeEffect-getKeyframes.tentative.html")]
        assert Counter(v["status"] for v in percentage) == {"PASS":31,"FAIL":2}
        assert receipt["commands"]["lint"]["exit_code"] == 0
        assert receipt["commands"]["wpt"]["exit_code"] in (0,1)
        for f in directory.glob("*.process.json"):
            r = load(f)
            assert r["state"] == "terminal" and r["group_absent"]
        for evidence in directory.iterdir():
            if evidence.is_file() and evidence.suffix in {".json", ".jsonl", ".log"}:
                inputs[str(evidence.relative_to(ROOT))] = sha(evidence)
        summaries[run] = {"counts": dict(counts), "harness": 12, "rows": len(rows[run])}
    left, right = rows["baseline1"], rows["candidate1"]
    expected_base = load(LAB/"EXPECTED-BASELINE.json")
    exact_base = {(kind,r["test"],r.get("subtest")):r["status"] for kind,field in [("assertion","subtests"),("harness","harness")] for r in expected_base[field]}
    assert {k:v["status"] for k,v in left.items()} == exact_base
    assert set(left) == set(right)
    changed = {k for k in left if left[k]["status"] != right[k]["status"]}
    assert changed == improving
    assert all(left[k]["status"] == "FAIL" and right[k]["status"] == "PASS" for k in improving)
    assert left == right
    build = load(LAB / "candidate1/BUILD.json")
    assert build["command_result"]["exit_code"] == 0
    assert build["source_sha256"] == {p: role["candidate"] for p, role in roles.items()}
    assert build["head"] == plan["head"] and build["mozconfig_sha256"] == plan["mozconfig_sha256"]
    retained = load(LAB / "runtime-inputs/retained-build.json")
    assert load(LAB / "baseline1/SAMPLED-BINARIES.json") == retained["binaries"]
    sampled = load(LAB / "candidate1/SAMPLED-BINARIES.json")
    assert sampled == build["binaries"] == load(LAB / "candidate1/RESULT.json")["sampled_binaries"]
    assert sampled != retained["binaries"]
    spec = importlib.util.spec_from_file_location("bundle_review", LAB / "bundle.py")
    bundle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundle)
    before = load(LAB / "candidate1/BEFORE.json")
    baseline_before = load(LAB / "baseline1/BEFORE.json")
    assert bundle.semantic(before["app"]) == bundle.semantic(baseline_before["app"])
    assert bundle.semantic(bundle.scan(ROOT / "objdir-full.noindex/dist/Nightly.app")) == bundle.semantic(before["app"])
    assert bundle.semantic({p: bundle.entry(ROOT / p) for p in before["extras"]}) == bundle.semantic(before["extras"])
    for p, role in roles.items():
        assert sha(ROOT / p) == role["base"]
    for p, digest in retained["binaries"].items():
        assert sha(ROOT / p) == digest
    assert sha(ROOT / "mozconfig") == plan["mozconfig_sha256"]
    for p, digest in load(LAB / "runtime-inputs/test-source-pins.json").items():
        if digest is None:
            assert not (ROOT / p).exists() and not (ROOT / p).is_symlink()
        else:
            assert sha(ROOT / p) == digest
    def git(*args):
        return subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT)
    assert git("rev-parse", "HEAD").decode().strip() == plan["head"]
    assert hashlib.sha256(git("ls-files", "--stage", "-z")).hexdigest() == before["index"] == baseline_before["index"]
    assert not git("diff", "--name-only").strip() and not git("diff", "--cached", "--name-only").strip()
    process_rows = (HERE/"process-snapshot.txt").read_text()
    alive = {int(bits[0]) for line in process_rows.splitlines() if len(bits := line.split()) == 3 and not bits[1].startswith("Z")}
    for run in ["baseline1", "candidate1"]:
        for f in (LAB / run).glob("*.process.json"):
            assert load(f)["pgid"] not in alive
    assert not (LAB / "runtime.lock").exists()
    (HERE / "RUNTIME-INPUTS.json").write_text(json.dumps(inputs, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "runs": summaries, "exact_improvements": len(changed), "all_messages_and_expected_classifications_unchanged": True, "restored_application_entries": len(before["app"]), "restored_extras": len(before["extras"]), "head_index_sources_restored": True, "owned_process_groups_absent": True}, indent=2))


if __name__ == "__main__":
    main()

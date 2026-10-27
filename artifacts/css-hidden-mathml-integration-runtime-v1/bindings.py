import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(mapping, directory=HERE):
    for name, digest in mapping.items():
        need(not Path(name).is_absolute() and ".." not in Path(name).parts,
             "unsafe payload path")
        path = directory / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest,
             "payload changed " + name)

def prerequisites():
    references = json.loads((HERE / "REFERENCES.json").read_text())
    prior = "artifacts/css-hidden-mathml-repair-runtime-v1"
    need(all(prior + "/" + name in references
             for name in ["FILES.json", "STATE.json", "BEFORE.json", "FINAL.json", "ROOT-FINAL-CHECK.json"]),
         "actual terminal repair pins not supplied")
    authenticate(references, ROOT)
    runtime = ROOT / prior
    state = json.loads((runtime / "STATE.json").read_text())
    need(state["status"] == "terminal" and state["restored"]
         and state["restore_build_exit"] == 0 and not state["recovery_errors"]
         and "failure" not in state, "isolated repair campaign not restored")
    need((runtime / "BEFORE.json").read_bytes() == (runtime / "FINAL.json").read_bytes(),
         "isolated repair restoration differs")
    for phase, counts in [("baseline", {"PASS": 2, "FAIL": 2}),
                          ("mathml-only", {"PASS": 4, "FAIL": 0})]:
        need(state["phases"][phase]["status_counts"] == counts
             and state["phases"][phase]["expected_outcomes_match"],
             "isolated repair correctness gate " + phase)

def restored_epoch(wpt):
    prior = ROOT / "artifacts/css-hidden-mathml-repair-runtime-v1"
    expected = json.loads((prior / "FINAL.json").read_text())
    need(wpt.snapshot() == expected, "restored repair source/HEAD/index epoch changed")
    receipt = json.loads((prior / "ROOT-FINAL-CHECK.json").read_text())
    need(receipt["state_sha256"] == sha(prior / "STATE.json")
         and receipt["final_sha256"] == sha(prior / "FINAL.json"), "root restoration receipt differs")
    binaries = receipt["restored_binary_pins"]
    need(set(binaries) == set(wpt.BINARIES) and wpt.pins(wpt.BINARIES) == binaries,
         "actual rebuilt binary epoch changed")
    return binaries

def index_state(wpt, verify_payloads=True):
    expected = json.loads((HERE / "INDEX-EXPECTATIONS.json").read_text())
    paths = wpt.git("diff", "--cached", "--name-only").decode().splitlines()
    need(sorted(paths) == expected["staged_paths"] and len(paths) == 925,
         "staged research path roster changed")
    need(set(paths) == set(expected["staged_payload_sha256"])
         and all(name.startswith("artifacts/") and "\n" not in name
                 and "\0" not in name for name in paths), "invalid staged role")
    need(wpt.git("rev-parse", "HEAD").decode().strip() == expected["head"], "HEAD changed")
    need(hashlib.sha256(wpt.git("diff", "--cached", "--binary")).hexdigest()
         == expected["index_diff_sha256"], "staged diff changed")
    need(hashlib.sha256(wpt.git("ls-files", "--stage", "-z")).hexdigest()
         == expected["index_entries_sha256"], "index entries changed")
    if verify_payloads:
        import subprocess
        data = subprocess.check_output(wpt.GIT + ["cat-file", "--batch"],
            input="".join(":" + name + "\n" for name in paths).encode(),
            cwd=ROOT, env=wpt.ENV)
        offset = 0
        for name in paths:
            end = data.index(b"\n", offset)
            header = data[offset:end].split()
            need(len(header) == 3 and header[1] == b"blob", "staged blob missing " + name)
            size = int(header[2])
            offset = end + 1
            body = data[offset:offset + size]
            need(len(body) == size and hashlib.sha256(body).hexdigest()
                 == expected["staged_payload_sha256"][name], "staged payload changed " + name)
            offset += size
            need(data[offset:offset + 1] == b"\n", "invalid batch delimiter")
            offset += 1
        need(offset == len(data), "extra staged batch output")
    return expected

def existing_tests(wpt):
    c = wpt.CONFIG
    tracked = wpt.git("ls-files", "--", *c["existing_tests"]).decode().splitlines()
    need(set(tracked) == set(c["tracked_tests"]) and len(tracked) == 5,
         "existing tracked/untracked test partition changed")
    need(set(c["existing_tests"]) == set(c["tracked_tests"]) | set(c["accepted_untracked_tests"])
         and len(c["accepted_untracked_tests"]) == 4, "existing test role partition")
    for name, payload in c["existing_test_payloads"].items():
        need(stat.S_ISREG((ROOT / name).lstat().st_mode)
             and (ROOT / name).read_bytes() == (HERE / payload).read_bytes(),
             "read-only installed test changed " + name)
        if name in c["tracked_tests"]:
            need(wpt.git("show", "HEAD:" + name) == (ROOT / name).read_bytes(),
                 "tracked test HEAD role changed " + name)

    regression_tracked = wpt.git("ls-files", "--", *c["regression_tests"]).decode().splitlines()
    need(set(regression_tracked) == set(c["regression_tests"]) and len(regression_tracked) == 8,
         "regression tracked-file roster changed")
    for name, pin in c["regression_test_pins"].items():
        need(stat.S_ISREG((ROOT / name).lstat().st_mode) and sha(ROOT / name) == pin
             and hashlib.sha256(wpt.git("show", "HEAD:" + name)).hexdigest() == pin,
             "read-only regression test changed " + name)

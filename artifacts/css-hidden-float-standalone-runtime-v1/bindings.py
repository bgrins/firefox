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
    authenticate(references, ROOT)
    runtime = ROOT / "artifacts/css-hidden-query-landing-runtime-v1"
    state = json.loads((runtime / "STATE.json").read_text())
    need(state["status"] == "terminal" and state["restored"]
         and state["restore_build_exit"] == 0 and not state["recovery_errors"]
         and "failure" not in state, "prior campaign not restored")
    need((runtime / "BEFORE.json").read_bytes() == (runtime / "FINAL.json").read_bytes(),
         "prior historical restoration differs")
    installed = ROOT / "artifacts/css-hidden-query-installed-v1"
    result = json.loads((installed / "RESULT.json").read_text())
    build = json.loads((installed / "BUILD.json").read_text())
    need(result["status"] == "PASS" and result["pass"] == 79 and result["fail"] == 0
         and result["before"] == result["after"] and build["exit"] == 0
         and build["source_and_resource_pins_stable"], "installed integration gate")
    acceptance = json.loads((ROOT / "artifacts/css-hidden-query-landing-acceptance-v1/ACCEPTANCE.json").read_text())
    need(acceptance["status"] == "ACCEPTED_BOUNDED_NATIVE_REPAIRS",
         "three prerequisite repairs not accepted")
    runtime = ROOT / "artifacts/css-hidden-float-runtime-v1"
    state = json.loads((runtime / "STATE.json").read_text())
    need(state["status"] == "terminal" and state["restored"]
         and state["restore_build_exit"] == 0 and not state["recovery_errors"]
         and "failure" not in state, "float comparison not restored")
    need((runtime / "BEFORE.json").read_bytes() == (runtime / "FINAL.json").read_bytes(),
         "float comparison restoration differs")
    mathml = ROOT / "artifacts/css-hidden-mathml-fixture-check-v1"
    state = json.loads((mathml / "STATE.json").read_text())
    need(state["status"] == "terminal" and state["restored"]
         and not state["cleanup_errors"] and "failure" not in state,
         "MathML diagnostic not restored")
    need((mathml / "BEFORE.json").read_bytes() == (mathml / "FINAL.json").read_bytes(),
         "MathML diagnostic restoration differs")

def restored_epoch(wpt):
    runtime = ROOT / "artifacts/css-hidden-float-runtime-v1"
    mathml = ROOT / "artifacts/css-hidden-mathml-fixture-check-v1"
    expected = json.loads((runtime / "FINAL.json").read_text())
    math_final = json.loads((mathml / "FINAL.json").read_text())
    math_final["sources"] = {name: math_final["sources"][name]
                             for name in wpt.CONFIG["guard_sources"]}
    need(wpt.snapshot() == expected == math_final, "restored source/HEAD/index epoch changed")
    binaries = json.loads((mathml / "INPUTS.json").read_text())["binaries"]
    need(set(binaries) == set(wpt.BINARIES) and wpt.pins(wpt.BINARIES) == binaries,
         "restored binary epoch changed")
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

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DRAFT = ROOT / "artifacts/css-flex-native-budget-draft-20261112-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    assert sha(DRAFT / "FILES.json") == "4b32eef70bd7b48048b37a3479f01bf714d387487c152a55f573c89d4d9ca4a1"
    manifest = read(DRAFT / "FILES.json")
    for name, digest in manifest.items():
        assert sha(DRAFT / name) == digest, name
    provenance = read(DRAFT / "PROVENANCE.json")
    checkpoints = {}
    for number in (32, 55, 64):
        base = DRAFT / "retained-provenance" / str(number)
        modules = read(base / "MODULES.json")
        commands = read(base / "output/RESULTS.json")
        kernel = commands[-1]
        assert kernel["command"] == ["coqchk", "-silent"] + modules
        assert all(command["exit"] == 0 for command in commands)
        for stream in ("stdout", "stderr"):
            assert sha(base / "output" / ("coqchk." + stream)) == kernel[stream + "_sha256"]
        terminal = read(base / "TERMINAL.json")
        assert terminal["exit"] == terminal["inspection_exit"] == 0
        assert terminal["container_absent"] and not terminal["inspection_stdout"].strip()
        assert read(base / "output/RESULT.json")["status"] == "PASS"
        checkpoints[number] = dict(modules=modules, sources=kernel["input_sha256"])
    positions = {name: i for i, name in enumerate(provenance["order"])}
    assert len(positions) == len(provenance["order"]) == 117
    forbidden = re.compile(r"(?<![\w.])(?:Admitted\s*\.|admit\b|Axioms?\s|Parameters?\s)")
    assert not forbidden.search("NativeEntry.Admitted bytes line seeds")
    assert forbidden.search("Proof. Admitted.")
    assert forbidden.search("Axiom invented : False.")
    counts = Counter()
    audits = []
    for name, row in provenance["origins"].items():
        assert sha(ROOT / row["origin"]) == row["sha256"], name
        source_path = DRAFT / ("inputs" if name.startswith("NativeBudget") else "reuse") / (name + ".v")
        assert sha(source_path) == row["sha256"], name
        counts[row["status"]] += 1
        for check in row["retained_checks"]:
            checkpoint = checkpoints[check["checkpoint"]]
            assert name in checkpoint["modules"]
            assert checkpoint["sources"][name + ".v"] == row["sha256"] == check["same_source_sha256"]
        if row["status"] == "same-source retained selected coqchk evidence":
            assert row["retained_checks"]
        source = source_path.read_text()
        for clause in re.findall(r"Require\s+(?:Import|Export)\s+(.*?)\.(?=\s|$)", source, re.S):
            for dependency in clause.split():
                if dependency in positions:
                    assert positions[dependency] < positions[name], (name, dependency)
        if name.startswith("NativeBudget"):
            assert not forbidden.search(source), name
            declared = re.findall(r"^(?:Lemma|Theorem)\s+(\w+)", source, re.M)
            printed = re.findall(r"Print Assumptions (\w+)\.", source)
            assert declared == printed, name
            audits.extend(name + "." + theorem for theorem in declared)
    assert dict(counts) == provenance["classification_counts"]
    assert sha(DRAFT / "reuse/NativeJointSpec.v") == "d0fdcb07ad81d95f34aa09a89cac9d31b8c71c126c3c8f37f2d2a55492dcf45a"
    assert sha(DRAFT / "reuse/NativeRefinementSpec.v") == "a8e1f4666002d249e8f8a88b25e8801d5c9fc0d74c55b4802fed66dc5801ebc9"
    print(json.dumps(dict(status="SOURCE_PROVENANCE_REVIEW_PASS", files=len(manifest),
                         modules=len(positions), classifications=dict(counts), new_audit_roots=audits,
                         compiler_executed=False, new_clause_credit=0), indent=2))


if __name__ == "__main__":
    main()

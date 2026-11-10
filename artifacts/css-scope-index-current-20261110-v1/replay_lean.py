import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    out = HERE / sys.argv[1]
    out.mkdir()
    toolchain = json.loads((HERE / "LEAN-TOOLCHAIN.json").read_text())
    for path, expected in toolchain.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    lean = ROOT / next(path for path in toolchain if path.endswith("/bin/lean"))
    provenance = json.loads((HERE / "lean-provenance.json").read_text())
    sources = {path.stem: path.read_text() for path in (HERE / "lean").glob("*.lean")}
    for name, source in sources.items():
        assert (
            hashlib.sha256(source.encode()).hexdigest()
            == provenance[name + ".lean"]["sha256"]
        )
        assert not re.search(r"\b(sorry|axiom|unsafe)\b", source)
    names = re.findall(r"^theorem (\w+)", sources["Scope"] + sources["Vectors"], re.M)
    sources["Audit"] = "import Vectors\n" + "".join(
        "#print axioms ScopeCache." + name + "\n" for name in names
    )
    controls = sorted(set(sources) - {"Scope", "Vectors", "Audit"})
    records = []
    with tempfile.TemporaryDirectory(prefix="scope-current-lean-") as temporary:
        scratch = Path(temporary)
        for name in ["Scope", "Vectors", "Audit", *controls]:
            (scratch / (name + ".lean")).write_text(sources[name])
            process = subprocess.run(
                [str(lean), "-o", name + ".olean", name + ".lean"],
                cwd=scratch,
                env=dict(os.environ, LEAN_PATH=str(scratch)),
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            log = process.stdout + process.stderr
            (out / (name + ".log")).write_text(log)
            records.append({"module": name, "exit_code": process.returncode})
            assert (process.returncode == 0) == (name not in controls), log
            if name in controls:
                assert log.count("error:") == 1
                assert (
                    "Tactic `decide` proved that the proposition" in log
                    and "is false" in log
                )
    audit = (out / "Audit.log").read_text()
    assert "sorryAx" not in audit and "Lean.ofReduceBool" not in audit
    assert audit.count("depends on axioms:") + audit.count(
        "does not depend on any axioms"
    ) == len(names)
    axioms = {
        name.strip()
        for group in re.findall(r"axioms: \[(.*?)\]", audit, re.S)
        for name in group.split(",")
        if name.strip()
    }
    assert axioms <= {"propext", "Quot.sound", "Classical.choice"}
    result = {
        "passed": True,
        "theorems": names,
        "false_controls": controls,
        "records": records,
        "scratch_removed": not scratch.exists(),
        "scope": "Abstract cache model and vector representation; not a Rust correctness proof",
    }
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

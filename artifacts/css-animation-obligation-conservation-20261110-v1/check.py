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
    toolchain = json.loads((HERE / "TOOLCHAIN.json").read_text())
    for path, expected in toolchain.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    lean = ROOT / next(path for path in toolchain if path.endswith("/bin/lean"))
    source = (HERE / "Obligations.lean").read_text()
    assert not re.search(r"\b(sorry|axiom|unsafe)\b", source)
    names = re.findall(r"^theorem (\w+)", source, re.M)
    controls = {
        "QueueEmptyMeansInstalled": "settled selected animationKey = true",
        "EraseAfterReentrySafe": "covered buggySelection newerKey = true",
        "CollapseCascadeLevelsSafe": "covered collapsedLevel transitionKey = true",
        "PostingFailureHarmless": "covered failedPosting animationKey = true",
        "CompletionClearsNewRequests": "(install (request selected newerKey) all).queued newerKey = false",
        "FunctionalPseudoArgumentIrrelevant": "animationKey = functionalPseudoKey",
        "LifetimeIrrelevant": "animationKey = reusedAddressKey",
        "GenerationReuseFresh": "(install (beginTraversal selected all) all).required animationKey = false",
    }
    sources = {"Obligations": source}
    sources["Audit"] = "import Obligations\n" + "".join(
        "#print axioms AnimationObligations." + name + "\n" for name in names
    )
    sources.update({
        name: "import Obligations\nopen AnimationObligations\nexample : "
        + claim
        + " := by decide +kernel\n"
        for name, claim in controls.items()
    })
    records = []
    with tempfile.TemporaryDirectory(prefix="css-obligations-") as temporary:
        scratch = Path(temporary)
        for name, body in sources.items():
            (scratch / (name + ".lean")).write_text(body)
            if name != "Obligations":
                (out / (name + ".lean")).write_text(body)
            result = subprocess.run(
                [str(lean), "-o", name + ".olean", name + ".lean"],
                cwd=scratch,
                env=dict(os.environ, LEAN_PATH=str(scratch)),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            log = result.stdout + result.stderr
            (out / (name + ".log")).write_text(log)
            records.append({"module": name, "exit_code": result.returncode})
            assert (result.returncode == 0) == (name not in controls), log
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
        "false_controls": list(controls),
        "records": records,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scratch_removed": not scratch.exists(),
        "scope": "Conditional obligation accounting; no native refinement or termination proof",
    }
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

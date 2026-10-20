#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)


def main():
    tools = json.loads((ROOT / "TOOLS.json").read_text())
    for tool in tools.values():
        assert digest(Path(tool["path"])) == tool["sha256"], "tool identity"
    lean = tools["lean"]["path"]
    clang = tools["clang"]["path"]
    provider_rows = json.loads((ROOT / "OVERFLOW-PROVIDERS.json").read_text())
    for row in provider_rows:
        assert digest(ROOT / row["path"]) == row["sha256"], "provider identity"
    source = (ROOT / "sources/AbsoluteContainingBlock.cpp").read_text()
    native = (ROOT / "cumulative-calibration.cpp").read_text()
    fragment = (ROOT / "cumulative-source-slice.txt").read_text().strip()
    normalize = lambda text: re.sub(r"\s+", "", text)
    assert normalize(fragment) in normalize(source), "native source extraction"
    assert normalize(fragment) in normalize(native), "native facade extraction"

    report = {"kernel": [], "false_claims": [], "axiom_guards": [], "native": [], "syntax": []}
    observations = ROOT / "external-observations"
    recounts = []
    for directory in sorted(observations.iterdir()):
        if not directory.is_dir():
            continue
        project = json.loads((directory / "project/RESULT.json").read_text())["observations"][0]["rows"]
        release = json.loads((directory / "release/RESULT.json").read_text())["observations"][0]["rows"]
        assert project == release, "release/project raw rows"
        row = {"capsule": directory.name, "rows": len(project), "release_project_rows_equal": True}
        if directory.name.startswith("css-flex"):
            values = [r["actual"]["descendants"] == r["expected"] for r in project]
            assert all(v == r["descendantGeometryMatches"] for v, r in zip(values, project))
        else:
            values = [r["actual"]["absoluteItems"] == r["expectedItems"] for r in project]
            counts = [len(r["actual"]["absoluteFragments"]) ==
                      (r["config"]["count"] if r["config"]["kind"] == "span" else 1)
                      for r in project]
            assert all(v == r["checks"]["absoluteItemGeometry"] for v, r in zip(values, project))
            assert all(v == r["checks"]["absoluteContinuationCount"] for v, r in zip(counts, project))
            row.update(fragment_count_pass=sum(counts), fragment_count_fail=len(counts)-sum(counts))
        row.update(geometry_pass=sum(values), geometry_fail=len(values)-sum(values))
        recounts.append(row)
    assert recounts == json.loads((observations / "INDEPENDENT-RECOUNT.json").read_text())
    report["browser_evidence_recount"] = recounts
    result = run([sys.executable, str(ROOT / "recount_native_evidence.py")], ROOT)
    assert result.returncode == 0, result.stdout
    report["native_candidate_evidence_recount"] = json.loads(result.stdout)
    with tempfile.TemporaryDirectory(prefix="css-overflow-review-") as name:
        work = Path(name)
        for filename in ["ObserverBoundaries.lean", "OverflowCoordinates.lean"]:
            shutil.copyfile(ROOT / filename, work / filename)
            result = run([lean, filename], work)
            assert result.returncode == 0, result.stdout
            audits = re.findall(r"depends on axioms: \[([^\]]*)\]", result.stdout)
            count = len(audits) + result.stdout.count("does not depend on any axioms")
            assert count == (8 if filename.startswith("Observer") else 11)
            for names in audits:
                axioms = {x.strip() for x in names.split(",") if x.strip()}
                assert axioms <= {"propext", "Quot.sound", "Classical.choice"}
            report["kernel"].append({"file": filename, "audits": count,
                                      "output": result.stdout})

        false_claims = [
            "example : (min (80 : Int) (-1)) = max 0 (min 80 (-1)) := by decide",
            "example : (1920000000 + 960000000 : Int) ≤ 2147483647 := by decide",
            "example : ((81 : Int) - (80 - 0) - 0) = 0 := by decide",
            "example : ((160 : Int) - (0 - 0) - 0) = 0 := by decide",
        ]
        for i, claim in enumerate(false_claims):
            path = work / f"FalseClaim{i}.lean"
            path.write_text("import Lean\n" + claim + "\n")
            result = run([lean, str(path)], work)
            assert result.returncode != 0 and "error:" in result.stdout
            report["false_claims"].append({"id": i, "claim": claim,
                                           "output": result.stdout})

        for name, body, forbidden in [
            ("CustomAxiom", "axiom injected : False\ntheorem fake : False := injected", "injected"),
            ("SorryAxiom", "theorem fake : False := by sorry", "sorryAx"),
        ]:
            path = work / (name + ".lean")
            path.write_text("import Lean\n" + body + "\n#print axioms fake\n")
            result = run([lean, str(path)], work)
            assert result.returncode == 0, result.stdout
            audits = re.findall(r"depends on axioms: \[([^\]]*)\]", result.stdout)
            assert len(audits) == 1
            axioms = {x.strip() for x in audits[0].split(",") if x.strip()}
            assert forbidden in axioms
            assert not axioms <= {"propext", "Quot.sound", "Classical.choice"}
            report["axiom_guards"].append({"name": name, "rejected_axiom": forbidden,
                                           "output": result.stdout})

        cases = [(0, 960000000, 960000000),
                 (960000000, 960000000, 1920000000),
                 (1920000000, 960000000, None),
                 (1920000000, 1073741823, 1920000000)]
        (work / "native.cpp").write_text(native)
        for opt in ["O0", "O2"]:
            exe = work / f"native-{opt}"
            result = run([clang, "-std=c++17", "-" + opt,
                          "-fsanitize=undefined", "-fno-sanitize-recover=all",
                          str(work / "native.cpp"), "-o", str(exe)], work)
            assert result.returncode == 0, result.stdout
            for prefix, available, expected in cases:
                result = run([str(exe), str(prefix), str(available)], work)
                if expected is None:
                    assert result.returncode != 0
                    assert "signed integer overflow" in result.stdout
                else:
                    assert result.returncode == 0 and result.stdout.strip() == str(expected)
                report["native"].append({"optimization": opt, "prefix": prefix,
                    "available": available, "expected_ub": expected is None,
                    "exit": result.returncode, "output": result.stdout})

        for path in sorted(ROOT.glob("*.js")):
            result = run(["node", "--check", str(path)], work)
            assert result.returncode == 0, result.stdout
            report["syntax"].append(path.name)
        result = run(["node", "--check", str(ROOT / "standalone-overflow-proposal/test-script.js")], work)
        assert result.returncode == 0, result.stdout
        report["syntax"].append("standalone-overflow-proposal/test-script.js")

        native_path = work / "layout/generic/nsFlexContainerFrame.cpp"
        native_path.parent.mkdir(parents=True)
        native_path.write_bytes((ROOT / "standalone-overflow-proposal/base.cpp").read_bytes())
        patch = ROOT / "standalone-overflow-proposal/proposal.patch"
        for reverse in [False, True]:
            args = ["git", "apply", "--unsafe-paths"]
            if reverse:
                args.append("--reverse")
            result = run(args + [str(patch)], work)
            assert result.returncode == 0, result.stdout
            filename = "base.cpp" if reverse else "candidate.cpp"
            assert native_path.read_bytes() == (ROOT / "standalone-overflow-proposal" / filename).read_bytes()
        report["standalone_apply_reverse"] = True
    report["temporary_products_removed"] = True
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

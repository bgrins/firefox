import hashlib, json, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ["git", "-c", "core.fsmonitor=false"]
CPP = "layout/generic/nsFlexContainerFrame.cpp"
patches = [HERE / "fix-candidate-v1.patch", ROOT / "artifacts/css-flex-natural-baseline-donor-fix-v2/fix-candidate-v2.patch"]
rows = []
for base in ["92a6fddf18e5828b17d7491a34663a0d5a9c12ad", "976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    original = subprocess.check_output(GIT + ["show", base + ":" + CPP], cwd=ROOT)
    results = []
    for order in [patches, list(reversed(patches))]:
        with tempfile.TemporaryDirectory(prefix="flex-baseline-commute-") as directory:
            work = Path(directory)
            source = work / CPP
            source.parent.mkdir(parents=True)
            source.write_bytes(original)
            for patch in order:
                subprocess.run(GIT + ["apply", str(patch)], cwd=work, check=True)
            results.append({str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest() for p in work.rglob("*") if p.is_file()})
            assert source.read_text().count("->GetLogicalNormalPosition(") == 3
            assert "->GetLogicalPosition(" not in source.read_text()
            for patch in reversed(order):
                subprocess.run(GIT + ["apply", "--reverse", str(patch)], cwd=work, check=True)
            assert source.read_bytes() == original
            assert [p for p in work.rglob("*") if p.is_file()] == [source]
    assert results[0] == results[1]
    rows.append({"base": base, "both_orders_identical": True, "exact_reverse": True, "combined_files": results[0]})
(HERE / "COMMUTATION.json").write_text(json.dumps({"patches": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in patches}, "checks": rows}, indent=2) + "\n")

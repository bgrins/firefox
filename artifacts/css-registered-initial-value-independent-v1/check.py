import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sys.flags.isolated and sys.flags.no_site
    root = Path(__file__).resolve().parent
    args = argparse.ArgumentParser()
    args.add_argument("--output", type=Path, required=True)
    out = args.parse_args().output.resolve()
    seal = json.loads((root / "FREEZE.json").read_text())
    assert digest(root / "MANIFEST.json") == seal["manifest_sha256"]
    manifest = json.loads((root / "MANIFEST.json").read_text())
    for rel, expected in manifest.items():
        path = Path(rel)
        assert not path.is_absolute() and ".." not in path.parts
        assert digest(root / path) == expected, rel
    assert not any(p.is_symlink() for p in root.rglob("*"))
    assert {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()} == set(manifest) | {"FREEZE.json", "MANIFEST.json"}
    assert not out.exists() and out != root and root not in out.parents
    out.mkdir(parents=True)
    final = root / "final-inputs"
    pair = json.loads((final / "FINAL-PAIR.json").read_text())
    pins = json.loads((final / "CANDIDATE-PINS.json").read_text())
    original = json.loads((final / "ORIGINAL-PINS.json").read_text())
    native = sorted(original)
    for phase, directory, expected in [("baseline", "source", original), ("candidate", "candidate", {k: pins[k] for k in native})]:
        run = next(x for x in pair["runs"] if x["variant"] == phase)
        assert run["sources"] == expected and run["stable_after"] and run["build_exit"] == 0
        for rel, sha in expected.items():
            assert digest(root / "provider" / directory / rel) == sha
        log = (final / ("final-" + phase + "-build.log")).read_text()
        assert "Compiling style" in log and "Compiling gkrust" in log and "toolkit/library/build/XUL" in log
        assert log.count("KeyError: 'export'") == 4
    assert pair["runs"][0]["test_exit"] == 1 and pair["runs"][1]["test_exit"] == 0
    assert all(pair["runs"][0]["binaries"][k] != v for k, v in pair["runs"][1]["binaries"].items())
    test = "testing/web-platform/tests/css/css-properties-values-api/registered-initial-computed-value.html"
    assert digest(final / "test.html") == pins[test] == pair["stable_sources"][test]
    maps = []
    for phase in ["baseline", "candidate"]:
        mapping = {}
        for line in (final / ("final-" + phase + "-raw.json")).read_text().splitlines():
            row = json.loads(line)
            if row.get("action") not in ("test_status", "test_end"):
                continue
            key = (row["action"], row["test"], row.get("subtest"))
            assert key not in mapping
            mapping[key] = row
        maps.append(mapping)
    a, b = maps
    assert a.keys() == b.keys() and len(a) == 107
    changed = []
    for key in a:
        if a[key]["status"] != b[key]["status"]:
            assert a[key]["status"] == "FAIL" and b[key]["status"] == "PASS"
            changed.append({"key": key, "baseline_message": a[key].get("message")})
    assert len(changed) == 4
    assert sum(x["key"][1].endswith("registered-initial-computed-value.html") for x in changed) == 3
    new = [v for k, v in b.items() if k[0] == "test_status" and k[1].endswith("registered-initial-computed-value.html")]
    assert len(new) == 12 and all(x["status"] == "PASS" for x in new)
    assert all(v["status"] == ("PASS" if k[0] == "test_status" else "OK") for k, v in b.items())
    assert (final / "final.patch").read_text().split("diff --git a/testing/")[0] == (final / "native.patch").read_text()
    packaging = json.loads((final / "STANDALONE-PACKAGING.json").read_text())
    assert digest(final / "final.patch") == packaging["patch_sha256"]
    for base in packaging["bases"]:
        work = out / base["label"]
        shutil.copytree(root / "standalone-source" / base["label"], work)
        for reverse in [False, True]:
            command = ["/usr/bin/patch", "-t", "-p1", "-i", str(final / "final.patch")]
            if reverse:
                command.append("-R")
            result = subprocess.run(command, cwd=work, capture_output=True, text=True)
            (out / (base["label"] + ("-reverse" if reverse else "-apply") + ".log")).write_text(result.stdout + result.stderr)
            assert result.returncode == 0 and "fuzz" not in result.stdout.lower()
            for name in native:
                expected = digest(root / "standalone-source" / base["label"] / name) if reverse else base["staged_source_pins"][name]
                assert digest(work / name) == expected
            assert not (work / test).exists() if reverse else digest(work / test) == pins[test]
    result = {"authenticated_inputs": len(manifest), "paired_keys": 107, "improvements": changed, "unchanged": 103, "new_subtests_pass": 12, "candidate_subtests_pass": 102, "harness_ok": 5, "standalone_apply_reverse": [x["label"] for x in packaging["bases"]], "build_monitor_keyerrors_per_phase": 4, "scope": "retained source/runtime evidence; no build/browser execution or universal proof"}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

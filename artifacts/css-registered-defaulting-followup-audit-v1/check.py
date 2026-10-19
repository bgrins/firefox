import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sys.flags.isolated and sys.flags.no_site
    root = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    out = ap.parse_args().output.resolve()
    freeze = json.loads((root / "FREEZE.json").read_text())
    assert h(root / "MANIFEST.json") == freeze["manifest_sha256"]
    manifest = json.loads((root / "MANIFEST.json").read_text())
    assert not any(p.is_symlink() for p in root.rglob("*"))
    for name, expected in manifest.items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert h(root / name) == expected, name
    assert {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()} == set(manifest) | {"FREEZE.json", "MANIFEST.json"}
    assert not out.exists() and out != root and root not in out.parents
    out.mkdir(parents=True)
    pins = json.loads((root / "SOURCE-PINS.json").read_text())
    for name, digest in pins.items():
        assert h(root / "source" / name) == digest
    run = json.loads((root / "root-baseline/RUN.json").read_text())
    assert run["stable_after"] and run["exit"] == 1
    for name, digest in pins.items():
        if name in run["pins"]:
            assert run["pins"][name] == digest
    assert (root / "root-baseline/test.html").read_bytes() == (root / "registered-inherit-invalid.html").read_bytes()
    rows = [json.loads(x) for x in (root / "root-baseline/raw.json").read_text().splitlines()]
    subs = [x for x in rows if x.get("action") == "test_status"]
    assert len(subs) == 10 and len({x["subtest"] for x in subs}) == 10
    failures = [x for x in subs if x["status"] == "FAIL"]
    assert {x["subtest"] for x in failures} == {"missing parent, direct inherit", "cyclic parent, direct inherit"}
    assert all('initial-token' in x["message"] and 'fallback-token' in x["message"] for x in failures)
    assert sum(x["status"] == "PASS" for x in subs) == 8
    assert any(x.get("action") == "test_end" and x["status"] == "OK" for x in rows)
    name = "servo/components/style/properties/cascade.rs"
    work = out / "work"
    target = work / name
    target.parent.mkdir(parents=True)
    shutil.copyfile(root / "source" / name, target)
    for reverse in [False, True]:
        cmd = ["/usr/bin/patch", "-t", "-p1", "-i", str(root / "native.patch")]
        if reverse:
            cmd.append("-R")
        result = subprocess.run(cmd, cwd=work, text=True, capture_output=True)
        (out / ("reverse.log" if reverse else "apply.log")).write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and "fuzz" not in result.stdout.lower()
        assert target.read_bytes() == (root / ("source" if reverse else "candidate") / name).read_bytes()
    htmls = ["registered-inherit-invalid.html", "registered-inherit-invalid-v2.html", "registered-defaulting-readiness-controls.html"]
    node = shutil.which("node")
    assert node
    for name in htmls:
        html = (root / name).read_text()
        assert html.count("<script>") == 1
        js = html.split("<script>", 1)[1].split("</script>", 1)[0]
        dst = out / (name + ".js")
        dst.write_text(js)
        result = subprocess.run([node, "--check", str(dst)], text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
    old = (root / htmls[0]).read_text().rsplit("</script>", 1)[0]
    assert (root / htmls[1]).read_text().startswith(old)
    result = {"authenticated_inputs": len(manifest), "baseline": {"FAIL": 2, "PASS": 8, "harness": "OK"}, "artifact_patch_apply_reverse": "PASS", "javascript_syntax": "PASS", "candidate_runtime": "NOT_RUN", "no_universal_proof_claim": True}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

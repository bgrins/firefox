import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, key
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def main():
    assert sys.flags.isolated and sys.flags.no_site
    root = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    assert digest(root / "MANIFEST.json") == read(root / "FREEZE.json")["manifest_sha256"]
    manifest = read(root / "MANIFEST.json")
    assert not any(p.is_symlink() for p in root.rglob("*"))
    for name, expected in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert digest(root / path) == expected, name
    assert {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()} == set(manifest) | {"MANIFEST.json", "FREEZE.json"}
    out = args.output.resolve()
    assert not out.exists() and out != root and root not in out.parents
    source = runpy.run_path(str(root / "source_check.py"))["inspect"](root)
    assert source == read(root / "SOURCE-BINDINGS.json")
    for record in read(root / "INPUT-PROVENANCE.json")["copies"].values():
        assert digest(root / record["to"]) == record["sha256"]
    config = read(root / "TOOLCHAIN.json")
    lean = config["lean"]
    assert digest(Path(lean)) == config["lean_sha256"]
    text = (root / "lean/Inherit.lean").read_text()
    assert not re.search(r"\b(sorry|axiom|admit|native_decide|unsafe)\b", text)
    names = ["RegisteredInherit." + n for n in re.findall(r"^theorem (\w+)", text, re.M)]
    assert names == read(root / "THEOREMS.json") and len(names) == 17
    out.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("LEAN_", "PYTHON"))}
    commands = []
    def command(cmd, cwd):
        e = dict(env, LEAN_PATH=str(cwd))
        r = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True)
        commands.append({"command": cmd, "cwd": str(cwd), "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
        (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        return r
    main_dir = out / "kernel"
    main_dir.mkdir()
    (main_dir / "Inherit.lean").write_text(text)
    r = command([lean, "-o", "Inherit.olean", "Inherit.lean"], main_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    (main_dir / "Audit.lean").write_text("import Inherit\n" + "".join("#print axioms " + n + "\n" for n in names))
    r = command([lean, "Audit.lean"], main_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", r.stdout, re.M)
    assert [n for n, _ in rows] == names, r.stdout
    for _, group in rows:
        assert set(filter(None, (x.strip() for x in group.split(',')))) <= {"propext", "Quot.sound", "Classical.choice"}
    (out / "AXIOMS.txt").write_text(r.stdout)
    definitions = text.split("theorem put_selected", 1)[0] + "def witness" + text.split("def witness", 1)[1].split("theorem witness_ready", 1)[0]
    assert definitions.count("def witness") == 1
    definitions += "\nend RegisteredInherit\n"
    rejected = []
    for mutation in read(root / "MUTANTS.json"):
        assert definitions.count(mutation["old"]) == 1
        work = out / "mutants" / mutation["name"]
        work.mkdir(parents=True)
        driver = "import Mutant\nopen RegisteredInherit\nexample : " + mutation["goal"] + " := by decide\n"
        (work / "Witness.lean").write_text(driver)
        (work / "Mutant.lean").write_text(definitions)
        r = command([lean, "-o", "Mutant.olean", "Mutant.lean"], work)
        assert r.returncode == 0, r.stdout + r.stderr
        r = command([lean, "Witness.lean"], work)
        assert r.returncode == 0, r.stdout + r.stderr
        (work / "Mutant.lean").write_text(definitions.replace(mutation["old"], mutation["new"]))
        r = command([lean, "-o", "Mutant.olean", "Mutant.lean"], work)
        assert r.returncode == 0, r.stdout + r.stderr
        r = command([lean, "Witness.lean"], work)
        assert r.returncode != 0 and "decide" in r.stdout and "false" in r.stdout, r.stdout + r.stderr
        assert not any(x in r.stdout.lower() for x in ["unknown identifier", "unexpected token", "failed to synthesize"])
        rejected.append(mutation["name"])
    work = out / "patch"
    name = "servo/components/style/properties/cascade.rs"
    target = work / name
    target.parent.mkdir(parents=True)
    shutil.copyfile(root / "source/original/cascade.rs", target)
    for reverse in [False, True]:
        cmd = ["/usr/bin/patch", "-t", "-p1", "-i", str(root / "native.patch")]
        if reverse:
            cmd.append("-R")
        r = command(cmd, work)
        assert r.returncode == 0 and "fuzz" not in r.stdout.lower()
        assert target.read_bytes() == (root / ("source/original/cascade.rs" if reverse else "source/candidate/cascade.rs")).read_bytes()
    result = {"authenticated_inputs": len(manifest), "theorems": names, "semantic_mutants_rejected": rejected, "source_bindings": len(source), "artifact_patch_apply_reverse": "PASS", "native_compilation": "NOT_RUN", "scope": "conditional selected explicit-inherit model; no universal native/cache/caller proof"}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

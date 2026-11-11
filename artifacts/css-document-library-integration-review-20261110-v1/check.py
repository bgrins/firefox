import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = HERE.parent / "css-document-library-integration-20261110-v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode())
    return result.stdout


def git_object(repo, commit, path):
    return run(["git", "-c", "core.fsmonitor=false", "show", commit + ":" + path], repo)


def tree(path):
    return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()}


def main():
    manifest = read_json(SOURCE / "SOURCE-ONLY.json")
    for name, expected in manifest.items():
        assert sha((SOURCE / name).read_bytes()) == expected, name
    base = read_json(SOURCE / "BASE.json")
    origins = read_json(SOURCE / "ORIGINS.json")
    objects = {}
    for name, expected in base["authenticated_git_objects"].items():
        data = git_object(REPO / "artifacts/css-spec-lean", base["commit"], name)
        assert sha(data) == expected and data == (SOURCE / "base" / name).read_bytes(), name
        objects["canonical:" + name] = expected
    source_objects = {}
    for name, expected in origins["authenticated_git_objects"].items():
        data = git_object(REPO, origins["commit"], name)
        assert sha(data) == expected, name
        source_objects[name] = data
        objects["firefox:" + name] = expected
    before = tree(SOURCE / "base")
    overlay = tree(SOURCE / "overlay")
    after = before | overlay
    changed = sorted(n for n in overlay if n in before and before[n] != overlay[n])
    assert changed == ["CssDerivation.lean", "README.md", "derivation_check.py", "research/derivation/README.md"]
    tracked = set(run(["git", "-c", "core.fsmonitor=false", "ls-tree", "-r", "--name-only", base["commit"]],
                      REPO / "artifacts/css-spec-lean").decode().splitlines())
    assert set(overlay) & tracked == set(changed)
    transport = json.loads(after["research/derivation/document/TRANSPORT.json"])
    original_manifest = source_objects[transport["origin_artifact"] + "/SOURCE-ONLY.json"] if transport["origin_artifact"] + "/SOURCE-ONLY.json" in source_objects else git_object(REPO, origins["commit"], transport["origin_artifact"] + "/SOURCE-ONLY.json")
    assert after["research/derivation/document/origin/SOURCE-ONLY.json"] == original_manifest
    records = transport["records"]
    assert {r["source"]: r["source_sha256"] for r in records} == json.loads(original_manifest)
    assert len(records) == len({r["source"] for r in records}) == len({r["installed"] for r in records})
    inverse = {v: k for k, v in transport["module_map"].items()}
    assert len(inverse) == len(transport["module_map"])

    def unmap(data):
        return "".join("import " + inverse.get(line[7:].strip(), line[7:].strip()) + "\n"
                       if line.startswith("import ") else line
                       for line in data.decode().splitlines(keepends=True)).encode()

    imports_changed = 0
    shared = []
    for record in records:
        data = after[record["installed"]]
        old = source_objects[transport["origin_artifact"] + "/" + record["source"]]
        assert sha(data) == record["installed_sha256"] and sha(old) == record["source_sha256"]
        assert (unmap(data) if record["installed"].endswith(".lean") else data) == old
        if record["installed"].endswith(".lean"):
            imports_changed += sum(a != b for a, b in zip(data.splitlines(), old.splitlines()))
        if record["shared"]:
            assert data == before[record["installed"]]
            shared.append(record["installed"])
    review = transport["review_boundary"]
    assert unmap(after[review["installed"]]) == source_objects[review["source"]]
    assert sha(after[review["installed"]]) == review["installed_sha256"]
    assert sha(after["research/derivation/document/origin/REVIEW-REPORT.md"]) == review["report_sha256"]
    controls = {}
    with tempfile.TemporaryDirectory(prefix="document-integration-review-") as tmp:
        work = Path(tmp)
        for name, data in before.items():
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        patch = str((SOURCE / "integration.patch").resolve())
        run(["git", "apply", "--check", patch], work)
        run(["git", "apply", patch], work)
        assert tree(work) == after
        run(["git", "apply", "--reverse", "--check", patch], work)
        run(["git", "apply", "--reverse", patch], work)
        assert tree(work) == before
        for name, data in after.items():
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        spec = importlib.util.spec_from_file_location("reviewed_collector", work / "derivation_check.py")
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        closure = helper.facade_sources(work)
        registry_name = "research/derivation/FACADE.json"
        registry = json.loads(after[registry_name])
        assert len(closure) == 30 and set(closure) == set(registry)
        assert not any("/Tools/" in n or "/Tests/" in n for n in closure)
        positions = {n: i for i, n in enumerate(closure)}
        for name in closure:
            for dependency in re.findall(r"(?m)^import ([\w.]+)$", after[name].decode()):
                path = dependency.replace(".", "/") + ".lean"
                if path in positions:
                    assert positions[path] < positions[name]
        facade = "CssDerivation.lean"
        dependency = "CssDerivation/FirstOrder/Weakening.lean"
        for label in ["unregistered-existing-dependency", "cycle", "third-party-import", "module-header", "prelude-header", "comment-import"]:
            (work / facade).write_bytes(after[facade])
            (work / dependency).write_bytes(after[dependency])
            reg = dict(registry)
            if label == "unregistered-existing-dependency":
                del reg[dependency]
                expected = "Changed or unregistered facade dependency: " + dependency
            elif label == "cycle":
                bad = after[dependency] + b"\nimport CssDerivation\n"
                (work / dependency).write_bytes(bad)
                reg[dependency] = sha(bad)
                expected = "Cyclic facade dependency: CssDerivation"
            else:
                suffix = {"third-party-import": "import Other.Library", "module-header": "module", "prelude-header": "prelude", "comment-import": "-- import Other.Library"}[label]
                bad = after[facade] + (suffix + "\n").encode()
                (work / facade).write_bytes(bad)
                reg[facade] = sha(bad)
                expected = "Unsupported facade import module: Other.Library" if label == "third-party-import" else "Unsupported facade module header: CssDerivation.lean"
            (work / registry_name).write_text(json.dumps(reg))
            try:
                result = helper.facade_sources(work)
            except ValueError as error:
                assert label != "comment-import" and str(error) == expected, (label, str(error))
                controls[label] = {"status": "rejected", "diagnostic": str(error)}
            else:
                assert label == "comment-import" and result == closure, label
                controls[label] = {"status": "accepted", "closure_unchanged": True}
        assert not list(work.rglob("*.olean"))
    for name, expected in manifest.items():
        assert sha((SOURCE / name).read_bytes()) == expected, name
    result = {"status": "pass", "source_manifest_sha256": sha((SOURCE / "SOURCE-ONLY.json").read_bytes()),
              "source_inputs": len(manifest), "git_object_count": len(objects) + 1,
              "git_objects": objects, "origin_manifest_sha256": sha(original_manifest),
              "patch_sha256": sha((SOURCE / "integration.patch").read_bytes()),
              "changed_existing_files": changed, "transported_inputs": len(records),
              "new_path_git_collision_absent": True,
              "shared_inputs": shared, "changed_import_lines_excluding_review": imports_changed,
              "facade_order": closure, "independent_collector_controls": controls,
              "patch_forward_reverse_exact": True, "default_css_target_built": False,
              "temporary_tree_removed": True}
    (HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "source_inputs", "git_object_count", "transported_inputs", "changed_import_lines_excluding_review"]}))


if __name__ == "__main__":
    main()

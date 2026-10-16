# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import hashlib
import json
import os
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(path):
    result = {}
    visited = set()
    for directory, directories, files in os.walk(path, followlinks=True):
        current = Path(directory)
        require(current.resolve() not in visited, f"Repeated library directory: {current}")
        visited.add(current.resolve())
        for name in sorted(directories + files):
            item = current / name
            entry = {"kind": "directory" if item.is_dir() else "file"}
            if item.is_symlink():
                target = os.readlink(item)
                if target.startswith(str(ROOT) + os.sep):
                    target = "<ROOT>/" + target[len(str(ROOT)) + 1:]
                entry = {"kind": "symlink", "target": target}
            if item.is_file():
                entry["sha256"] = digest(item)
            result[str(item.relative_to(path))] = entry
    return result


def check_tools(manifest):
    for name, expected in manifest["sha256"].items():
        path = ROOT / name
        require(path.is_file() and digest(path) == expected, f"Pinned extraction input changed: {name}")
    backend = ROOT / manifest["backend"]
    expected = json.loads((HERE / "provider-tools/backend-inventory.json").read_text())
    require(inventory(backend) == expected, "Original Lean backend inventory changed")


def audit(output, expected):
    records = re.findall(
        r"'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|(does not depend on any axioms))", output,
    )
    found = {}
    for name, payload, _ in records:
        require(name not in found, f"Duplicate proof audit: {name}")
        values = [item.strip() for item in payload.split(",") if item.strip()]
        require(len(values) == len(set(values)), f"Duplicate axiom: {name}")
        found[name] = sorted(values)
    require(set(found) == set(expected), "Missing or unexpected proof audit")
    for name, values in found.items():
        require(values == sorted(expected[name]), f"Unexpected proof axioms: {name}")
    return found


def check_source(crate, source_root):
    require(crate.get("has_errors") is False, "Charon reported embedded errors")
    translated = crate["translated"]
    for section in ("type_decls", "fun_decls", "trait_decls", "trait_impls"):
        for declaration in translated[section]:
            if declaration is not None:
                require(not declaration["item_meta"].get("has_errors"), "Errored declaration")
    sources = {}
    for source in translated["files"]:
        if source is None or "Local" not in source["name"] or source["contents"] is None:
            continue
        path = (source_root / source["name"]["Local"]).resolve()
        if path.is_relative_to(ROOT):
            require(path.read_text() == source["contents"], f"Embedded source mismatch: {path}")
            sources[str(path.relative_to(ROOT))] = digest(path)
    return sources


def check_unchanged(sources):
    for name, expected in sources.items():
        require(digest(ROOT / name) == expected, f"Verification input changed during run: {name}")


def setup_overlay(manifest, directory, env, lean, run):
    backend = ROOT / manifest["backend"]
    directory.mkdir(parents=True)
    for source in backend.rglob("*"):
        target = directory / source.relative_to(backend)
        if source.is_dir():
            target.mkdir(exist_ok=True)
        elif source.is_file():
            target.symlink_to(source)
    module = directory / "Aeneas/Do/Elab"
    for old in module.parent.glob("Elab.*"):
        old.unlink()
    source = ROOT / manifest["elaborator_source"]
    shutil.copyfile(source, module.with_suffix(".lean"))
    run(["patch", "-p1", "--fuzz=0", "-i", HERE / "provider-tools/normalize-caseson-type.patch"],
        "elaborator-patch", directory)
    env["LEAN_PATH"] = str(directory) + os.pathsep + env["LEAN_PATH"]
    run([lean / "lean", "-DwarningAsError=true", "-Dlinter.dupNamespace=false",
         "-o", "Aeneas/Do/Elab.olean", "Aeneas/Do/Elab.lean"], "elaborator-compile", directory)
    return inventory(directory)


def verify_baseline(manifest, generated, env, lean, run, charon, aeneas):
    work = generated / "baseline"
    work.mkdir()
    llbc = work / "baseline.llbc"
    run([charon, "cargo", "--preset", "aeneas", "--sysroot", "default",
         "--monomorphize-mut=except-types", "--remove-adt-clauses",
         "--lift-associated-types", "*", "--start-from", "stylo_bloom_verification::storage_hash",
         "--start-from", "stylo_bloom_verification::candidate_hash", "--dest-file", llbc,
         "--", "--lib", "--locked", "--offline"], "baseline-charon", HERE / "baseline/crate")
    data = json.loads(llbc.read_text())
    sources = check_source(data, HERE / "baseline/crate")
    require(str((HERE / "baseline/old_bloom_storage.rs").relative_to(ROOT)) in sources,
            "Missing immutable original storage source")
    require("servo/components/style/bloom_storage.rs" in sources, "Missing current storage source")
    for declaration in data["translated"]["fun_decls"]:
        if declaration is None:
            continue
        names = [part["Ident"][0] for part in declaration["item_meta"]["name"] if "Ident" in part]
        if names[0] == "stylo_bloom_verification":
            require(isinstance(declaration["body"], dict) and "Structured" in declaration["body"],
                    f"Unchecked baseline function: {names}")
    run([aeneas, "-backend", "lean", "-namespace", "Baseline", "-dest", work,
         "-abort-on-error", "-warnings-as-errors", "-no-progress-bar", llbc], "baseline-aeneas", ROOT)
    previous_path = env["LEAN_PATH"]
    env["LEAN_PATH"] = str(work) + os.pathsep + previous_path
    try:
        run([lean / "lean", "-DwarningAsError=true", "-o", "Model.olean", "Baseline.lean"],
            "baseline-model", work)
        proof = HERE / "baseline/WrapperEquivalence.lean"
        shutil.copyfile(proof, work / proof.name)
        output = run([lean / "lean", "-DwarningAsError=true", "-o", "WrapperEquivalence.olean", proof.name],
                     "baseline-proof", work)
        expected = json.loads((HERE / "provider-audits.json").read_text())["baseline"]
        audits = audit(output, expected)
    finally:
        env["LEAN_PATH"] = previous_path
    return {"audits": audits, "sources": sources, "model_sha256": digest(work / "Baseline.lean")}

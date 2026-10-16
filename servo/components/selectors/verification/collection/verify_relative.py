#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os
import platform
import shutil
import subprocess
import sys

from verify_helper import PROJECT, ROOT, TOOLS, digest, validate_tools


def main(scope="relative"):
    if scope == "ancestor":
        from ancestor_boundary import AUDITS, audit_axioms, audit_boundary
    elif scope == "matching":
        from matching_boundary import AUDITS, audit_axioms, audit_boundary
    else:
        assert scope == "relative"
        from relative_boundary import AUDITS, audit_axioms, audit_boundary
    generated = PROJECT / "generated" / scope
    (generated / "evidence.json").unlink(missing_ok=True)
    aeneas = validate_tools()
    source = generated / "collection.llbc"
    normalized = generated / "normalized.llbc"
    report = generated / "normalization-report.json"
    for stale in [source, normalized, report]:
        stale.unlink(missing_ok=True)
    model_root = generated / "model"
    output = model_root / "Normalized"
    if model_root.exists():
        shutil.rmtree(model_root)
    output.mkdir(parents=True)
    commands = [
        ("source", [sys.executable, PROJECT / "extract.py", f"--{scope}", "--llbc-only"]),
        ("normalize", [sys.executable, PROJECT / "normalize.py", source, normalized, report]),
        ("extract", [aeneas, "-backend", "lean", "-namespace", "Collection", "-split-files",
                     "-loops-to-rec", "-dest", output, "-sequential", "-abort-on-error",
                     "-warnings-as-errors", "-no-progress-bar", normalized]),
    ]
    for name, command in commands:
        log = TOOLS / f"collection-{scope}-{name}.log"
        print(f"Running {name}; log: {log}", flush=True)
        with log.open("w") as stream:
            subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    audit_boundary(json.loads(source.read_text()), output)
    lock = json.loads((PROJECT.parent / "toolchain.json").read_text())
    asset = lock["platforms"][f"{platform.system()}-{platform.machine()}"]["lean"]
    lean = TOOLS / asset.removesuffix(".tar.zst") / "bin"
    env = dict(os.environ)
    env["PATH"] = str(lean) + os.pathsep + env["PATH"]
    dependencies = subprocess.check_output(
        [lean / "lake", "env", "printenv", "LEAN_PATH"], env=env,
        cwd=TOOLS / "aeneas/backends/lean", text=True,
    ).strip()
    env["LEAN_PATH"] = str(model_root) + os.pathsep + dependencies
    models = {name: PROJECT / "lean/relative" / f"{name}.lean" for name in [
        "TypesExternal", "FunsExternal", "IteratorProofs", "CollectorStepProofs",
        "CollectorInvariantProofs", "CollectorLoopProofs", "RecursiveCollectorProofs", "LoopInvariantProofs", "FrameProofs", "BoundaryAudit",
    ]}
    if scope == "matching":
        models["TypesExternal"] = PROJECT / "lean/matching/TypesExternal.lean"
        models["MatchingProofs"] = PROJECT / "lean/matching/MatchingProofs.lean"
    if scope == "ancestor":
        for name in ["FunsExternal", "AncestorIteratorProofs", "AncestorProgressProofs",
                     "AncestorLoopProofs", "AncestorContracts", "AncestorSubjectProofs",
                     "AncestorScanProofs", "AncestorComponentProofs", "AncestorFullProofs",
                     "AncestorBoundaryAudit"]:
            models[name] = PROJECT / "lean/ancestor" / f"{name}.lean"
    for name, source_model in models.items():
        shutil.copyfile(source_model, output / f"{name}.lean")
    transcript = ""
    log = TOOLS / f"collection-{scope}-check.log"
    print(f"Running Lean checks; log: {log}", flush=True)
    with log.open("w") as stream:
        for name in ["TypesExternal", "Types", "FunsExternal", "Funs", *[name for name in models if name not in {"TypesExternal", "FunsExternal"}]]:
            result = subprocess.run(
                [lean / "lean", "-DwarningAsError=true", "-R", model_root,
                 "-o", output / f"{name}.olean", output / f"{name}.lean"],
                env=env, cwd=model_root, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, check=False,
            )
            stream.write(result.stdout)
            stream.flush()
            result.check_returncode()
            transcript += result.stdout
    audit_axioms(transcript)
    rust_sources = {}
    for entry in json.loads(source.read_text())["translated"]["files"]:
        local = entry["name"].get("Local")
        if local:
            path = (PROJECT / local).resolve()
            if path.is_file() and path.is_relative_to(ROOT):
                rust_sources[str(path.relative_to(ROOT))] = digest(path)
    evidence = {
        "scope": (
            "ancestor: finite-depth required-prefix and zero-tail collector theorem; no matching-to-region theorem"
            if scope == "ancestor" else
            scope + ": recursive collector required-hash invariant; no full matching-to-region theorem"
        ),
        "aeneas_sha256": digest(aeneas),
        "charon_sha256": digest(TOOLS / "aeneas/charon"),
        "source_llbc_sha256": digest(source),
        "normalized_llbc_sha256": digest(normalized),
        "normalization_report_sha256": digest(report),
        "boundary_sha256": digest(PROJECT / f"{scope}-boundary.json"),
        "rust_sources": rust_sources,
        "lean_sources": {str(p.relative_to(PROJECT)): digest(p) for p in sorted(output.glob("*.lean"))},
        "axioms": {name: sorted(values) for name, values in AUDITS.items()},
    }
    (generated / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Fresh {scope} extraction, boundary checks, declared proofs, and exact axiom audits passed.")


if __name__ == "__main__":
    main()

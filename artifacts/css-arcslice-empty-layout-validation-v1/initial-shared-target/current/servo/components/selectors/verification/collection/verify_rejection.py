#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile

from normalize import require
from verify_helper import PROJECT, ROOT, TOOLS, digest, validate_tools


def validate_release(asset):
    archive = TOOLS / asset["aeneas"]
    require(digest(archive) == asset["aeneas_sha256"], "Pinned release archive changed")
    with tarfile.open(archive) as bundle:
        for name in ["aeneas", "charon"]:
            members = [entry for entry in bundle.getmembers() if entry.name == name]
            require(len(members) == 1 and members[0].isfile(), "Unexpected release executable entry")
            with bundle.extractfile(members[0]) as stream:
                expected = hashlib.sha256(stream.read()).hexdigest()
            require(digest(TOOLS / "aeneas" / name) == expected, f"Release executable changed: {name}")


def validate_collection_sources(output, manifest, scope="matching"):
    actual = {str(source.relative_to(PROJECT)) for source in output.glob("*.lean")}
    require(set(manifest["lean_sources"]) == actual, f"Fresh {scope} source inventory changed")
    for relative, expected in manifest["lean_sources"].items():
        require(digest(PROJECT / relative) == expected, f"Fresh {scope} model changed")


def main(scope="matching"):
    if scope == "ancestor":
        from ancestor_rejection_boundary import audit_combined, expected_audits
    else:
        require(scope == "matching", "Unexpected rejection scope")
        from rejection_boundary import audit_combined, expected_audits
    target = "ancestor-rejection" if scope == "ancestor" else "rejection"
    generated = PROJECT / "generated" / target
    evidence = generated / "evidence.json"
    evidence.unlink(missing_ok=True)
    model = generated / "model"
    if model.exists():
        shutil.rmtree(model)
    model.mkdir(parents=True)
    validate_tools()
    lock = json.loads((PROJECT.parent / "toolchain.json").read_text())
    asset = lock["platforms"][f"{platform.system()}-{platform.machine()}"]
    validate_release(asset)
    core_llbc = PROJECT.parent / "generated/stylo_bloom_verification.llbc"
    core_model = PROJECT.parent / "lean/Generated/StyloBloomVerification.lean"
    core_llbc.unlink(missing_ok=True)
    core_model.unlink(missing_ok=True)
    commands = [
        ("core", [sys.executable, PROJECT.parent / "verify.py"]),
        (scope, [sys.executable, PROJECT / f"verify_{scope}.py"]),
    ]
    for stage, command in commands:
        log = TOOLS / f"collection-{target}-{stage}.log"
        print(f"Running fresh {stage}; log: {log}", flush=True)
        with log.open("w") as stream:
            subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    collection_output = PROJECT / "generated" / scope / "model/Normalized"
    collection_evidence = PROJECT / "generated" / scope / "evidence.json"
    collection_manifest = json.loads(collection_evidence.read_text())
    validate_collection_sources(collection_output, collection_manifest, scope)
    for source in collection_output.glob("*.lean"):
        destination = model / "Normalized" / source.name
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, destination)
    (model / "Generated").mkdir()
    shutil.copyfile(core_model, model / "Generated/StyloBloomVerification.lean")
    for name in ["BloomProofs", "PackingProofs", "NormalizationProofs"]:
        shutil.copyfile(PROJECT.parent / "lean" / f"{name}.lean", model / f"{name}.lean")
    shutil.copyfile(PROJECT / "lean" / scope / "RejectionProofs.lean", model / "Normalized/RejectionProofs.lean")
    shutil.copyfile(PROJECT / "lean/PackingBridgeProofs.lean", model / "Normalized/PackingBridgeProofs.lean")
    lean = TOOLS / asset["lean"].removesuffix(".tar.zst") / "bin"
    env = dict(os.environ)
    env["PATH"] = str(lean) + os.pathsep + env["PATH"]
    dependencies = subprocess.check_output(
        [lean / "lake", "env", "printenv", "LEAN_PATH"], cwd=TOOLS / "aeneas/backends/lean",
        env=env, text=True,
    ).strip()
    env["LEAN_PATH"] = str(model) + os.pathsep + dependencies
    scope_modules = ["MatchingProofs"] if scope == "matching" else [
        "AncestorIteratorProofs", "AncestorProgressProofs", "AncestorLoopProofs",
        "AncestorContracts", "AncestorSubjectProofs", "AncestorScanProofs",
        "AncestorComponentProofs", "AncestorFullProofs", "AncestorBoundaryAudit",
    ]
    modules = [
        "Generated/StyloBloomVerification", "BloomProofs", "PackingProofs", "NormalizationProofs",
        *[f"Normalized/{name}" for name in [
            "TypesExternal", "Types", "FunsExternal", "Funs", "IteratorProofs",
            "CollectorStepProofs", "CollectorInvariantProofs", "CollectorLoopProofs",
            "RecursiveCollectorProofs", "LoopInvariantProofs", "FrameProofs",
            "BoundaryAudit", *scope_modules, "PackingBridgeProofs", "RejectionProofs",
        ]],
    ]
    transcript = ""
    log = TOOLS / f"collection-{target}-check.log"
    print(f"Compiling combined proof from source; log: {log}", flush=True)
    with log.open("w") as stream:
        for name in modules:
            result = subprocess.run(
                [lean / "lean", "-DwarningAsError=true", "-R", model,
                 "-o", model / f"{name}.olean", model / f"{name}.lean"],
                env=env, cwd=model, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False,
            )
            stream.write(result.stdout)
            stream.flush()
            result.check_returncode()
            transcript += result.stdout
    audit_combined(transcript)
    evidence.write_text(json.dumps({
        "scope": (
            "Finite-depth FullGood and ValidHistory imply actual ancestor collection/packing/rejection safety; no successful-match or DOM-region theorem"
            if scope == "ancestor" else
            "Local-name compound conjunction implies collector/packing/rejection safety under explicit DOM HashAlignment and ValidHistory"
        ),
        "core_llbc_sha256": digest(core_llbc),
        "core_aeneas_sha256": digest(TOOLS / "aeneas/aeneas"),
        f"{scope}_evidence_sha256": digest(collection_evidence),
        f"{scope}_evidence": collection_manifest,
        "collection_boundary_sha256": digest(PROJECT / f"{scope}-boundary.json"),
        "boundary_sha256": digest(PROJECT / "rejection-boundary.json"),
        "lean_sources": {str(path.relative_to(model)): digest(path) for path in sorted(model.rglob("*.lean"))},
        "axioms": {name: sorted(axioms) for name, axioms in expected_audits().items()},
    }, indent=2) + "\n")
    print(f"Fresh {scope} collection, packing, and rejection proof passed with {len(expected_audits())} exact audits.")


if __name__ == "__main__":
    main()

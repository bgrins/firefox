#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[4]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_tools():
    manifest = json.loads((PROJECT / "tool-patch.json").read_text())
    build = manifest["builds"]["collection"]
    aeneas = ROOT / build["path"]
    pinned = [
        (aeneas, build["sha256"]),
        (TOOLS / "aeneas/charon", manifest["charon_binary_sha256"]),
    ]
    pinned += [(PROJECT / p["path"], p["sha256"]) for p in manifest["patches"]]
    for path, expected in pinned:
        if digest(path) != expected:
            raise RuntimeError(f"Pinned extraction input changed: {path}")
    if (
        subprocess.check_output([aeneas, "-version"], text=True).strip()
        != "aeneas " + build["version"]
    ):
        raise RuntimeError("Unexpected patched Aeneas version")

    return aeneas


def main():
    generated = PROJECT / "generated"
    (generated / "helper-evidence.json").unlink(missing_ok=True)
    aeneas = validate_tools()
    source = generated / "simple/collection.llbc"
    normalized = generated / "simple/normalized.llbc"
    report = generated / "simple/normalization-report.json"
    for stale in [source, normalized, report]:
        stale.unlink(missing_ok=True)
    output = generated / "Normalized"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    commands = [
        ("source", [sys.executable, PROJECT / "extract.py", "--simple", "--llbc-only"]),
        (
            "normalize",
            [sys.executable, PROJECT / "normalize.py", source, normalized, report],
        ),
        (
            "extract",
            [
                aeneas,
                "-backend",
                "lean",
                "-namespace",
                "Collection",
                "-split-files",
                "-dest",
                output,
                "-abort-on-error",
                "-warnings-as-errors",
                "-no-progress-bar",
                normalized,
            ],
        ),
        ("check", [sys.executable, PROJECT / "check_model.py"]),
    ]
    for name, command in commands:
        log = TOOLS / f"collection-helper-{name}.log"
        print(f"Running {name}; log: {log}", flush=True)
        with log.open("w") as stream:
            subprocess.run(
                command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True
            )

    rust_sources = {}
    for entry in json.loads(source.read_text())["translated"]["files"]:
        local = entry["name"].get("Local")
        if local:
            path = (PROJECT / local).resolve()
            if path.is_file() and path.is_relative_to(ROOT):
                rust_sources[str(path.relative_to(ROOT))] = digest(path)
    evidence = {
        "scope": "generic production simple_selector_hash policy; no DOM matching or iterator theorem",
        "aeneas_sha256": digest(aeneas),
        "charon_sha256": digest(TOOLS / "aeneas/charon"),
        "source_llbc_sha256": digest(source),
        "normalized_llbc_sha256": digest(normalized),
        "normalization_report_sha256": digest(report),
        "rust_sources": rust_sources,
        "lean_sources": {
            str(p.relative_to(PROJECT)): digest(p)
            for p in sorted(output.glob("*.lean"))
        },
        "proof_sha256": digest(PROJECT / "lean/ComponentProofs.lean"),
        "axioms": ["propext", "Classical.choice", "Quot.sound", "core.fmt.Formatter"],
    }
    (generated / "helper-evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n"
    )
    print(
        "Fresh production helper extraction, policy proof, and exact axiom audit passed."
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "artifacts/stylo-bloom-tools/recovery-binder-check",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").unlink(missing_ok=True)
    tools = ROOT / "artifacts/stylo-bloom-tools"
    provenance = json.loads((HERE / "tool-patch.json").read_text())
    binaries = {}
    for name, info in provenance["binaries"].items():
        path = ROOT / info["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"], name)
        binaries[name] = path
    for info in provenance["prerequisite_patches"] + provenance["patches"]:
        path = HERE / info["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"], str(path))
    charon = tools / "aeneas/charon"
    require(
        hashlib.sha256(charon.read_bytes()).hexdigest() == provenance["charon_binary_sha256"],
        str(charon),
    )
    lean = tools / "lean-4.35.0-rc4-darwin_aarch64/bin"
    env = dict(
        os.environ,
        RUSTUP_HOME=str(tools / "rustup"),
        CARGO_HOME=str(tools / "cargo"),
        RUSTUP_TOOLCHAIN="nightly-2026-09-17",
    )
    env["PATH"] = str(lean) + os.pathsep + env["PATH"]
    env["LEAN_PATH"] = subprocess.check_output(
        [lean / "lake", "env", "printenv", "LEAN_PATH"],
        cwd=tools / "aeneas/backends/lean", env=env, text=True,
    ).strip()
    results = {}

    def run(command, name, expected_error=None):
        log = output / (name + ".log")
        with log.open("w") as stream:
            result = subprocess.run(
                command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=False,
            )
        if expected_error is None:
            require(result.returncode == 0, str(log))
        else:
            require(result.returncode != 0, str(log))
            require(expected_error in log.read_text(), str(log))
        results[name] = {"exit_code": result.returncode, "expected_error": expected_error}

    for case in ["repro", "two_regions", "two_regions_outlives", "two_regions_equal"]:
        llbc = output / (case + ".llbc")
        llbc.unlink(missing_ok=True)
        run([
            charon, "rustc", "--preset", "aeneas", "--monomorphize-mut=all",
            "--sysroot", "default", "--start-from", "borrowed_trait::invoke",
            "--dest-file", llbc, "--", "--crate-type", "lib", "--crate-name",
            "borrowed_trait", "--edition", "2024", HERE / (case + ".rs"),
        ], case + "-charon")
        require(llbc.is_file(), f"Charon did not produce {llbc}")
        for variant in ["baseline", "binder_only"]:
            failure = (
                "interp/InterpExpansion.ml, line 500"
                if variant == "baseline" and case != "two_regions_equal" else None
            )
            run([
                binaries[variant], "-borrow-check", "-abort-on-error",
                "-warnings-as-errors", "-no-progress-bar", llbc,
            ], case + "-" + variant + "-borrow", failure)
        destination = output / case
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir()
        failure = (
            "symbolic/SymbolicToPureExpressions.ml, line 1033"
            if case == "two_regions_outlives" else None
        )
        run([
            binaries["patched"], "-backend", "lean", "-namespace", "BorrowedTrait",
            "-dest", destination, "-abort-on-error", "-warnings-as-errors",
            "-no-progress-bar", llbc,
        ], case + "-patched-extract", failure)
        if failure is None:
            generated = [p for p in destination.glob("*.lean") if p.name != "Model.lean"]
            require(len(generated) == 1, str(destination))
            run([lean / "lean", "-DwarningAsError=true", generated[0]], case + "-lean")
            model = destination / "Model.lean"
            shutil.copyfile(generated[0], model)
            old_path = env["LEAN_PATH"]
            env["LEAN_PATH"] = str(destination) + os.pathsep + old_path
            run([lean / "lean", "-o", destination / "Model.olean", model], case + "-model")
            proof = {
                "repro": "ReproProofs.lean",
                "two_regions": "TwoRegionsProofs.lean",
                "two_regions_equal": "TwoRegionsEqualProofs.lean",
            }[case]
            run([lean / "lean", "-DwarningAsError=true", HERE / proof], case + "-proof")
            audit = (output / (case + "-proof.log")).read_text().strip()
            require(audit == "'invoke_exact' depends on axioms: [propext, Classical.choice, Quot.sound]", audit)
            env["LEAN_PATH"] = old_path
    expected = json.loads((HERE / "expected-results.json").read_text())
    require(results == expected, "Native extraction results differ from expected-results.json")
    (output / "report.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"All expected gates matched; report: {output / 'report.json'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[3]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"
LOCK = json.loads((PROJECT / "toolchain.json").read_text())
OPERATIONS = ("new", "insert", "remove", "contains", "clear")
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
ITERATOR_EXTERNAL = (
    "core.slice.iter.Iter.Insts.CoreIterTraitsIteratorIteratorSharedAT.all"
)
THEOREMS = {
    "new_eq_empty",
    "clear_eq_empty",
    "saturated_slot_unchanged",
    "key_mask_spec",
    "hash1_spec",
    "hash2_spec",
    "first_index_spec",
    "second_index_spec",
    "slot_is_empty_spec",
    "contains_of_nonzero",
    "adjust_slot_represents",
    "insert_represents",
    "remove_represents",
    "liveCounts_append",
    "member_contributions",
    "empty_represents",
    "history_represents",
    "history_no_false_negatives",
}


def run(args, *, cwd=ROOT, env=None, log=None):
    args = [str(arg) for arg in args]
    print("Running:", " ".join(args), flush=True)
    if log is None:
        return subprocess.run(args, cwd=cwd, env=env, check=True)
    with log.open("w") as output:
        result = subprocess.run(
            args, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT, check=False
        )
    if result.returncode:
        print(log.read_text(), file=sys.stderr)
        result.check_returncode()


def download(url, path, expected):
    if not path.exists():
        temporary = path.with_suffix(path.suffix + ".part")
        run(["curl", "--fail", "--location", "--retry", "3", url, "-o", temporary])
        temporary.replace(path)
    with path.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError(f"SHA-256 mismatch: {path}")


def bootstrap(assets, lean, env):
    for name, repo, release, directory in (
        ("aeneas", "AeneasVerif/aeneas", LOCK["aeneas_release"], TOOLS / "aeneas"),
        ("lean", "leanprover/lean4", LOCK["lean_release"], lean),
    ):
        archive = TOOLS / assets[name]
        download(
            f"https://github.com/{repo}/releases/download/{release}/{assets[name]}",
            archive,
            assets[name + "_sha256"],
        )
        if not directory.exists():
            destination = TOOLS if name == "lean" else directory
            destination.mkdir(parents=True, exist_ok=True)
            run(["tar", "-xf", archive, "-C", destination])
    run(
        [
            "rustup",
            "toolchain",
            "install",
            LOCK["rust_toolchain"],
            "--profile",
            "minimal",
            "--component",
            "rustc-dev,rust-src",
            "--no-self-update",
        ],
        env=env,
        log=TOOLS / "rust-setup.log",
    )
    run(
        [lean / "bin/lake", "update"],
        cwd=TOOLS / "aeneas/backends/lean",
        env=env,
        log=TOOLS / "lean-dependencies.log",
    )


def audit_proofs(output):
    reports = re.findall(
        r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output, re.DOTALL
    )
    expected = {f"BloomProofs.{name}" for name in THEOREMS}
    if {name for name, _ in reports} != expected:
        raise RuntimeError("Lean did not report the expected theorem dependencies")
    for theorem, names in reports:
        axioms = {name.strip() for name in names.split(",") if name.strip()}
        allowed = STANDARD_AXIOMS.copy()
        if theorem in {
            "BloomProofs.new_eq_empty",
            "BloomProofs.clear_eq_empty",
            "BloomProofs.contains_of_nonzero",
            "BloomProofs.insert_represents",
            "BloomProofs.remove_represents",
            "BloomProofs.history_represents",
            "BloomProofs.history_no_false_negatives",
        }:
            allowed.add(ITERATOR_EXTERNAL)
        if unexpected := axioms - allowed:
            raise RuntimeError(f"Unexpected axioms in {theorem}: {unexpected}")
    print(f"Audited dependencies of {len(reports)} theorems.")


def main():
    parser = argparse.ArgumentParser(description="Check the Stylo Bloom filter proofs")
    parser.add_argument(
        "--bootstrap", action="store_true", help="Download pinned tools"
    )
    args = parser.parse_args()
    key = f"{platform.system()}-{platform.machine()}"
    if key not in LOCK["platforms"]:
        raise RuntimeError(f"No pinned tool binaries for {key}")
    assets = LOCK["platforms"][key]
    lean = TOOLS / assets["lean"].removesuffix(".tar.zst")
    aeneas = TOOLS / "aeneas"
    TOOLS.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        RUSTUP_HOME=str(TOOLS / "rustup"),
        RUSTUP_TOOLCHAIN=LOCK["rust_toolchain"],
        CARGO_HOME=str(TOOLS / "cargo"),
        MATHLIB_CACHE_DIR=str(TOOLS / "mathlib-cache"),
        PATH=str(lean / "bin") + os.pathsep + env["PATH"],
    )
    if args.bootstrap:
        bootstrap(assets, lean, env)
    for executable in (aeneas / "aeneas", aeneas / "charon", lean / "bin/lean"):
        if not executable.exists():
            raise RuntimeError(f"Missing {executable}; run verify.py --bootstrap first")
    version = subprocess.check_output(
        [aeneas / "aeneas", "-version"], text=True
    ).strip()
    if version != f"aeneas {LOCK['aeneas_release']}":
        raise RuntimeError(f"Unexpected Aeneas version: {version}")

    generated = PROJECT / "generated"
    generated.mkdir(exist_ok=True)
    run(
        [
            "cargo",
            "test",
            "--offline",
            "--locked",
            "--manifest-path",
            PROJECT / "Cargo.toml",
        ],
        env=env,
        log=generated / "rust-tests.log",
    )
    llbc = generated / "stylo_bloom_verification.llbc"
    command = [aeneas / "charon", "rustc", "--preset", "aeneas", "--sysroot", "default"]
    for operation in OPERATIONS:
        command += ["--start-from", f"stylo_bloom_verification::{operation}"]
    command += [
        "--dest-file",
        llbc,
        "--",
        "--crate-type",
        "lib",
        "--crate-name",
        "stylo_bloom_verification",
        "--edition",
        "2024",
        PROJECT / "lib.rs",
    ]
    run(command, env=env, log=generated / "charon.log")
    lean_generated = PROJECT / "lean/Generated"
    lean_generated.mkdir(exist_ok=True)
    run(
        [
            aeneas / "aeneas",
            "-backend",
            "lean",
            "-namespace",
            "Bloom",
            "-dest",
            lean_generated,
            "-abort-on-error",
            "-warnings-as-errors",
            "-no-progress-bar",
            llbc,
        ],
        env=env,
        log=generated / "aeneas.log",
    )
    search_path = subprocess.check_output(
        [lean / "bin/lake", "env", "printenv", "LEAN_PATH"],
        cwd=aeneas / "backends/lean",
        env=env,
        text=True,
    ).strip()
    env["LEAN_PATH"] = str(PROJECT / "lean") + os.pathsep + search_path
    run(
        [
            lean / "bin/lean",
            "-DwarningAsError=true",
            "-o",
            "Generated/StyloBloomVerification.olean",
            "Generated/StyloBloomVerification.lean",
        ],
        cwd=PROJECT / "lean",
        env=env,
        log=generated / "lean-model.log",
    )
    proof_log = generated / "lean-proofs.log"
    run(
        [lean / "bin/lean", "-DwarningAsError=true", "BloomProofs.lean"],
        cwd=PROJECT / "lean",
        env=env,
        log=proof_log,
    )
    audit_proofs(proof_log.read_text())
    print(f"Verification passed. Logs: {generated}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))

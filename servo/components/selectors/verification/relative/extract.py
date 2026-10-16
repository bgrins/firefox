#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import os
import platform
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ROOT = PROJECT.parents[3]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"
LOCK = json.loads((PROJECT / "toolchain.json").read_text())
ASSETS = LOCK["platforms"][f"{platform.system()}-{platform.machine()}"]
LEAN = TOOLS / ASSETS["lean"].removesuffix(".tar.zst")
AENEAS = TOOLS / "aeneas"
ENV = dict(os.environ)
ENV.update(
    RUSTUP_HOME=str(TOOLS / "rustup"),
    RUSTUP_TOOLCHAIN=LOCK["rust_toolchain"],
    CARGO_HOME=str(TOOLS / "cargo"),
    MATHLIB_CACHE_DIR=str(TOOLS / "mathlib-cache"),
    PATH=str(LEAN / "bin") + os.pathsep + ENV["PATH"],
)

RELATIVE_THEOREMS = {
    "next_children",
    "new_eq_empty",
    "reuse_filter",
    "discard_failed_build",
    "publish_successful_build",
    "next_descendants",
    "finish_inside",
    "sequence_bound",
    "sequence_head",
    "sequence_unique_head",
    "sequence_members",
    "sequence_nodup",
    "sequence_exists",
    "descendant_suffix",
    "descendants_trace",
    "descendant_interval",
    "children_bound",
    "children_head",
    "children_members",
    "children_nodup",
    "children_exists_from",
    "children_exists",
    "children_suffix",
    "children_trace",
    "target_mapping",
    "key_separation",
    "successful_trace_coverage",
    "descendants_coverage",
    "children_coverage",
}
CACHE_THEOREMS = {
    "get_filter_spec",
    "first_lookup_without_build",
    "update_preserves_coverage",
    "get_filter_preserves_epoch",
}
BRIDGE_THEOREMS = {
    "contains_eq",
    "insert_eq",
    "bind_if",
    "present_lookup",
    "insertions_to_bloom",
    "insertions_coverage",
    "build_coverage",
    "get_filter_no_false_negatives",
}
MAP_EXTERNALS = {
    "Box.Insts.CoreConvertAsRef.as_ref",
    "Isize.Insts.CoreHashHash.hash",
    "Usize.Insts.CoreHashHash.hash",
    "std.hash.random.DefaultHasher",
    "std.hash.random.RandomState",
    "std.collections.hash.map.HashMap",
    "std.collections.hash.map.OccupiedEntry",
    "std.collections.hash.map.VacantEntry",
    "std.collections.hash.map.HashMap.entry",
    "std.collections.hash.map.OccupiedEntry.get_mut",
    "std.collections.hash.map.OccupiedEntry.into_mut",
    "std.collections.hash.map.VacantEntry.insert",
    "std.hash.random.DefaultHasher.Insts.CoreHashHasher.finish",
    "std.hash.random.DefaultHasher.Insts.CoreHashHasher.write",
    "std.hash.random.RandomState.Insts.CoreHashBuildHasherDefaultHasher.build_hasher",
}


def audit(output, *, bridge=False):
    reports = re.findall(
        r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output, re.DOTALL
    )
    reports += [
        (name, "")
        for name in re.findall(r"'([^']+)' does not depend on any axioms", output)
    ]
    expected = {f"RelativeProofs.{name}" for name in RELATIVE_THEOREMS}
    expected |= {f"CacheProofs.{name}" for name in CACHE_THEOREMS}
    expected |= {
        "RelativeWitnesses.sampleForest",
        "RelativeWitnesses.branch_and_chain",
        "RelativeWitnesses.sampleNavigation",
    }
    if bridge:
        expected |= {f"RelativeBridgeProofs.{name}" for name in BRIDGE_THEOREMS}
    if {name for name, _ in reports} != expected or len(reports) != len(expected):
        raise RuntimeError(
            "Relative proof dependency reports did not match the expected declarations"
        )
    for name, dependencies in reports:
        allowed = {"propext", "Classical.choice", "Quot.sound"}
        if name in {
            "CacheProofs.get_filter_spec",
            "CacheProofs.first_lookup_without_build",
            "CacheProofs.get_filter_preserves_epoch",
        }:
            allowed |= MAP_EXTERNALS
        if name == "RelativeBridgeProofs.get_filter_no_false_negatives":
            allowed |= {f"Relative.{external}" for external in MAP_EXTERNALS}
        actual = {
            dependency.strip()
            for dependency in dependencies.split(",")
            if dependency.strip()
        }
        if unexpected := actual - allowed:
            raise RuntimeError(f"Unexpected axioms in {name}: {unexpected}")
    print(f"Audited dependencies of {len(reports)} relative proof declarations.")


def run(args, log, cwd=ROOT):
    with log.open("w") as output:
        result = subprocess.run(
            [str(arg) for arg in args],
            cwd=cwd,
            env=ENV,
            stdout=output,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if result.returncode:
        print(log.read_text())
    result.check_returncode()


def audit_adapter_exclusion(path):
    translated = json.loads(path.read_text())["translated"]
    crate = {"Ident": ["stylo_relative_verification", 0]}
    parser = {"Ident": ["parser", 0]}
    context = {"Ident": ["context", 0]}
    hint = [crate, parser, {"Ident": ["RelativeSelectorMatchHint", 0]}]
    hints = 0
    for section in [
        "fun_decls",
        "type_decls",
        "global_decls",
        "trait_decls",
        "trait_impls",
    ]:
        for declaration in translated[section]:
            if declaration is None:
                continue
            name = declaration["item_meta"]["name"]
            if name[:2] not in ([crate, parser], [crate, context]):
                continue
            if section == "type_decls" and name == hint:
                hints += 1
                continue
            raise RuntimeError(f"Extraction retained mock selector semantics: {name}")
    if hints != 1:
        raise RuntimeError(
            "Expected exactly one extracted RelativeSelectorMatchHint type"
        )
    print("Verified mock selector collection declarations are excluded.")


parser = argparse.ArgumentParser()
parser.add_argument("--bridge", action="store_true")
args = parser.parse_args()
generated = HERE / "generated"
generated.mkdir(exist_ok=True)
lean_generated = HERE / "RelativeGenerated"
lean_generated.mkdir(exist_ok=True)
version = subprocess.check_output([AENEAS / "aeneas", "-version"], text=True).strip()
if version != f"aeneas {LOCK['aeneas_release']}":
    raise RuntimeError(f"Unexpected Aeneas version: {version}")


def hint_variants(path):
    source = path.read_text()
    enum = source.split("pub enum RelativeSelectorMatchHint {", 1)[1].split("}", 1)[0]
    return set(re.findall(r"^\s*(In\w+),\s*$", enum, re.MULTILINE))


if hint_variants(PROJECT.parent / "parser.rs") != hint_variants(HERE / "lib.rs"):
    raise RuntimeError(
        "RelativeSelectorMatchHint variants changed; update the extraction adapter"
    )
llbc = generated / "stylo_relative_verification.llbc"
command = [
    AENEAS / "charon",
    "rustc",
    "--preset",
    "aeneas",
    "--sysroot",
    "default",
]
for operation in ["walk", "update", "target", "same_key", "cached"]:
    command += [
        "--start-from",
        "stylo_relative_verification::relative_filter::" + operation,
    ]
for operation in ["insert", "contains"]:
    command += ["--start-from", "stylo_relative_verification::" + operation]
run(
    command
    + [
        "--dest-file",
        llbc,
        "--",
        "--crate-type",
        "lib",
        "--crate-name",
        "stylo_relative_verification",
        "--edition",
        "2024",
        HERE / "lib.rs",
    ],
    generated / "charon.log",
)
audit_adapter_exclusion(llbc)
run(
    [
        AENEAS / "aeneas",
        "-backend",
        "lean",
        "-namespace",
        "Relative",
        "-dest",
        lean_generated,
        "-abort-on-error",
        "-warnings-as-errors",
        "-no-progress-bar",
        llbc,
    ],
    generated / "aeneas.log",
)
search_path = subprocess.check_output(
    [LEAN / "bin/lake", "env", "printenv", "LEAN_PATH"],
    cwd=AENEAS / "backends/lean",
    env=ENV,
    text=True,
).strip()
ENV["LEAN_PATH"] = os.pathsep.join([str(PROJECT / "lean"), str(HERE), search_path])
run(
    [
        LEAN / "bin/lean",
        "-DwarningAsError=true",
        "-o",
        "RelativeGenerated/StyloRelativeVerification.olean",
        "RelativeGenerated/StyloRelativeVerification.lean",
    ],
    generated / "lean-model.log",
    cwd=HERE,
)
proof_logs = []
for name in ["RelativeProofs", "CacheProofs", "Witnesses"]:
    log = generated / f"{name}.log"
    run(
        [
            LEAN / "bin/lean",
            "-DwarningAsError=true",
            "-o",
            f"{name}.olean",
            f"{name}.lean",
        ],
        log,
        cwd=HERE,
    )
    proof_logs.append(log.read_text())
if args.bridge:
    log = generated / "RelativeBridgeProofs.log"
    run(
        [
            LEAN / "bin/lean",
            "-DwarningAsError=true",
            "RelativeBridgeProofs.lean",
        ],
        log,
        cwd=PROJECT / "lean",
    )
    proof_logs.append(log.read_text())
audit("\n".join(proof_logs), bridge=args.bridge)

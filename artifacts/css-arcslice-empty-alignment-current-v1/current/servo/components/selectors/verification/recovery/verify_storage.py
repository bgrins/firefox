#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

import provider_controls
import provider_tools

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ROOT = HERE.parents[4]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"
PROOFS = (
    "BloomProofs",
    "PackingProofs",
    "NormalizationProofs",
    "StyleBloomProofs",
    "CoverageProofs",
    "RecoveryProofs",
    "StorageHistoryProofs",
    "ZeroedProofs",
)
STORAGE_OPERATIONS = (
    "storage_hash",
    "storage_push",
    "storage_clear",
    "storage_recover",
    "storage_rebuild",
    "provider_insert",
    "provider_expected",
    "provider_storage_push",
)
STORAGE_PROOFS = (
    "HashInsertProofs", "PendingProofs", "StorageClearProofs",
    "StorageQueryProofs", "StoragePopProofs", "StoragePushProofs",
    "StorageResourceProofs", "StorageInvariantProofs", "RecoverySimulationProofs",
    "StorageContractProofs", "StorageBackProofs", "StorageProductionProofs",
    "RecoverSimulationProofs", "StorageRecoverProofs",
)
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
STORAGE_AUDITS = {
    f"HashInsertProofs.{name}": STANDARD_AXIOMS | {
        "smallvec.SmallVec", "smallvec.SmallVec.push", "ArrayT64.Insts.SmallvecArray.size",
    }
    for name in (
        "push_hash_exact", "push_hash_inv", "calls_accounting",
        "calls_borrowed_fields", "calls_close", "calls_history",
    )
}
for operation in ("push", "pop"):
    for suffix in ("exact", "inv"):
        STORAGE_AUDITS[f"PendingProofs.{operation}_{suffix}"] = STANDARD_AXIOMS | {
            "smallvec.SmallVec", f"smallvec.SmallVec.{operation}",
            "core.fmt.Formatter", "ArrayT16.Insts.SmallvecArray.size",
        }
for name in ("restore_fields", "restore_compose"):
    STORAGE_AUDITS[f"PendingProofs.{name}"] = STANDARD_AXIOMS | {"smallvec.SmallVec"}
STORAGE_AUDITS["StorageClearProofs.empty_zeroed"] = STANDARD_AXIOMS
for name in ("clear_exact", "clear_history"):
    STORAGE_AUDITS[f"StorageClearProofs.{name}"] = STANDARD_AXIOMS | {
        "smallvec.SmallVec", "smallvec.SmallVec.clear", "core.fmt.Formatter",
        "ArrayT16.Insts.SmallvecArray.size", "ArrayT64.Insts.SmallvecArray.size",
        "smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref",
    }
QUERY_BASE = STANDARD_AXIOMS | {"smallvec.SmallVec", "core.fmt.Formatter"}
QUERY_LEN = {"smallvec.SmallVec.len", "ArrayT16.Insts.SmallvecArray.size"}
QUERY_LAST = {
    "ArrayT16.Insts.SmallvecArray.size", "core.slice.Slice.last",
    "smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref",
}
for name in ("parent_exact", "closure_exact", "option_map_exact"):
    STORAGE_AUDITS[f"StorageQueryProofs.{name}"] = QUERY_BASE
STORAGE_AUDITS["StorageQueryProofs.len_exact"] = QUERY_BASE | QUERY_LEN
STORAGE_AUDITS["StorageQueryProofs.current_parent_exact"] = QUERY_BASE | QUERY_LAST
for name in ("len_contents", "current_parent_contents"):
    STORAGE_AUDITS[f"StorageQueryProofs.{name}"] = QUERY_BASE | QUERY_LEN | QUERY_LAST
STORAGE_AUDITS["StoragePopProofs.remove_history"] = STANDARD_AXIOMS
POP_LOOP = STANDARD_AXIOMS | {
    "smallvec.SmallVec", "smallvec.SmallVec.pop", "ArrayT64.Insts.SmallvecArray.size",
    "alloc.vec.Vec.pop",
}
STORAGE_AUDITS["StoragePopProofs.pop_loop_history"] = POP_LOOP
for name in ("pop_some_history", "pop_none_history"):
    STORAGE_AUDITS[f"StoragePopProofs.{name}"] = POP_LOOP | {
        "core.fmt.Formatter", "ArrayT16.Insts.SmallvecArray.size",
        "core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual",
        "core.option.Option.Insts.CoreOpsTry_traitTry.branch",
    }
PUSH_INTERNAL = STANDARD_AXIOMS | {
    "smallvec.SmallVec", "smallvec.SmallVec.len", "smallvec.SmallVec.push",
    "core.fmt.Formatter", "ArrayT16.Insts.SmallvecArray.size",
    "ArrayT64.Insts.SmallvecArray.size",
}
for suffix in ("history", "success"):
    STORAGE_AUDITS[f"StoragePushProofs.push_internal_{suffix}"] = PUSH_INTERNAL
    STORAGE_AUDITS[f"StoragePushProofs.push_{suffix}"] = PUSH_INTERNAL | {"smallvec.SmallVec.is_empty"}
for name in ("flatMap_length_bound", "push_capacity"):
    STORAGE_AUDITS[f"StorageResourceProofs.{name}"] = {"propext", "Quot.sound"}
for name in ("push_hash_success", "calls_exist"):
    STORAGE_AUDITS[f"StorageResourceProofs.{name}"] = STANDARD_AXIOMS | {
        "smallvec.SmallVec", "smallvec.SmallVec.push", "ArrayT64.Insts.SmallvecArray.size",
    }
SEQUENCE_MODEL = PUSH_INTERNAL | {
    "smallvec.SmallVec.clear", "smallvec.SmallVec.pop", "alloc.vec.Vec.pop",
    "smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref",
}
STORAGE_AUDITS["StorageInvariantProofs.push_valid"] = SEQUENCE_MODEL | {"smallvec.SmallVec.is_empty"}
STORAGE_AUDITS["StorageInvariantProofs.clear_valid"] = SEQUENCE_MODEL
STORAGE_AUDITS["StorageInvariantProofs.pop_valid"] = SEQUENCE_MODEL | {
    "core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual",
    "core.option.Option.Insts.CoreOpsTry_traitTry.branch",
}
for name in ("trace_loop", "onSuccess_admissible", "loop_trace"):
    STORAGE_AUDITS[f"RecoverySimulationProofs.{name}"] = STANDARD_AXIOMS
for name in (
    "collect_body_simulation", "collect_loop_simulation", "collect_success_simulation",
    "flush_body_simulation", "flush_loop_simulation", "flush_success_simulation",
    "rebuild_simulation",
):
    STORAGE_AUDITS[f"RecoverySimulationProofs.{name}"] = STANDARD_AXIOMS | {"smallvec.SmallVec"}
for name in (
    "len_spec", "current_parent_spec", "clear_spec", "pop_spec", "push_spec",
    "pending_push_spec", "pending_pop_spec", "contract",
):
    STORAGE_AUDITS[f"StorageContractProofs.{name}"] = SEQUENCE_MODEL | {
        "smallvec.SmallVec.is_empty", "core.slice.Slice.last",
        "core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual",
        "core.option.Option.Insts.CoreOpsTry_traitTry.branch",
    }
STORAGE_AUDITS["StorageBackProofs.push_internal_back"] = PUSH_INTERNAL
for name in ("push_back", "stack_push_back"):
    STORAGE_AUDITS[f"StorageBackProofs.{name}"] = PUSH_INTERNAL | {"smallvec.SmallVec.is_empty"}
for name in ("clear_back", "stack_clear_back"):
    STORAGE_AUDITS[f"StorageBackProofs.{name}"] = STORAGE_AUDITS["StorageClearProofs.clear_exact"]
for name in ("pop_back", "stack_pop_back"):
    STORAGE_AUDITS[f"StorageBackProofs.{name}"] = STORAGE_AUDITS["StoragePopProofs.pop_some_history"]
for operation in ("push", "pop"):
    STORAGE_AUDITS[f"StorageBackProofs.pending_{operation}_back"] = STORAGE_AUDITS[f"PendingProofs.{operation}_exact"]
for name in ("projection_inv", "successful_spec"):
    STORAGE_AUDITS[f"StorageProductionProofs.{name}"] = STANDARD_AXIOMS
for name in ("unary_relation", "option_relation"):
    STORAGE_AUDITS[f"StorageProductionProofs.{name}"] = STANDARD_AXIOMS | {"smallvec.SmallVec"}
STORAGE_AUDITS["StorageProductionProofs.valid_hash_lookup"] = SEQUENCE_MODEL - {"core.fmt.Formatter"}
for name in ("rebuild_contract", "rebuild_ancestors", "rebuild_retains_hashes"):
    STORAGE_AUDITS[f"StorageProductionProofs.{name}"] = STORAGE_AUDITS["StorageContractProofs.contract"]
STORAGE_AUDITS["RecoverSimulationProofs.loop_transport"] = STANDARD_AXIOMS
for name in (
    "recover_simulation", "trim_body_simulation", "trim_simulation",
    "ascend_body_simulation", "ascend_simulation", "common_body_simulation", "common_simulation",
):
    STORAGE_AUDITS[f"RecoverSimulationProofs.{name}"] = STANDARD_AXIOMS | {"smallvec.SmallVec"}
for name in ("recover_contract", "recover_ancestors", "recover_retains_hashes"):
    STORAGE_AUDITS[f"StorageRecoverProofs.{name}"] = STORAGE_AUDITS["StorageContractProofs.contract"]
STORAGE_THEOREMS = set(STORAGE_AUDITS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def audit_storage(output):
    records = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output)
    records += [
        (name, "") for name in re.findall(r"'([^']+)' does not depend on any axioms", output)
    ]
    require(len(records) == len(STORAGE_THEOREMS), "Missing or duplicate storage proof audit")
    seen = set()
    for name, axioms in records:
        require(name in STORAGE_THEOREMS and name not in seen, f"Unexpected storage proof audit: {name}")
        require(set(re.split(r",\s*", axioms.strip())) == STORAGE_AUDITS[name], f"Unexpected storage axioms: {name}")
        seen.add(name)
    require(seen == STORAGE_THEOREMS, "Missing storage proof audit")


def audit_source(crate):
    functions = [f for f in crate["fun_decls"] if f]
    names = []
    for function in functions:
        name = function["item_meta"]["name"]
        parts = [p["Ident"][0] for p in name if "Ident" in p]
        if parts[0] != "stylo_bloom_verification":
            continue
        if parts[:2] == ["stylo_bloom_verification", "each_relevant_element_hash"]:
            continue
        require(
            isinstance(function["body"], dict)
            and "Structured" in function["body"],
            f"Production function has no extracted body: {parts}",
        )
        if len(parts) > 1 and parts[1] in ("bloom_storage", "bloom_hashes"):
            span = function["item_meta"]["span"]["Untagged"]["data"]
            source = next(item for item in crate["files"] if item["id"] == span["file_id"])
            path = (HERE / "crate" / source["name"]["Local"]).resolve()
            require(
                path == ROOT / "servo/components/style" / f"{parts[1]}.rs",
                f"Storage method does not come from production source: {parts}",
            )
        names.append(parts)
    for operation in STORAGE_OPERATIONS:
        require(
            names.count(["stylo_bloom_verification", operation]) == 1,
            f"Missing or duplicate storage entry point: {operation}",
        )
    methods = [n[2:] for n in names if n[:2] == ["stylo_bloom_verification", "bloom_storage"]]
    for method in ("push_hash", "push_internal", "pop", "clear", "pending_push", "pending_pop"):
        require([method] in methods, f"Missing production storage method: {method}")


def main():
    generated = HERE / "generated/combined"
    if generated.exists():
        shutil.rmtree(generated)
    generated.mkdir(parents=True)
    evidence = generated / "evidence.json"
    evidence.unlink(missing_ok=True)
    provenance = json.loads((HERE / "tool-patch.json").read_text())
    storage_tools = json.loads((HERE / "storage-tool.json").read_text())
    charon = TOOLS / "aeneas/charon"
    aeneas = ROOT / storage_tools["binary"]["path"]
    before_names = ROOT / provenance["binaries"]["patched"]["path"]
    pinned = [
        (charon, provenance["charon_binary_sha256"]),
        (aeneas, storage_tools["binary"]["sha256"]),
        (before_names, provenance["binaries"]["patched"]["sha256"]),
    ]
    pinned += [
        (HERE / item["path"], item["sha256"])
        for item in provenance["prerequisite_patches"]
        + provenance["patches"]
        + storage_tools["patches"]
    ]
    for path, expected in pinned:
        require(digest(path) == expected, f"Pinned extraction input changed: {path}")

    provider_manifest = json.loads((HERE / "provider-tool.json").read_text())
    provider_tools.check_tools(provider_manifest)
    charon = ROOT / provider_manifest["charon"]
    aeneas = ROOT / provider_manifest["aeneas"]
    tracked_inputs = [HERE / "verify_storage.py", HERE / "provider_tools.py", HERE / "provider_controls.py", HERE / "provider-audits.json",
                      HERE / "provider-tool.json", HERE / "crate/lib.rs", HERE / "crate/Cargo.toml",
                      HERE / "crate/Cargo.lock", PROJECT / "verify.py", PROJECT / "toolchain.json",
                      HERE / "baseline/source.json", HERE / "function_names.rs",
                      HERE / "tool-patch.json", HERE / "storage-tool.json"]
    tracked_inputs += list((PROJECT / "lean").glob("*.lean")) + list((HERE / "lean").glob("*.lean"))
    tracked_inputs += list((HERE / "baseline").rglob("*.rs")) + list((HERE / "baseline").rglob("*.lean"))
    tracked_inputs += list((HERE / "baseline").rglob("Cargo.*"))
    tracked_inputs += list((HERE / "provider-tools/controls").glob("*"))
    input_hashes = {str(path.relative_to(ROOT)): digest(path) for path in tracked_inputs}

    spec = importlib.util.spec_from_file_location("bloom_verifier", PROJECT / "verify.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    key = f"{platform.system()}-{platform.machine()}"
    require(key == storage_tools["platform"], f"Native tool is not pinned for {key}")
    lean = TOOLS / verifier.LOCK["platforms"][key]["lean"].removesuffix(".tar.zst") / "bin"
    env = dict(
        os.environ,
        RUSTUP_HOME=str(TOOLS / "rustup"),
        RUSTUP_TOOLCHAIN=verifier.LOCK["rust_toolchain"],
        CARGO_HOME=str(TOOLS / "cargo"),
        CARGO_NET_OFFLINE="true",
        CARGO_TARGET_DIR=str(generated / "target"),
    )
    env["PATH"] = str(lean) + os.pathsep + env["PATH"]
    work = generated / "lean"
    if work.exists():
        shutil.rmtree(work)
    (work / "Generated").mkdir(parents=True)
    dependencies = subprocess.check_output(
        [lean / "lake", "env", "printenv", "LEAN_PATH"],
        cwd=TOOLS / "aeneas/backends/lean", env=env, text=True,
    ).strip()
    env["LEAN_PATH"] = str(work) + os.pathsep + dependencies

    def run(command, name, cwd, expected_error=None):
        log = generated / f"{name}.log"
        print(f"Running {name}; log: {log}", flush=True)
        with log.open("w") as stream:
            result = subprocess.run(
                command, cwd=cwd, env=env, stdout=stream,
                stderr=subprocess.STDOUT, check=False,
            )
        text = log.read_text()
        if expected_error is None:
            result.check_returncode()
        else:
            require(result.returncode == 2 and expected_error in text, f"Unexpected tool regression result: {log}")
        return text

    overlay = generated / "lean-override"
    overlay_before = provider_tools.setup_overlay(provider_manifest, overlay, env, lean, run)
    env["LEAN_PATH"] = str(work) + os.pathsep + env["LEAN_PATH"]

    controls = provider_controls.verify(generated, lean, run, charon, aeneas)

    repro = generated / "function-names"
    if repro.exists():
        shutil.rmtree(repro)
    repro.mkdir()
    repro_llbc = repro / "function_names.llbc"
    run([
        charon, "rustc", "--preset", "aeneas", "--monomorphize-mut=except-types",
        "--remove-adt-clauses", "--lift-associated-types", "*", "--sysroot", "default",
        "--start-from", "function_names::advance", "--start-from", "function_names::invoke",
        "--dest-file", repro_llbc, "--", "--crate-type", "lib", "--crate-name", "function_names",
        "--edition", "2024", HERE / "function_names.rs",
    ], "function-names-charon", ROOT)
    for label, binary, error in (
        ("before", before_names, 'bound to the same name "advance"'),
        ("after", aeneas, None),
    ):
        destination = repro / label
        destination.mkdir()
        run([
            binary, "-backend", "lean", "-namespace", "FunctionNames", "-dest", destination,
            "-abort-on-error", "-warnings-as-errors", "-no-progress-bar", repro_llbc,
        ], f"function-names-{label}", ROOT, error)
    models = list((repro / "after").glob("*.lean"))
    require(len(models) == 1, "Expected one generated naming reproducer model")
    run([lean / "lean", "-DwarningAsError=true", models[0]], "function-names-lean", ROOT)

    llbc = generated / "stylo_bloom_verification.llbc"
    llbc.unlink(missing_ok=True)
    command = [
        charon, "cargo", "--preset", "aeneas", "--sysroot", "default",
        "--monomorphize-mut=except-types", "--remove-adt-clauses",
        "--lift-associated-types", "*",
        "--opaque", "stylo_bloom_verification::each_relevant_element_hash",
    ]
    for operation in (*verifier.OPERATIONS, *STORAGE_OPERATIONS):
        command += ["--start-from", f"stylo_bloom_verification::{operation}"]
    command += ["--dest-file", llbc, "--", "--lib", "--locked", "--offline"]
    run(command, "charon", HERE / "crate")
    data = json.loads(llbc.read_text())
    extracted_sources = provider_tools.check_source(data, HERE / "crate")
    crate = data["translated"]
    audit_source(crate)
    run([
        aeneas, "-backend", "lean", "-namespace", "Bloom", "-dest", work / "Generated",
        "-abort-on-error", "-warnings-as-errors", "-no-progress-bar", llbc,
    ], "aeneas", ROOT)
    for name in PROOFS:
        shutil.copyfile(PROJECT / "lean" / f"{name}.lean", work / f"{name}.lean")
    output = []
    for name in ("Generated/StyloBloomVerification", *PROOFS):
        log = run([
            lean / "lean", "-DwarningAsError=true", "-o", f"{name}.olean", f"{name}.lean",
        ], name.replace("/", "-"), work)
        if name in PROOFS:
            output.append(log)
    transcript = "\n".join(output)
    verifier.audit_proofs(transcript)
    count = len(re.findall(r"'[^']+' (?:depends on axioms:|does not depend on any axioms)", transcript))
    storage_output = []
    for name in STORAGE_PROOFS:
        shutil.copyfile(HERE / "lean" / f"{name}.lean", work / f"{name}.lean")
        storage_output.append(run([
            lean / "lean", "-DwarningAsError=true", "-o", f"{name}.olean", f"{name}.lean",
        ], name, work))
    audit_storage("\n".join(storage_output))
    provider_audits = {}
    expected_provider = json.loads((HERE / "provider-audits.json").read_text())["proofs"]
    for name, expected in expected_provider.items():
        source = HERE / "lean" / f"{name}.lean"
        require(str(source.relative_to(ROOT)) in input_hashes, f"Unpinned selected proof: {source}")
        require(not re.search(r"\b(?:sorry|admit|axiom|native_decide|implemented_by)\b", source.read_text()),
                f"Unchecked provider proof: {name}")
        shutil.copyfile(source, work / source.name)
        output = run([lean / "lean", "-DwarningAsError=true", "-o", f"{name}.olean", source.name], name, work)
        provider_audits[name] = provider_tools.audit(output, expected)
    baseline = provider_tools.verify_baseline(provider_manifest, generated, env, lean, run, charon, aeneas)
    provider_tools.check_tools(provider_manifest)
    provider_tools.check_unchanged(input_hashes | extracted_sources | baseline["sources"])
    require(provider_tools.inventory(overlay) == overlay_before, "Generated Lean overlay changed during proof checks")
    sources = {}
    for item in crate["files"]:
        local = item["name"].get("Local")
        if local:
            path = (HERE / "crate" / local).resolve()
            if path.is_file() and path.is_relative_to(ROOT):
                sources[str(path.relative_to(ROOT))] = digest(path)
    evidence.write_text(json.dumps({
        "scope": "shared storage extraction, core proofs, storage invariants and actual rebuild/recovery hash retention under explicit library, provider, DOM and resource contracts",
        "rust_sources": sources,
        "llbc_sha256": digest(llbc),
        "lean_sources": {
            str(path.relative_to(work)): digest(path) for path in sorted(work.rglob("*.lean"))
        },
        "aeneas_sha256": digest(aeneas),
        "charon_sha256": digest(charon),
        "core_theorems": count,
        "storage_theorems": sorted(STORAGE_THEOREMS),
        "provider_audits": provider_audits,
        "provider_tool_controls": controls,
        "baseline_equivalence": baseline,
        "verification_inputs": input_hashes,
        "lean_overlay": overlay_before,
        "storage_axioms": {name: sorted(axioms) for name, axioms in STORAGE_AUDITS.items()},
        "naming_reproducer": {
            "source_sha256": digest(HERE / "function_names.rs"),
            "model_sha256": digest(models[0]),
        },
    }, indent=2) + "\n")
    print("Shared production verification passed: 73 core + 83 adapter + 17 provider + 1 baseline equivalence.")


if __name__ == "__main__":
    main()

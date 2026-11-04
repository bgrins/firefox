#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import os
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[4]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"
LOCK = json.loads((PROJECT.parent / "toolchain.json").read_text())


def main():
    parser = argparse.ArgumentParser()
    scope_args = parser.add_mutually_exclusive_group()
    scope_args.add_argument("--simple", action="store_true")
    scope_args.add_argument("--relative", action="store_true")
    scope_args.add_argument("--matching", action="store_true")
    scope_args.add_argument("--ancestor", action="store_true")
    parser.add_argument("--monomorphize", action="store_true")
    parser.add_argument("--partial-monomorphize", action="store_true")
    parser.add_argument("--aeneas", type=Path, default=TOOLS / "aeneas/aeneas")
    parser.add_argument("--llbc-only", action="store_true")
    args = parser.parse_args()
    scope = (
        "simple"
        if args.simple
        else "relative"
        if args.relative
        else "matching"
        if args.matching
        else "ancestor"
        if args.ancestor
        else "full"
    )
    if args.monomorphize:
        scope += "-monomorphized"
    if args.partial_monomorphize:
        scope += "-partial"
    generated = PROJECT / "generated" / scope
    generated.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        RUSTUP_HOME=str(TOOLS / "rustup"),
        CARGO_HOME=str(TOOLS / "cargo"),
        RUSTUP_TOOLCHAIN=LOCK["rust_toolchain"],
    )
    charon = [
        TOOLS / "aeneas/charon",
        "cargo",
        "--preset",
        "aeneas",
        "--sysroot",
        "default",
        "--no-dedup-serialized-ast",
        "--start-from",
        "selectors::parser::collect_simple",
        "--opaque",
        "selectors::parser::_::slice",
        "--include",
        "selectors",
        "--exclude",
        "selectors::parser::NonTSPseudoClass::visit",
        "--opaque",
        "selectors::parser::NonTSPseudoClass",
        "--opaque",
        "selectors::parser::PseudoElement",
        "--opaque",
        "selectors::parser::SelectorImpl",
        "--include",
        "selectors::parser::SelectorImpl::should_collect_attr_hash",
        "--opaque",
        "selectors::visitor",
        "--opaque",
        "alloc",
        "--opaque",
        "core::fmt",
        "--opaque",
        "cssparser",
        "--opaque",
        "servo_arc",
        "--include",
        "servo_arc::ArcUnionBorrow",
        "--dest-file",
        generated / "collection.llbc",
        "--",
        "--offline",
        "--locked",
        "--manifest-path",
        PROJECT / "Cargo.toml",
        "--lib",
        "--config",
        'source.crates-io.replace-with="vendored-sources"',
        "--config",
        "source.vendored-sources.directory="
        + json.dumps(str(ROOT / "third_party/rust")),
    ]
    if args.simple or args.relative or args.matching or args.ancestor:
        charon[charon.index("--opaque") : charon.index("--opaque")] = [
            "--exclude",
            "selectors::parser::SelectorImpl::ExtraMatchingData",
            "--remove-unused-clauses",
        ]
    if args.monomorphize:
        charon.insert(charon.index("--sysroot"), "--monomorphize")
    if args.partial_monomorphize:
        charon.insert(charon.index("--sysroot"), "--monomorphize-mut=all")
    if not args.simple:
        charon[charon.index("--opaque") : charon.index("--opaque")] = [
            "--start-from",
            "selectors::parser::collect_relative_compound",
            *(
                []
                if args.relative or args.matching
                else ["--start-from", "selectors::parser::collect_ancestors"]
            ),
        ]
    if args.matching:
        charon[charon.index("--opaque") : charon.index("--opaque")] = [
            "--start-from",
            "selectors::matching::matches_local_name",
            "--opaque",
            "selectors::tree::Element",
            "--opaque",
            "selectors::context::MatchingContext",
        ]
    aeneas = [
        args.aeneas.resolve(),
        "-backend",
        "lean",
        "-namespace",
        "Collection",
        "-dest",
        generated,
        "-abort-on-error",
        "-warnings-as-errors",
        "-no-progress-bar",
        generated / "collection.llbc",
    ]
    if args.ancestor:
        aeneas.insert(aeneas.index("-dest"), "-loops-to-rec")
    clean = [
        "cargo",
        "clean",
        "-p",
        "stylo-collection-verification",
        *[arg for arg in charon[charon.index("--offline") :] if arg != "--lib"],
    ]
    commands = [("clean", clean), ("charon", charon)]
    if not args.llbc_only:
        commands.append(("aeneas", aeneas))
    for name, command in commands:
        log = generated / f"{name}.log"
        print(f"Running {name}; log: {log}", flush=True)
        with log.open("w") as output:
            result = subprocess.run(
                command,
                env=env,
                cwd=PROJECT,
                stdout=output,
                stderr=subprocess.STDOUT,
                check=False,
            )
        result.check_returncode()


if __name__ == "__main__":
    main()

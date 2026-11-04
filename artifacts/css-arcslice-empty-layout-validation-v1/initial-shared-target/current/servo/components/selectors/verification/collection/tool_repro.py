#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[4]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"
LOCK = json.loads((PROJECT.parent / "toolchain.json").read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aeneas", type=Path, default=TOOLS / "aeneas/aeneas")
    parser.add_argument("--output", type=Path, default=PROJECT / "generated/repro")
    parser.add_argument(
        "--source", type=Path, default=PROJECT / "missing_trait_repro.rs"
    )
    parser.add_argument("--generic", action="store_true")
    parser.add_argument("--loops-to-rec", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        RUSTUP_HOME=str(TOOLS / "rustup"),
        CARGO_HOME=str(TOOLS / "cargo"),
        RUSTUP_TOOLCHAIN=LOCK["rust_toolchain"],
    )
    commands = [
        (
            "charon",
            [
                TOOLS / "aeneas/charon",
                "rustc",
                "--preset",
                "aeneas",
                *([] if args.generic else ["--monomorphize"]),
                "--sysroot",
                "default",
                "--start-from",
                "missing_trait_repro::collect",
                "--dest-file",
                output / "missing_trait_repro.llbc",
                "--",
                "--crate-type",
                "lib",
                "--crate-name",
                "missing_trait_repro",
                "--edition",
                "2024",
                args.source.resolve(),
            ],
        ),
        (
            "aeneas",
            [
                args.aeneas.resolve(),
                "-backend",
                "lean",
                "-namespace",
                "Repro",
                "-dest",
                output,
                *(["-loops-to-rec"] if args.loops_to_rec else []),
                "-abort-on-error",
                "-warnings-as-errors",
                "-no-progress-bar",
                output / "missing_trait_repro.llbc",
            ],
        ),
    ]
    for name, command in commands:
        log = output / f"{name}.log"
        print(f"Running {name}; log: {log}", flush=True)
        with log.open("w") as stream:
            subprocess.run(
                command, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True
            )
    assets = LOCK["platforms"][f"{platform.system()}-{platform.machine()}"]
    lean = TOOLS / assets["lean"].removesuffix(".tar.zst") / "bin"
    env["PATH"] = str(lean) + os.pathsep + env["PATH"]
    env["LEAN_PATH"] = subprocess.check_output(
        [lean / "lake", "env", "printenv", "LEAN_PATH"],
        env=env,
        cwd=TOOLS / "aeneas/backends/lean",
        text=True,
    ).strip()
    with (output / "lean.log").open("w") as stream:
        subprocess.run(
            [lean / "lean", "-DwarningAsError=true", output / "MissingTraitRepro.lean"],
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
        )


if __name__ == "__main__":
    main()

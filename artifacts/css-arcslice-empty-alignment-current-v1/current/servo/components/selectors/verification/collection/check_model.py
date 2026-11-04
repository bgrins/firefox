#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[4]
TOOLS = ROOT / "artifacts/stylo-bloom-tools"


def audit_policy(output):
    audits = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output)
    audits += [
        (name, "")
        for name in re.findall(r"'([^']+)' does not depend on any axioms", output)
    ]
    expected = {"propext", "Classical.choice", "Quot.sound", "core.fmt.Formatter"}
    if (
        len(audits) != 1
        or audits[0][0] != "CollectionProofs.simple_component_policy"
        or set(re.split(r",\s*", audits[0][1].strip())) != expected
    ):
        raise RuntimeError(
            "Unexpected or missing production helper theorem axiom audit"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--proof-only",
        action="store_true",
        help="Development only: reuse previously compiled generated models",
    )
    args = parser.parse_args()
    lock = json.loads((PROJECT.parent / "toolchain.json").read_text())
    asset = lock["platforms"][f"{platform.system()}-{platform.machine()}"]["lean"]
    lean = TOOLS / asset.removesuffix(".tar.zst") / "bin"
    generated = PROJECT / "generated"
    model = generated / "Normalized"
    env = dict(os.environ)
    env["PATH"] = str(lean) + os.pathsep + env["PATH"]
    dependencies = subprocess.check_output(
        [lean / "lake", "env", "printenv", "LEAN_PATH"],
        env=env,
        cwd=TOOLS / "aeneas/backends/lean",
        text=True,
    ).strip()
    env["LEAN_PATH"] = str(generated) + os.pathsep + dependencies
    for name in [] if args.proof_only else ["TypesExternal", "FunsExternal"]:
        shutil.copyfile(PROJECT / "lean" / f"{name}.lean", model / f"{name}.lean")
    for name in (
        [] if args.proof_only else ["TypesExternal", "Types", "FunsExternal", "Funs"]
    ):
        subprocess.run(
            [
                lean / "lean",
                "-DwarningAsError=true",
                "-R",
                generated,
                "-o",
                model / f"{name}.olean",
                model / f"{name}.lean",
            ],
            env=env,
            cwd=generated,
            check=True,
        )
    result = subprocess.run(
        [lean / "lean", "-DwarningAsError=true", PROJECT / "lean/ComponentProofs.lean"],
        env=env,
        cwd=generated,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )
    print(result.stdout, end="")
    audit_policy(result.stdout)


if __name__ == "__main__":
    main()

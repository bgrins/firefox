# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
from pathlib import Path

import provider_tools

HERE = Path(__file__).resolve().parent


def verify(generated, lean, run, charon, aeneas):
    source = HERE / "provider-tools/controls"
    expected = json.loads((source / "expected.json").read_text())
    results = {}
    for name, stages in expected.items():
        work = generated / "controls" / name
        work.mkdir(parents=True)
        llbc = work / "control.llbc"
        command = [charon, "rustc", "--preset", "aeneas", "--sysroot", "default",
                   "--monomorphize-mut=except-types", "--remove-adt-clauses",
                   "--lift-associated-types", "*", "--start-from", "closure_control::invoke"]
        for opaque in stages["opaque"]:
            command += ["--opaque", f"closure_control::{opaque}"]
        command += ["--dest-file", llbc, "--", "--crate-type", "lib", "--crate-name",
                    "closure_control", "--edition", "2024", source / f"{name}.rs"]
        run(command, f"control-{name}-charon", work)
        sources = provider_tools.check_source(json.loads(llbc.read_text()), work)
        run([aeneas, "-backend", "lean", "-namespace", "Control", "-dest", work,
             "-abort-on-error", "-warnings-as-errors", "-no-progress-bar", llbc],
            f"control-{name}-aeneas", work)
        models = list(work.glob("*.lean"))
        provider_tools.require(len(models) == 1, f"Expected one fresh control model: {name}")
        run([lean / "lean", "-DwarningAsError=true", models[0]], f"control-{name}-lean", work)
        actual = {"charon": 0, "aeneas": 0, "lean": 0}
        provider_tools.require(actual == {key: stages[key] for key in actual}, f"Unexpected control result: {name}")
        results[name] = {"stages": actual, "sources": sources,
                         "model_sha256": provider_tools.digest(models[0])}
    return results

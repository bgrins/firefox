# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from mozbuild.util import FileAvoidWrite


def wasm2c(output, wasm2c_bin, wasm_lib, *flags):
    target = Path(output.name)
    with TemporaryDirectory() as tmp:
        generated = Path(tmp)
        result = subprocess.run(
            [
                wasm2c_bin,
                "-n",
                Path(wasm_lib).stem,
                *flags,
                "-o",
                generated / target.name,
                wasm_lib,
            ],
            check=False,
        )
        if result.returncode:
            return result.returncode
        for path in generated.iterdir():
            if path.name == target.name:
                output.write(path.read_bytes())
            else:
                with FileAvoidWrite(target.with_name(path.name), readmode="rb") as side:
                    side.write(path.read_bytes())
    return 0

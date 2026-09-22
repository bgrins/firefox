# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Assemble an iOS bundle from an IOS_BUNDLES spec and sign it ad hoc, as Xcode
# does for the Simulator. Nested code is signed before the bundle containing
# it, because a bundle's signature covers the signatures of everything inside.

import json
import os
import shutil
import subprocess
import sys

MACHO_MAGICS = {
    b"\xcf\xfa\xed\xfe",
    b"\xce\xfa\xed\xfe",
    b"\xca\xfe\xba\xbe",
}
NESTED_CODE_DIRS = ("Frameworks", "Extensions")
BUNDLE_SUFFIXES = (".app", ".appex", ".framework")


def _is_macho(path):
    with open(path, "rb") as fh:
        return fh.read(4) in MACHO_MAGICS


def codesign(path):
    subprocess.run(
        ["codesign", "--force", "--sign", "-", "--timestamp=none", path],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def sign_bundle(bundle, sign=codesign):
    for name in NESTED_CODE_DIRS:
        nested_dir = os.path.join(bundle, name)
        if not os.path.isdir(nested_dir):
            continue
        for entry in sorted(os.listdir(nested_dir)):
            path = os.path.join(nested_dir, entry)
            if entry.endswith(BUNDLE_SUFFIXES):
                sign_bundle(path, sign)
            elif os.path.isfile(path) and _is_macho(path):
                sign(path)
    sign(bundle)


def main(argv):
    with open(argv[0], encoding="utf-8") as fh:
        spec = json.load(fh)

    bundle = spec["bundle"]
    # Start from scratch so nothing from a previous build lingers in the
    # bundle, where it would be signed along with the rest.
    shutil.rmtree(bundle, ignore_errors=True)

    for source, dest in spec["files"]:
        target = os.path.join(bundle, dest)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)
        shutil.copymode(source, target)

    excludes = [arg for pattern in spec["excludes"] for arg in ("--exclude", pattern)]
    for source, dest in spec["trees"]:
        target = os.path.join(bundle, dest)
        os.makedirs(target, exist_ok=True)
        subprocess.run(
            ["rsync", "-rtpL", *excludes, source + "/", target + "/"], check=True
        )

    sign_bundle(bundle)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

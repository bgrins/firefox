# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import shutil
import subprocess
import unittest
from tempfile import mkdtemp
from unittest import mock

import mozunit

from mozbuild.action import assemble_ios_bundle

MACHO = b"\xcf\xfa\xed\xfe"


@unittest.skipIf(not shutil.which("rsync"), "rsync is required")
class TestAssembleIOSBundle(unittest.TestCase):
    def setUp(self):
        self.tmpdir = mkdtemp()
        self.bundle = os.path.join(self.tmpdir, "Test.app")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _write(self, path, content=b""):
        full = os.path.join(self.tmpdir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(content)
        return full

    def _assemble(self, spec):
        spec_path = self._write("spec.json", json.dumps(spec).encode())
        signed = []
        run = subprocess.run

        def fake_run(cmd, **kwargs):
            if cmd[0] == "codesign":
                signed.append(os.path.relpath(cmd[-1], self.tmpdir))
                return None
            return run(cmd, **kwargs)

        with mock.patch.object(assemble_ios_bundle.subprocess, "run", fake_run):
            assemble_ios_bundle.main([spec_path])
        return signed

    def test_signs_nested_code_first(self):
        spec = {
            "bundle": self.bundle,
            "files": [
                [self._write("bin/Test", MACHO), "Test"],
                [self._write("bin/Lib", MACHO), "Frameworks/Lib.framework/Lib"],
                [self._write("bin/Ext", MACHO), "Extensions/Ext.appex/Ext"],
            ],
            "trees": [[os.path.join(self.tmpdir, "dist"), "Frameworks/Lib.framework"]],
            "excludes": ["test_*"],
        }
        self._write("dist/Frameworks/libdep.dylib", MACHO)
        self._write("dist/Frameworks/test_dep", MACHO)
        self._write("dist/Frameworks/prefs.js", b"pref();")

        signed = self._assemble(spec)

        self.assertEqual(
            signed,
            [
                "Test.app/Frameworks/Lib.framework/Frameworks/libdep.dylib",
                "Test.app/Frameworks/Lib.framework",
                "Test.app/Extensions/Ext.appex",
                "Test.app",
            ],
        )
        self.assertFalse(
            os.path.exists(
                os.path.join(
                    self.bundle, "Frameworks/Lib.framework/Frameworks/test_dep"
                )
            )
        )

    def test_removes_previous_contents(self):
        self._write("Test.app/Stale.nib")
        spec = {
            "bundle": self.bundle,
            "files": [[self._write("bin/Test", MACHO), "Test"]],
            "trees": [],
            "excludes": [],
        }

        self._assemble(spec)

        self.assertEqual(os.listdir(self.bundle), ["Test"])


if __name__ == "__main__":
    mozunit.main()

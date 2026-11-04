#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import tempfile
import unittest
from pathlib import Path

import provider_tools


class ProofAuditTests(unittest.TestCase):
    def setUp(self):
        self.expected = {"proof": ["propext", "Quot.sound"]}
        self.output = "'proof' depends on axioms: [propext, Quot.sound]"

    def test_accepts_expected(self):
        provider_tools.audit(self.output, self.expected)

    def test_rejects_duplicate(self):
        with self.assertRaises(RuntimeError):
            provider_tools.audit(self.output + "\n" + self.output, self.expected)

    def test_rejects_missing(self):
        with self.assertRaises(RuntimeError):
            provider_tools.audit("", self.expected)

    def test_rejects_extra_axiom_free(self):
        with self.assertRaises(RuntimeError):
            provider_tools.audit(self.output + "\n'extra' does not depend on any axioms", self.expected)

    def test_rejects_extra_axiom(self):
        with self.assertRaises(RuntimeError):
            provider_tools.audit(self.output.replace("]", ", sorryAx]"), self.expected)

    def test_rejects_duplicate_axiom(self):
        with self.assertRaises(RuntimeError):
            provider_tools.audit(self.output.replace("]", ", propext]"), self.expected)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.library = self.root / "library"
        self.library.mkdir()
        self.original = self.root / "original.olean"
        self.original.write_text("compiled")
        self.link = self.library / "Module.olean"
        self.link.symlink_to(self.original)
        self.before = provider_tools.inventory(self.library)

    def test_accepts_unchanged(self):
        self.assertEqual(self.before, provider_tools.inventory(self.library))

    def test_detects_shadow(self):
        (self.library / "Aeneas.olean").write_text("shadow")
        self.assertNotEqual(self.before, provider_tools.inventory(self.library))

    def test_detects_companion(self):
        (self.library / "Module.olean.private").write_text("extra")
        self.assertNotEqual(self.before, provider_tools.inventory(self.library))

    def test_detects_retarget(self):
        other = self.root / "other.olean"
        other.write_bytes(self.original.read_bytes())
        self.link.unlink()
        self.link.symlink_to(other)
        self.assertNotEqual(self.before, provider_tools.inventory(self.library))

    def test_rejects_directory_cycle(self):
        (self.library / "cycle").symlink_to(self.library, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            provider_tools.inventory(self.library)


class EmbeddedErrorsTests(unittest.TestCase):
    def test_rejects_errors_or_missing_status(self):
        for data in [{}, {"has_errors": True}]:
            with self.assertRaises(RuntimeError):
                provider_tools.check_source(data, Path.cwd())

    def test_expected_provider_theorem_count(self):
        data = json.loads((provider_tools.HERE / "provider-audits.json").read_text())
        self.assertEqual(sum(map(len, data["proofs"].values())), 17)
        self.assertEqual(len(data["baseline"]), 1)


if __name__ == "__main__":
    unittest.main()

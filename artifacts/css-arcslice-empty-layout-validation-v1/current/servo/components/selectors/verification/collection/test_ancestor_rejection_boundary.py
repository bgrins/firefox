#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import unittest

import ancestor_rejection_boundary as boundary
import test_rejection_boundary as common
from normalize import UnsupportedShape


def transcript():
    return "\n".join(f"'{name}' depends on axioms: [{', '.join(sorted(axioms))}]"
                     for name, axioms in boundary.expected_audits().items())


class AuditTests(unittest.TestCase):
    def test_exact_reports(self):
        self.assertEqual(len(boundary.expected_audits()), 90)
        boundary.audit_combined(transcript())

    def test_missing_duplicate_unrelated_reports(self):
        text = transcript()
        lines = text.splitlines()
        for changed in ["\n".join(lines[:-1]), text + "\n" + lines[0],
                        text + "\n'extra' does not depend on any axioms",
                        text.replace("ancestor_collection_no_rejection", "local_name_no_false_rejection")]:
            with self.subTest(changed=changed), self.assertRaises(UnsupportedShape):
                boundary.audit_combined(changed)

    def test_forbidden_behavioral_axioms(self):
        for axiom in ["sorryAx", "Lean.ofReduceBool", "AncestorContracts.collector_soundness",
                      "context.MatchingContext", "core.ptr.non_null.NonNull"]:
            with self.subTest(axiom=axiom), self.assertRaisesRegex(UnsupportedShape, "Unexpected axioms"):
                boundary.audit_combined(transcript().replace("[", f"[{axiom}, ", 1))


class SourceInventoryTests(common.SourceInventoryTests):
    scope = "ancestor"


class FreshnessTests(common.FreshnessTests):
    scope = "ancestor"
    target = "ancestor-rejection"


if __name__ == "__main__":
    unittest.main()

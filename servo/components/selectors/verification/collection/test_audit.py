#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import unittest

from check_model import audit_policy


class PolicyAuditTests(unittest.TestCase):
    output = (
        "'CollectionProofs.simple_component_policy' depends on axioms: "
        "[propext,\n Classical.choice,\n Quot.sound,\n core.fmt.Formatter]\n"
    )

    def test_exact_audit(self):
        audit_policy(self.output)

    def test_rejects_missing_duplicate_and_wrong_theorem(self):
        for text in [
            "",
            self.output * 2,
            self.output.replace("simple_component_policy", "other"),
        ]:
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                audit_policy(text)

    def test_rejects_unexpected_dependencies(self):
        for axiom in ["sorryAx", "collector_soundness", "native_decide_axiom"]:
            with self.subTest(axiom=axiom), self.assertRaises(RuntimeError):
                audit_policy(self.output.replace("Quot.sound", axiom))

    def test_rejects_extra_theorem_reports(self):
        for extra in [
            "'CollectionProofs.other' depends on axioms: [sorryAx]\n",
            "'CollectionProofs.other' does not depend on any axioms\n",
        ]:
            with self.subTest(extra=extra), self.assertRaises(RuntimeError):
                audit_policy(self.output + extra)


if __name__ == "__main__":
    unittest.main()

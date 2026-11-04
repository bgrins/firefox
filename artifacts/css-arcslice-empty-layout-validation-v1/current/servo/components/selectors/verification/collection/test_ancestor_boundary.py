#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ancestor_boundary
import relative_boundary
import verify_relative
from normalize import UnsupportedShape

SOURCE = json.loads(Path(sys.argv.pop(1)).read_text())
OUTPUT = verify_relative.PROJECT / "generated/ancestor/model/Normalized"


class AncestorBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.source = copy.deepcopy(SOURCE)

    def test_current_boundary(self):
        ancestor_boundary.audit_boundary(self.source, OUTPUT)
        text = "\n".join(f"'{name}' depends on axioms: [{', '.join(sorted(axioms))}]" for name, axioms in ancestor_boundary.AUDITS.items())
        ancestor_boundary.audit_axioms(text)
        with self.assertRaises(UnsupportedShape):
            ancestor_boundary.audit_axioms(text + "\n'extra' does not depend on any axioms")
        with self.assertRaises(UnsupportedShape):
            ancestor_boundary.audit_axioms(text.replace("propext", "sorryAx", 1))

    def test_exact_audit_records(self):
        records = [f"'{name}' depends on axioms: [{', '.join(sorted(axioms))}]" for name, axioms in ancestor_boundary.AUDITS.items()]
        for invalid in [records[:-1], records + [records[0]], records + ["'extra' does not depend on any axioms"],
                        [record.replace("propext", "Lean.ofReduceBool") for record in records],
                        [record.replace("propext", "AncestorContracts.collector_soundness") for record in records]]:
            with self.subTest(invalid=invalid[-1]), self.assertRaises(UnsupportedShape):
                ancestor_boundary.audit_axioms("\n".join(invalid))

    def test_missing_ancestor_bodies(self):
        for path in ancestor_boundary.BODIES:
            with self.subTest(path=path):
                source = copy.deepcopy(SOURCE)
                fun = next(fun for fun in source["translated"]["fun_decls"] if fun and fun["item_meta"]["name"] == relative_boundary.identifiers(*path))
                fun["body"] = {"Unexpected": {}}
                with self.assertRaisesRegex(UnsupportedShape, "matching body"):
                    ancestor_boundary.audit_boundary(source, OUTPUT)

    def test_new_opaque_ancestor_function(self):
        fun = next(fun for fun in self.source["translated"]["fun_decls"] if fun and fun["item_meta"]["name"] == relative_boundary.identifiers(*ancestor_boundary.BODIES[0]))
        fun["body"] = "Opaque"
        with self.assertRaisesRegex(UnsupportedShape, "only SelectorList"):
            ancestor_boundary.audit_boundary(self.source, OUTPUT)

    def test_missing_ancestor_root(self):
        self.source["translated"]["options"]["start_from"].remove("selectors::parser::collect_ancestors")
        with self.assertRaisesRegex(UnsupportedShape, "roots"):
            ancestor_boundary.audit_boundary(self.source, OUTPUT)

    def test_ancestor_source_drift(self):
        real_digest = relative_boundary.digest
        def changed(path):
            return "changed" if path.name == "parser.rs" else real_digest(path)
        with patch.object(relative_boundary, "digest", side_effect=changed):
            with self.assertRaisesRegex(UnsupportedShape, "source requires review"):
                ancestor_boundary.audit_boundary(self.source, OUTPUT)

    def test_external_type_or_accessor_drift(self):
        for template in ["TypesExternal_Template.lean", "FunsExternal_Template.lean"]:
            with self.subTest(template=template), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                for name in ["TypesExternal_Template.lean", "FunsExternal_Template.lean"]:
                    text = (OUTPUT / name).read_text()
                    if name == template:
                        text += "\naxiom unreviewed_behavior : False\n"
                    (output / name).write_text(text)
                with self.assertRaisesRegex(UnsupportedShape, "boundary changed"):
                    ancestor_boundary.audit_boundary(self.source, output)

    def test_failed_provenance_removes_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            evidence = project / "generated/ancestor/evidence.json"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("stale")
            with patch.object(verify_relative, "PROJECT", project), patch.object(verify_relative, "validate_tools", side_effect=RuntimeError("changed tool")):
                with self.assertRaisesRegex(RuntimeError, "changed tool"):
                    verify_relative.main("ancestor")
            self.assertFalse(evidence.exists())

    def test_failed_extraction_removes_source_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            generated = project / "generated/ancestor"
            generated.mkdir(parents=True)
            stale = [generated / name for name in ["collection.llbc", "normalized.llbc", "normalization-report.json"]]
            for path in stale:
                path.write_text("stale")
            with patch.object(verify_relative, "PROJECT", project), patch.object(verify_relative, "TOOLS", project), patch.object(verify_relative, "validate_tools", return_value=project / "tool"), patch.object(verify_relative.subprocess, "run", side_effect=RuntimeError("extraction failed")):
                with self.assertRaisesRegex(RuntimeError, "extraction failed"):
                    verify_relative.main("ancestor")
            self.assertTrue(all(not path.exists() for path in stale))


if __name__ == "__main__":
    unittest.main()

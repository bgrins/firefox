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

import relative_boundary
import verify_helper
import verify_relative
from normalize import UnsupportedShape
from relative_boundary import (
    AUDITS,
    audit_axioms,
    audit_boundary,
    audit_source,
    identifiers,
)

SOURCE = json.loads(Path(sys.argv.pop(1)).read_text())


def transcript():
    return "\n".join(f"'{name}' depends on axioms: [{', '.join(sorted(axioms))}]" for name, axioms in AUDITS.items())


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.source = copy.deepcopy(SOURCE)

    def test_current_boundary_and_exact_audits(self):
        audit_source(self.source)
        audit_axioms(transcript())

    def test_opaque_receiver_identity(self):
        decl = audit_source(self.source)
        adt = decl["item_meta"]["name"][2]["Impl"]["Ty"]["skip_binder"]["Untagged"]["Adt"]
        other = next(t for t in self.source["translated"]["type_decls"] if t and t["item_meta"]["name"] == identifiers("selectors", "parser", "Selector"))
        adt["id"] = other["def_id"]
        with self.assertRaisesRegex(UnsupportedShape, "receiver type"):
            audit_source(self.source)

    def test_new_opaque_local_method(self):
        decl = copy.deepcopy(audit_source(self.source))
        decl["item_meta"]["name"][-1] = {"Ident": ["other_method", 0]}
        self.source["translated"]["fun_decls"].append(decl)
        with self.assertRaisesRegex(UnsupportedShape, "only SelectorList"):
            audit_source(self.source)

    def test_collector_body_missing(self):
        for decl in self.source["translated"]["fun_decls"]:
            if decl and decl["item_meta"]["name"] == identifiers("selectors", "parser", "collect_selector_hashes"):
                decl["body"] = {"Unexpected": {}}
        with self.assertRaisesRegex(UnsupportedShape, "body became opaque"):
            audit_source(self.source)

    def test_transmute_retained(self):
        decl = copy.deepcopy(audit_source(self.source))
        decl["item_meta"]["name"] = identifiers("core", "intrinsics", "transmute")
        self.source["translated"]["fun_decls"].append(decl)
        with self.assertRaisesRegex(UnsupportedShape, "transmute"):
            audit_source(self.source)

    def test_extraction_scope_and_pruning(self):
        for field, value in [("remove_unused_clauses", False), ("start_from", ["other"])]:
            with self.subTest(field=field):
                source = copy.deepcopy(SOURCE)
                source["translated"]["options"][field] = value
                with self.assertRaises(UnsupportedShape):
                    audit_source(source)

    def test_missing_duplicate_and_wrong_audits(self):
        text = transcript()
        for changed in ["", text + "\n" + text, text.replace("next_in_bounds", "unrelated"), text + "\n'extra' does not depend on any axioms"]:
            with self.subTest(changed=changed):
                with self.assertRaises(UnsupportedShape):
                    audit_axioms(changed)

    def test_extra_axiom(self):
        for axiom in ["sorryAx", "native_decide", "collector_soundness"]:
            with self.subTest(axiom=axiom):
                text = transcript().replace("[", f"[{axiom}, ", 1)
                with self.assertRaisesRegex(UnsupportedShape, "Unexpected axioms"):
                    audit_axioms(text)


class RepresentationDriftTests(unittest.TestCase):
    def setUp(self):
        self.source = copy.deepcopy(SOURCE)
        self.output = verify_helper.PROJECT / "generated/relative/model/Normalized"

    def test_changed_slice_observation(self):
        audit_source(self.source)["item_meta"]["source_text"] += "changed contract"
        with self.assertRaisesRegex(UnsupportedShape, "slice representation contract"):
            audit_boundary(self.source, self.output)

    def test_changed_representation_source(self):
        with patch.object(relative_boundary, "digest", return_value="changed"):
            with self.assertRaisesRegex(UnsupportedShape, "Representation source requires review"):
                audit_boundary(self.source, self.output)

    def test_changed_external_declaration(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for name in ["TypesExternal_Template.lean", "FunsExternal_Template.lean"]:
                text = (self.output / name).read_text()
                if name == "FunsExternal_Template.lean":
                    text += "\naxiom extra_function : Nat\n"
                (output / name).write_text(text)
            with self.assertRaisesRegex(UnsupportedShape, "External declaration boundary changed"):
                audit_boundary(self.source, output)


class FreshnessTests(unittest.TestCase):
    def test_previous_success_removed_before_provenance_failure(self):
        for module, relative in [(verify_helper, "generated/helper-evidence.json"),
                                 (verify_relative, "generated/relative/evidence.json")]:
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                evidence = project / relative
                evidence.parent.mkdir(parents=True)
                evidence.write_text("stale success")
                with patch.object(module, "PROJECT", project), patch.object(module, "validate_tools", side_effect=RuntimeError("changed tool")):
                    with self.assertRaisesRegex(RuntimeError, "changed tool"):
                        module.main()
                self.assertFalse(evidence.exists())

    def test_previous_llbc_removed_before_failed_extraction(self):
        for module, scope in [(verify_helper, "simple"), (verify_relative, "relative")]:
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                generated = project / "generated" / scope
                generated.mkdir(parents=True)
                stale = [generated / name for name in ["collection.llbc", "normalized.llbc", "normalization-report.json"]]
                for path in stale:
                    path.write_text("stale")
                with patch.object(module, "PROJECT", project), patch.object(module, "TOOLS", project), patch.object(module, "validate_tools", return_value=project / "tool"), patch.object(module.subprocess, "run", side_effect=RuntimeError("extraction failed")):
                    with self.assertRaisesRegex(RuntimeError, "extraction failed"):
                        module.main()
                self.assertTrue(all(not path.exists() for path in stale))


if __name__ == "__main__":
    unittest.main()

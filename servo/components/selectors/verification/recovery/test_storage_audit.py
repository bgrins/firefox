#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_storage
from verify_storage import audit_source


class SourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.crate = copy.deepcopy(SOURCE)

    def wrapper(self):
        return next(
            function for function in self.crate["fun_decls"]
            if function and function["item_meta"]["name"] == [
                {"Ident": ["stylo_bloom_verification", 0]},
                {"Ident": ["storage_hash", 0]},
            ]
        )

    def test_accepts_production_bodies(self):
        audit_source(self.crate)

    def test_rejects_opaque_wrapper(self):
        self.wrapper()["body"] = "Opaque"
        with self.assertRaisesRegex(RuntimeError, "no extracted body"):
            audit_source(self.crate)

    def test_rejects_missing_wrapper(self):
        self.crate["fun_decls"].remove(self.wrapper())
        with self.assertRaisesRegex(RuntimeError, "storage entry point"):
            audit_source(self.crate)

    def test_rejects_duplicate_wrapper(self):
        self.crate["fun_decls"].append(copy.deepcopy(self.wrapper()))
        with self.assertRaisesRegex(RuntimeError, "storage entry point"):
            audit_source(self.crate)

    def test_rejects_missing_insertion_body(self):
        self.crate["fun_decls"] = [
            function for function in self.crate["fun_decls"]
            if not function or function["item_meta"]["name"][-1] != {"Ident": ["push_hash", 0]}
        ]
        with self.assertRaisesRegex(RuntimeError, "storage method"):
            audit_source(self.crate)

    def test_rejects_copied_storage_source(self):
        source = next(
            item for item in self.crate["files"]
            if item["name"].get("Local", "").endswith("style/bloom_storage.rs")
        )
        source["name"] = {"Local": "copied_storage.rs"}
        with self.assertRaisesRegex(RuntimeError, "production source"):
            audit_source(self.crate)

    def test_failed_provenance_removes_prior_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            here = Path(directory)
            evidence = here / "generated/combined/evidence.json"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("previous success")
            for name in ("tool-patch.json", "storage-tool.json"):
                shutil.copyfile(verify_storage.HERE / name, here / name)
            with patch.object(verify_storage, "HERE", here):
                with patch.object(verify_storage, "digest", side_effect=RuntimeError("changed tool")):
                    with self.assertRaisesRegex(RuntimeError, "changed tool"):
                        verify_storage.main()
            self.assertFalse(evidence.exists())


class ProofAuditTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            f"'{name}' depends on axioms: [{', '.join(sorted(verify_storage.STORAGE_AUDITS[name]))}]"
            for name in sorted(verify_storage.STORAGE_THEOREMS)
        ]

    def test_accepts_expected_reports(self):
        verify_storage.audit_storage("\n".join(self.records))

    def test_rejects_missing_report(self):
        with self.assertRaises(RuntimeError):
            verify_storage.audit_storage("\n".join(self.records[1:]))

    def test_rejects_duplicate_report(self):
        self.records[-1] = self.records[0]
        with self.assertRaises(RuntimeError):
            verify_storage.audit_storage("\n".join(self.records))

    def test_rejects_extra_axiom_free_report(self):
        self.records.append("'extra' does not depend on any axioms")
        with self.assertRaises(RuntimeError):
            verify_storage.audit_storage("\n".join(self.records))

    def test_rejects_unexpected_axiom(self):
        self.records[0] = self.records[0].replace("]", ", sorryAx]")
        with self.assertRaises(RuntimeError):
            verify_storage.audit_storage("\n".join(self.records))


if __name__ == "__main__":
    SOURCE = json.loads(Path(sys.argv.pop(1)).read_text())["translated"]
    unittest.main()

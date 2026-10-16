#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import copy
import json
import sys
import unittest
from pathlib import Path

from normalize import UnsupportedShape, normalize, walk

SOURCE = json.loads(Path(sys.argv.pop(1)).read_text())


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.source = copy.deepcopy(SOURCE)
        self.decl = next(
            decl
            for decl in self.source["translated"]["trait_decls"]
            if decl
            and any(
                slot and slot["skip_binder"]["name"] == "ExtraMatchingData"
                for slot in decl["types"]
            )
        )

    def test_only_reported_fields_change(self):
        snapshot = copy.deepcopy(self.source)
        result, report = normalize(self.source)
        self.assertEqual(self.source, snapshot)
        self.assertGreaterEqual(len(report["changes"]), 1)
        for change in report["changes"]:
            target = snapshot
            for key in change["path"][:-1]:
                target = target[key]
            self.assertEqual(target[change["path"][-1]], change["old"])
            target[change["path"][-1]] = change["new"]
        self.assertEqual(snapshot, result)

    def test_rejects_live_projection_in_every_declaration_table(self):
        bound = self.decl["types"][0]["skip_binder"]["implied_clauses"][0]
        projection = next(
            value
            for _, value in walk(bound)
            if isinstance(value, dict) and "TraitType" in value
        )
        for table in [
            "fun_decls",
            "global_decls",
            "type_decls",
            "trait_decls",
            "trait_impls",
        ]:
            with self.subTest(table=table):
                source = copy.deepcopy(self.source)
                declaration = next(item for item in source["translated"][table] if item)
                declaration["generics"]["trait_type_constraints"].append({
                    "type": {"Untagged": copy.deepcopy(projection)}
                })
                with self.assertRaisesRegex(UnsupportedShape, "Retained SelectorImpl"):
                    normalize(source)

    def test_rejects_unknown_declaration_table(self):
        self.source["translated"]["future_decls"] = []
        with self.assertRaisesRegex(UnsupportedShape, "translated schema"):
            normalize(self.source)

    def test_rejects_unknown_root_field(self):
        self.source["future_decls"] = []
        with self.assertRaisesRegex(UnsupportedShape, "root schema"):
            normalize(self.source)

    def test_rejects_declaration_index_mismatch(self):
        self.decl["def_id"] += 1
        with self.assertRaisesRegex(UnsupportedShape, "index mismatch"):
            normalize(self.source)

    def test_rejects_live_bound_reference(self):
        function = next(fn for fn in self.source["translated"]["fun_decls"] if fn)
        function["generics"]["trait_clauses"].append({"ItemClause": [0, 0, 0]})
        with self.assertRaisesRegex(UnsupportedShape, "bound reference"):
            normalize(self.source)

    def test_rejects_deduplication(self):
        self.source["translated"]["fun_decls"].append({"Deduplicated": 0})
        with self.assertRaisesRegex(UnsupportedShape, "Deduplicated"):
            normalize(self.source)

    def test_rejects_changed_declaration(self):
        self.decl["types"][0]["skip_binder"]["name"] = "OtherData"
        with self.assertRaisesRegex(UnsupportedShape, "name or default"):
            normalize(self.source)

    def test_rejects_additional_associated_type(self):
        self.decl["types"][1] = copy.deepcopy(self.decl["types"][0])
        with self.assertRaisesRegex(UnsupportedShape, "Other associated types"):
            normalize(self.source)

    def test_names_in_text_are_not_projections(self):
        function = next(fn for fn in self.source["translated"]["fun_decls"] if fn)
        function["item_meta"]["source_text"] = "ExtraMatchingData"
        normalize(self.source)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import copy
import hashlib
import json
from pathlib import Path


class UnsupportedShape(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise UnsupportedShape(message)


def walk(value, path=()):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, (*path, index))


def normalize(original):
    require(
        set(original) == {"charon_version", "translated", "has_errors"},
        "Unexpected root schema",
    )
    require(
        set(original["translated"])
        == {
            "crate_name",
            "options",
            "target_information",
            "runtime_checks",
            "files",
            "item_names",
            "assoc_item_names",
            "short_names",
            "type_decls",
            "fun_decls",
            "global_decls",
            "trait_decls",
            "trait_impls",
            "ordered_decls",
        },
        "Unexpected translated schema",
    )
    require(original["charon_version"] == "0.1.287", "Unsupported Charon version")
    require(original["has_errors"] is False, "Extraction contains errors")
    for path, value in walk(original):
        require(
            not isinstance(value, dict) or "Deduplicated" not in value,
            f"Deduplicated input at {path}",
        )
    result = copy.deepcopy(original)
    translated = result["translated"]
    tables = ["type_decls", "fun_decls", "global_decls", "trait_decls", "trait_impls"]
    for table in tables:
        for index, item in enumerate(translated[table]):
            require(
                item is None or item["def_id"] == index,
                f"Declaration index mismatch in {table}",
            )
    expected_name = [
        {"Ident": [part, 0]} for part in ["selectors", "parser", "SelectorImpl"]
    ]
    matches = [
        decl
        for decl in translated["trait_decls"]
        if decl and decl["item_meta"]["name"] == expected_name
    ]
    require(len(matches) == 1, "Expected one SelectorImpl declaration")
    decl = matches[0]
    trait_id = decl["def_id"]
    require(len(decl["types"]) == 10, "Unexpected SelectorImpl associated-type slots")
    require(
        all(slot is None for slot in decl["types"][1:]), "Other associated types remain"
    )
    slot = decl["types"][0]
    require(slot is not None, "Expected ExtraMatchingData in slot zero")
    require(
        set(slot) == {"params", "skip_binder", "kind"}, "Unexpected declaration binder"
    )
    require(
        slot["kind"] == {"TraitType": [trait_id, 0]},
        "Unexpected associated-type identity",
    )
    params = slot["params"]
    require(
        len(params["regions"]) == 1 and params["regions"][0]["index"] == 0,
        "Expected one lifetime parameter",
    )
    require(
        all(value == [] for key, value in params.items() if key != "regions"),
        "Unexpected associated-type parameters or constraints",
    )
    body = slot["skip_binder"]
    require(
        set(body) == {"name", "attr_info", "default", "implied_clauses"},
        "Unexpected associated type",
    )
    require(
        body["name"] == "ExtraMatchingData" and body["default"] is None,
        "Unexpected associated-type name or default",
    )
    require(len(body["implied_clauses"]) == 1, "Expected only the Default bound")
    bound = body["implied_clauses"][0]
    default_ref = bound["trait_"]["skip_binder"]
    default_decl = translated["trait_decls"][default_ref["id"]]
    require(
        default_decl["item_meta"]["name"]
        == [
            {"Ident": ["core", 0]},
            {"Ident": ["default", 0]},
            {"Ident": ["Default", 0]},
        ],
        "Unexpected associated-type bound",
    )
    projections = [
        value["TraitType"]
        for _, value in walk(bound)
        if isinstance(value, dict) and "TraitType" in value
    ]
    require(len(projections) == 1, "Unexpected Default-bound projection")
    projection = projections[0]
    require(
        len(projection) == 3 and projection[1] == 0,
        "Unexpected Default-bound associated-type index",
    )
    require(
        projection[0]["Untagged"]["kind"] == "SelfId"
        and projection[0]["Untagged"]["trait_decl_ref"]["skip_binder"]["id"]
        == trait_id,
        "Default bound does not refer to this associated type",
    )

    removed = []

    def erase(table, item):
        removed.append({
            "path": ["translated", table, item["def_id"], "types", 0],
            "old": copy.deepcopy(item["types"][0]),
            "new": None,
        })
        item["types"][0] = None

    erase("trait_decls", decl)
    for impl in translated["trait_impls"]:
        if not impl or impl["impl_trait"]["id"] != trait_id:
            continue
        require(
            not impl["is_negative"] and not impl["is_unsafe"],
            "Unexpected implementation",
        )
        require(
            len(impl["types"]) == 10
            and all(slot is None for slot in impl["types"][1:]),
            "Unexpected implementation associated types",
        )
        impl_slot = impl["types"][0]
        require(
            impl_slot is not None
            and set(impl_slot) == {"params", "skip_binder", "kind"},
            "Unexpected implementation binder",
        )
        require(
            impl_slot["kind"] == {"TraitType": [trait_id, 0]}
            and impl_slot["params"] == params,
            "Unexpected implementation associated-type identity",
        )
        require(
            set(impl_slot["skip_binder"]) == {"value", "implied_trait_refs"},
            "Unexpected implementation value",
        )
        erase("trait_impls", impl)

    for table in tables:
        for path, value in walk(translated[table], ("translated", table)):
            if isinstance(value, dict):
                require(
                    "ItemClause" not in value,
                    f"Retained associated-type bound reference at {path}",
                )
                if "TraitType" in value:
                    projection = value["TraitType"]
                    if len(projection) == 2 and all(
                        isinstance(i, int) for i in projection
                    ):
                        owner = projection[0]
                    else:
                        require(
                            len(projection) == 3 and isinstance(projection[0], dict),
                            f"Unexpected associated-type projection at {path}",
                        )
                        owner = projection[0]["Untagged"]["trait_decl_ref"][
                            "skip_binder"
                        ]["id"]
                    require(
                        owner != trait_id,
                        f"Retained SelectorImpl associated-type projection at {path}",
                    )
    replay = copy.deepcopy(original)
    for edit in removed:
        target = replay
        for key in edit["path"][:-1]:
            target = target[key]
        require(target[edit["path"][-1]] == edit["old"], "Transformation path mismatch")
        target[edit["path"][-1]] = None
    require(replay == result, "Unexpected transformation outside reported fields")
    return result, {
        "transformation": "erase-unused-SelectorImpl-ExtraMatchingData",
        "changes": removed,
        "checked_tables": tables,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    source = args.input.read_bytes()
    result, report = normalize(json.loads(source))
    output = (json.dumps(result, indent=2) + "\n").encode()
    report.update(
        input_sha256=hashlib.sha256(source).hexdigest(),
        output_sha256=hashlib.sha256(output).hexdigest(),
    )
    args.output.write_bytes(output)
    args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

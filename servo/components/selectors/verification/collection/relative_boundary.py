#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import hashlib
import json
import re

from normalize import require
from verify_helper import PROJECT, ROOT, digest

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
AUDITS = {
    "CollectionIteratorProofs.next_in_bounds": STANDARD_AXIOMS,
    "CollectionIteratorProofs.next_exhausted": STANDARD_AXIOMS,
    "CollectionIteratorProofs.selector_iter": STANDARD_AXIOMS,
    "CollectionStepProofs.simple_component_step": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "CollectionInvariantProofs.store_some": STANDARD_AXIOMS,
    "CollectionInvariantProofs.store_preserves_allowed": STANDARD_AXIOMS,
    "CollectionInvariantProofs.store_some_full": STANDARD_AXIOMS,
    "CollectionInvariantProofs.simple_component_preserves": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "CollectionLoopProofs.loop_preserves": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "RecursiveCollectionProofs.component_preserves": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "RecursiveCollectionProofs.selector_preserves": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "CollectionLoopInvariantProofs.loop_preserves_invariant": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "CollectionFrameProofs.store_frame": STANDARD_AXIOMS,
    "CollectionFrameProofs.component_preserves_frame": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "CollectionFrameProofs.selector_preserves_frame": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "CollectionFrameProofs.relative_zero_tail": STANDARD_AXIOMS | {"core.fmt.Formatter"},
    "Collection.parser.collect_relative_compound": STANDARD_AXIOMS | {"Aeneas.Std.core.fmt.Formatter"},
    "Collection.parser.collect_selector_hashes": STANDARD_AXIOMS | {"Aeneas.Std.core.fmt.Formatter"},
    "Collection.parser.collect_component_hashes": STANDARD_AXIOMS | {"Aeneas.Std.core.fmt.Formatter"},
}


def identifiers(*parts):
    return [{"Ident": [part, 0]} for part in parts]


RELATIVE_ROOTS = {
    "selectors::parser::collect_simple",
    "selectors::parser::collect_relative_compound",
}


def audit_source(source, roots=None, extra_bodies=()):
    translated = source["translated"]
    options = translated["options"]
    require(options["remove_unused_clauses"], "Unused-clause pass missing")
    require(
        set(options["start_from"]) == (RELATIVE_ROOTS if roots is None else roots),
        "Unexpected extraction roots",
    )
    local_opaque = [
        decl for decl in translated["fun_decls"]
        if decl and decl["body"] == "Opaque"
        and decl["item_meta"]["name"][0] == {"Ident": ["selectors", 0]}
    ]
    require(len(local_opaque) == 1, "Expected only SelectorList::slice opaque locally")
    decl = local_opaque[0]
    name = decl["item_meta"]["name"]
    require(
        len(name) == 4 and name[:2] == identifiers("selectors", "parser")
        and name[-1] == {"Ident": ["slice", 0]},
        "Wrong opaque local method",
    )
    impl = name[2]["Impl"]["Ty"]
    require(impl["kind"] == "InherentImplBlock", "Wrong slice implementation kind")
    adt = impl["skip_binder"]["Untagged"]["Adt"]
    require(
        translated["type_decls"][adt["id"]]["item_meta"]["name"]
        == identifiers("selectors", "parser", "SelectorList"),
        "Wrong slice receiver type",
    )
    require(decl["item_meta"]["opacity"] == "Opaque", "Slice was not made opaque")
    required = {"simple_selector_hash", "collect_component_hashes", "collect_selector_hashes", "collect_relative_compound"}
    found = set()
    for fun in translated["fun_decls"]:
        if not fun:
            continue
        name = fun["item_meta"]["name"]
        require(name != identifiers("core", "intrinsics", "transmute"), "Unsafe transmute remains")
        if len(name) == 3 and name[:2] == identifiers("selectors", "parser"):
            leaf = name[-1].get("Ident", [None])[0]
            if leaf in required:
                require(isinstance(fun["body"], dict) and "Structured" in fun["body"], "Collector body became opaque")
                found.add(leaf)
    require(found == required, "Missing production collector body")
    for path in extra_bodies:
        bodies = [fun for fun in translated["fun_decls"]
                  if fun and fun["item_meta"]["name"] == identifiers(*path)]
        require(len(bodies) == 1 and isinstance(bodies[0]["body"], dict)
                and "Structured" in bodies[0]["body"], "Missing production matching body")
    return decl


def template_digest(text):
    text = re.sub(r"/\-.*?\-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    return hashlib.sha256(" ".join(text.split()).encode()).hexdigest()


def audit_boundary(source, output, manifest_name="relative-boundary.json", roots=None, extra_bodies=()):
    manifest = json.loads((PROJECT / manifest_name).read_text())
    decl = audit_source(source, roots, extra_bodies)
    require(
        hashlib.sha256(decl["item_meta"]["source_text"].encode()).hexdigest()
        == manifest["selector_list_slice_source_sha256"],
        "SelectorList slice representation contract requires review",
    )
    for name, expected in manifest["representation_sources"].items():
        require(digest(ROOT / name) == expected, f"Representation source requires review: {name}")
    for name, expected in manifest["external_templates"].items():
        require(template_digest((output / name).read_text()) == expected, f"External declaration boundary changed: {name}")


def audit_axioms(text, expected=None):
    expected = AUDITS if expected is None else expected
    records = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", text)
    records += [(name, "") for name in re.findall(r"'([^']+)' does not depend on any axioms", text)]
    require(len(records) == len(expected), "Missing or duplicate axiom audit")
    seen = set()
    for name, axioms in records:
        require(name not in seen and name in expected, "Unexpected or duplicate audited declaration")
        require((set(re.split(r",\s*", axioms.strip())) if axioms.strip() else set()) == expected[name], f"Unexpected axioms: {name}")
        seen.add(name)
    require(seen == set(expected), "Missing audited declaration")

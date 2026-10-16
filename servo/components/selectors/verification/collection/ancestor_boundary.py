#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import relative_boundary

ROOTS = relative_boundary.RELATIVE_ROOTS | {"selectors::parser::collect_ancestors"}
BODIES = tuple(("selectors", "parser", name) for name in [
    "collect_ancestors", "collect_ancestor_hashes", "scan_ancestor_hash_subject",
    "collect_subject_ancestor_hashes",
])
AUDITS = dict(relative_boundary.AUDITS)
for name in ["skip_step", "skip_exact", "skip_path", "skip_bounds", "skip_first_stop",
             "skip_contract", "is_ancestor_exact", "next_after_combinator",
             "next_component", "next_end"]:
    AUDITS[f"AncestorIteratorProofs.{name}"] = (
        {"propext", "Quot.sound"} if name in {"skip_path", "skip_first_stop"}
        else relative_boundary.STANDARD_AXIOMS
    )
for path in BODIES:
    AUDITS["Collection.parser." + path[-1]] = relative_boundary.STANDARD_AXIOMS | {
        "Aeneas.Std.core.fmt.Formatter",
    }

for namespace, names in {
    "AncestorProgressProofs": ["selector_read", "next_exact", "jump_bounds", "read_some", "next_yield"],
    "AncestorSubjectProofs": ["finished_weaken"],
    "AncestorComponentProofs": ["store_invariant"],
    "AncestorFullProofs": ["phase_reach", "good_region"],
}.items():
    for name in names:
        AUDITS[f"{namespace}.{name}"] = relative_boundary.STANDARD_AXIOMS
for namespace, names in {
    "AncestorLoopProofs": ["loop_preserves"],
    "AncestorSubjectProofs": ["subject_loop"],
    "AncestorScanProofs": ["scan_loop"],
    "AncestorComponentProofs": ["component_preserves", "ancestor_region_preserves"],
    "AncestorFullProofs": ["full_preserves", "ancestors_required_and_zero"],
}.items():
    for name in names:
        AUDITS[f"{namespace}.{name}"] = relative_boundary.STANDARD_AXIOMS | {"core.fmt.Formatter"}


def audit_boundary(source, output):
    relative_boundary.audit_boundary(source, output, "ancestor-boundary.json", ROOTS, BODIES)


def audit_axioms(text):
    relative_boundary.audit_axioms(text, AUDITS)

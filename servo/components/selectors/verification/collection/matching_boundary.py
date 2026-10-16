#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import relative_boundary

ROOTS = relative_boundary.RELATIVE_ROOTS | {"selectors::matching::matches_local_name"}
BODIES = (("selectors", "matching", "matches_local_name"), ("selectors", "matching", "select_name"))
AUDITS = dict(relative_boundary.AUDITS)
for name in ["local_name_requires_hash", "local_name_component_good", "local_name_compound_requires_hash", "local_name_relative_collection"]:
    AUDITS[f"MatchingProofs.{name}"] = relative_boundary.STANDARD_AXIOMS | {
        "core.fmt.Formatter", "context.MatchingContext", "core.ptr.non_null.NonNull",
    }


def audit_boundary(source, output):
    relative_boundary.audit_boundary(source, output, "matching-boundary.json", ROOTS, BODIES)


def audit_axioms(text):
    relative_boundary.audit_axioms(text, AUDITS)

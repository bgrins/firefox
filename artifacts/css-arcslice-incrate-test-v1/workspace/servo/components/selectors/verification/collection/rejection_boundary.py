#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json

from matching_boundary import AUDITS as MATCHING_AUDITS
from normalize import require
from relative_boundary import STANDARD_AXIOMS, audit_axioms
from verify_helper import PROJECT

BRIDGE_AUDITS = {
    "CollectionRejectionProofs.prefix_members": STANDARD_AXIOMS,
    "CollectionRejectionProofs.padding_members": STANDARD_AXIOMS,
    "CollectionRejectionProofs.mask_idempotent": {"propext", "Quot.sound"},
    "CollectionRejectionProofs.array_pack_no_rejection": STANDARD_AXIOMS,
    "CollectionRejectionProofs.local_name_no_false_rejection": STANDARD_AXIOMS | {
        "context.MatchingContext", "core.ptr.non_null.NonNull", "core.fmt.Formatter",
    },
}


def core_audits():
    manifest = json.loads((PROJECT / "rejection-boundary.json").read_text())
    core = {name: set(axioms) for name, axioms in manifest["core_axioms"].items()}
    require(len(core) == 36, "Unexpected core theorem audit count")
    require(all(axioms <= STANDARD_AXIOMS for axioms in core.values()), "Unexpected core axioms")
    return core


def expected_audits():
    core = core_audits()
    require(not (core.keys() & MATCHING_AUDITS.keys() or core.keys() & BRIDGE_AUDITS.keys()), "Overlapping axiom audit names")
    return core | MATCHING_AUDITS | BRIDGE_AUDITS


def audit_combined(text):
    audit_axioms(text, expected_audits())

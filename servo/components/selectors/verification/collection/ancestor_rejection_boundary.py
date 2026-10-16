#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from ancestor_boundary import AUDITS as ANCESTOR_AUDITS
from normalize import require
from rejection_boundary import BRIDGE_AUDITS, core_audits
from relative_boundary import STANDARD_AXIOMS, audit_axioms


def expected_audits():
    core = core_audits()
    bridge = {name: axioms for name, axioms in BRIDGE_AUDITS.items()
              if name != "CollectionRejectionProofs.local_name_no_false_rejection"}
    bridge["CollectionRejectionProofs.ancestor_collection_no_rejection"] = STANDARD_AXIOMS | {"core.fmt.Formatter"}
    require(len(bridge) == 5, "Unexpected ancestor bridge audit count")
    require(not (core.keys() & ANCESTOR_AUDITS.keys() or core.keys() & bridge.keys()
                 or ANCESTOR_AUDITS.keys() & bridge.keys()), "Overlapping ancestor audit names")
    return core | ANCESTOR_AUDITS | bridge


def audit_combined(text):
    audit_axioms(text, expected_audits())

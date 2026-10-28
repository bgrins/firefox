# Infinite-value Round research checkpoint

This checkpoint preserves completed observations and a held proposal. It adds
no native repair, accepted ID, or formal coverage. The accepted count remains
144 across 145 tracked IDs; held ID 120 is excluded.

| Completed work | Result | Evidence |
|---|---|---|
| System Firefox 158 observation | Known nonfinite failures; incomplete initial transport retained separately | `css-round-infinite-value-browser-v1` |
| Current local app numeric baseline | 24 tests: 16 PASS, 8 FAIL; 72 calibrated snapshots. Only the relative step at zero font size failed; literal NaN passed | `css-round-infinite-value-baseline-runtime-1` |
| Current local app admission baseline | All 8 tests passed across 32 calibrated snapshots. Constant-result expressions remain accepted; four easing consumers reject direct context | `css-round-infinite-value-admission-runtime-1` |
| Independent source and saved-result review | Both observations replayed; no candidate execution claimed | `css-round-infinite-value-review-v1`, `css-round-infinite-value-local-baseline-review-v1` |
| Inactive representation groundwork | Two-source private patch with parser guards retained; syntax/format/transport checks only, no compile or browser validation | `css-contextual-easing-representation-prototype-v1` |
| Numeric source/WPT proposal | Held, uncompiled and unexecuted; admission regression predicted from source | `css-round-infinite-value-repair-v1` |
| Isolated observation runners | Current local app, private WPT resources and profiles, preserved source/app/index/control state | `css-round-infinite-value-validation-plan-v1`, `css-round-infinite-value-admission-plan-v1` |

The full accepted-work table remains
[readout v5](../css-all-work-readout-20261028-v5/README.md). Historical accepted
144 source metadata remains unchanged; current generic source is the accepted
145 postimage. The shared provider prototype remains unaccepted. These results
do not establish independent upstream applicability.

Next compile and rebase the contextual consumer representation against the
existing keyframe/dependency handoff, migrate infallible callers, and validate
admission/readiness before opening parser guards. The completed inactive representation prototype is archived; its
integration, native compilation and browser validation remain unfinished.
The held numeric proposal has no observed candidate failure because it has not
been compiled or run. No fix 146 is allocated.

`run.py --run MANIFEST_SHA` is root-owned execution. It authenticates the listed
packages and the helper bodies, verifies the full canonical epoch in memory,
prepends the exact roadmap text while preserving the old suffix, stages only
the selected artifact paths in an isolated index, and creates one signed
research commit. It verifies the actual signature, parent, tree, bodies, flags,
nested index, accepted payloads and unchanged native diff before synchronizing
only canonical `CURRENT-EPOCH.json`. ROLE, OWNED, native source and binaries are
preserved. Counts and acceptance records are unchanged.

The runtime stores compact selection/digest and signature receipts. It does not
save or commit another full epoch, repeated staged patch, or full state snapshot.
The new commit's own receipts necessarily follow that commit and remain outside
its tree. The preceding v42 final receipt/signature is archived here. Signing
failure preserves the staged selection and roadmap with a recovery lock; no
automatic retry or index reset occurs. A synchronization failure reports that
the old canonical epoch cannot certify the newly signed HEAD.

`--check` authenticates package selection and roadmap transport without staging,
signing, publishing the roadmap, or changing canonical state. It does not replace
the runtime's full preservation checks.

Direct references additionally retain two small historical source/model audit
capsules at their original paths. The 3.99 MB v42 `CURRENT-EPOCH.json` remains
a hash-bound local execution input; it is intentionally not recopied into this
commit. The runner verifies its canonical state fully in memory before signing.

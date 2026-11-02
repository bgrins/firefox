# Selected-reference browser pair: partial improvement, page crash

The fresh candidate passes all 13 metric callbacks and all four phase callbacks, repairing 14 original failures. The typed-attribute page crashes before reporting any of its four callbacks. This is an incomplete, failed pair, not 21 passing callbacks or native-fix acceptance.

| Lane | Fresh original | Candidate | Saved observation gate |
| --- | --- | --- | --- |
| Metric | 3 PASS, 10 FAIL, 1 OK ending | 13 PASS, 1 OK ending | true |
| Phase | 4 FAIL, 1 OK ending | 4 PASS, 1 OK ending | true |
| Typed attribute | 3 PASS, 1 FAIL, 1 OK ending | 0 callbacks, 1 CRASH ending | false |

All three original PASS signatures in the completed lanes and both corresponding endings remain exact. The crashed lane does not preserve its three original PASS observations or its OK ending. Its four callbacks are missing, not numerical FAIL results. `OBSERVATIONS.json` enumerates all 21 identities and their actual transitions.

The independent saved replay reproduced all original assessments and all three candidate assessments and comparisons, including the incomplete crash result. It joined both full builds, command/source roles, application metadata, binary hashes, saved preservation snapshots, cleanup receipts, staged resources and genuine manifests. Both builds use HEAD `70d9abdf9784cf84732aed747cbec87fe0589d95`; their BuildIDs are `20261102122116` and `20261102124837`. The candidate is exactly cascade `25e8a27a` with provider `90acb505`, not the later ownership successor. Each metadata tree contains only its manifest; there are no fixture pref or expected-FAIL overlays. The normal `testing/profiles` harness defaults remain in use, so this is not an untouched release configuration.

The crash log records `assertion failed: matches!(result, VisitResult::Complete | VisitResult::CycleSettled)`. Its stack identifies the frozen candidate's `substitute_all` terminal assertion and custom-root loop. That loop can stop with unresolved computation when no executable action exists or an action cannot progress. The evidence identifies this experimental tripwire, but does not record the pending property, action or precise dependency. It does not establish that the separately demonstrated LineHeight ordinary-reentry route caused this typed-attribute crash, or that the ownership or LineHeight successors repair it.

The smallest useful next diagnostic is conditional logging immediately before this assertion: retained root identity, result variant, current frame phase and pending action identity, plus the already-produced `drive_metric_action` result where it stops. It should inspect retained state only, without another substitution, property read or dependency traversal. A root-controlled run of this single unchanged page can then distinguish an absent producer, nested wait, foreign semantic wait and ordinary-ownership conflict before another broad experiment. No instrumentation was implemented by this review.

Owner terminal `37339 / 69c55d / c4e706`, exit 1, binds the saved unsuccessful RESULT. The owner reports restoration verified with no publication errors. This review does not independently verify live restoration or backup removal; root owns that separate audit. The top-level result contains only the completed original aggregate, and no candidate OUTCOMES aggregate exists. Complete candidate lane evidence remains in its individual directories.

An inherited assessor description still mentions 32 callbacks and twelve endings. That prose is stale; the authenticated executable policy and raw roster are 21 callbacks and three endings. No owner, runtime, native source, application, index or canonical control was changed.

Saved verification: original replay `da5b9a/0`, candidate build join `fd2070/0`, completed-lane replay `57952f/0`, final three-lane replay and 92 reference pins `0d6169/0`. PASS callbacks establish the fixture assertions; they do not archive every sampled numeric value.

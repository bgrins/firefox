## 2026-10-29: exact-source hypot final validation complete; native commit pending

Clean generic calc b7a6ac and corrected proposal-v5 WPT0be27 completed final
Gecko build 25436/3864b9/0 and installed-path lint 23787/8ac819/0. Fresh original
21394/f64837/0 has199 PASS and 28 FAIL; final 94240/f4ad48/0 has215 PASS and 12 FAIL, with
four OK endings each. All 30 new callbacks pass, all 16 targets improve, and
211 control plus four ending full signatures/every originalPASS are unchanged.
Both raw logs replay exactly. The 12 known pow failures remain preserved controls.

The three zero-control expressions now generate negative zero using (-1 * 0).
The historical v3 pair retains its16-target evidence but does not prove its
mislabeled negative-zero controls. All three corrected controls pass in both
fresh phases. The earlier baseline-v2 attempt stopped before browser launch
because two restored application metadata identities differed; v3 rebinds only
those identities, preserving bytes/BuildID/lineage and the strict guard.

V60 records research/validation before a standalone native commit. Candidate
calc and the single 30-case WPT remain installed and unaccepted; their ownership,
the held provider and all 147 prior fixes are preserved. Existing145 source/hash/
commit/WPT provenance remains historical, with explicit current-pin supersession.
Only the later root-owned exact calc+WPT signed commit and acceptance publication
may update IDs/counts. Counts remain147 accepted fixes and 148 tracked IDs, held fix 120 excluded.
No push is included. The native change is numerical robustness; CSS precision/
range allowance means there is no settled conformance claim or formal-discovery
credit. Shared held-provider/configuration limits remain explicit.

Separate pow proposals remain unexecuted native research. Historical v1's
literal-negative-zero controls are superseded by corrected v2. The independent
model review accepts its scoped 11-theorem/three-negative-control abstract guard
and folding model, not native Rust/IEEE/full-pow or invalidation verification.
No new pow execution, fix, accepted count or canonical proof credit is claimed.


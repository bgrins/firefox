# Pending cycle defaults must remain pending during traversal

Status: scoped repair to the unactivated v4 prototype, with an executable finite witness. Neither v4 nor v5 has a recorded native typecheck or browser run here. V3's separate successful typecheck does not transfer to them. This is not a stock Firefox bug report or an accepted fix.

V4 marks all members of a completed SCC in invalidated_pending before computing their defaults. Its substitution readiness snapshot consults that set, but traverse() did not. While computing one member's contextual initial, a demanded prioritary declaration can lead traversal into another retired participant whose default is still pending. The stale raw declaration then appears invalid during fallback selection. A fallback that should be unused can create a false new SCC.

V5 adds one guard before deferred-declaration and raw-map handling in traverse(): a pending invalidated custom property is serviced through apply_invalid_default(), then returns resolved. It is not treated as missing. That existing helper preserves InvalidatedParticipant classification, uses the owned default-applying guard, retains its prepared initial AST, and returns incomplete on a reentrant owner. No scheduling request is converted into a semantic SCC edge.

## Exact conditional witness

Assume these three non-inheriting length registrations are admitted: A initial 5px, B initial 10em, C initial 7px. Their declarations are A=var(B), B=var(A), C=var(A,var(C)); font-size consumes C. Assume a completion owner that certifies the relevant constant/em inputs, zoom 1, and traversal starting at A. Admission of the contextual initial 10em is explicitly conditional; this package does not adjudicate the CSS-rule admission specification.

1. Visiting A then B classifies the A/B SCC and retires its records. Default publication order is B, then A; both are pending.
2. B's 10em initial needs font-size. Computing font-size requests C.
3. In v4, C visits A's retired record but raw var(B) is still visible. A is mistaken for an invalid primary, so C's self fallback is traversed. C is falsely classified cyclic and gets 7px.
4. Font-size becomes 7px, B gets 70px, and A finally gets 5px. C is already published as 7px.
5. In v5, C's visit to pending A computes A's classified default 5px first. C's fallback is unused; C and font-size become 5px, and B becomes 50px.

The finite Python witness implements this traversal/default interleaving. It rejects both v4 raw visibility and the tempting but incorrect pending-as-missing alternative. A second fixture has C request already-applying B and verifies incomplete return without publishing C. This is source-correspondence evidence, not execution of Rust, Firefox, or a Lean kernel theorem.

## Other activation blockers remain

V4's incomplete-result/discard contract and missing production context certificate remain. Its conservative prioritary scheduling can also block a valid selected fixed line-height: registered --n:1lh, line-height:40px, font-weight:calc(var(--n)/1px). Line-height's prerequisite set includes font-weight; font-weight requests active --n, so strict servicing stops incomplete. A selected fixed line-height need not read font-weight. Fixing this needs actual selected prioritary read requirements, not globally deleting the prerequisite or adding a CSS cycle edge. This is an unexecuted activation counterexample; typed-division support and actual source scheduling need native calibration.

Initial/random keys are deterministic in the inspected implementation; no reparsing identity churn has been demonstrated. AST retention is an ownership/retry guarantee, not proof of a random-identity defect.

Production activation, complete context discovery, native typechecking and full runtime validation remain outstanding. No fix or formal-coverage counts change.

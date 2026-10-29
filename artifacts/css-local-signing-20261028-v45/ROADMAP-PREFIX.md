## Current research checkpoint: preserve the resolved tree-scope behavior

The zero-fallback hypothesis is rejected. CSSWG issue 13736 resolved on
24 June 2026 to return one when tree-counting reference resolution fails;
Gecko bug 2050171 / D308700 and WPT commit 418c211 implement that decision.
The draft text saying zero is stale (Needs Edits). Preserve the historical
hypothesis and system-browser observations with their superseding correction.
The alternative-zero local adapter is retired, never enabled or executed, and
no zero-repair paired build was prepared. This is not a new Gecko defect.

The six-source contextual easing check first failed with ten serde trait errors,
then passed the configured Gecko Rust graph check after removing two unnecessary
derives. Both attempts restored the exact original sources and preserved the
app, indexes and runtime controls. The successful check took 32.05 seconds.
The corrected eight-source selected-rule scope candidate keeps the resolved
fallback of one and has no zero-repair prerequisite. Its configured Gecko
check passed in 18.86 seconds with all eight sources restored and full
preservation verified. The separate scope-v3 cleanup removes an unused helper
and avoids the own-shadow rank walk when no style data exists; it remains
uncompiled and unexecuted. Rebind and compile that exact cleanup next, then
validate selected-rule scope transport and dependency/lifecycle behavior.

Parser guards remain closed. Compilation alone does not establish browser
behavior, Servo cfg support, dependency/lifecycle correctness, or activation
readiness. Keep the existing animation-name declaring-root lookup boundary
explicit: its source-only diagnostic is unexecuted and already represented by
an expected-failure upstream test, not a new discovery. Continue scope and
consumer validation without changing accepted 144/145 Round behavior or the
held provider. The standalone selected-keyframe rank model has nine audited
kernel-checked declarations and three rejected false controls. A separate
bounded root source/log review is clear, without a kernel rerun; neither the
model nor that review establishes native correspondence.
Neither this model nor the canonical tree-counting audit adds formal coverage
credit.

Acceptance remains 144 fixes across 145 tracked IDs, with 120 held and excluded.
No fix 146 is allocated. All bound execution recipes become historical after
this research commit and require current-state rebinding before reuse. The
compact work summary is `artifacts/css-local-signing-20261028-v45/README.md`.

---


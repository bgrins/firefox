# View-transition type invalidation candidate review

## Source and WPT verdict

No source or WPT blocker found for the bounded document-root mutation repair. Final reviewed native inputs are the three formatted snapshots in `formatted/`; ViewTransition.cpp SHA256 is `93725f16af96dd6bf73e4e9dd27cfbe18b690059b486d6e1086fa234bef39ccf`. `FORMAT-TRANSFER.json` verifies exactly one added alignment space from the offline proposal; header and type-set implementation are identical. `EXACT-DELTA.json` reconstructs the original candidate using only the expected helper/declaration/three notification sites and empty-Clear guard.

WPT snapshot `wpt-v2.html` SHA256 is `41cded591e60ca2ffb7db363fa10de520157757b29eac870463adc723f6025c3`. Bounded native/WPT acceptance is recommended: the candidate build and paired tests pass, scoped lint is clean, and exact four-file standalone packaging is verified. Root owns final acceptance. No browser/build/native/Git changes were performed by this review.

## Branch and lifetime audit

- `TypesChanged()` checks current document active-object identity, then current root availability. It does not test only phase or merely the existence of any active transition. Completed, skipped or replaced objects can continue to mutate their sets without scheduling restyles for a different transition. `mDocument` and the type set's `mTransition` are existing strong references; the patch adds no stored pointer or new ownership.
- Add retains Has/exception/duplicate early exits and the Add helper exception exit. Native append precedes notification. Delete retains absent/error exits; removal precedes notification. Public return values are unchanged.
- Clear still invokes its generated helper first. Failure still returns. The added empty-native-list test avoids redundant notifications without skipping the public helper. A nonempty list is cleared before notification.
- No hook is added to lazy `Types()` exposure or initial-list construction. The candidate does not change constructor uniqueness or initial duplicate handling.
- Notifications use `RestyleSubtree()` rather than a synthetic ACTIVE state transition. Actual matching reads the current list; synthetic old-bit snapshots lack old types and can miss deletions. Subtree rematching covers selectors whose predicates live on the root and declarations on descendants.
- `PostRestyleEvent` defers style work; this function neither flushes layout nor enqueues script callbacks. The source argument relies on normal main-thread DOM mutation and the existing no-Servo-traversal posting invariant. It does not prove scheduler delivery or arbitrary document teardown.

The authenticated predecessor review supplies the complete local source chain, fresh primary spec snapshots and original diagnostic receipts. It was reauthenticated across all 46 inputs before reuse. StyleChildrenIterator includes generated before/after nodes and the active transition's native-anonymous snapshot wrapper; recursive subtree hints cover that tree. The existing explicit-hint path also increments undisplayed-style generation. A complete style-system refinement theorem is not claimed.

## WPT oracle and calibration

Eighteen promise tests cover six mutation/no-op cases both synchronously and after ready, plus three operations on a completed object with no active owner and with a new beta owner. Unique IDs and fresh stylesheets isolate tests; initial computed-value assertions warm every observed style cache before mutation. Public membership and fresh selector matching separate matching correctness from cache invalidation.

The first twelve tests query ordinary root color/child width and root/child before opacity. Ready-only cases additionally query group(root) opacity. Fixed pixel widths and numeric opacities avoid resource, font or interpolation dependencies. The UA group animation changes geometry; the predecessor retains complete BuildGroupKeyframes showing no opacity contribution. Long group duration keeps a ready transition active while the test synchronously reads its values. Cleanup skips each transition, awaits finished, and removes both style and target; ready rejection is handled for immediately skipped cases.

The old-object tests independently verify the old set still changes and the document owner/current resolved values do not change. They cannot detect redundant restyle scheduling or prove no-op performance; the exact native guard supplies that branch guarantee. Generated helper failure branches are source-reviewed, not fault-injected.

No expectation is weakened. The candidate does not depend on the initial-duplicate fix for these unique-input tests, and does not repair duplicate native membership if that older defect is separately present. Standalone patch applicability and isolated upstream runtime remain separate gates.

## Retained baseline

Independent raw-log inspection found 42 distinct subtests, 36 PASS and six FAIL, with three OK harness completions. All six failures occur at the post-mutation computed-style assertion for successful Add/Delete/Clear in both phases; initial calibration and direct membership assertions were reached successfully. All 43 before/after pins match. Two existing files contribute 24 passing subtests. The baseline uses root's shared built binary; this reviewer did not rebuild it.

## Final paired gates and packaging

Independent parsing of both retained raw logs confirms the exact same 42 unique test identities and three OK harnesses per phase. Candidate has 42 PASS. Exactly the six successful-mutation rows change FAIL to PASS; all 36 other status/expected/message tuples are unchanged. All 43 pins are stable within each run; across runs only the three native files and two binaries differ. Candidate native pins match the successful build receipt and final snapshots. Build exited zero; retained Mach progress export KeyError diagnostics did not indicate a compiler failure. Format and both native/WPT scoped lint gates passed, with zero lint errors or warnings.

The exact four-file final patch has SHA256 `a17790522e9e2c39aab2b235e5f96720ca286b2442e0fbbedc7912f7097984a7`. Root's inspected packaging script uses isolated temporary indexes, verifies every result blob and the exact path roster, then reverses to the original tree at integration base 92a6fddf18e5828b17d7491a34663a0d5a9c12ad and upstream 976279105b2e78b8666a959eb3f25c9176cefaf8. I additionally read all three original blobs from both Git bases: each exactly matches the reviewed original file; the new WPT is absent at both bases. These read-only checks are retained in BASE-CORRESPONDENCE.json. No earlier native fix is included or required by this patch for its unique-type WPT. This does not imply the independent initial-duplicate bug is repaired.

The runtime uses the shared local build. There was no isolated upstream build/run, no performance neutrality measurement, and no formal proof of native scheduler delivery. Formal companion acceptance is separate. Root owns final native acceptance.

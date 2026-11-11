# Transient recascade revision 3 readiness review

No blocker found for the bounded build/runtime experiment. The exact source amendment and frozen runtime preparation pass independent copied checks. No native build, browser run or live source/app/Git mutation was performed by this review.

Source manifest `d79e802f50a8193e2f45297c3ea2f0e5ad906979551db4b28116c8abddb05138` authenticates 75 files. Frozen runtime manifest `b81b1a21cb270cf75a25f6a440402120c0272b30888de9d6c12e4ceca2bd03d7` authenticates 67 inputs. The copied source checker validates 16 pinned Git objects and patch composition; the copied frozen-runtime checker validates the source roles, retained baseline, exact inventories, restoration implementation, patch reconstruction and 30 ordinary + 23 query + 23 recascade rejection controls. Scratch was removed and both manifests reauthenticated afterward.

Compared with runtime revision 1, exactly three candidate files change:

- ServoStyleSet.cpp capitalizes the three Before/After/Marker enum references.
- The temporary nsDOMWindowUtils.cpp driver capitalizes its one After reference.
- glue.rs adds one Marker-only early return through `Stylist::compute_pseudo_element_style_with_inputs`, after both origin rule paths have been updated.

The marker branch receives the same owned inputs, explicit pseudo, stylesheet guards, primary style and originating element. It avoids the eager-only assertion while retaining both existing normal/visited paths. Before/After still use the pseudo-aware default-parent resolver. The chosen lazy helper already uses its parent style for both inheritance and layout adjustment; its existing source TODO remains a limitation. This does not establish new Marker display:contents correctness, nor waive the final debug gate for a public missing-pseudo repair.

The candidate manifest, four fixture contents, test-source pins, 208-query and 100-recascade assertion inventories, 130-record ordinary vector, actual runner, freeze routine, process/bundle/restoration helpers, all analyzers and parser-control scripts are byte-identical to revision 1. Runtime checker additions authenticate the amendment; they do not weaken a status, lifecycle, restoration or callback gate. The exact frozen executable input roster was checked after root set the execution HEAD and retained receipt.

Two review-harness preparation failures are retained separately: root froze RUN-PLAN while the first audit was still using preparation pins, and the copied runtime checker used `HERE.parents[1]` rather than the source checker's `HERE.parent.parent`. Neither was a native or fixture failure. The accepted audit uses the stable frozen manifest and adjusts only the repository locator in memory, leaving copied checker bytes intact for the runtime's own hash checks.

Passing this preparation review permits the proposed experiment, not semantic acceptance. Require a successful real build, genuine installed lint, complete 100/208 driver inventories with setup gates, exact ordinary-vector preservation, no unexpected errors/crashes and complete restoration. Donor-map recascading remains separate from full sampled-effect/provider integration; public CSSOM timing/cache/admission, visited exposure and final debug transform/change-hint coverage remain open.

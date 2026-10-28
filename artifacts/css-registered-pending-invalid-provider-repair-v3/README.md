# Registered provider admission and defaulting proposal

Source-ready for an isolated native experiment; uncompiled, untested and unaccepted. Signed v1/v2 artifacts are unchanged. Both native preimages match committed HEAD 9abc806ef333f4cf9567ba28c3243ab9d9bc26e8. native.patch is the complete two-file delta; V2-DELTA.patch isolates the participant correction and incidental import cleanup. The accepted zoom implementation is untouched. No type whitelist is used.

## Defaulting and admission

Recursive substitution against a partially resolved map admits selected text against the referenced provider's own grammar, URL context, identity and taint. Rejected text or failed substitution supplies its registered default. Valid contextual providers remain unevaluated; this does not solve all valid pending-provider scheduling.

Normal application, graph-loop handling and recursive invalid defaults share one policy: clone the actual parent's computed value for inherited properties on nonroot elements, otherwise clone Stylist's computed initial map. This replaces the old normal invalid handler's target-context initial recomputation. CSS-wide handling retains its existing initial-map/parent policy, INHERITS_RESET_STYLE, substituted-revert behavior and initial remove-first sequence. Replacement values retain their own taint and URL data; valid selected input retains existing taint processing.

Stylist rebuilds initial values in new_for_initial_at_property_value and stores computation flags; cascade_rules adds those flags before resolution. Cloning avoids early contextual evaluation and preserves symbolic currentcolor. Consistency with existing initial/CSS-wide use is supporting evidence, not proof of equivalence for every currently admitted initial. See INITIAL-INDEPENDENCE.md.

## Participant correction

The v2 ancestor bit was insufficient. For A=var(B,var(C)), B=var(A), C=var(--missing), newly defaulted C could change A's raw fallback before cyclic A returned. Skipping only A's grammar admission did not preserve cycle behavior or select A's own default.

V3 tracks active custom names and marked participants. Reentry marks precisely the active suffix starting at the repeated name. Fallback retains marks. A marked registered provider yields its own default on unwind; a marked universal provider remains invalid and its caller's existing fallback remains available. Outside dependents are not marked merely for consuming a completed default. Normal custom application seeds/checks its own name so its outer expression cannot transform its own returned default again.

This manually corresponds to the pinned ProviderDefaults model, not a Rust refinement proof. The state covers recursive custom properties, not the complete attribute/relative-unit Tarjan graph or all computation-context identities. Parser, effects, cache publication and invalidation remain native obligations. Existing graph-loop handling is retained with the shared cached-default policy.

## Evidence and next experiment

The exact original mixed16 and reduced16 fixtures reproduced the discrepancy on installed Firefox158.0: 28 PASS / 4 FAIL, full signatures matching local observations. The pinned release report records preservation and repository WPT preferences; this is not a stock-default-profile claim. The candidate has not run.

check.py authenticates references and bodies, checks formatting, and applies/reverses/reapplies the exact two-file patch without fuzz/offsets in removed scratch. Cascade formatting disables import reordering solely to avoid unrelated churn; custom_properties uses the existing config. The earlier all-files reorder_imports=false attempt failed only on unrelated custom_properties import wrapping; the final per-file check passes. Independent review found no new concrete blocker after participant repair, subject to typecheck and exact cycle tests.

Expanded tests are separately sealed in css-registered-provider-default-expansion-v2, alongside unchanged mixed16/reduced16/supplement32. Root owns baseline/candidate execution and final WPT packaging. Keep missing/failed substitutions, inheritance/root/CSS-wide/taint, self/mutual cycles, the A/B/C fallback, and color-context controls visible. The eventual standalone fix must include actual tested WPTs; this capsule does not invent a final fixture selection. No accepted-fix or canonical Lean coverage increment is claimed.

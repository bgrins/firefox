# Preserve implicit-scope stylesheet positions in the cascade cache

The cache previously compared effective stylesheet contents while compiled implicit scopes retained raw collection indices. An inactive sheet before an otherwise identical active sheet changed those indices without changing the cache key. Reusing the cached rules could therefore resolve the receiver's scope against the wrong stylesheet owner, or fail to find it.

The repair adds the raw collection position of each effective sheet to the key. Enumeration includes inactive sheets; recording uses the applicability result already computed by the preceding collection-local media repair. It leaves media snapshot publication and failed-rebuild invalidation unchanged. One usize is retained per effective sheet. Performance and complete cache memory accounting are not established here.

The WPT checks both donor/receiver insertion directions, a unique-URL control, stylesheet loading and inactive-prefix calibration. Neither accessing cssRules nor a state-preserving move is required. The owner-relative oracle follows CSS Cascade's omitted scope-start rule, retained in spec-scope.json and cited by the test. Source discovery is pinned in searchfox.txt.

## Current branch comparison

The baseline binary matched the preceding stylesheet-move build and source HEAD 2fc2d5517651. The four-page suite produced 10 PASS and 4 FAIL, with four OK harness endings. Its shell exit was lost across a context transition and remains null; the full raw stream, suite ending and server shutdown are retained. Binary, source and WPT hashes were unchanged afterward.

The index patch applied and reversed without fuzz against the current stylist.rs. The local binaries build exited zero. Its log retains the existing Mach progress reporter KeyError for export; native compilation and linking completed successfully. Scoped Rustfmt and WPT lint passed. The candidate produced 12 PASS and 2 FAIL, four OK endings: exactly the two index failures became passes, all ten prior passes remained, and both host-context failure messages remained unchanged. The WPT exit is correctly recorded as one because the separate host-context defect remains. No expected-failure metadata was added.

Installed Nightly independently reproduced the same four scope failures and two unique-URL passes. It also has four failures in the shared-media controls, which our branch's earlier repair already fixes: its complete result is 6 PASS / 8 FAIL, not the local baseline's 10 / 4. Its executable, XUL and application metadata hashes were stable during execution. This establishes exposure in that Nightly, not release-channel exposure.

## Formal evidence and limits

The retained Scope and Vectors sources model active-sheet filtering, raw positions, receiver-relative root resolution and compile-time host dispatch. The stronger key includes content identity, raw position and host context. Equal keys imply equal compiled lists and sound receiver interpretation in this model. The vector proof establishes aligned lengths and lossless reconstruction of that tuple key. Root identities may differ; inactive contents and trailing inactive sheets need not prevent sharing.

A fresh isolated replay checked 34 theorems, audited their axioms and rejected 12 deliberately false propositions. These controls are false model claims, not mutated Rust executions. The index-only native repair deliberately does not satisfy the full stronger-key condition: the second missing host-context component is a separate fix. The abstraction assumes stable sheet contents, applicability and ownership during collection. It does not prove the Rust implementation, the complete CSS selector engine, mutation epochs, allocation recovery or memory safety. The temporary Lean output directory was removed.

## Delivery and replay

The native commit contains only stylist.rs, implicit-scope-cache-index.html and its two CSS resources. The sibling host-context page is used for attribution but is delivered with its own repair. Research and proof files precede the native commit.

This parent-relative patch follows the media repair's collector API. Earlier standalone index and host-context variants have independent historical comparisons in css-shadow-scope-standalone-readiness-v1; that does not make this exact patch directly applicable to every upstream revision. No new clean-upstream build is claimed.

Run `python3 -I -B check.py` to authenticate and compare the saved evidence. Run `python3 -I -B replay_lean.py <new-output-directory>` to recheck the retained models with the pinned local Lean toolchain. The replay driver removes temporary compiled objects. run_wpt.py records the explicit browser, command, exit and before/after fingerprints; use a fresh artifact directory for new observations rather than overwriting this record.

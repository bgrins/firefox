# Float-owner readiness: existing-model instantiation

Scoped mathematical component, not native acceptance. `FloatReady.lean` imports unchanged Hidden, Subtree and LineReady modules. It adds22 audited theorems and four false-universal rejection controls. It does not duplicate their30/36/22 result counts as new results.

## Concrete result

A principal line containing a placeholder and a separate current-owner Float-list root with a clean leaf is expressible in the existing Subtree.World. LineReady.newSkip dirties the placeholder but leaves the real float and its leaf ineligible. A nested inline placeholder gives the same counterexample. Conversely, an ordinary marked subtree that actually contains its owner's float reaches it: the result is about ownership edges, not a blanket exclusion of floats.

The proposed owner pass maps Subtree.markRoot over current Float-list entries whose supplied pushed flag is false, under `HidesContentForLayout() && !OWNS_ANON_BOXES`. Every selected root becomes eligible. A selected descendant becomes eligible under the existing clearRootPath predicate; alternatively rootClosure derives all-bit coverage and the existing LineReady.allDirty_locate theorem supplies target readiness. Neither premise assumes the conclusion that the selected target is eligible after marking. Dirty-root/clean-leaf, pushed, external and other-continuation counterexamples prevent universal coverage claims. Visible and anonymous-owner guards return the same model state.

The final theorem instantiates the existing Hidden query/provider contract: stale32 becomes provider50 only after the selected leaf is made eligible. Those numbers are a mathematical provider example, not browser results or a CSS sizing oracle. The general recovery theorem retains the actual provider function as an input; the model's synchronous query completing that provider is inherited, not proved for arbitrary Gecko float layout.

## Source correspondence and open joins

Retained audit manifest554db971… and proposal manifestb9ce433c… bind actual HEAD90e7 sources. `MarkSubtreeDirty` traverses ChildLists and prunes already-dirty nodes/table-column descendants. `nsPlaceholderFrame` stores its external OOF pointer separately; the helper never follows it. GetChildLists, ReflowLine, TrialReflow, CheckFloats, ReflowFloat and DrainPushedFloats complete retained bodies support the bounded edge/order discussion. The exact candidate patch and its BINDINGS/PROOF-REFERENCE are retained; this component does not compile or translate C++.

For this projection only, World.otherLists denotes the current owner's Float list. Native other child lists are outside that selected projection, not silently all marked. World.principal denotes the selected skipped line roots, not every line in a block. Tree.children denotes the helper's actual owned-child traversal. Finite, coherent, stable tree/list projection, nonaliasing between these separately modeled storage regions, correct selected-frame lookup, and current frame lifetime remain admissions. Placeholder and float are distinct frames here, not an alias encoded by equal IDs.

The native pass enumerates after DrainOverflowLines/DrainPushedFloats/ReflowPushedFloats at each ReflowDirtyLines invocation. The model does not derive that moving/pushed/overflow/continuation ownership settles into this snapshot; found membership and the supplied pushed predicate must describe that precise invocation. It proves nothing about excluded pushed entries, other owners, overflow lists or other continuations. Multiple trials can repeat; no cross-trial idempotence or stable identity claim. HidesContentForLayout describes this owner's forced-layout state, not global forcing. Native query-to-frame association, actual hidden-ancestor walk, callback completion and publication remain inherited open providers.

Already-dirty float roots can block a clean leaf. rootClosure/clearRootPath are explicit readiness assumptions, not a newly proved native dirty-history invariant. The proposed guard and loop are source-shaped; current candidate/browser effectiveness requires its separate runtime gate. Full allocation F1–F16/F11/F12 remain open.

## Replay and evidence

Run `python3 -I -S replay.py --manifest-sha EXTERNAL_FILES_SHA --output FRESH_EXTERNAL_DIRECTORY`. Optional `--timing-state ABS_STATE_JSON` refuses each Lean invocation while root status begins `cost `. The small replay recompiles all four modules, checks exact22 ordered axioms against the standard allowlist, and requires four falseclaims to fail because decide proves the proposition false. Generated work lives only in a temporary owned output subdirectory and is removed with CLEANUP receipt; source/logs remain.

The checker pins the Lean executable; its installed Std/runtime are trusted toolchain inputs, not a fresh complete library authentication. Source hashes and successful kernel replay do not establish Rust/C++ translation, source semantic fidelity or browser conformance. No browser, native build, production edits or Git operations were performed.

Development: the first manifest-copy attempt encountered a wrapped manifest schema before copying model payloads; corrected by reading its files member. Initial concrete `decide` proofs could not unfold well-founded markDesc; explicit simplification followed by kernel decide fixed those proofs, then unused simp arguments were removed. All development failures/logs are retained separately; no theorem statement was weakened to make compilation succeed.

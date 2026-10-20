# Type mutation invalidation: proposed proof contract

## Scope preserved

This companion addresses style cache coherence after mutation of an already representation-consistent type set. It does not repair or require initial-duplicate deduplication. Native/public membership consistency and unique native types are input contracts; the WPT starts with no duplicates. The earlier set proof may provide reusable pure list lemmas, never an assumed native prerequisite commit.

## State and independent specification

A finite collection of currently observable subjects distinguishes the document root, ordinary descendants and transition pseudo-elements. Tree/topology and presentation membership are fixed over each analyzed interval. A document has an optional active transition identity; each transition has native type membership. Cached style values, pending subtree rematch and request count are separate state.

The independent style oracle evaluates a small authored selector/rule language: current-active-type predicates, Boolean composition, target-specific rule lists and explicit ordered rule replacement. Base values and rules are defined inputs, not arbitrary final-cache answers. The WPT's root colors and descendant widths instantiate this language; a pseudo subject gives the parallel dependency obligation. Selector parsing, CSS cascade priority beyond the instantiated ordered rules, inheritance/property computation and translation to actual Stylo remain named resolver-provider obligations.

## Source-shaped mutation and notification

Add-existing, Delete-absent, Clear-empty and native error exits leave native membership unchanged and do not call the helper. Successful effective mutations change the native collection before invoking TypesChanged. The helper checks current active ownership and root presence, then posts RestyleSubtree with zero explicit change hint. Exact offline candidate sources and patch are pinned in evidence/CANDIDATE-SOURCE.json. nsLayoutUtils::PostRestyleEvent additionally gates composed document and prescontext.

The model records native error exits separately from successful operations. Cache correctness relative to the native selector input can include arbitrary such failures because callers return before native mutation. Public/spec membership agreement across errors additionally requires generated helper/JS Set failure atomicity or a representation-consistent cutpoint. It is not silently assumed from an error label.

Mutation of an old transition can change that object's type list while leaving current-owner selector inputs, style expectations and pending-request count unchanged. No operation changes the active owner merely to force restyling. Repeated effective mutations may coalesce into one pending subtree request; a later flush uses current membership, not saved obsolete type snapshots.

## Coherence invariant and flush delivery

Invariant: for every currently observable subject, its cached value equals the independently evaluated current rules, or an outstanding subtree rematch covers that subject. This allows stale caches between mutation and flush without presenting them as correct.

A delivered flush explicitly visits a supplied subject list. Pending visited subjects are recomputed using the defined rule evaluator. Partial visits retain a pending obligation; complete coverage permits the pending marker to clear. Prove successful/no-op/error/old-owner mutations and partial/full flushes preserve the invariant for arbitrary finite histories. Then derive fresh root/descendant/pseudo observations after a sufficiently delivered flush.

Actual RestyleSubtree propagation, root/descendant/pseudo traversal completeness, resolver translation, post-traversal change application and CSSOM's delivery of an appropriate style/layout flush are admitted source/provider contracts unless separately proved. The admission states which work is delivered, not that the final cache is already correct. Reentrancy or membership changes during traversal require restart/coherent-snapshot treatment; they are not hidden inside a generic scheduler assumption.

## Ownership/lifecycle boundaries

Within a mutation/flush interval, document/root topology and active-owner identity are stable, while both active and old transitions may mutate arbitrarily. Start/finish/owner handoffs and root replacement are explicit external cutpoints. Their existing lifecycle invalidation must re-establish the invariant; this repair does not claim to verify those algorithms. WPT completed/no-active and old-during-new cases start from calibrated current-owner caches.

Absent root means no root/subtree resolved-style observation in this model. A later root/presentation installation is a separate cutpoint requiring lifecycle construction/invalidation. RestyleManager::PostRestyleEvent also exits if disconnected or the PresShell is destroying. A live interval assumes a connected, nondestroying restyle manager and no call during Servo traversal; installed presentation is insufficient without those explicit delivery premises.

## Required counterexamples and gates

- Missing notification preserves direct matching but leaves root/descendant/pseudo caches stale.
- State-only notification fabricates old flags by XOR with the active bit while retaining current type membership. Deleting the selected type makes both fabricated-old and current predicates false despite a previously true cached predicate.
- Root-only rematching leaves descendant/pseudo caches stale.
- Dropping pending work on a partial traversal invalidates the invariant.
- A flush that uses a saved membership snapshot may miss the latest mutation.
- No-op/error/old-transition calls must not spuriously notify or alter active ownership.

Bind exact native helper and all three callers, generated helper/error boundaries, RestyleHint routing and retained state-only snapshot source. Preserve discovery's six failures/twelve controls and each of the eighteen WPT identities. Add artifact-only source/control/Lean calibration and semantic mutants after exact candidate handoff. Fresh/relocated isolated replay, strict closed manifests and independent review are final gates. No production/browser/build/Git edits are performed by this agent.

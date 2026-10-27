# Active attribute-watch publication

This research model isolates three obligations identified by the source audit `css-keyframe-attr-mutation-design-v1` (FILES SHA256 `92be7b0058571cb5f8f8bdc411aed10f468e143c2912c60485af39d7601f2d63`): retain absent reads, replace dependency sets even when endpoint values are equal, and preserve other effects’ watches when one effect disappears. It does not implement or verify the native repair.

## Model and proved scope

An active entry contains an effect identity, target, opaque endpoint value, and an ordered query trace. A query has an opaque attribute key and an optional result. Publication maps every query to its key, without filtering missing results or consulting endpoint equality. Watches remain per effect; the target aggregate is an existential search across published entries. A mutation matching any watch records a target update obligation. This deliberately permits conservative updates of other active effects on the same target.

`install` replaces both the active entry and its watches for that identity, including on retargeting. `remove` removes only that identity. The publication invariant is proved from these operational transitions for arbitrary finite histories, rather than required as an event-admission premise. `finite_history_covers` proves every supplied query of every remaining entry is watched. `queried_change_admits` derives an update obligation from that coverage. `other_effect_keeps_coverage` proves cancelling a different effect preserves the survivor’s query coverage.

The existing animation-obligation model is reused only for `delivered_normal_builds_current`. The projection maps an admitted target obligation to pending work on active effects at that target; applying the existing normal pass produces its current context stamp. This is a conditional delivery/computation bridge, not a scheduler liveness theorem or a proof of CSS numerical computation. No inherited theorem receives new credit.

## Discriminating controls

Three explicit faulty implementations are evaluated independently of the safe transitions:

- Drop queries whose result is absent: adding the previously missing attribute is not admitted.
- Update an entry but retain its old watches when endpoints compare equal: a different queried name is not watched despite the equal value.
- Cancel one effect and remove every watch for its target: another active effect still depends on that attribute but no update is admitted.

Each mutant has a kernel-proved failure witness and a separate expected-to-fail claim asserting successful admission. Positive controls cover those same histories under the safe implementation and replacement onto another target. There are 17 support declarations and 7 closed examples audited for axioms, addressing the three obligations above; these counts are not a count of distinct discoveries or CSS specification coverage.

## Explicit premises and exclusions

Query discovery, completeness, target association, and event delivery are external. Attribute keys are opaque naturals: a concrete mapping must preserve qualified-name distinctions or conservatively overapproximate them. The model does not implement namespace matching, CSS attr parsing, fallback selection, taint, dependency discovery, or animation interpolation. Query result and endpoint values are supplied; no arithmetic correspondence is claimed.

Native refinement must show that the temporary AttributeTracker’s queried names (including failed lookups) reach effect-owned storage, that all relevant rebuild/equal-property paths replace that storage, and that EffectSet aggregation and effect lifecycle preserve it. Attribute mutation callbacks must consult this aggregate and deliver normal semantic recomputation, surviving animation-only traversal and coalescing. A target-level request may rebuild more effects than strictly necessary. A correct native implementation may instead use a conservative attribute-sensitive bit, with a separate abstraction argument.

Only active registration is represented. Removing an entry does not model destruction of a retained native effect object or freshness of its dormant cache. Re-registering a retained effect, context changes while inactive, scheduler fairness, and same-flush delivery remain covered only by their separately stated obligations; the dormant-cache companion is referenced, not collapsed into this model. Pending targets are not consumed here; the normal-pass bridge is a one-step conditional observation. Its ghost stamp denotes a successful recomputation supplied by the inherited abstraction.

## Reproduction

Run `python3 -I -S -B artifacts/css-keyframe-attribute-watch-model-v1/replay.py --output /absolute/new/output-directory`. The runner authenticates source pins, the existing dependency capsule, and Lean 4.35.0-rc4; compiles in an owned temporary directory with two Lean threads; audits axiom sets; rejects the three false claims for the intended reason; and removes all owned scratch build products.

The author replay and failed intermediate compilation logs are retained. No browser execution, native build, staging/index mutation, canonical registration, or additional accepted bug is claimed.

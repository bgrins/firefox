# Completed lookup and evaluated-prefix certificates

Do not implement the earlier exact-single-var shortcut. A reusable extension should admit aliases, selected fallbacks and dynamic rollback through the existing substitution and retained-selection machinery. The final absolute FontSize AST remains an explicit facet boundary. This is an API/source proposal, not a native implementation or browser result.

## Graph discovery is not an evaluation receipt

PriorityReferences traverses recorded FontSize references before semantic Close/Publish. ReferenceWalk retains cursors and flags but discards observed values and primary/fallback decisions. It can classify SemanticOpen during graph discovery; later SCC closure may change the invalid/default map outcomes. Complete shortcuts also cover absent and no-dependency values without a node. Thus neither walk completion, map presence nor generic Complete proves an immutable value was consumed. Preserve this graph traversal and its semantic edges separately.

The actual evaluation boundary is `Cascade::substitute_variables_if_needed` calling declaration substitution. The frozen provider's `substitute_one_reference` currently treats missing var entries as invalid, recursively substitutes unresolved universal entries, and maps recursive Err(()) to fallback selection. That behavior cannot supply a scheduler readiness certificate without distinguishing unfinished work from settled invalidity.

## Concrete lookup API

Add a certifying substitution mode whose var/typed-attr lookup returns one of:

- `Pending(target, session)`: no value/fallback authority; propagate a distinct suspended outcome.
- `SettledInvalid(binding identity, invalidity provenance)`: fallback is permitted.
- `SettledValue(binding identity, exact value, provenance)`: retain CSS serialization boundaries, taint and the actual computed/universal representation.

A binding identity includes registration/namespace as applicable, semantic session and a value revision or immutable owned value identity. Provenance distinguishes settled graph publication, no-dependency local value, inherited/initial value and proven absence. A missing map entry needs explicit absence/invalidity evidence; a present unresolved value is not settled. Alias values require transitive finality evidence. A frozen map view must remain stable through evaluation and certificate use; comparing a map fingerprint afterward cannot repair an already published stale value.

Produce the read receipt at **actual successful substitution/parse**, not at ReferenceWalk completion. Key it by declaration occurrence, raw Arc, substitution property context and session. Record actual terminal lookups, their primary-valid decisions and chosen fallback paths. Unused fallbacks contribute no evaluated reads. Include environment results and attribute namespace/raw-input/consumer parsing context; retain attribute taint and token metadata. Registered values additionally depend on their real computation prerequisites: a partial computed-size certificate can authorize its narrow read but does not certify arbitrary font metrics.

The resulting declaration evaluation is either `Pending(retained state)`, `Evaluated(owned operation, read receipt, effects)`, or an explicit invalid declaration result. Pending must not be represented by the current Err(()) invalidity channel. The completed operation enters `MetricPreparation::retain` exactly once. Existing longhand/context/Arc/state checks remain required.

There is an unresolved implementation choice at partial effects: either retain the substitution cursor/output and effect state across Pending, or obtain a stable input lease before beginning the existing substitution so its actual lookups cannot suspend. Do not call the current function, observe a late Pending, discard its output and silently retry. Shorthand-cache writes, parsing/random bookkeeping and attribute-tracker effects require an actual commit/retention audit. The frozen source reads here establish the API gap, not that either transaction is already implemented. Legacy noncertifying callers need not change behavior merely to add this opt-in producer.

## General evaluated prefix

`MetricPreparation` already owns the cursor, waiting raw Arc, initial/local rollback state and substituted operations. Its `retain` uses the **resolved** RevertKind and advances the actual declaration chain. A reusable validator can consume that retained visited trace: each skipped/eligible entry has occurrence/priority and rollback state; each dynamic eligible entry has its evaluated operation and valid read receipt. Reject encountered APPEARANCE_BASE gates until their eligibility has a stronger proof. Dynamic rollback then extends the checked prefix naturally, including newly skipped candidates, until the actual terminal absolute operation. Never-reached lower gates are irrelevant. No special var grammar is needed.

Custom selection provenance is a separate missing input. `iter_declarations`/`cascade_custom_property` see custom priorities, but current Declarations stores only longhands. Preserve the custom winner/default/inherited source and the visited-prefix stability witness there, including skipped gated candidates. Before a receipt survives adding APPEARANCE_BASE, its own selection and transitive read selections must remain stable. Merely pinning the current custom value does not prove it was the correct final winner. Input readsets for the absolute size and XTextScale operation remain the existing separate obligation; no whole-property completion or new scheduling SCC edge follows from evaluation success.

## Concrete rejection cases and next tests

A direct source-shaped counterexample to naive map admission is `font-size:var(--a,30px)` while --a is an unresolved universal value referring to --late. If --late is only unavailable because its computation is Pending, treating that absence as invalid can choose30px; a later settled20px binding changes the result. The certifying lookup must suspend before fallback. This is a hypothetical scheduler-state discriminator, not an observed browser bug or claim that the current graph necessarily reaches that state.

Other required checks: a completed alias chain ending20px/30px; settled-invalid primary selecting an absolute fallback; valid primary with unused cyclic fallback; dynamic revert-layer skipping a same-layer declaration then selecting an absolute winner; a gated candidate newly reached after rollback; same raw Arc under distinct consumers; attribute invalidity that depends on typed parsing; registered font-relative binding still Pending; repeated suspension with one substitution/effect commit; and later ordinary completion applying the size operation only once. Initial/Inherit/Unset, invalid or nonabsolute terminal operations must transfer retained work to the ordinary path without being promoted to the absolute facet or reevaluated blindly.

The formal extension can prove actual substitution stability under immutable **completed** bindings, including settled-invalid outcomes, and then prove evaluated/visited/rollback-prefix agreement from the executable certificate. Native finality, provenance, side-effect retention, snapshot ownership and scheduler progress remain refinement obligations. Existing PriorityReferences closure alone cannot discharge them.

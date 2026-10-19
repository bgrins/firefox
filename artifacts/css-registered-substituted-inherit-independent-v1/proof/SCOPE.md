# Scope and source correspondence

This component starts after successful substitution and recognition of a sole `inherit` keyword for a custom property. It models the selected parent/root publication and dependency bit, then a projection of change classification, child hints and conditional recascade. It does not prove substitution parsing or the rest of CSS-wide keyword handling.

## Model to source

- `resolve` corresponds to the `is_var` CSS-wide Inherit branches in complete original/candidate `substitute_references_if_needed_and_apply`. Root uses the admitted computed initial. Nonroot reads the registration-selected parent Option and inserts/clones Some or removes None. Candidate ORs the reset dependency for inherits=false. This is a selected-value projection: unrelated map entries and values are not modeled here. Incoming state is after any substitution-side effects; no claim erases their flags or taint.
- `State.otherFlags` abstracts bits other than INHERITS_RESET_STYLE. `StyleBuilder::add_flags` OR and `build` publication are bound. The marker is a local style dependency, not automatically inherited. Root/inherited registration exclusions are checked.
- `difference` follows the complete GeckoRestyleDamage function's ordinary result, inherited-map change and reset-map change order. Ordinary inherited equality comes from Gecko_CalcStyleDifference's inherited struct mask. Booleans represent provider observations; semantic equality, including NaN/value/taint distinctions, is not proved.
- `childrenHint` follows the relevant change/reset-only branches of `accumulate_damage_for`, with earlier forcing recascade summarized as otherForce and reset structural exceptions as resetForce. Other hint bits are omitted. `recascade` is the first two branches of `needs_to_recascade_self`; its later font-relative condition and other restyle-kind overriding branches are outside this projection. Root source records retain them so they cannot be mistaken for proved complete behavior.
- `resetEventHint` supplies a reset-map-only parent observation: ordinaryChanged=false, ordinary inherited and inherited custom equal=true, reset custom equality=!changed; both forcing inputs false. `reset_only_provider` and `exact_conditional_consumption` derive the resulting gate rather than assuming the flag alone causes scheduling.
- `refresh` means the caller honors that gate and runs the selected resolution with the fresh parent Option, same registration and same effective substituted Inherit declaration. It is a conditional scheduler contract, not an implementation of traversal or graph evaluation.

## History contract

`EventReady` says an event reported unchanged actually retains the selected parent value. `HistoryReady` applies that condition at every consecutive parent step. Changed observations may conservatively overinvalidate; false negatives that change the selected parent value are excluded explicitly. Payloads need no decidable or reflexive equality. The independent `expected` folds every parent input, without consulting markers, hints or change observations.

`publication_history` proves any finite admitted history ends with that reference parent value, keeps the dependency and preserves other flag bits. No-op histories are included. It requires fresh parent inputs, registration stability and execution of the selected source branch when recascade occurs. It does not establish DOM mutation delivery, dirty traversal, pseudo scheduling, rule-cache/registration-cache freshness, animation scheduling, or concurrent ordering. `unchanged_event_requires_soundness` exposes the result when the change-provider premise fails.

## Explicit native boundaries

The source ledger contains 13 complete definitions, not a verified Rust/C++ compiler translation. The extractor uses exact native indentation and names, validated against retained definitions; it is not a general parser. Containers, cloning, Cell representation, flags lowering, heap/normal completion, source syntax and compiler are trusted boundaries. Source-only replay compiles Lean and checks exact patch application; it does not compile Firefox or a native facade. Numeric payload computation and the initial-cache repair are admitted as Option inputs. No universal inherited map or all-CSS theorem is claimed.

Four mutants are compiled Lean model mutations, not compiled native Rust mutants. Each unchanged concrete witness first passes; the mutated definitions still compile; then the same witness is rejected specifically as a false `decide` proposition. The witnesses cover missing marker, marking only present parent, reversed registration guard and dropping conditional hint consumption.

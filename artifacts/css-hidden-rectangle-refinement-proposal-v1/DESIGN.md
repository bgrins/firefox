# Whole-state rectangle observation refinement

Design only. Add a small generic observation adapter and one rectangle example module; reuse the existing transition runner. The substantive addition is observing geometry that depends on provider-updated ancestors, not proving readiness again.

## Existing work and imports

`CssSemantics.TransitionMachine` already provides `run`, `Runs`, `run_iff` and `Runs.preserves`. Use that runner for mutation/query histories. `GuardedState` is variable-cycle bookkeeping; `OrderedQueries` is selector enumeration. Neither is a geometry lifecycle abstraction. No other accepted generic observation/lifecycle implementation was identified; broader observer architecture notes are proposals.

`Hidden.geometryQuery` returns a selected `Hidden.Frame` whose geometry is only a `Size`. `Subtree`/`LineReady` provide marking and admission premises. `ColumnReadiness` and `ProviderPath` model provider lookup, hidden-ancestor selection and eligibility, without observation of updated geometry. Preserve those boundaries rather than folding them into a new query framework.

Proposed imports: generic `CssSemantics.ProviderObservation` imports only `CssSemantics.TransitionMachine`. A separate `MathMLRectObservation` example module imports it plus the authenticated `Hidden`/`Subtree` modules for the explicit size view and readiness adapter. `LineReady` remains a referenced interaction-control model, not a necessary dependency. No existing module needs rewriting.

## Small interface

Parameterize by `State`, stable `Target` and `Observation`:

- `admitted : State → Target → Bool` supplies the existing admission decision.
- `force : State → Target → Option State` returns the whole updated modeled state.
- `observe : State → Target → Option Observation` resolves the target in that returned state.
- `query` returns `Option (State × Observation)`: select the forced state when admitted, otherwise the original state, then call `observe` on that selected state.

Target denotes a stable element/identity key, not a borrowed native frame pointer. Re-resolution after forcing can fail. `none` means no successful abstract observation; it does not assert rollback of native side effects. The first implementation need not model failed partial mutations.

A thin session adapter stores the current world and emitted observations. Its mutation and query events run through existing `TransitionMachine.run`. Do not introduce a second recursion over histories or conflate the observation with a replacement for the selected frame's size.

## Required results, with limits

1. **Observation after provider update.** A successful admitted query emits `observe after target`, where `after` is the state actually returned by `force`. The contract must retain both that state and the emitted value. A deliberately incorrect adapter that samples `observe before target` should fail the positional witness below. This is an ordering/observation contract, not proof that the provider is a correct CSS implementation.
2. **Observation erasure commutes.** For any `erase : Observation → SizeView`, using `Option.map erase ∘ observe` must produce exactly the same returned state and the erased observation as mapping the result of the full query. Lift this to histories using the existing runner, preserving the same mutation/force transitions and failure outcomes. Crucially, erase observations, not ancestor state: dropping position-dependent state before calling the provider is not licensed by this law.
3. **Position distinguishes equal sizes.** Prove the concrete paired-state counterexample below, including failure of a selected-size-only update and of pre-force observation. Evaluate a two-query history with the reference provider to expose first/repeat results; its second query is unforced only when the returned state really makes admission false.

These are the proposed mathematical obligations, not existing theorems or checked implementation. Reuse `Subtree.clear_root_path_marks` when connecting repaired dirty state to admission; add no second theorem that merely says a marked clear path is eligible.

## Concrete c3 observation witness

Define `Rect` with integer x, y, width, height and `eraseSize r = Hidden.Size.mk r.width r.height`. For the small witness, modeled state contains a leaf-local rectangle, an aggregate ancestor translation, and eligibility/hidden-ancestor fields. Observation translates the local rectangle by the aggregate offset.

| State | Leaf-local rectangle | Aggregate ancestor translation | Observed rectangle |
|---|---|---|---|
| stale | [0,0,40,16] | [70,25] | [70,25,40,16] |
| reference | [0,0,40,16] | [30,10] | [30,10,40,16] |

The local leaf state and size-erased observations agree, but full observations differ. Overwriting the stale leaf size with the already-correct40×16 leaves the wrong rectangle unchanged. A reference whole-state provider updates the ancestor translation and clears eligibility; a selected-size-only provider does neither positional repair. Sampling the stale observation before invoking the correct provider also produces the wrong emitted rectangle, despite ending with the reference state.

This models the observation footprint of c3, not a complete frame heap or proof of the native y-position setter. The trace directly records local leaf rectangle0,0,2400,960 and the DOM rectangle70,25,40,16; the aggregate translation is their difference in CSS pixels. The reference tuple comes from the calibrated visible peer. Do not assign y25 to a particular native ancestor without further evidence. Parent chains, fragments, transforms and scrolling are not implemented in this initial witness.

## Compatibility with Hidden and native code

Observation erasure is unconditional for the same whole-state lifecycle. Equivalence to `Hidden.geometryQuery` is different and conditional: admission, selected-target identity, forced-provider size output, completion and any represented cache fields must correspond. There is no automatic whole-world-to-Hidden.Frame erasure, and MathML's unconditional output publication is not Hidden's cache-miss transition. Initially compare only the size observations under explicit provider correspondence, without claiming a full state refinement.

The native bridge must still establish that forced layout updates the relevant ancestor-dependent observation state, that the target is safely re-resolved, and that the observation composes the actual coordinate spaces. The generic provider contract deliberately permits changes outside the queried frame. Neither a successful readiness proof nor a selected-frame Size replacement establishes those obligations.

Implementation can follow in a small standalone proof capsule with pinned imports. Acceptance should require the erasure/history statements, the equal-size/different-position witness, and rejection of both erroneous observation adapters. Tie its four-tuples to the retained c3 trace and final WPT, keeping reference-provider arithmetic distinct from a verified Gecko layout algorithm. No compiler, native/build/browser action, production edit or index write was performed for this proposal.

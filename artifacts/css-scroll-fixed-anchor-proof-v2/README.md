# Fixed-anchor interpreter refinement and native trace companion

This v2 completes the interpreter-agreement extension required by the original fixed-anchor scope. Frozen v1 remains unchanged. **This is universal Lean interpreter agreement under explicit provider/rank premises, with bounded C++ execution. It is not universal C++ refinement or a memory-safety proof.** Final producer status is recorded in `FINAL-v1.json`; root replay and independent review remain required.

## Replay and source capsule

```
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-scroll-fixed-anchor-proof-v2/verify.py --live
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-scroll-fixed-anchor-proof-v2/check.py --out NEW_EMPTY_DIRECTORY
```

The output directory must not exist. Runtime inputs are authenticated before and after the entire check. `--skip-mutations` is an incomplete preflight and omits the required extension. `SOURCE-ONLY-v1.json` lists the standalone source closure: copy those paths plus the manifest itself, preserving relative paths. `verify.py --source-only` requires no producer binaries/logs. Exact external compiler/Lean/SDK paths remain prerequisites, not bundled hermetic tools.

## What v1 did and did not establish

`V1-BOUNDARY.md` preserves the preceding boundary description. Its complete extracted classifier, traversal, public selection and flag transitions passed bounded comparisons; its structural `Plan` theorems establish exclusion/safety/preservation. It did not implement the separately defined native-shaped Lean traversal and universal agreement theorem required by `SCOPE-v1`. Its universal visit-preservation theorem covered examination IDs, not the richer required semantic trace. The independent/root review correctly kept that milestone incomplete. `PROVENANCE-v1.json` records the frozen predecessor identity without rewriting it.

The v1 executable core remains here, including 48 audited theorems, 4,929 original/candidate native cases, 12 compiling semantic native mutants, six Lean proof-failure-plus-executable-witness mutations and eight distinct diagnostics. The separate removed-ancestry assertion is still not counted as a completed semantic corpus.

## Independent algorithms and universal theorem boundary

`Traversal.lean` adds 37 audited theorems. The semantic `Program` retains candidate occurrences, child/rest alternatives, frame boundaries, raw slot resolution and list/pass annotations. Its compiler performs structural expansion, never classification or winner precomputation. Its `interpret` evaluates the four decisions independently.

`nativeSlots`, `nativeFirst`, `nativeBody` and `nativeFrame` instead recurse directly over the raw graph/list representation. They do not call the compiler or specification interpreter. They implement first-pass filtering, slot order, immediate acceptance, PassThrough/Traverse child return and fallback, then the first matching Absolute list as a second pass. Both algorithms share the independently modeled classifier and elementary provider definitions; this theorem does not by itself prove the C++ classifier equivalent.

`traversal_agreement` proves equality of the entire `Outcome`: selected Pick, ordered semantic event list, and exhaustion bit, for every graph, finite list structure and fuel. Exhaustion is explicit and propagates before normal fallback. `Ranked` requires decreasing rank across every eligible resolved edge in retained first-pass lists and the chosen absolute list. `ranked_program_stable`, `ranked_no_exhaustion`, `ranked_complete_refinement` and `any_sufficient_fuel_agrees` then establish complete non-exhausted traversal and independence of sufficient fuel. Returning ordinary null at a cut-off is not permitted.

The graph is a total Nat-to-Node provider, with finite lists. The theorem therefore handles every finite-ID fixture and more generally every finitely branching reachable graph satisfying the rank premise. Cycles in effective descent violate the premise; repeated sibling/alias/absolute visits do not. Empty and skipped list boundaries remain observable. Absolute access deliberately selects the first matching list even if duplicate kinds are supplied. Duplicate kinds and identity aliases are abstract adapter robustness fixtures, not asserted Gecko frame-tree constructions.

A slot whose resolved target equals itself bypasses proper-ancestor checking, matching the actual `child != realFrame` branch. Other aliases require the target's supplied `within` observation. This is explicit in v2; the older `Anchor.resolveSlot` helper is not used by the new refinement. Its older distinct-alias corpus remains independently checked. The v2 Python provider oracle similarly handles identity targets without inventing an ancestry call.

Safety, selected-occurrence and excluded-route barriers are proved directly for the richer specification program, then selection safety transfers through the universal interpreter agreement. This is the explicitly equivalent structural safety route allowed by the extension scope; no unproved erasure theorem is claimed. The excluded-subtree statement retains its absent-alternate-route premise. `native_nonfixed_full_trace_preserved` and its reachable-program variant preserve the complete outcome; public gating/refinement/selection safety are also proved. The public flags/offset/dirty/suboptimal bridge remains complete bounded native execution and the original abstract transition lemmas.

## Native binding and instrumentation

`bridge.py` still authenticates and extracts complete ordinary bodies: `ExamineAnchorCandidate`, `FindAnchorIn`, `FindAnchorInList`, `SelectAnchor`, `CanMaintainAnchor`, `SetAnchorFlags`, the result enum and placeholder helper bundle. Ordinary source generation is verbatim.

`instrument.py` produces a **separate derivative translation unit** with 14 authenticated edit entries per variant. Each records old/new text, exact occurrence count and before/after body hashes. Logging reads stable adapter IDs and already computed classification/return values. It does not call ancestry, geometry, child-list or classification providers a second time. Five separately inventoried adapter edits maintain a separate trace vector. The checker reverses both edit inventories in reverse order, checks each intermediate hash and occurrence count, and requires byte-for-byte recovery of every extracted body, the original adapter, and the complete ordinary translation unit. Corrupted-count controls must be rejected for both inventories and variants. Each instrumented row must match the ordinary run's complete public values and original provider events exactly before its semantic trace is compared. This equivalence is bounded evidence, not a universal instrumentation-transparency theorem.

Semantic event encoding, in its own third pipe-separated native output field:

| Code | Meaning |
| --- | --- |
| `Eid` | Enter frame traversal |
| `Lparent:pass:kind` | Enter retained first-pass list (pass0) or absolute pass (pass1), including empty lists |
| `Kparent:kind` | Skip a first-pass out-of-flow list |
| `Rslot:target:accepted` | Actual slot resolution and ancestry result where applicable |
| `Did:decision` | Actual classifier result, Exclude/PassThrough/Traverse/Accept=0..3 |
| `Nid` | Descend into that candidate |
| `Bid` | Traverse fallback after a null child result |
| `Usource:selected` | Accept, descendant-success or fallback return |
| `Fframe:selected:exhausted` | Frame call completion; native C++ always has exhaustion0 |
| `Zselected` | Public final selection, including disabled null |
| `Xframe` | Model fuel exhaustion, never allowed in a ranked native corpus row |

A failed child return is visible as `Fchild:-1:0`, followed by sibling traversal or explicit fallback. The original provider trace uses its original schema in a different field; do not confuse its flag-event `F` with this semantic frame event.

## Bounded independent comparison

`semantic.py` uses an iterative activation stack and a decision table over raw observations, separate from both recursive Lean implementations and C++ control flow. It also validates effective traversal ranks. `lean_semantic_cases.py` independently constructs Lean observations from raw flags/rectangles and checks supplied ranks against raw list/alias edges inside Lean before evaluating both programs.

The extended corpus has 4,936 cases: 4,170 direct classifier and 766 public graph cases. Seven additions cover identity aliases, external identity targets that are otherwise excluded, first-match duplicate Absolute lists, repeated ordinary kinds, empty/skipped lists, same-null-winner/different-flow controls, and nested PassThrough return after Traverse fallback. Every original/candidate ordinary and instrumented native row, and all four Lean outcomes per row, must agree with the independent expected state/trace. The inherited 12 semantic native mutant binaries are also executed over the entire extended corpus; each must exit zero, emit all rows and produce a selected-value/state difference. Their compiler receipts remain in the parent run directory.

Six new Lean mutations challenge excluded descent, omitted skip events, reversed list order, Traverse fallback, identity-target ancestry and exhaustion becoming null. Each separately fails theorem compilation and successfully executes explicit reference/changed counterexamples with exact expected output. Three have unchanged selected IDs but changed required semantic flow. A zero-fuel witness tests model exhaustion semantics; it is not a valid native ranked-corpus execution. The six inherited Lean executable mutations remain required.

A separate instrumentation diagnostic removes a skip trace write. It must run the complete extended corpus with unchanged values/provider events and detectable semantic trace differences. This tests the observer gate; it is not credited as a native algorithm bug mutation. Assertion failures, invalid provider graphs, missing API, source drift and prohibited proof tokens remain diagnostics.

## Providers and limits

Real frame construction/ancestry, stable child lists, style and sticky predicates, geometry, continuation unions, ownership and no mutation during traversal remain bridge assumptions. Fixture storage is stable and initialized; `Frame()` is an explicit owner adapter, not copied containing-object pointer arithmetic. Highlight invalidation only exercises singleton continuation chains (`FirstContinuation=this`, next=null); continuation classification has separate observations. There is no universal continuation-chain highlighting theorem.

Toolchain executable hashes, compiler realpath, actual versions and SDK settings are checked. Native runs use UBSan and implicit-integer-truncation sanitization. No ASan execution or memory-safety proof is claimed. The root's accepted native/WPT browser evidence remains bound by retained source and receipt hashes; this producer runs no browser or shared build. No scroll-adjustment, suppression-endpoint, APZ or scheduling theorem is added.

## Preparation history

Development logs retain intermediate syntax/proof errors and successful native/Lean/witness preflights; none substitutes for the full gate. `preparation-v1` completed the initial combined gate successfully, then was superseded to require the inherited native semantic mutants on all 4,936 extended inputs as well. `preparation-v2` also completed successfully, then was superseded to add executable reverse-edit recovery and corrupted-count diagnostics. Only the successful preparation named by `FINAL-v1.json` is accepted producer evidence. Root replay and independent review decide whether the original milestone is complete.

# Reuse existing guarded profile; no canonical defect

**Conclusion:** the ordinary unused-fallback witness is already covered. VariablesGraph/VariablesBase intentionally implement the 2022 CR snapshot, while the canonical guarded profile separately implements lazy fallback and active cycle marking. `CssSemantics.GuardedExamples.snapshot_draft_difference` already proves the normalized version of this witness. No new theorem, canonical fix or proof-credit increment is justified.

I initially inspected only the static model and built a smaller duplicate exploration before root identified the documented modern profile. That exploration is retained with status SUPERSEDED_DUPLICATE_EXPLORATION_NOT_FOR_ADOPTION and explicit zero credit; its fuel and persistent historical mark list are weaker than the existing model. It must not be integrated. The present report supersedes any implication that an existing canonical obligation was missing.

## Existing coverage to reuse

| Obligation | Existing source/theorem |
|---|---|
| Valid primary suppresses even cyclic fallback | GuardedExpr.evaluate fallback branch; GuardedCompletion.Evaluates.fallbackValue; GuardedExamples.snapshot_draft_difference |
| Cycle participant cannot recover through its own fallback | GuardedCompletion.resolve final owner check; GuardedExamples self/pair cases |
| Outside consumer can recover | GuardedExamples pair --c case |
| Remaining top-level substitutions run after failure | GuardedExpr.append_after_failure and missingFirst/missingLast/markedFirst examples |
| Frame-scoped marks survive callees and disappear on owner return | GuardedState.pop laws, GuardedSolver.resolve_marks and resolve_fresh_marks |
| No arbitrary recursion cutoff | Finite remaining-declaration support, resolve_iff, expand_eq_resolve with proved budget bound |
| Fresh-request determinism and interpretation | GuardedSolver.compute_iff and Resolves.unique; no cross-request cache theorem |

The existing unused example uses --a/--b and token 1; the requested --x/--ok and token 10px is the same branch pattern with renamed properties and a different opaque literal. No new general renaming theorem is asserted here. The duplicate exploration measured the exact requested spelling against the historical model, but those measurements add no coverage beyond this existing family. Archived guarded-browser-evidence records an October 16 run with 25 matching queries; that is historical evidence, not a new browser run or a full conformance claim.

## Pinned-to-current deciding-algorithm comparison

I read the local historical HTML and checked its hashes against the existing version trace: Variables 2, October 9, `2ff256dc…`; Values 5, September 4, `567e5445…`. Current primary web pages identify Variables 1, October 9, and Values 5, October 27. Root independently downloaded their bytes (`2bf819fe…` and `f00cecca…`); those current full-body hashes are root-supplied, not independently downloaded here (local curl failed DNS).

The inspected deciding steps have the same behavior in both draft combinations: computed-name substitution/parsing before lookup, invalid-primary-only fallback, top-level substitution traversal with continuation after failure, repeated-context marking, and final owner validation. I found no new change in these algorithms requiring the fixed-name guarded profile to be rewritten. This is a bounded semantic comparison, not whole-document equality. The module name/location changed from the trace's Variables 2 URL to the current Variables 1 draft; the old CR snapshot remains a separate pinned profile. [Current var replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function), [substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function), [guards](https://drafts.csswg.org/css-values-5/#guarded), [property replacement](https://drafts.csswg.org/css-values-5/#property-replacement).

## Useful next extension: computed property-name arguments

This is an existing documented exclusion, not a newly introduced standards requirement. Current var step 2 substitutes its first argument and parses the result as a custom-property name; the checked VariableExpr stores a fixed String directly. Add a narrowly normalized name-expression form, preserving the existing fixed-name form as an embedding. Reuse GuardedState and the finite-support resolver, extending their expression relation rather than building a second cycle solver.

A name-expression evaluator must thread cycle marks from name evaluation into the subsequent target lookup and fallback. Decode a successful name token sequence through an explicit exact-name parser contract; distinguish invalid, valid empty and wrong-shaped tokens. Parsing failure must not invent a lookup under an arbitrary token spelling. Resolve the decoded target in the same active property stack. Only then apply the existing invalid-primary fallback rule. A marked enclosing owner still fails its final check. Names must preserve exact identity; do not add reserved sentinel names or ASCII normalization.

Four proposed normalized controls, not browser observations:

1. `--name:--ok; --ok:10px; --x:var(var(--name),var(--x))` → 10px; unused fallback stays unvisited.
2. `--name:--x; --x:var(var(--name),20px)` → invalid; the dynamically selected self-reference marks --x.
3. `--name:10px; --x:var(var(--name),20px)` → 20px; a length token is not a property name, and no property named 10px is queried.
4. `--name:var(--x); --x:var(var(--name),20px)` → invalid; marks generated while evaluating the name survive fallback.

These predictions follow the current primary var algorithm under the same ordinary/unregistered/no-spread assumptions. The extension should first prove conservative embedding of fixed-name expressions, preservation of marks across name decoding, and finite-support termination for dynamically selected declared names. Full CSS token parsing may remain an explicit adapter premise; it cannot be replaced by treating every String as an accepted CSS name. The exact native/browser parser support is unmeasured here.

No implementation is supplied in this review. Registered types, taint, custom functions/context identities, spread, native caches, active animation providers and animated SCCs remain separate obligations. The useful next step is this name-expression adapter, not another legacy-versus-modern fallback proof.

## Evidence and limits

REFERENCES pins the inspected canonical sources, trace and historical HTML; no canonical or shared .lake files were changed. The initial duplicate exploratory compiler runs are preserved separately and excluded from new proof credit. This reuse review performed no additional compilation, browser run, native/index/ledger edit, acceptance change or normative coverage increment. Spec-trace and webspec-index workflows were consulted; unavailable webspec-index was replaced by manual primary-page reading, with no claim of exhaustive generated trace enumeration.

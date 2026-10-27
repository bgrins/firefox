# Demand completion and stable substitution

This artifact proves a conditional property of substitution against a partially completed provider map. If evaluation finishes without requesting unfinished work, any later completion that preserves already completed inputs produces exactly the same value or CSS-invalid result and the same ordered read trace. It also proves a stronger local replay theorem: agreement on just the keys reached by the first evaluation is sufficient, including when that evaluation stopped at a demand.

This is a new standalone Lean model, not an extracted Rust proof, a browser repair, a canonical CSS coverage increment, or a proof of the animation completion scheduler. It is tied to the sealed typed-attribute demand proposal and the versioned CSS Variables trace in REFERENCES.json. Those source artifacts were authenticated before constructing the model. The root owns any subsequent application, compilation or correction of that proposal; this artifact certifies no live native revision.

## Model and theorem

`Slot` distinguishes a completed token value, completed CSS invalidity/absence, and pending work. `lookup` checks the pending set before reading the cached value: pending may mask stale cached tokens. `Refines old current` permits any change to an old pending slot, including leaving it pending, but preserves every old known value and every old invalid slot. A merely absent map entry is not completed invalidity when its winning provider remains pending.

Expressions are finite normalized trees of literal tokens, unconditional invalidity, references with fallbacks, and left-to-right sequences. An omitted fallback is the invalid expression. References evaluate a fallback only for completed invalidity. Pending returns a demand immediately, without evaluating fallback. Sequences stop at the first invalidity or demand. Token values are abstract lists of natural numbers; their numbers have no built-in CSS parsing or numeric-conversion meaning.

Every result carries the exact ordered list of lookup keys visited, retaining repetitions. The trace includes invalid and pending lookups and excludes unused fallback references and the unvisited suffix after an early stop. This is the model's trace, not an instrumented native AttributeTracker or scheduler log.

The proof is not an assumption that whole outcomes agree. `replay_reached` proceeds by structural induction, reconstructing branch choices from the old evaluation's reached lookups. `settled_reached_known` proves that a completed evaluation reached no pending slot. `settled_stable_with_trace` combines these facts with provider coherence. In particular, an early genuine CSS-invalid result stays invalid even if unread later providers finish. Requiring every lexical reference to finish before accepting such a result is stronger than this theorem needs.

`complete_is_settled` proves that a finite expression over a map containing no pending slots cannot demand. It does not prove that the actual dependency graph can be completed or that a scheduler terminates. `completion_order_independent` compares two extensions of an **already settled initial evaluation**; it is not confluence of arbitrary cyclic or unfinished computations. `fillPending` provides a concrete coherent complete extension for examples, but it is not an implementation of provider computation.

## Native correspondence and limits

| Native source point in the captured proposal | Model correspondence | Remaining obligation |
|---|---|---|
| `substitute_one_reference`, Var branch checks pending before `get_var` | `lookup`, `reference_pending`, `pending_masks_cache` | Pending membership must describe the actual current winning provider, including absent or stale typed entries. |
| Recursive substitution returns `Demand` instead of treating it as `Invalid` | A reference never converts pending to invalidity or fallback | Unresolved token-map recursion and active cycle contexts are outside the finite normalized expression model. |
| Final `Some(substitution)` return precedes fallback evaluation | `unused_fallback` and reference evaluation | Tokenization, fallback boundaries, substitution-kind rules and CSS-wide keyword handling must normalize correctly. A valid token value that later fails a target syntax is not a missing primary. |
| `do_substitute_chunk` traverses references in order and propagates errors with `?` | Sequence early stopping and exact read trace | Token concatenation is modeled without native serialization limits, taint ranges, allocation failures or parser errors. |
| `substitute_references_with_pending_and_apply` returns demand before CSS-invalid handling | Distinct demand and settled-invalid outcomes | This model does not prove the caller discards incomplete maps/effects or applies registered initial/inherited values correctly. |
| Typed `attr()` requests unprepared expanded names; prepared `None` is completed invalidity | Attribute keys can represent atomic prepared reads | Attribute text, namespace/type/URL context, current target, map membership and any type-dependent conversion must be coherent. Shared key identity alone does not prove this. The root clearing old attribute entries is a native mechanism, not a theorem here. |
| Pending prioritary prerequisites are checked before conversion | Prioritary keys can represent explicit required reads | The actual dependency classifier, transitive prerequisite sets and conversion context are not modeled. An empty pending set is a caller assertion, not a proven ready context. |

For the principal application, known provider slots must contain current completed substitution values. A universal value still containing references needs either a correct finite normalization or the native recursive machinery, whose correctness is not proved. Attributes and prioritary properties are tagged keys to permit explicit atomic dependency examples; they do not add semantic coverage of `attr()`, units, registrations or CSS property types.

Provider coherence is stronger than cache presence: it includes the same sample, target, winning declarations, registrations, inherited values, environment inputs and all context affecting any normalized lookup. A known invalidity cannot later be reclassified as pending or become valid within a coherent extension. If winner selection or context changes, a new evaluation epoch is required. The theorem does not prove freshness, winner admission, owner identity or absence of external mutation.

The model is pure. Native attribute tracking, cacheability flags, watches and style mutations may happen before a later demand. No theorem here proves their isolation, discarding or successful publication. The existing completion owner's effect buffering obligations remain necessary. Nor is the trace a complete declaration dependency graph: it records only the primitive reads of this normalized evaluation, not SCC traversal, prioritary classification or all authored keyframe endpoints.

## Versioned fallback and cycle boundary

The captured CSS Variables Editor's Draft dated 9 October 2026 and CSS Values 5 Editor's Draft dated 27 October 2026 select a fallback only when its primary is invalid. The versioned trace documents the older 16 June 2022 Candidate Recommendation's separate fallback-inclusive cycle graph. Ordinary Stylo already conditionally visits fallbacks, with a source reference to CSSWG issue 11500. This model preserves that primary-first behavior; it does not identify a new ordinary-cascade bug.

The finite expression model has no recursive property definitions or active guarded contexts. Cyclic providers may enter it only after an external cycle mechanism has correctly established their invalidity. In particular, this is **not** a model that permits a literal fallback to rescue a declaration participating in a detected cycle. Full normative cycle marking, fallback behavior of outside consumers, SCC traversal and animation-owner cycles are separate obligations. A theorem about lazy requests must not be substituted for those semantics.

## Actual checks

Lean 4.35.0-rc4 ran single-threaded in an owned temporary directory. Actual replay session 47076 completed with outer exit 0 (launch b41543, completion 552280). Both source modules and the axiom audit compile without warnings. All 17 named declarations were audited; only `propext` and, for three central/composed results, `Quot.sound` appear. No added axioms, `sorry`, or `native_decide` are used. Sixteen closed examples use kernel decision reduction. The owned scratch directory and generated object files were removed; the canonical library and native tree were not edited.

Six deliberately false claims were rejected by the kernel with exactly one decisive `decide`-false diagnostic each. Parser failures, reduction failures, unrelated errors and exit-zero logs do not pass the diagnostic gate.

| Rejected claim | Distinguishing observations |
|---|---|
| Treat pending as CSS invalidity and retain its fallback across completion | Wrong fallback 7 versus completed value 40. |
| Read a stale cached value before checking pending | Stale 7 versus completed 40; the correct initial result is demand. |
| Evaluate every unused fallback eagerly | Spurious demand for provider 1 versus completed value 20 with only provider 0 read. |
| Allow a previously completed invalid provider to change while retaining the old result | Fallback 7 versus newly available value 40; coherence is necessary. |
| Commute early invalidity with a later pending read | Invalid with trace `[provider 2]` versus demand with trace `[provider 1]`. |
| Omit the no-demand premise from completion stability | A taken fallback's initial demand becomes value 40 after completion. |

`INPUTS.json` pins the compiler executable, Init import, model sources and audit roster. `replay/CHECK.json` retains every child command, exit and log digest. The draft diagnostics are retained as development history and are not successful proof evidence. To replay, invoke `python3 -I -S -B artifacts/css-keyframe-demand-completion-model-v1/replay.py --output` with a fresh absolute output directory.

The next useful refinement is a separately reviewed correspondence for actual normalized native inputs and returned demand variants, including recursive universal values and typed-attribute preparation. Composition with the real winning-provider scheduler additionally needs cycle ownership, context readiness and effect publication invariants. This artifact does not establish those by renaming its abstract environment.

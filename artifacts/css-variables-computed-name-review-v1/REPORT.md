# Computed-name model: independent scoped review

**GO for research adoption under the documented normalized profile.** No semantic or proof blocker found. One negative-control description needs qualification below. This review authenticates and reads the existing root replay; it does not rerun Lean or claim current preservation measurements.

## Spec correspondence

Current Variables 1 var replacement step 2 substitutes the first argument, parses a custom-property name and then obtains that property's computed value. Its failed-parse branch says: “Otherwise, let result be the guaranteed-invalid value.” Step 4 permits fallback after that invalid result. Thus `lookupName` preserving the name-evaluation state on parse failure, followed by `evaluate.fallback`, has the correct ordering within the selected profile. A valid empty target value is distinct from failure. [Current var replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function).

The enlarged append form evaluates both branches even when the first token result is invalid. It preserves state for later substitutions, matching the top-level substitution loop. Property resolution checks active repetition before missing/base lookup, retains marks through fallback and invalidates the marked owner before popping its mark. These are appropriate uses of the existing guard representation. [Substitution and final context check](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function), [guard lifetime](https://drafts.csswg.org/css-values-5/#guarded).

**Trace verdict: REACHED** for name substitution/parsing before lookup and invalid-name fallback in this restricted draft scenario. Scenario premises: already-separated normalized var arguments, ordinary same-element winning declarations, no spread, custom functions, taint restrictions, registration defaulting or animation providers. This is a manual deciding-algorithm trace, not a generated exhaustive reference graph or a formal correspondence theorem. `webspec-index` is absent; official pages were read through the web tool without installing tools or changing the build environment. Variables identifies its October 9 draft; Values identifies October 27. The 2022 CR dependency-graph profile remains separate.

## Proof meaning

`embedded_resolve` is substantive compatibility: it equates the entire `(value, marks)` result with `GuardedCompletion.resolve` for arbitrary embedded finite entries, active/marked lists, parser, base and completion callbacks. The proof follows lookup/removal correspondence and recursive callback equality; it does not assume the conclusion in a transition premise. The static evaluator itself is reused.

`evaluate_preserves` is conditional on the resolver preserving its supplied invariant. `resolve_marks` discharges the relevant recursive invariant and proves containment plus preservation of incoming active-owner marks. `fresh_marks` means no marks escape a fresh invocation; it does not make a cyclic value valid or prove cache reuse across independent requests. Termination decreases remaining bindings on every successful expansion; missing dynamic names use the base callback, and active names are checked before removal can hide them. No arbitrary fuel is introduced. No list-enumeration independence, cost bound, winning-declaration selection or independent relational semantics for the enlarged language is proved.

## Parser and negative-control boundaries

`NameAdapter.exact` is a caller-supplied relation equivalence, and `parse_exact` projects that field. The generic solver takes the parser function, not a proof that it recognizes CSS. The example adapter accepts one tagged name containing **any String**: CSS validity of that tag is an external premise, not enforced by the datatype. Tokenization, escapes, whitespace normalization, the forbidden bare `--`, raw argument grammar and case-sensitive identity must be handled by an actual adapter. The embedding theorem's static references bypass this parser; it is not a theorem equating arbitrary static strings with parsed dynamic names.

The three negative files rewrite the same proposed false claim using a kernel-proved positive result, then obtain decisive false-proposition diagnostics. The exact log/exit gate rejects unknown identifiers, reduction failures, wrong exits and additional errors. Root evidence records all 18 gate rejection cases. This is stronger than counting arbitrary compiler failures.

**Scope correction:** `early-fallback.lean` rejects `run valid = 20px`; however `valid` uses a self-reference as its fallback, not literal `20px`. It is a decisive wrong-result negative, not an executed eager-fallback mutant. An eager evaluation of that cyclic fallback would mark the owner and produce invalidity under the modeled guard rules. The positive `valid_result = 10px` already distinguishes that behavior. Describe the existing negative accurately, or use a separately reviewed successor claim against invalidity if specifically advertising an eager-fallback mutant. No change to the sealed model is required for its existing statements to be correct. This clarification was sent to the integration author.

## Authenticated replay

Both manifests and every payload authenticate. The nine retained source copies match the source entries in IMPORT-PINS. Root session 83562 exited 0, terminal 44b7ed, and names the exact producer manifest. Its logs match the producer's final replay and exact expected logs: 25 unique named axiom inspections, 12 examples and three decisive false controls. Actual audited axioms are limited to `propext` and `Quot.sound`, or none. The replay gates recheck canonical import pins and owned scratch removal; this review relies on that authenticated historical execution rather than executing those checks again.

The 13 implementation/bridge statements include projections and adapted proof patterns; they are not 13 independent new CSS conformance results. Retain zero normative-coverage increment and no duplicate credit for the imported guarded solver. Native resolution, current animation providers, animated SCC policy and persistent caching remain outside this package.

Reviewer did not author this model or root replay. No canonical/native/index/ledger writes, compiler runs or browser runs occurred during review.

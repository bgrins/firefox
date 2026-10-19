# Reconstructing dependencies of successful substitution output

## Recommendation and scope

Add a narrowly named constructor such as `VariableValue::new_resolved`, used at two persistence points in `custom_properties.rs`:

1. The attribute branch of `substitute_references_if_needed_and_apply`.
2. The universal-registration branch of `Substitution::into_value`.

It should retain the successful CSS string and reconstruct its relative-unit flags by token inspection. Do not change the general `VariableValue::new`, and do not copy flags from the original declaration. This avoids scanning every serialized computed typed value and avoids copying unused fallback flags into newly stored results.

This is a source design, not a native patch. The retained candidate precedes root's separate attr-only non-custom collection repair. Its relevant constructors and substitution paths are the ones inspected here. Root reports that all four earlier graph-probe predictions reproduced; that message is not substituted for a retained browser receipt in this package.

## Exact output preservation

Build the same `VariableValue` as before, changing only `references.flags` to the reconstructed non-custom flags. Keep its reference list empty under the resolved-output admission. Preserve CSS bytes, URL data, first/last token serialization metadata and `explicitly_attr_tainted` behavior. Existing callers continue to copy `Substitution::attr_tainted` into the computed wrapper. No reserialization or default-taint change is needed.

The flags describe token dependencies, not a minimal dependency set after numeric simplification or type validation. A dimension inside a valid `calc()` is included even if algebra could cancel it. COLOR_SCHEME still comes from the registered syntax policy, not this relative-unit scanner. Root-element rem/rlh mapping remains at the existing consumer.

## Token scanner contract

For a syntactically valid, fully substituted component-value sequence:

- Inspect Dimension tokens and map their decoded unit through the existing `ReferenceFlags::from_unit` policy.
- Descend into ordinary function and grouping blocks, including `calc()`.
- Ignore strings, URL token contents, identifiers, hashes, comments and whitespace. The text `em` alone is not a dimension, and a string or URL containing `1em` contributes no unit dependency.
- Recognize arbitrary substitution-function blocks as an incomplete-summary boundary, rather than scanning possibly unused fallback contents as if they were selected output.
- Do not invoke property parsing, DOM providers, substitution, computed-value conversion or serialization while scanning.

The last point needs a concrete implementation decision before native acceptance. Recommended API shape is `resolved_token_dependencies(css) -> Option<ReferenceFlags>`: `Some(flags)` establishes the resolved-token contract; `None` marks malformed or still-unresolved input. The two callers must explicitly document their handling of `None`. Retaining the old empty flags on `None` is a bounded compatibility choice, not a repair or correctness claim for unresolved env payloads. Silently treating `None` as a complete zero summary would invalidate admission.

A recursive Parser walk is easy to express but needs a nesting/stack audit. Existing specified values have already passed parsing, but substitution can assemble deeper output; that does not prove a fresh recursive scanner is bounded safely. An implementation should reuse an appropriate tokenizer traversal limit or demonstrate a finite bounded stack policy. This package does not assume such a limit exists.

## Why not reuse the original parser's flags?

`parse_declaration_value_block` bubbles flags from every fallback, before branch selection. It also applies `from_unit` to identifiers and several other textual tokens, not just dimensions. Consequently its aggregate is unsuitable as an exact summary of successful emitted tokens. Re-running the entire declaration parser merely to extract its flags would retain those classification differences, allocate reference structures unnecessarily, and mix syntax/reference reconstruction with the narrower unit scan.

Scanning the actual successful output selects the right branch by construction. It does not resolve the separate question of the graph's original, pre-substitution root flags: `find_non_custom_references` and `visit_value_references` still use those summaries. The earlier unused-relative-fallback diagnostic and its normative ambiguity remain separate. This proposal fixes lost summaries at resolved cache entries; it does not claim all graph summaries become exact.

## Constructor and caller inventory

| Path | Output and current behavior | Proposed action |
| --- | --- | --- |
| Attribute persistence after substitution | Universal cached CSS; `new` discards all flags | Use resolved constructor; necessary for literal and chained relative-unit attributes |
| `Substitution::into_value`, universal branch | Universal custom-property output; `new` discards flags | Use resolved constructor; necessary for var/attr/env chains later consumed by a typed registration |
| Same function, typed registration | Calls registered computation, producing computed typed value | Keep unchanged; ordering must already have admitted the required graph dependencies |
| Trivial universal custom-property path | Retains the original `Arc<VariableValue>` without reconstruction | Keep unchanged; existing original flags remain, including their conservative limitations |
| `Value::to_variable_value`, universal variant | Clones the stored universal value | Reconstructed flags naturally survive this path |
| `Value::to_variable_value`, typed variant | Serializes specified or computed typed components through general `new` | Keep unchanged; a specified attr result reaches a persistence sink before becoming reusable universal data, while computed typed values are terminal |
| Unit-form attr substitution | Builds a dimension using `ComputedValue::new`, then returns a `Substitution` | Keep intermediate constructor unchanged; a persisted universal/attr result reaches a selected sink |
| `VariableValue::empty` / `push` | Temporary output assembly preserves bytes and adds separators; currently no flags | Keep unchanged for post-output scan design |
| `from_token`, pixels/int-ms/integer/ident helpers | Built-in environment values are absolute pixels, numbers, times, or light/dark identifiers | No relative-unit scan required for those finite constructors |
| `VariableValue::parse` | Unresolved specified input, with reference lists and conservative flags | Keep unchanged |

The indexed constructor inventory is retained under `discovery/`. It is an inventory aid, not proof that indexed bytes match this changed source. Complete local candidate files and the typed value serializer are retained and authenticated separately.

## Environment and unresolved output limit

`CssEnvironment::get` handles link parameters beginning with `--` by parsing arbitrary supplied text as a `VariableValue`. Its existing comment cites bug 2028998. The env branch of `substitute_one_reference` wraps that value directly; it does not recursively substitute any remaining var/attr functions. Thus successful return from `substitute_internal` is not an unconditional proof that all arbitrary substitution functions are gone.

This defeats an unconditional native theorem “all successful output is resolved.” An env payload such as `var(--x, 1em)` is a concrete source-level counterexample to that admission. A scanner must not mistake its unselected fallback for resolved dependency data. The proposed mathematical component admits only resolved token output and keeps the native admission obligation visible. Correct env chaining, fallback evaluation and provider behavior are outside this repair.

The current built-in environment evaluators emit no relative units, so the issue does not arise for their fixed forms. Direct registered properties using arbitrary env link payloads can also need ordering work before the persistence sinks; this proposal does not address that independent provider path.

## Alternative: carry flags through Substitution

Adding flags to `Substitution` would require updating borrowed chunks, empty output, generated env values, raw-string attr values, unit attr values, typed serialization, selected fallback recursion, single-reference fast returns, and composite `push` results. Original reference summaries cannot supply exact flags for a literal chunk: they include text outside the slice and unused fallbacks. Literal chunks would still need token scanning or new source annotations.

The carried approach can avoid rescanning large output, but adds transient state and more branch obligations. It should follow measurement if the narrow post-output scan is too costly. No performance-neutrality claim is made for either choice. The narrow constructor requires no new persistent field; scanning cost is linear in emitted token count, subject to the chosen tokenizer and nesting implementation.

## Token boundaries and separator counterexample

Flags cannot be combined from raw string pieces without a lexical correspondence condition. Separate pieces `1` and `em` each contain no dimension, but their plain concatenation is `1em`, which does. Native `VariableValue::push` inserts a comment when `TokenSerializationType::needs_separator_when_before` requires one; `1/**/em` retains two tokens and contributes no font-unit flag.

The scan of final CSS follows the actual bytes after this separator logic. A model of carried summaries needs an explicit bridge from piece serialization plus separators to the intended token sequence. It cannot assume arbitrary string concatenation preserves token kinds. Typed list serialization's first/last metadata and single-reference fast returns are additional bridge obligations; this design does not prove them.

## Proposed Lean component, before native admission

The useful bounded obligation is a selected-output composition theorem over arbitrary finite piece streams, not an identity lemma about a stored flag field:

1. Define semantic tokens with dimension units and inert tokens, with block contents flattened by an explicit tokenizer adapter. Define four relative-unit dependency predicates.
2. Define a replacement result as failure or a token list. A primary/fallback choice selects the primary on success, otherwise the fallback; failures propagate. Define a stream evaluator that appends successful literal/replacement pieces and inserts inert separators according to a supplied boundary predicate.
3. Independently define the accumulated dependency summary by joining summaries of only the selected pieces. Prove by induction that successful evaluation has exactly this summary, including failure cases and arbitrary primary/fallback payloads.
4. Prove inert separator insertion cannot add/remove dependencies, and arbitrary unused fallback changes do not affect successful-primary output or its summary.
5. State the source bridge conditionally: if the real tokenizer of final serialized output equals the modeled selected token stream up to inert separators, the scan and carried summary agree. Retain the `1`/`em` example as a counterexample without that condition.

This proves useful summary algebra for arbitrary streams. It does not prove CSS tokenization, serializer boundary metadata, native construction admission, branch eligibility, attribute/var provider stability, numeric simplification, SCC scheduling or observer equivalence. No theorem is implemented or claimed in this design seal. Native scanner handling of incomplete output and nesting should be settled before selecting its precise adapter contract.

## Controls required for the eventual implementation

Retain the reproduced attribute and universal-chain cycle cases and the acyclic 23px-versus-17px ordering case. Add nested calc dimensions; lh/rem/rlh distinctions with explicit element/root contexts; escaped and case-varied dimension units; inert strings, identifiers and URL text; number-plus-unit pieces requiring a separator; a successful primary with a different-unit unused fallback; and an explicitly unresolved env link payload if that provider can be exercised independently. These are concrete source-admission risks, not grounds to claim broader substitution correctness.

No live source, Git, build or browser operation was performed. The full historical C1–C13 and Tarjan obligations remain open.

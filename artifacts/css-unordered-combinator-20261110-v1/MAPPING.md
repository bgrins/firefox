# Mapping and trust boundaries

## Specification interpretation

`CONTRACT.md` and `PROPOSAL-FILES.json` were frozen before proof implementation and reviewed independently. They pin the current CSS Values 4 combinator/multiplier rules and CSS Text 3 property grammar. CSS Values source revision `f43d8bfcfdfd073cdf6d87f626a6831e1507dc8a` was the latest file-specific revision observed on 2026-11-11 UTC (commit date 2026-10-21); the rendered Editor's Draft agreed on the relevant rules. The previously frozen Text 3 and Display 3 sources retain their original revision metadata in `compatibility/property-sources.json`; they were not silently refreshed.

Primary anchors: [component combinators](https://drafts.csswg.org/css-values-4/#component-combinators), [component multipliers](https://drafts.csswg.org/css-values-4/#component-multipliers), [text-transform](https://drafts.csswg.org/css-text-3/#text-transform-property). Exact source excerpts and hashes are local. The readonly webspec-index failure is retained; no tool upgrade/cache modification was made.

Human interpretation chooses indexed component occurrences, nonempty distinct selections, contiguous chunks, and explicit group boundaries. The formal implementation does not prove this interpretation follows from English. In particular, full nullable-child semantics is deferred: CSS permits cases this supported subset refuses. `A? || B? || C?` can match empty under the specification; this implementation rejects that operator node rather than claiming CSS rejects empty. Optional subexpressions inside a nonnullable complete child remain supported.

## Formal chain

- `Selections` enumerates all ordered subsets structurally. `orders_spec` independently characterizes membership by no repeated occurrences and inclusion in the source. `index_orders_spec` specializes to bounded occurrence indices. There is no fuel, arbitrary permutation bound, or hidden uniqueness-of-keywords premise.
- `UnorderedMatches` existentially quantifies a nonempty `List (Fin children.length)` with `Nodup`, then matches the selected child grammars through intermediate input/remainder states. It does not mention `orders`, `plans`, `lower`, or executable `run`.
- `nullable_spec` relates the executable empty-input query to `Matches grammar [] []`. `valid_spec` characterizes the explicit arity/nonnullable domain.
- `lowering_spec`, `run_spec`, and `lower_matching` establish exact matching/remainder correspondence between lowering and the independent relation under that domain. `exact_remainder` prevents invented/discarded suffixes; `append_remainder` preserves arbitrary trailing input. These are language/remainder-membership results, not preservation of derivation multiplicity or parse-result order.
- `unordered_step` and `unordered_step_matching` connect the actual postfix opcode, reversed stack operands and remaining stack to the same relation. Each child opcode is interpreted first. `rejected_prefix` ensures a refused nested unordered child cannot be rescued by an outer sequence/alternative or later opcode.
- `legacy_execute` and `legacy_decode` preserve every old typed opcode program and arbitrary starting stack exactly. `legacy_encode` preserves the old Grammar encoder. Historical source files remain byte-identical; old program execution has 70 preserved rows. This does not claim newly supported `||` retains the old refusal: only the opt-in reader admits it.
- `text_json` kernel-checks decoding the quoted actual JSON value to `textGrammar`; `text_decode` checks the typed program. `text_language` proves permutation equality with the independently frozen 38-word oracle. `text_accepts` and `text_remainder` quantify over arbitrary normalized input/remainder lists, not a bounded test corpus.
- `Cases` additionally proves indexed duplicate text, non-associative grouping, nullable refusals including hidden nested nodes, required-child optionality, arity/stack refusals and exact trailing suffix behavior.

## Extraction and runtime seams

`extract_v2.py` is a separate opt-in revision. It tokenizes the reviewed notation subset, retains same-level `||` as an n-ary node, and does not flatten bracketed children. Its precedence is juxtaposition, then `||`, then `|`; `&&` is unsupported and rejected. References are also refused by this narrow parser rather than resolved speculatively. The pinned text-transform grammar is reference-free. Display's exact `display-listitem` production still refuses because it contains `&&`; no display claim follows.

The reviewed source-span selector is bound to the full CSS Text 3 source hash, exact property anchor and block/value/heading slices. Maps retain full expression spans and operator spans. This is not a generic Bikeshed parser: preprocessing, comments/includes, prose restrictions, source context and ambiguity beyond this selected subset are not translated. Unsupported or trailing notation is rejected, never truncated. Seven legacy notation examples compare ASTs exactly; older actual decoded programs additionally execute through the new reader.

`generate.py` emits a quoted Lean JSON value and typed fixture from the extracted program. The checker independently reconstructs and compares these files and the serialized JSON. This byte/value consistency check is ordinary Python, not a proved quotation procedure. `RunnerV2` imports only the actual JSON decoder/interpreter and executes the input file; it does not import the text-transform reference or fixture. Its fixed-file results are compared against the independent oracle, and a changed-valid file changes actual behavior.

`Lean.Json.parse`, JSON number lexical representation (including equivalent exponent spellings), Python extraction/quotation, OS/runtime and compiler execution remain outside the kernel theorem. Unknown opcodes, malformed arity fields and invalid stacks are refused. A kernel theorem over a JSON value does not prove a JSON text parser or arbitrary input-file integrity.

## Scope

Inputs are normalized keyword-token strings. CSS case folding, escapes, whitespace/tokenization, comments, implicit CSS-wide keywords, variable substitution and text-transform rendering are outside. Therefore rejection of the string `UPPERCASE` or `inherit` in the token-layer corpus is not a browser conformance assertion. No Stylo, Rust, browser, whole-property conformance, full CSS coverage or mechanically derived prose proof is claimed. The finite enumerative lowering is suitable for this small grammar research slice; its factorial growth has no production performance claim.

The only admitted proof axioms are Lean's standard `propext`, `Quot.sound`, and `Classical.choice`; individual declarations are audited. There is no `sorry`, new axiom, `native_decide` or arbitrary fuel.

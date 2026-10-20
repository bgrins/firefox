# Registered token boundary summary

## Scoped result

The Lean model proves a source-shaped accumulator returns the first and last classes of an independently flattened token sequence. This holds for every finite event list, arbitrary block bodies, comments, whitespace and empty streams; it is not just equality between two renamed loops. Arbitrary list composition is derived separately. Twenty-two theorem declarations are audited for standard axioms only.

The final v2 native candidate is bound at SHA256 `fd2b72943646fe84c22a16e21f21b8f890fc2782bc77e7db54d93db4d125ee93`. This includes `drop(input)` before moving the serialized String. V1's compile error is not hidden by a wrapper: the isolated checker extracts the entire parser initialization/loop/drop region from v2. The helper adapter receives an already serialized `&str`, so this replay does not compile the full generic Stylo method or prove its String lifetime; root's Firefox build owns that gate.

## Independent mathematical reference

`flattenOne` maps an ordinary token to its class, a comment to no token, and a block to its opener followed by an arbitrary list of interior classes and an actual closing Other. Interior classes may represent arbitrarily deep nested content; no endpoint property of that body is assumed. `reference` reads the head and last of the complete flattened list.

`step` instead follows the native assignment pattern: preserve the first non-Nothing class, replace last with the current ordinary class or closing Other, and leave state unchanged for an omitted comment. `loop_reference` proves an arbitrary initial-state invariant. `complete_summary`, `first_token` and `last_token` derive the real endpoints from it. `composition` and `arbitrary_list_composition` handle arbitrary finite lists. `serialized_pair` explicitly includes separator events between components: actual list ToCss inserts whitespace or commas, so raw component concatenation alone is not claimed to represent list serialization.

The model's `Option Class` represents Nothing versus every actual serialization class. Every non-Nothing native class has a distinct constructor, including WhiteSpace, OpenParen and Other. This makes the assumption that real emitted tokens do not classify as Nothing explicit in the class projection. The complete native classifier and setter are bound; translating that classifier into the type remains a source admission, not a kernel-verified Rust translation.

## Counterexamples and mutations

Kernel witnesses reject the original LP Percentage/Percentage summary for both a Dimension output and a Function…Other output. A separate percentage-first/dimension-last sequence rejects using the first component for the last boundary. Other witnesses distinguish opener-as-last, comment-as-slash and dropped whitespace.

The native replay compiles the actual full vendored cssparser with optional features disabled, and the exact extracted candidate loop. Its independent comparison uses the raw tokenizer over every input byte, suppressing pending block skipping and filtering only actual Comment tokens. This sees real closing tokens rather than assigning Other at a parser opener. Twenty-four manually expected fixtures additionally constrain that shared classifier/tokenizer reference. These include all four block types, nested contents, later siblings, comments, quoted comment-looking text, whitespace, escaped identifiers, URL forms, dimensions, percentages and list endpoints.

Four compiled loop mutants must compile and then fail a boundary assertion: opener-as-last, skip-whitespace, include-comments, and retain-only-first-last. No compiler failure counts as a successful mutation rejection. The initial development raw-reference shim lacked documentation and failed the crate's missing_docs lint; the retained development command receipt records that failed attempt. The final shim adds documentation and succeeds. No source behavior was changed to bypass the lint.

## Source and provider admissions

Ten exact complete definition bindings cover candidate conversion, both original variant/list classifiers, original conversion, parser whitespace/comment fetchers, block consumption, serialization classifier/setter, and pending-block cleanup. Full source files and the Rust dependency closure are included. Candidate loop bytes are independently re-extracted during every replay.

The following remain explicit:

- Typed `ToCss` output is valid and balanced. Unmatched closers, unfinished blocks, malformed strings and arbitrary invalid CSS are outside the native loop correspondence. Empty/comment-only theorems are mathematically covered; this package does not establish that a registered typed value can serialize to those inputs.
- The actual public parser emits the corresponding top-level events, omits comments, preserves whitespace, skips every pending balanced block through its closing token, and reports only end-of-input on this admitted domain. This package does not universally prove parser byte traversal, cache histories, tokenization, Unicode codec correctness or native failure behavior.
- Block interior class lists are an abstraction of complete nested tokenization, not a proof of that projection. The native finite reference exercises this premise but does not discharge it universally.
- The universal-value early return clones its existing raw value before this loop. It is a source-path fact, not a theorem that old universal metadata is correct.
- Serialization, token classification and the native-to-model representation are trusted source correspondences. Heap ownership, finite machine sizes, allocation, compiler/stdlib/linker/runtime and optional-feature equivalence remain external.
- The global token-separator table, preservation of complete concatenated CSS token streams, all ToCss alternatives, and downstream declaration semantics are not proved here. This component establishes the summary obligation needed before such a composition.

The formal witnesses are symbolic lexical-class counterexamples; actual LP serialization and browser font/margin behavior are supplied by the separately retained oracle and root runtime evidence. No additional browser tests or native edits were performed by this producer.

## Replay and evidence

Run the closed checker as described in README. It authenticates the complete roster before executing helpers or creating output, verifies actual Lean/rustc identities and the Lean library inventory, audits all named theorems, rebuilds the native closure, runs the fixed corpus/mutants, and reauthenticates inputs. Fresh relocated replay and integrity-negative receipts are stored outside this source capsule. Passing finite native observations is not a proof of the admitted parser or compiler.

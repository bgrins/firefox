# Proposed next tokenizer admission target

## Decision

Proceed with numeric lexical consumption and decoded Dimension/reference-unit composition as the next provider component. Preserve numeric payload fidelity as an explicit separate unresolved obligation, with the concrete finite-result witness below. Do not claim full numeric correctness from lexical progress or unit equality.

The reviewed roadmap leaves numeric/string/comment/URL providers, global arithmetic admission, flat-token dispatch and graph-consumer composition open. The separate name/escape component already models complete name and escape loops, ownership selection, consumed suffix and return boundaries, including internal UTF-8 positions. Its report still requests independent review. This proposal reuses that work; it does not reimplement it or close its exclusions. Its original is_ident_start progress theorem must be connected to the corrected guard, using that the correction only removes old false admissions. Do not instantiate it silently on changed source.

## Source preservation and discovery

Searchfox discovery identified consume_numeric and the style numeric/opacity consumers; complete indexed files are retained under searchfox/. The actual locally changed tokenizer and custom_properties.rs were copied read-only under source/. Their pins and the roadmap/name component snapshots are in SOURCE-PINS.json. The indexed and local complete tokenizer may differ, but consume_numeric body bytes are exactly identical. The local file contains the corrected identifier-start offset. This is a source snapshot, not an assertion about whichever binary root currently runs.

consume_numeric calls byte_to_decimal_digit, Parser byte/bounds/advance operations, f64 arithmetic and powf, then either percentage conversion, is_ident_start plus consume_name, or Number construction. Token payloads include f32 value, an optional clamped i32, has_sign and (for Dimension) the decoded name. NumberOrPercentage/Number and Opacity consumers are independently indexed context, not live-source/binary admission.

## Proposed obligations

1. Derive numeric entry admission from every actual next_token_unchecked digit/sign/dot branch. A leading decimal point may leave the first digit loop at zero iterations. Do not assume arbitrary consume_numeric inputs are nonempty or safe.
2. Prove the three digit loops' maximal consumed prefixes, sign handling, optional decimal/exponent lookahead and exact remaining suffix against an independent grammar decomposition. Incomplete e, e+, dot and sign sequences must be retained rather than overconsumed.
3. Derive every next_byte_unchecked read's non-EOF precondition from entry/guards and the break immediately after advance. Prove finite progress by remaining input length. Admit native usize addition and UTF-8 representation explicitly; do not infer a global source-size bound from the model's Nat arithmetic.
4. Prove syntactic type/has_sign observations and the token choice. Native tests percent before identifier start, while the spec orders those checks oppositely; establish mutual exclusion of percent and identifier-start instead of assuming branch-order equivalence. Percentage stores a unit fraction rather than the spec's percentage magnitude.
5. Compose the suffix with the already modeled name/escape provider, deriving decoded unit, total consumption and return boundary. The numeric prefix consumes ASCII only; escape/unit handling can temporarily enter a UTF-8 sequence. Reuse the name theorem's final-boundary contract, not a false per-step boundary invariant.
6. Bind decoded unit bytes to ReferenceFlags::from_unit at both current sinks: resolved_token_dependencies and parse_declaration_value_block. Case folding and escape decoding matter. FONT/LH and ROOT_FONT/ROOT_LH bit combinations must use the current helper. Only Dimension token units contribute here; strings, identifiers, hashes and URL content must not acquire flags. This is distinct from complete graph-edge admission.
7. Retain the actual floating operation trace and integer saturation rather than pretending numeric values are exact reals. An optional independent integer-only clamp theorem looks feasible because i32 thresholds are exactly represented; it must derive the bounds. General decimal/exponent payload agreement cannot currently be assumed, given the executable witnesses.
8. Compose numeric return state with the raw-token/fresh-suffix scanner. Parser block skipping, whole-tokenizer progress, line/column observations, all provider paths, heap and graph/SCC composition remain open.

## Unit-boundary challenges

| Raw input | Intended boundary/classification challenge |
| --- | --- |
| 1em | e is not an exponent without a digit; decoded unit em |
| 1e-1em | exponent consumed before unit em |
| 1\65 m | escape plus optional whitespace decodes unit em |
| 1e+em | incomplete exponent; first Dimension unit e, leaving +em |
| 1em2em | one unit em2em, not two font-relative dimensions |
| 1%em | percentage then identifier; no dimension-unit flag from em |
| 0em | numeric zero still carries a font-relative unit dependency |
| 1-\ followed by LF | corrected start predicate rejects a dimension suffix; preserve the escaped-newline repair boundary |

These are target obligations, not a newly executed finite browser matrix or claimed proven lemmas.

## Concrete payload obstruction

The source-bound compiled witness contains the complete unmodified consume_numeric, byte_to_decimal_digit and current is_ident_start definitions. A small explicit Parser/Token facade provides equivalent byte operations for its admitted short ASCII cases; a plain ordered-match macro replaces optimized dispatch. consume_name is deliberately limited to ASCII names and rejects unsupported trailing characters. Inputs use empty or px units, so no name/escape theorem is assumed in this experiment. This does not establish complete parser-object refinement.

With rustc 1.92.0 on aarch64-apple-darwin, optimized execution returns:

- 5 followed by 308 zeros and e-309: Number(+infinity), mathematical value 0.5.
- 5 followed by 399 zeros and e-400: Number(NaN), mathematical value 0.5.
- 0. followed by 399 zeros, then 5e399: Number(NaN), mathematical value 0.5.
- 17 followed by 308 zeros and e-308px: Dimension(+infinity, px), mathematical value 17px.

All input bytes are consumed. These demonstrate actual extracted-source arithmetic, not only a mathematical model discrepancy. They are not a Firefox browser reproduction. Intermediate overflow/underflow precedes exponent multiplication; f32 conversion cannot recover the information. This refutes unconditional exact finite-value payload admission for this operation sequence while leaving lexical/unit obligations meaningful.

The seven-case proposed opacity probe has three predicted failures and four controls. Indexed Number normalizes NaN to zero and clamps infinity; Opacity then clamps to [0,1], predicting 1/0/0 for the three half-valued cases. Browser acceptance, exact consumer build correspondence and external prior art remain unverified. The separate dimension witness demonstrates the payload boundary; its browser behavior is not asserted by this probe.

## Replay and boundaries

Run check.py for authentication/source binding and reference checks; use --run-rust --output NEW_DIRECTORY to freshly compile/run only the small extracted witness. Rustc version, exact commands, source and executable hashes, and stdout are retained. The binary itself is excluded from the source companion. No Firefox/Cargo build, live edit, Git/index operation or browser run was performed. Compilation was explicitly authorized by root after the initial source-only task.

This capsule proposes a target and reports an actionable hypothesis. It neither adds a repair nor creates new Lean acceptance. The full tokenizer and original C1–C13 scope remain open.

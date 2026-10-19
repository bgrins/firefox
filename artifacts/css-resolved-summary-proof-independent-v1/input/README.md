# Selected-output dependency composition

This component proves dependency-summary composition for arbitrary finite token-piece streams. It is a mathematical component for the proposed resolved-output scanner, not acceptance of a native repair.

The principal theorem, `selected_output_summary`, relates two independently defined computations:

- `execute` selects successful primary/fallback replacements, assembles their tokens with optional inert separators, and propagates substitution failure.
- `accumulate` never assembles output or calls the emitter. It independently selects successful branches and combines their dependency summaries.

For every stream, initial token output and boundary predicate, scanning execution's successful result equals the accumulator's result. The proof proceeds by induction over the stream and handles both replacement failures and incomplete token summaries. It is not limited to the concrete browser witnesses.

`unused_fallback_independence` and its summary corollary allow arbitrary prefix/suffix streams and arbitrary fallback changes, including failure or unresolved content, when the primary succeeds. `emit_scan` and the separator-erasure theorem establish that inserting inert separators cannot change dependencies. `execute_append` supplies composition across an arbitrary prefix. The lexical-boundary counterexample distinguishes two inert tokens from one font-dimension token; it does not execute a CSS tokenizer.

## Three outcomes remain distinct

The model uses nested option types deliberately:

| Result | Meaning |
| --- | --- |
| `none` | Substitution execution failed |
| `some none` | Execution emitted output, but its dependency scan is incomplete |
| `some (some flags)` | Execution emitted output with a complete dependency summary |

Complete zero flags differ from incomplete output. An unresolved token anywhere in selected output makes its scan incomplete. An unresolved token in an unused fallback does not. No default-to-zero operation exists in the model.

## Conditional source bridge

`tokenizer_bridge` requires an actual token correspondence: tokens obtained from serialized CSS must equal the emitted semantic tokens after removing inert separator tokens. It does not assume the desired equality of summaries. Given that lexical premise and successful stream execution, the theorem transfers the independent accumulated result to the serialized-output scan.

The supplied `tokenize` function is a parameter. CSS tokenization, decoded unit/function classification, serialization boundary metadata, and native scanner termination/progress are not proved. Native ordinary blocks are flattened into semantic tokens; dimension classes map to four dependency bits. Strings, URLs, identifiers and comments must be mapped correctly by an external adapter.

Root has selected a native scanner design that repeatedly constructs a parser on the remaining suffix, reads one token and advances by its consumed position. This avoids a recursive block walk. It reports incomplete output for known remaining var/env/attr functions and bad strings/URLs. The model's unresolved token covers those incomplete results; it does not prove that resetting lexical context at every token is valid. Closing/group tokens are inert only under the source adapter's valid-input premise. The actual scanner is not supplied or accepted here.

The planned native compatibility behavior retains old empty references on an incomplete scan. That behavior cannot be admitted as an exact zero summary by this component. Native correspondence is restricted to the complete-result branch; unresolved env link payloads remain an explicit counterexample to a global resolved-output invariant.

## Source mapping and limits

See `SOURCE-MAPPING.md` for both persistence sinks and native separator behavior. Complete historical candidate files, the serializer and the approved design are retained with integrity bindings. These snapshots establish the source design being modeled; they are not a pin of a future scanner implementation or root's final binary.

Primary/fallback eligibility is an input to this model. Provider/cache stability, observer effects, taint correctness, property parsing, used versus syntactic root flags, SCC traversal, root reset order, memory/resource bounds and full C1–C13 remain open. Output summaries describe relative dimensions in selected token output, not a minimal dependency set after type checking or algebraic cancellation. No native or browser tests were run by this component's author.

## Replay

Use the pinned Lean 4.35.0-rc4 toolchain from the project toolkit, or provide the same binary explicitly:

```sh
python3 artifacts/css-resolved-dependency-summary-proof-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /tmp/resolved-summary-fresh-replay
```

The output directory must not exist. Replay authenticates retained inputs, compiles all three modules from sources in a new temporary directory, checks all 25 declaration audits, and compiles four semantic mutants that must fail. The count includes supporting algebra; it is not a claim of 25 independent native obligations. Only `propext` and `Quot.sound` occur in the audited axiom sets. There are no external Lean library imports beyond the local modules and the Lean prelude.

The retained `replay-v1` results show all modules passing and four mutants failing on semantic proof goals: preferring fallback over successful primary, accumulating an unused fallback, making separators add font dependencies, and turning incomplete scans into exact zero. Those mutation checks demonstrate that these claims constrain the modeled definitions; they do not validate CSS parser admission.

# Translation vocabulary and manual meaning

This is a deliberately restricted prototype, authored using the valid-escape and number-start algorithms. It is not a general English or Bikeshed parser. The held-out experiment applies these same rules without adding consumption semantics.

Source selection uses a unique heading ID and the next heading at the same or a higher level. Source bytes must match SOURCE.json before the command-line translator runs. All operative body text must match the grammar. Inline markup is removed while retaining its text; whitespace is normalized. Introductions are retained but not translated, and their whole meaning is outside the correspondence claim.

The admitted forms are:

- A non-consumption note followed by a sequence of conditional Boolean returns and a final return.
- The same note followed by “Look at the first code point” and one flat definition-list switch. Consecutive labels share a body; exactly one final “anything else” case is required.
- Conditions on first, second or third input observations, literal scalar equality or inequality, and named `newline` or `digit` tests. Conjunction is permitted within a condition. The parser does not infer missing conditions.
- The source definition of newline provides a literal scalar. The source definition of digit provides an inclusive scalar range. Both definitions are extracted even when only one is used; this is a conservative dependency set for this benchmark.

The manual semantic choices are ordered fallthrough, Boolean returns, conjunction, disjunction between switch labels, equality, inequality and inclusive ranges. `Option Char` represents a Unicode scalar or EOF; EOF never satisfies a scalar or range test. Literal code-point numbers are interpreted as Unicode values. The prototype relies on the checked source snapshot and does not independently validate descriptive Unicode names against those numbers.

The generated list adapter supplies `head?`, `tail.head?` and `tail.tail.head?`. The non-consumption note is interpreted as returning the supplied list unchanged. This is an explicit abstraction: the supplied list begins at the current observation, and EOF is represented by exhaustion. There is no modeled tokenizer cursor, reconsume flag, decoder, preprocessing stage or browser state. The note-to-list-state mapping is authored manually; a checked state-preservation theorem proves what the adapter does, not that this abstraction covers every real caller.

No mutation, loop, accumulator, numeric decoding, parse error, Unicode replacement, whitespace consumption, stream advancement or opaque helper call is admitted. Those constructs must be rejected rather than mapped to an existing Lean parser by name.

The compiler and extraction code are unverified Python. Lean checks the resulting functions against separate, previously written library definitions and relations. It does not check the prose-to-IR mapping or prove compiler correctness for arbitrary input programs. The bridge proof files are independently authored during this experiment and are not generated from the same IR.

The freeze records translate.py, this file, PROTOCOL.json and input/library manifests. Proofs and the benchmark driver may be developed after the freeze, but must not change those translation rules or silently substitute a held-out implementation.

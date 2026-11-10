# Reviewed number transfer mapping

Consume-number is development material here. The prior held-out refusal is
retained in `PRIOR-REFUSAL.json`; it remains a failure of the earlier frozen
translator. No blind, held-out or automatic English-translation success is
claimed by this new manually authored program.

The source is the unchanged pinned CSS Syntax revision in `SOURCE.json`.
`source_map.py` extracts exact bytes for the algorithm, digit definition and caller predicate and
refuses full-source drift. `CLAUSES.json` records provenance, not semantic proof.
The full algorithm body, including the caller note and WPT metadata, is retained;
this checker does not classify arbitrary new prose or metadata.

| Consume-number clause | Reviewed construction | Checked connection |
| --- | --- | --- |
| Initial integer type, empty number/exponent strings | Product of optional sign, integer digits, optional fraction and optional exponent; absent optionals imply integer type | `number_run`, `projection_meaning` |
| Optional leading sign | `optional (take signPredicate)` | `sign_run` connects its optional scalar to the independent `Signed` relation via `sign` |
| Maximal integer digits | `scan digitPredicate` | Structural `scanWhile`, generic maximal-prefix relation and `scan_digits` |
| Dot followed by a digit | Optional transaction over dot then nonempty maximal digits | `fraction_run`, `optional_fraction_run`; failure restores the original dot and entire suffix |
| E/e, optional sign, then a digit | Optional transaction over marker, optional sign and nonempty maximal digits | `exponent_run`, `optional_exponent_run`; truncated sign/marker restores the entire original sequence |
| Base-10 value and exponent arithmetic | Existing first-order natural fold, followed by an explicit signed significand/scale projection | `magnitude_meaning`, `projection_meaning`, `projection_rational_meaning` |
| Return value, integer/number type and optional sign | `Exact` and retained state | `execute_reference`, `execute_iff` with independent `CssNumberSyntax.Consumed` |

`Exact.isNumber` means that the type flag is **number rather than integer**. It
does not mean the source is a valid number. Explicit plus/minus is retained even
when the exact integer significand is zero. The scale is symbolic and unbounded;
there is no floating-point, machine overflow/clamping or browser equivalence claim.

The actual typed parser result is the structured lexical parts. The final
numeric projection is ordinary Lean, separately proved against the existing
exact-number model. It is not an extra opaque parser primitive, a generated
numeric IR, or an arbitrary function stored in the AST. This is the deliberate
small boundary of this experiment.

The added parser constructors are generic: prior first-order statement embedding,
predicate read, maximal scan, nonempty scalar-list requirement, ordered product,
right projection and transactional optional. Product/optional result shapes are
data-only and typed; no parser field stores an arbitrary Lean function. A decoder
or serializer round-trip is not implemented. There is no consume-number opcode,
general while-loop instruction or caller-selected loop fuel. `scanWhile` recurses
on the remaining finite input, and `scan_matches_length_bound` connects it to
the old bounded scanner when that bound is exactly the source length.

The old FirstOrder, lowering and escape definitions/proofs are preserved byte for
byte (`PRESERVED.json`) and recompiled. `legacy_preserved` and `legacy_lowering`
cover every old closed statement and arbitrary initial state. These theorems do
not establish a lowering pass for the added parser combinators. Their number
correspondence is checked directly against the independent reference relations.
The old effect language has no input snapshot/restore primitive; lowering generic
transactional optional into that effect language would require an additional
verified state contract. This prototype does not provide that lowering.

The algorithm assumes would-start-number at its call boundary. `ready_call` and
`ready_result` state that assumption explicitly. The total parser also returns
model values for empty, sign-only and other off-domain input, because the copied
reference consumer does; those examples are separately labeled and are not
CSS-conformance claims. A tokenizer caller also supplies the already filtered
code-point stream. This model accepts finite `List Char` (Unicode scalars); it
does not perform byte, DOMString or input-preprocessing conversion itself.

The source interpretation, primitive ASCII predicates, representation choice and
exact-value interpretation remain review obligations. Kernel checking establishes
the stated internal correspondence; it cannot establish that an English clause
was correctly chosen or interpreted. Nor does one manually developed second
algorithm measure broad transfer coverage.

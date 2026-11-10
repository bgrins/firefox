# Next derivation milestone

**Recommend reusable consume-number lowering, then a typed codec.** Streaming
machine descriptions should follow once the IR has suitable raw-unit/point and
structured-state types. Adding examples or dedicated number/UTF-16 opcodes would
not remove these gaps.

| Order | Work | Assurance gained | Boundary retained |
| --- | --- | --- | --- |
| 1 | Generic `ParserIR` lowering with snapshot/restore | A universal state-preservation theorem for the seven existing parser constructors, composed with the checked number bridge | Numeric projection and source-to-tree interpretation remain separately reviewed/proved |
| 2 | Typed structured-data codec | Replace the current unchecked Python AST-to-Lean emitter mapping with a typed decoder and encode/decode theorem | Textual JSON parsing and English-to-tree interpretation need separate treatment |
| 3 | Data-only streaming transducer descriptions | Replace arbitrary function fields in `Machine` with interpreted expression trees and reusable lowering | Requires larger domain/state/fold extensions first |

Qualification: the number interpreter already has a direct proof against its
reference relation. Lowering closes a missing reusable refinement edge; it does
not remove an unchecked compiler currently used by that artifact. The Python
emitter is an actual existing unchecked translation boundary. If minimizing
currently trusted translation code is the sole criterion, the codec outranks
lowering. The order above favors completing the small semantic core before
freezing its interchange schema.

## Smallest lowering interface

`ParserIR.Parser` already has typed products and optionals and no arbitrary
function payloads. Its constructors are `legacy`, `take`, `scan`, `nonempty`,
`pair`, `right`, and `optional`. The old backend `Program α` already supports
arbitrary result types, so product/optional lowering does not require expanding
`FirstOrder.Ty`.

Preserve the old files and add a backend layer with old-program embedding, state
read/write, and sequencing. Define transactional rollback using those operations.
Snapshot the complete `State` (input and error flag). For maximal scanning, reuse
the old scanner at the saved `state.input.length` and the existing
`scan_matches_length_bound` theorem; no new loop opcode or arbitrary fuel is needed.

Proposed universal contract, not yet implemented in this review:

```lean
lowerParser : ParserIR.Parser shape → ExtendedProgram (Option shape.Value)

theorem parser_lowering_correct (parser : ParserIR.Parser shape) (state : State) :
  runExtended (lowerParser parser) state =
    match ParserIR.run parser state with
    | none => (none, state)
    | some (value, next) => (some value, next)
```

This specifies atomic failure. `ParserIR.run` erases state on failure, so atomic
rollback is an explicit strengthening, not a property already implied by its
type. A failed right side of `pair`, for example, must restore the state before
the left side. A weaker theorem could erase backend failure state instead, but
`optional` still needs its own full-state transaction.

Prove old embedding and transaction behavior, then induct over the seven parser
constructors. Compose the number instance with `number_run`, `projection_meaning`,
`projection_rational_meaning`, and `execute_iff`, retaining `StartsNumber` at the
caller boundary. The final signed numeric projection remains ordinary Lean;
do not call this a complete first-order numeric compiler.

Useful new controls: omit rollback of a child-raised error, restore the wrong
checkpoint after an earlier consumed prefix, cap maximal scanning, swap
same-typed product values, lose an embedded error effect, or return the left value
for `right`. Each should typecheck and fail the generic contract plus an exact
semantic witness.

## Codec interface

Use an explicit data interchange type and context/result parameters:

```lean
encodeExpr : FirstOrder.Expr context type → Raw
decodeExpr : (context : List FirstOrder.Ty) → (type : FirstOrder.Ty) →
  Raw → Except DecodeError (FirstOrder.Expr context type)

theorem decode_encode (expression : FirstOrder.Expr context type) :
  decodeExpr context type (encodeExpr expression) = .ok expression
```

Extend this to typed variables/statements, then parser shapes. Reject unknown
constructors, wrong arity/types, out-of-scope indices, and executable-text fields.
State canonicalization explicitly. Use the checked decoder directly rather than
adding an unchecked emitter after it. A structured-data round trip does not
verify JSON text parsing. Keep the independent algorithm bridge: both a codec
and lowering can faithfully preserve a wrong but well-typed AST.

## Streaming fit

The current IR has natural numbers, `Char`, Boolean, `List Char`, and unit.
Unmatched surrogate points cannot inhabit `Char`. `ParserIR.Shape` supplies
compound results but does not extend expression environments. `foldNat` only
folds scalar lists into a natural accumulator.

A faithful stream description would need raw unit/point domains (or checked
natural encodings), typed lists/options/products, a structured finite fold,
data expressions for hold/combine/single, and a raw-input backend. It must also
prove `Machine.unheld`; well-typedness alone does not imply this semantic law.
Later `loweredFeed = feed (denote description)` and `loweredFinish = flush`
theorems could reuse the completed continuation/chunk/pipeline proofs. This is
larger than number lowering and cannot be achieved by the unchanged syntax.

## Provenance and limits

`INPUTS.json` pins the inspected artifacts. Number work can reuse the unchanged
CSS Syntax revision `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`, its exact clauses,
and the old IR/number bridges. Streaming can reuse its four pinned library modules
and nine normative excerpts. No new spec fetch is necessary for these milestones.

Freeze the core before another transfer experiment. Number remains development
material; the earlier frozen translator refusal remains a refusal. This review
implements nothing and changes no earlier artifact, canonical library, native
code, browser, build, or Git state. None of the proposals proves a general
English-to-Lean mapping, held-out success rate, or Firefox refinement.

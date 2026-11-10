# Interim typed codec source review

No blocker found in the current generic codec and theorem statements. This is
an interim source inspection; runner, harness and frozen inputs remain pending.

`inferVar` returns the type stored at the precise de Bruijn position;
`expect` checks equality with the required type and transports only across that
equality. Empty/out-of-range contexts fail. Expression inference checks each
operand type; `ite` checks both branches against the first branch type. Fold
uses scalar :: nat :: Γ. Statements extend let/read/scan contexts correctly,
and the requested result type passes to all result branches.

`Laws.lean` proves recovery for all typed variables, expressions and statements
with arbitrary contexts and result types. The `checkExpr`/`checkStmt` guards then
compare the encoded result with the supplied data tree after removing only scope
wrappers. Their faithful-result theorems establish that exact equality for every
accepted DataExpr/DataStmt. This strengthens encoded-image roundtrip: changed
operators, literal values or variable positions cannot be silently accepted by
these guarded entry points. It does not prove JSON-to-Data conversion faithful,
and unguarded inference/decoding entry points have no such exported acceptance
claim. Normalization does not simplify arithmetic, reorder branches or strip
any executable constructor.

Aliases are fixed names and types. Each definition is decoded without aliases
under [head], so it cannot contain recursive alias use or free references to
unseen ambient tail bindings. A use becomes a scope wrapper; inference checks
that the actual context head matches before rechecking the body. This is
re-decoding of preserved de Bruijn positions, not runtime string evaluation or
unchecked declaration-name resolution. The current source has no generic alias
weakening theorem; fixture equality and schema controls cover that adapter seam.

`JsonCodec` constructs data by structural recursion over Lean.Json. Strings are
used only as literal operator/alias names, not evaluated as Lean. Source maps are
required to be objects but their prose is provenance, not executable input.
Definitions require the exact four names; each operator requires exact object
fields and arity. Scalar literals reject surrogate values and values at or above
0x110000 before `Char.ofNat`; Nat literals are not scalar literals. The existing
`scalarOf` expression intentionally retains the core's Char.ofNat semantics and
can be applied to arbitrary Nats. That is not a literal-admission bypass.

The generic theorems start at typed trees/DataExpr/DataStmt. JSON schema mapping,
Char admission, numeric extraction and alias construction are executable Lean
code but have no universal JSON correspondence theorem. The concrete fixture
bridge reduces `decodeDocument fixture` to the prior escapeTree by kernel
reflexivity, then reuses the independent escape relation. FixtureJson uses a
literal `json%` macro, not the runtime JSON text parser; their connection needs
separate provenance/runtime checks. Importing the old escapeTree into this
reference proof is appropriate, provided the actual runtime does not import it
or call it instead of the decoded program.

## Confirmed JSON text boundary

`JsonParserBoundary.lean` and its log independently exercise Lean4.35.0-rc4.
JSON object parsing inserts into a TreeMap and overwrites duplicate keys; both
`{"schema":0,"schema":1}` and its reversal parse successfully with their last
value. Exact field counting on the resulting object cannot reject duplicate
keys in the original text.

`getNat?` accepts parsed nonnegative mantissas with zero internal exponent.
The observations accept 0, -0, 1, 1e0, 1e1 and 1.0e1; reject 1.0 and10e-1 despite
their integral mathematical values; and reject -1,true and malformed01. This
is not a theorem about JSON numerical equivalence or exact lexical compatibility
with Python's old integer-only emitter. The parser, macros, IO and source-to-JSON
mapping remain distinct trusted or observed boundaries.

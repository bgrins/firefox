# Typed interchange codec: initial independent review

This is a design checklist against the existing FirstOrder core and schema-1
emitter, not acceptance of an implementation. Final source review is pending.

## Existing boundary

`FirstOrder.Expr Γ t` admits only natural numbers, scalars, booleans, scalar lists
and unit. Variables are typed de Bruijn references. `Stmt` contains return,
let, read, bounded scan, error and branch. No syntax constructor carries an
arbitrary function. Expression evaluation is shared by direct interpretation
and lowering; the universal lowering theorem therefore does not certify pure
primitive semantics or the English-to-AST mapping.

The external schema uses exact `{op,args}` objects. Four definitions are named
expression aliases (`hexExpr`, `whitespaceExpr`, `magnitudeExpr`, `decodeExpr`);
`use` is a serialization macro, not a FirstOrder expression constructor. The
old emitter constructs Lean source and relies on elaboration to check scopes
and types. The interchange document also includes `source_map`, which contains
prose as provenance rather than an executable payload.

## Required proof and acceptance boundaries

A useful `decode (encode tree) = some tree` theorem quantifies over all contexts
and result types, including open terms and all binding constructors. It must
account for every context extension: let adds the expression type; read-present
adds scalar; scan predicate adds scalar and its continuation adds chars; fold
step adds scalar then nat. Variable decoding must check both index range and
the type at that exact context position. Scalar literals need range and surrogate
checks, not silent `Char.ofNat` replacement.

This roundtrip certifies recovery of encoded well-typed trees. By itself it does
not characterize arbitrary untrusted raw data or prove rejection of unsupported
tags. A typed return value establishes scoped/type-safe output by construction,
but does not alone show that output faithfully reflects an arbitrary accepted
raw tree. A reverse property or explicit accepted-syntax correspondence would
strengthen that boundary; otherwise document the restriction and test unknown
constructors, extra fields, wrong arity, wrong literals, variable type mismatch,
out-of-scope references and shadowing. Type-correct wrong-variable mutants
must still be caught by the independent escape bridge, not merely type checking.

Alias expansion must have a precise contract. Existing aliases are polymorphic
in the tail context but have fixed head and result types. Expansion cannot
accidentally capture the wrong local or accept cycles, arbitrary names or an
executable function field. The codec should not call the reference parser or
execute source text, dynamically resolve declaration names, import supplied
modules, or use reflection/evaluation as a decoding oracle.

## Actual integration and remaining trust

The practical route is a fixed Lean runner reading JSON, validating the envelope
and decoding a closed scalar statement, then interpreting or lowering that
returned typed statement. The generated AST-to-Lean emitter must be absent from
that execution path. Merely proving a codec while continuing to run the old
emitted constructors would leave the targeted trust boundary unchanged.

A proof over an inductive raw tree or Lean Json values does not verify parsing
JSON bytes. Lean's JSON parser, duplicate-key treatment, integer/number admission,
string/unicode handling and external file acquisition remain explicit boundaries
unless separately proved. If Python expands aliases or converts JSON to another
raw form, that transformation remains trusted until it is checked or proved.
The source recognizer and prose-to-AST construction remain manually reviewed;
source hashes and clause links establish provenance, not normative semantics.
The existing semantic bridge remains necessary even after a fully correct codec.

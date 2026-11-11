# Generic alias weakening and document-design review

Accepted as a useful bounded proof milestone and a concrete next implementation
plan. No blocking source or validation finding. The prototype proves safe
reuse of singleton-checked expression bodies under arbitrary extra environment
bindings; it does not implement or prove the proposed generic outer-document
reader.

Reviewed artifact: `css-document-schema-design-20261110-v1`.
Frozen nine-input `SOURCE-ONLY.json` SHA256:
`cdc743efddb179b9fe5588e54e8877e163223590079274fc7aa9c62e7c467596`.
The author's design/report SHA256 is
`2157c3e30126ff7f9f0143f204ca977e362b0f31fd2fe89977633b20bc766994`.
Additional inspected input hashes are recorded in `INPUTS.json` here.

## What the seven laws establish

`weakenVar` and `weakenExpr` append context entries at the tail. They preserve
the original de Bruijn positions rather than inserting a new head binder.
The first two laws prove exact variable/expression data erasure preservation.
`lookup_weakening` and `evaluation_weakening` then prove lookup and complete
expression-value preservation for arbitrary original environments and arbitrary
typed tails. This is a pure expression theorem, not a statement-state or
browser-state theorem.

The `foldNat` case is substantive: its step has a scalar and accumulator prefix
before the original environment. The recursive weakening keeps that prefix,
and the evaluation proof uses function equality for every accumulator/scalar
pair. It neither drops the step nor substitutes an interpreter result as an
oracle. All expression constructors in the preserved IR are covered.

`scoped_alias_rechecks` proves that encoding an expression checked at singleton
context `[head]`, wrapping it in `.scope head`, and checking it at
`head :: tail` returns the explicitly weakened expression. The sixth law
proves the result is independent of the tail's values. The seventh transfers
this statement to supplied normalized raw data already accepted at the
singleton context, using the preserved codec's erasure-faithfulness theorem.

The normalized-data and successful-singleton-check premises are explicit.
They are not derived here from the existing `readDefinition` implementation.
The planned alias-free JSON bridge must establish normalized data, and the
future document theorem must connect the actual stored definition and use-site
lookup to these premises. The current fixed adapter does perform singleton
checking, but these seven laws alone are not a universal theorem about its
complete document execution.

## Independent composition and executable boundaries

`Boundary.lean` adds two generic review proofs. One composes accepted normalized
data, scoped rechecking, and evaluation independence into a complete result:
checking and evaluating the wrapped body under any tail yields `some` of its
singleton meaning. The other allows two tails of different types and values
and proves both evaluations equal. These are kernel-checked compositions of
the reviewed laws, not a second independent implementation of weakening.

All four author cases were replayed. The fold case uses both its accumulator
and the original singleton input, producing 10 despite an ambient value 900.
The singleton checker rejects `var 1`. Conversely, merely checking
`.scope nat (var 1)` in `[nat, nat]` succeeds and returns ambient 900. That
counterexample accurately demonstrates why a head-type marker is not a binder
or a substitute for singleton prevalidation. A mismatching scope head is
separately rejected.

The semantic mutant replaces the weakened fold step by constant zero. The
modified implementation compiles; the unchanged erasure/evaluation laws fail,
and a witness that passed before mutation fails with the exact kernel
diagnostic that `decide` proved the proposition false. This is a behavioral
mutation, not an intentionally ill-typed source or an incidental syntax error.

## Source-only validation

The independent `replay.py` authenticates the frozen inputs, copies only those
inputs into a fresh review-owned directory, and runs the author's checker.
That checker creates another fresh build tree and removes it afterward. It
passes 24 exact axiom audits: 13 preserved, seven new laws, and four cases,
plus the compiling semantic mutation and concrete rejection. This review also
freshly builds and audits both additional generic proofs. Dependencies are
limited to the standard permitted Lean axioms; no `sorry`, custom axiom,
`native_decide`, or unsafe proof shortcut is accepted.

The four preserved module files match the already authenticated import-only
integration overlay byte for byte. Their prior signed-origin transport is
unchanged. The replay records the compiler hash and checks Lean 4.35.0-rc4.
All temporary compiled directories were removed. `CHECK.json`,
`author-replay/report.json`, and the command logs record this review's actual
execution, rather than relying solely on the author's earlier receipt.

## Assessment of the proposed outer-document milestone

The proposed signature-parameterized, flat, alias-free definition reader is a
reasonable next step. Requiring distinct signature names, exact keys, ordered
signature/definition alignment, and singleton input/result checks gives a
specific theorem boundary. An empty profile and a second profile are useful
checks against accidentally hard-coding the escape document again.

The plan correctly distinguishes raw map-key enumeration from map lookup on
arbitrary `Lean.Json.obj` trees. Treating `Field` as the existing shared lookup
primitive is explicit; it is not an independent proof of map lookup correctness.
The proposed definition-list equivalence is stronger than the proposed
document result, which is soundness only. This is justified: normalized erasure
for alias-using programs discards scope guards, so it does not by itself give
the converse accepted-document theorem. That converse needs retained scoped
typing evidence and is deliberately deferred.

The all-JSON equivalence between the future generic escape-profile wrapper
and the current fixed reader remains an implementation obligation, including
all refusal behavior. No such outer reader, relation, or equivalence theorem
is present in this prototype. JSON text parsing, duplicate text-key collapse,
recursive aliases, CSS prose interpretation, new CSS feature coverage, and
native/Stylo refinement remain outside the milestone.

No canonical library, native/browser source, Git index, or commit was changed.
Only this review directory was written.

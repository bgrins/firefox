# A second algorithm through a typed parser extension

Consume-number is now implemented as a small data-only parser tree, with exact
numeric result projection and kernel-checked correspondence to the existing
standalone number model. The old escape IR, lowering theorem, program and bridge
remain byte-identical and recompile successfully. This is a manually developed
second algorithm; it does not turn the earlier held-out refusal into a success.

## What changed

The old first-order IR already had typed scalar/natural/list expressions and
bounded scans. It did not have compound/optional result shapes, maximal digit
runs or non-consuming lookahead. Rather than add a consume-number primitive or
a generic numeric language, `ParserIR.lean` adds seven generic constructors:

- Embed an unchanged closed first-order statement.
- Read one scalar satisfying a first-order predicate.
- Scan a maximal prefix satisfying a predicate.
- Require a scalar-list result to be nonempty.
- Sequence two parsers and return their ordered product.
- Sequence two parsers and return the right result.
- Optionally parse, restoring the entire incoming state on failure.

The result shape extends the existing base types with products and optionals.
No AST field carries an arbitrary Lean function. The syntax is structurally
serializable data; no serializer round-trip or JSON emitter is implemented here.
`scanWhile` recurses structurally on remaining finite input, with no arbitrary
fuel. Its independent maximal-prefix relation is checked, and
`scan_matches_length_bound` relates it to the old bounded scanner at exactly the
input length.

`NumberTree.lean` composes those constructors into optional sign, integer digits,
optional nonempty fraction, and optional signed nonempty exponent. Transactional
optionals implement the required fractional and exponent lookahead: failed
lookahead retains the entire original suffix, including the dot, E/e and any sign.

The typed tree returns structured lexical parts. A separate `project` function
produces exact significand/scale, number-vs-integer type flag and optional sign.
Decimal magnitude uses the existing first-order natural fold. Signed arithmetic
and final result assembly are ordinary Lean, separately proved against
`CssNumberValue`; they are not hidden parser primitives or a new numeric IR.
`Exact.isNumber` denotes the **type flag**, not source validity. Explicit minus
on zero is retained in the separate sign field.

## Checked statements

`NumberBridge.lean` relates the new program to copied, independent
`CssNumberParts`, `CssNumberSyntax` and `CssNumberValue` sources:

| Result | Checked claim |
| --- | --- |
| `number_run` | The typed tree returns the exact decimal parts and remaining input of the reference consumer, preserving any incoming error flag |
| `projection_meaning` | Significand, scale, type flag and optional sign match the reference exact-value representation |
| `projection_rational_meaning` | That exact representation has the reference mathematical rational denotation |
| `execute_iff` | The resulting exact value and suffix correspond to an independently related `Consumed` decimal |
| `ready_result` | With the explicit would-start-number premise, a returned result satisfies the stated numeric relation |
| `optional_rollback` | Failed generic optional parsing restores the complete original state, including its error flag |
| `legacy_preserved` / `legacy_lowering` | Every embedded old closed statement retains its old interpreted/lowered behavior for arbitrary initial state |

This does **not** prove a lowering transformation for the added parser
combinators. The old effect language has no input snapshot/restore primitive;
generic transactional optional would need an additional verified state contract
to lower into that language. Here the new interpreter is connected directly to
the independent number relations. The old universally checked lowering theorem
remains available for old statements and has not been weakened or rewritten.

## Source and interpretation

The pinned source remains [CSS Syntax at
c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs),
SHA-256 `4a4a5a3994bda10a56885e66776169d0e05d5a7515b0def4e8859c20e3fd4afc`.
This is the same version used in the frozen refusal. No source-version change
was needed to explain this capability change.

`CLAUSES.json` retains exact byte spans for consume-number, ASCII digits and the
would-start-number predicate. `source_map.py` performs mechanical extraction and
full-source hash checks. [MAPPING.md](MAPPING.md) links the reviewed clauses to
the tree, projection and proofs. The clause-to-constructor choices, primitive
meaning and exact-value representation remain manually interpreted. A source
hash or checked correspondence to the older model does not mechanically prove
the English specification was interpreted correctly.

`PROTOCOL.json` records number as development material and discloses prior source
and model exposure. `PRIOR-REFUSAL.json` retains the earlier frozen translator's
failed number-interface evaluation; that translator is not reclassified or
rerun as a successful translator here. This artifact supports two concrete
program families across the old and additive layers; it provides no held-out
generalization rate or broad prose-translation coverage estimate.

`PRESERVED.json` hashes eight old IR/program/proof/example files plus the old
scalar-input and escape reference sources. `LIBRARY.json` pins all nine copied
reference modules to the standalone library commit from which they were copied.
Canonical library files and previous artifacts were not modified.

## Domain and evidence

CSS consume-number requires would-start-number at its caller boundary. The
underlying total consumer also returns model results for empty, sign-only and
other inputs outside that domain; those are separately labeled, not accepted
CSS behavior. A tokenizer caller supplies an already filtered code-point stream.
This artifact accepts finite Unicode-scalar lists and does not implement byte,
DOMString or preprocessing conversion.

The value representation is exact mathematical significand/scale, not a machine
float. No browser precision, range, overflow/clamping, signed-zero storage,
resource-limit or Firefox implementation equivalence is claimed. Different exact
representations may have equal rational denotations.

The accepted checks are recorded in `clean-verification/report.json`:

- **212 audited declarations, including 30 new declarations.** Only `propext`,
  `Classical.choice` and `Quot.sound` are admitted.
- **33 ordered executable/kernel observations:** 23 caller-ready numbers,
  four explicitly off-domain cases, six generic/legacy-state cases. Nine unchanged
  prior escape examples also compile.
- **Six type-correct semantic mutations rejected by both the unchanged number
  bridge and exact false-witness diagnostics:** missing fractional lookahead,
  missing exponent lookahead, capped digit scanning, cleared rollback error,
  wrong scale and wrong type flag. These include malformed/truncated exponent
  suffixes and a true incoming error flag.
- **Four additional controls:** a scalar result cannot inhabit the compound result
  shape; sign-only input fails caller readiness; changed pinned CSS bytes are
  refused; changed old first-order IR bytes are refused.

For parser-interpreter mutations, the harness first compiles runtime definitions
without their laws to establish that the altered code is well-typed, then checks
the unchanged independent number bridge. It does not count a broken generic law
as a successful typed runtime. Concrete witnesses import only the changed runtime,
so rejection cannot be explained by a previously failed bridge import. The bridge
failure logs contain no unknown-identifier errors. Each semantic witness must
produce the single intended `decide`-proved-false diagnostic.

The first check attempt stopped because an overbroad diagnostic detector mistook
the case label `legacy escape error` for a compiler error. The detector was made
specific to diagnostic lines; the example vector still must match exactly. No
model semantics were changed for that harness correction. Development logs remain
separate from the successful receipt.

## Replay and next decision

`SOURCE-ONLY.json` lists 32 hashed source inputs. No newly generated program, cached
object, package installation or network access is required. Two previously
generated escape programs are retained as pinned reference source inputs. A clean replay can
be run from the parent checkout with a fresh output directory:

```sh
python3 artifacts/css-spec-number-transfer-20261110-v1/clean_replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /private/tmp/css-number-transfer-independent
```

Alternatively copy only the allowlisted files and run `python3 -O check.py
--lean /absolute/path/to/lean --out /fresh/result` there. Output directories must
not already exist. Input hashes are verified, and owned temporary source/build
directories are removed after success.

The experiment buys a reusable typed product/optional parsing core and exact
rollback/maximal-scan obligations, while retaining a separately checked numeric
projection. It does not yet buy a generic lowering pass or prose translator.
After review, the useful transfer experiment would be to freeze this core before
attempting a third structured algorithm, such as guarded Unicode-range consumption,
and preserve any refusal without silently adding new primitives. That would be a
new declared experiment, with prior exposure disclosed, rather than an extension
of this development result.

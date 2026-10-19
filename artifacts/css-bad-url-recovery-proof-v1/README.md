# Bad-URL recovery proof companion

This companion formalizes the recovery suffix contract behind the accepted
bad-URL whitespace handoff repair. The source bug was found by static inspection
and reproduced in a browser **before** this Lean development. The proof extends
that finding to arbitrary finite scalar input under its stated interface.

## What is proved

`Recovery.lean` contains 25 kernel-checked theorems, with explicit axiom reports.
The central `suffix_equivalence` theorem equates two algorithms on every finite
`List Char`:

- `specification` recognizes valid escapes, treats a newline escape as invalid,
  consumes one through six hexadecimal digits and optional normalized
  whitespace, and stops after an unescaped right parenthesis or at EOF.
- `optimized` only treats an immediately escaped right parenthesis or backslash
  specially; other characters can be scanned individually without moving the
  final recovery boundary.

The proof establishes that scanning hex digits and their optional whitespace
cannot hide a raw terminator. Decoded U+0029 and U+005C are data: decoded values
are never reinjected into the token stream. `handoff_equivalence` composes this
with whitespace consumption and the candidate caller's untouched fallback
input. Arbitrary backslash-pair lemmas explain both parity directions, and
concrete theorems refute the original caller in both directions.

`normalized_suffix_equivalence` applies the theorem after explicit CR/CRLF/FF
and null preprocessing. Lean `Char` contains Unicode scalars; lone UTF-16
surrogates are outside this input representation. `raw_suffix_transfer` is an
explicit **conditional** bridge: it assumes that a supplied raw-byte decoder
maps the observed native suffix to the optimized scalar result. This does not
prove UTF-8 byte/scalar correspondence, validate a decoder, or turn raw byte
indices into scalar offsets. It records exactly the additional premise a
universal native refinement would require.

Escape payload decoding is irrelevant to this suffix theorem. The model
consumes the full specified escape extent but does not calculate its decoded
numeric value. Native URL payload decoding, cursor arithmetic, original-source
spans and line/column updates are checked finitely below, not proved universally.
The trusted base includes Lean's kernel, standard library, and approved
`propext`/`Quot.sound` axioms; the checker rejects added axioms and admissions.

## Exact native boundary

The capsule compiles complete retained `tokenizer.rs`, `parser.rs`,
`cow_rc_str.rs` and `macros.rs` modules. It uses the actual parser state and
cursor operations, rather than replacement scanner or string providers.
`fallback-macro.rs` is extracted exactly from the retained crate `lib.rs`.
`SmallVec` is the retained real dependency. Two configurations are exercised:

1. The crate's ordinary Rust match fallback.
2. Its actual `fast_match_byte` procedural macro, built from the retained
   cssparser-macros/quote/syn/proc-macro2/unicode-ident dependency closure.

Unrelated crate modules and the color macro feature are omitted. Parser
SmallVec is built with its default feature set. The URL scanner does not use
its delimiter-stack storage. The capsule allows dead code because these whole
modules expose APIs unused by this narrow entry point; other compiler warnings
are errors. Native builds keep debug assertions enabled.

`ORIGINS-v1.json` records complete source-copy provenance. The checker verifies
that the candidate equals the original after exactly the accepted fallback-arm
change, that no other tokenizer bytes changed, and that the vendor checksum
changed only for this file. `SOURCE-v1.json` authenticates retained inputs.
Compiler executables and versions are pinned in `TOOLCHAIN-v1.json`; installed
compiler runtime/standard-library distributions remain trusted toolchain
inputs, not an independently verified compiler pipeline.

## Finite bridge

There are 7,132 complete URL fixtures. They cover borrowed and allocated-buffer
prefixes, null, BMP and supplementary Unicode, all CSS whitespace including
CRLF, valid/invalid escapes, six-digit limits, escaped hexadecimal zero,
surrogates and out-of-range values, EOF, literal terminators, and alternative
bad-URL entry branches. The Python oracle uses normalized code-point units
with explicit original-input spans, independently of the byte scanner.

Each native row records token kind, payload, remaining raw suffix, byte cursor,
and line/UTF-16-column state. BadUrl's retained payload is an implementation
source-slice invariant; the CSS specification does not assign that token a
payload. Ordinary URL payloads are decoded according to the reference escape
algorithm. The finite inputs do not approach integer position wrapping or
allocation limits.

Both macro configurations match every candidate field. Original source has
375 disagreeing rows, confined to whitespace handoff and recovery-alphabet
fixtures. These are finite manifestations of one recovery family. An additional
8,268 Lean executions compare specification, optimized and whitespace-handoff
suffixes against the independent Python oracle, including tails beginning at
whitespace. These executions exercise model exporters; the arbitrary-input
result comes from the kernel proof.

No part of this bundle proves arbitrary compiled Rust behavior, all CSS
parsing, caller declaration semantics, UTF-16 conversion, stylesheet loading,
or rendering. Browser correctness is supported separately by the paired WPT
and independent native review in `css-bad-url-recovery-fix-v1` and
`css-bad-url-recovery-independent-v1`.

## Controls and replay

Semantic native mutants must compile and run without diagnostics and disagree
with the oracle: restored premature handoff, lost escaped-close handling,
lost escaped-backslash handling, newline consumed without its line-state
update, wrong bad-URL payload and wrong UTF-8 column bookkeeping.
Lean mutants change the six-digit bound, optional whitespace, newline
classification, terminator selection, null normalization and caller handoff.
Compiler/runtime diagnostics, malformed output, missing axiom reports,
additional output, admissions, and altered source identities are rejected.
A noncompiling or crashing mutation is not credited as a semantic kill.

Run from the checkout, using a new output directory:

```sh
python3 artifacts/css-bad-url-recovery-proof-v1/check.py \
  --out artifacts/css-bad-url-recovery-proof-v1/root-replay-v1
```

The checker uses offline Cargo only for the procedural macro dependencies;
all targets, Rust binaries, generated modules, Lean objects and transcripts
are created below that output directory. It never uses the browser's Cargo
cache. Compare the resulting `receipt.json` byte-for-byte with
`producer-v1/receipt.json`. Historical `development-*` outputs retain failed
construction attempts and are not acceptance receipts. The source-only
packaging list is `tooling-paths-v1.txt`.

The retained primary CSS Syntax editor draft and the deciding extracts are
under `spec/`, with their original fetch headers and date. `NATIVE-REVIEW-v1.md`
and `PROOF-PLAN-v1.md` preserve the accepted native boundary and initial scope.
EOF serialization, separator-table CDC issues and declaration retry proofs are
separate work and are not silently included here.

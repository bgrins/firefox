# Numeric attr token proof preparation, version 2

Version 1 remains frozen, including its checker, source snapshots, and receipts.
Two limits became concrete after that preparation passed. Firefox build session
75467 exited 2 because Gecko's `CssString` is `nsCString`, which lacks `push_str`
and does not match `ComputedValue::new`'s `String` parameter. The original harness
aliased `CssString` to `String`; its finite execution therefore did not establish
native storage compatibility. `native-build-v1-failure.log` and
`native-correction-v2.json` preserve that evidence. Version 2 uses `String::from`
in both the proposed native body and the harness, with no storage alias.

Independent review also found that the original fixture omitted `SortKey::S`
because its extraction pattern required at least two letters. Version 1 covered
48 units in 2,400 cases, and its statement of complete unit coverage was wrong.
Version 2 covers 49 units in 2,450 cases, checks the fixture against the frozen
enum, and rejects missing-seconds, duplicate-unit, and unknown-unit inventories.
The enum snapshot now includes the derive and `serialize_all = "lowercase"`
attributes. The Lean model and its theorems are unchanged.

This companion proves the independent token model in `NumericAttr.lean` and
executes a bounded bridge against the existing cssparser library. It does not
prove the Rust tokenizer, float arithmetic, DOM attribute lookup, cascade,
fallback recursion, taint propagation beyond the primary, or native integration.
The separate attr fallback cycle defect is excluded.

Replay from this repository with:

```sh
python3 artifacts/css-attr-numeric-proof-v1/check_v2.py NEW_OUTPUT_DIRECTORY
```

The native repair need not already be applied. The source gate accepts either
the frozen old `substitute_one_reference` function or the frozen proposed
function, reporting which is live. All other function text must agree exactly.
The checker requires the frozen Lean 4.35.0-rc4 compiler, Rust 1.97.1, and the
already built cssparser rlib at their recorded local paths. It writes exclusively
to the new output directory and does not build Firefox or run a browser.
`TOOLCHAIN-v1.json` pins compiler and relevant rlib/proc-macro library hashes;
the cssparser Cargo manifest and prior build fingerprint are retained. This
task did not rebuild that library, so its source-to-binary provenance additionally
relies on the existing local build. Source and binary identity checks do not
constitute a verified compiler.

## Contract

The spec grammar accepts exactly one number token after whitespace and comments
are removed. The implementation model traverses trivia, reads one number, and
checks that no significant suffix remains. `whole_token_classification` proves
their equality for every finite token list, with no parsing agreement premise.
The model is independently specified; it is not translated Rust.

`Payload α` retains the abstract numeric value, negative/sign flags, integer
flag, and original numeric lexeme. `construction_preserves_payload` and
`construction_preserves_unit` prove construction retains every payload field
and selects the right number/percentage/dimension category. This is an abstract
CSS numeric payload, not cssparser's f32 representation. Percentage storage
normalizes by 100 and can round differently from number storage.

The primary, fallback, and taint theorems cover successful parsing, missing
attributes, rejected suffixes, and arbitrary surrounding trivia. Trivia
invariance is proved at the token level. There is no claim to have proved
character-string trimming or CSS tokenization. `old_prefix_counterexample`
formally distinguishes accepting an initial number from the specified grammar.

Fourteen audited theorems compile. Their axiom inventories contain only Lean's
standard `propext` and, for primary refinement, `Quot.sound`; the payload and
unit projection theorems have no axioms. There are no admissions, custom axioms,
unsafe code, or native evaluation proof shortcuts. Five semantic mutations
must fail in the specified theorem bodies; thirteen corrupt diagnostic records
must be rejected. Compiler errors outside those bodies do not count as evidence.

## Native repair and bridge

The proposed branch calls `skip_whitespace`, saves the start position, parses a
number, copies precisely `slice_from(start)`, checks `expect_exhausted`, and
appends the requested unit. This excludes preceding and following trivia and
rejects significant suffixes. It preserves exponent/sign spelling without a
float serialization step. The existing `attr_tainted: true`, serialization
categories, and outer fallback selection are retained.

The bridge compiles the exact candidate body, adapting only `unit.as_ref()` to
an already selected string and the enclosing block result to `Some(s)`.
The body uses the same `String::from` constructor as the native candidate;
there is no `CssString` alias or storage-type adaptation in this bridge. The source gate checks this body mapping against the frozen complete
proposed function. It also binds all current cssparser parser/tokenizer/serializer
files and the unit enum to their frozen snapshots.

The finite bridge checks 25 accepted and 25 rejected inputs against every one of
49 numeric unit forms, totaling 2,450 cases. Accepted cases include the five
CSS whitespace characters, comments, exponent notation, signed zero, integer
rounding/clamping boundaries, overflow, and underflow. Rejected cases include
extra numbers/identifiers, existing dimensions/percentages, functions, delimiters,
non-CSS whitespace, NUL, and malformed exponent prefixes. Every accepted result
must equal an explicit lexeme-plus-unit oracle and tokenize as exactly one token.
Number/dimension f32 bits and flags match the original number token. Percentage
bits match the independent Rust f64 decimal parse divided by 100 and cast to f32
for these particular cases. This finite decimal parser comparison is not a
universal numeric accuracy proof. Four source mutations must compile and then
fail an actual bridge assertion.

## Explicit bridge premises and limits

1. CSS input normalization and cssparser tokenization correctly classify the
   relevant character strings. The Lean input already consists of tokens.
2. The source cursor APIs delimit exactly the number lexeme, with their checked
   whitespace/comment behavior. Source inspection and the finite bridge support
   this premise; there is no universal cursor proof.
3. Appending a supported unit to that lexeme produces the corresponding numeric
   CSS token. The 49-unit enum excludes the `e`/`e-` spellings that can conflict
   with exponent parsing. The finite bridge covers all unit spellings, but not
   every numeric string.
4. The mathematical CSS numeric payload represented by the lexeme is preserved.
   Number and percentage f32 representations are different projections. No
   theorem equates those projections, proves decimal conversion, or establishes
   overflow/range behavior of every consuming property.
5. Native fallback recursion and taint consumers implement the modeled branch
   meaning. The gate binds the source function; WPT/browser evidence belongs to
   the separate tests and repair artifacts.

`development-v1.log` is an intentionally retained failed proof development
attempt. `bridge-development-v5.log` retains a rejected percentage oracle:
using the already rounded number f32 divided by 100 differed by one ULP at
`16777217`. That was an oracle mistake, not an additional Firefox defect.

Current normative snapshots and source fragments are pinned in `SOURCE-v2.json`.
The preparation report records compiler commands, exit codes, input/output hashes,
mutation failures, and source state. A successful replay is a source-bound
preparation receipt, not a completed native verification claim.

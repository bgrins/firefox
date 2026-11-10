# Chunked DOMString interpretation and CSS preprocessing

The incremental adapter is proved equivalent to whole-input decoding and CSS
preprocessing for every finite partition into chunks, including empty chunks.
Both the UTF-16 high-surrogate carry and the preprocessing CR carry survive
chunk boundaries. The direct two-stage pipeline is proved against the existing
standalone library's `DomString.Prepared` relation.

`PairStream.lean` implements a generic adjacent-pair transducer. Its contract
requires that an item emitted immediately cannot form a pair with a later item.
The UTF-16 specialization holds leading surrogates; the CSS specialization holds
CR. `Pipeline.lean` feeds each emitted decoded chunk into the preprocessing stage
with both carries preserved. At EOF it feeds the flushed UTF-16 carry through
preprocessing, then flushes the preprocessing carry. Empty input chunks do not
flush either stage.

The 27 new laws include:

* Continuation invariants for individual input items, feeds, and finite chunks.
* Feed concatenation and exact equivalence between chunked and whole-input runs.
* UTF-16 correspondence to the existing `Decoded` relation and CSS filtering
  correspondence to the existing `Preprocess` relation.
* Factorization of the incremental pipeline, composed equivalence to `Prepared`,
  normalized output, and output-length bounds.
* Reachable-state invariants: only a leading surrogate can remain in the UTF-16
  carry, and only CR can remain in the preprocessing carry.

The input domain is already-acquired 16-bit units. Natural-number examples use
checked admission; a supplementary code-point number is rejected as a single
unit. These demonstration wrappers validate their complete input before calling
the typed streaming functions. The universal theorems cover arbitrary finite
typed inputs, a mathematical superset of ECMAScript's string-length limit.

## Validation

Lean 4.35.0-rc4 accepted 66 audited declarations: 27 new and 39 in four unchanged
reference modules from library revision
`0127c4f42c620cdaba4f9b92cca93ca95df2d913`. The axiom inventory contains only the
standard `propext`, `Quot.sound`, and `Classical.choice`. No proofs are admitted
and no additional axioms are declared.

Thirty-two executable observations cover split/minimum/maximum pairs, empty
chunks, unmatched/reversed/overlapping surrogates, CRLF and repeated CR across
boundaries, simultaneous carries, EOF, NUL/FF, immediate emission, and invalid
code-unit admission. Six type-correct mutations are rejected by unchanged proofs
and exact false semantic witnesses: resetting surrogate carry, omitting either
EOF flush, resetting CR carry, premature surrogate replacement, and incorrect
pair output. Three controls reject drift in the reference library or the CSS
and UTF-16 source excerpts.

The premature-replacement control checks the intermediate decoded code points.
Final CSS output alone can conceal that error because preprocessing replaces
unmatched surrogate points anyway.

## Sources and scope

Nine exact excerpts cover [WebIDL DOMString](https://webidl.spec.whatwg.org/#idl-DOMString),
[Infra strings](https://infra.spec.whatwg.org/#string),
[ECMAScript string interpretation](https://tc39.es/ecma262/#sec-ecmascript-language-types-string-type),
[StringToCodePoints](https://tc39.es/ecma262/#sec-stringtocodepoints),
[CSS preprocessing](https://drafts.csswg.org/css-syntax-3/#input-preprocessing),
and the [CSSOMString choice](https://drafts.csswg.org/cssom/#cssomstring-type).
`SOURCES.json` records immutable source revisions and URLs; `CLAUSES.json` binds
the retained excerpts to exact byte spans and hashes. `ORIGIN-REPLAY.json`
authenticates them against the prior artifact's complete source snapshots and
checks all four library modules against their pinned Git objects.

The chunking strategy is an implementation choice proved equivalent to the
reviewed whole-input contract. It is not mechanically derived from prose.
`MAPPING.md` identifies the assumptions and boundaries. CSSOM coercion, API
exceptions, byte decoding, encodings/BOMs, native Firefox code, tokenization,
infinite streams, allocation costs, and stack/performance limits are not proved.
The canonical library and live browser sources are unchanged.

## Reproduction

Source-only replay copies exactly 26 files; complete normative source files and
the remaining library are not duplicated. From the Firefox repository root:

```sh
python3 artifacts/css-domstring-streaming-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out artifacts/css-domstring-streaming-20261110-v1/review-replay
```

The output directory must not exist. All temporary Lean objects are removed.
Source-only replay authenticates the retained excerpts. To independently repeat
their full-snapshot and library-origin checks:

```sh
python3 artifacts/css-domstring-streaming-20261110-v1/verify_origins.py \
  --spec-root artifacts/css-domstring-codepoint-boundary-20261110-v1 \
  --library artifacts/css-spec-lean \
  --out artifacts/css-domstring-streaming-20261110-v1/review-origins.json
```

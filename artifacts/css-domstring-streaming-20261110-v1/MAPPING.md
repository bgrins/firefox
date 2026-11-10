# Streaming boundary and normative mapping

The adapter consumes already-acquired 16-bit code units, represented by
`Fin 0x10000`. Natural-number entry helpers use `unitOfNat?` for each unit;
values above 0xFFFF are rejected rather than wrapped. The mathematical domain is
arbitrary finite lists of finite chunks, including empty chunks. ECMAScript's
separate string-length bound is not enforced by those numeric helpers.

The source contract is the existing whole-input interpretation and filtering,
not a normative mandate for this particular carry representation. A generic
`Machine` provides single-item conversion, optional adjacent-pair conversion,
and a hold predicate. Its checked `unheld` obligation establishes that an item
emitted immediately cannot pair with a later item. `accept`, `feed`, and `chunks`
retain at most one pending item. Empty chunks preserve pending state; only
`finish`/`pipeFinish` performs EOF flushing.

| Source clause | Existing whole-input boundary | Streaming specialization |
| --- | --- | --- |
| WebIDL DOMString and successful conversion | Already-acquired Infra string/code units; coercion excluded | `DomString.CodeUnit`, checked numeric admission |
| Infra strings and ECMAScript String Type | Combine adjacent leading/trailing surrogates; preserve unmatched surrogate code points | `utf16`: hold only leading surrogates, exact existing pair arithmetic |
| CodePointAt and StringToCodePoints | `DomString.decode` / independent `Decoded` relation | `utf16_chunks`, `utf16_decoded_iff` |
| CSS Syntax input preprocessing | `CodePointInput.preprocess` / independent `Preprocess` relation | `css`: hold CR, combine CRLF, apply existing single-point conversion |
| Composition of both boundaries | `DomString.preprocess` / independent `Prepared` relation | `domstring_preprocessing_chunks`, `domstring_prepared_iff` |
| CSSOMString choice | DOMString or USVString depends on caller/type choice | Boundary evidence only; no CSSOM caller is proved |

`pipeChunks` actually feeds each decoded chunk's emitted points into the CSS
stage with both carries preserved. It does not decode or preprocess each chunk
in isolation. At EOF, `pipeFinish` flushes the UTF-16 carry through the CSS stage
before flushing the CSS carry. The generic factorization and composition proofs
show this incremental execution equals whole decoding followed by whole
preprocessing for every finite chunk partition. The reachable pending-domain
law proves high-surrogate-only and CR-only carries in the composed pipeline.

Four reference modules are copied unchanged from standalone-library revision
0127c4f42c620cdaba4f9b92cca93ca95df2d913. They provide the independently stated
whole-input relations and their existing correspondence proofs. The new proofs
establish generic continuation invariants, chunk concatenation, specialization,
and composition; they do not change the reference definitions or infer the
reference's meaning from executable examples.

Nine exact normative excerpts were authenticated against their full pinned
primary snapshots in the earlier DOMString artifact. SOURCES.json contains the
immutable source URLs, revisions, and full-file hashes; CLAUSES.json retains
byte offsets, excerpt hashes, and local excerpt paths. ORIGIN-CHECK.json records
that full-snapshot and exact-span authentication. To keep this artifact small,
source-only replay checks the retained excerpts, not duplicate full ECMAScript,
WebIDL, Infra, CSSOM, and CSS Syntax source files. The original full snapshots
remain in ../css-domstring-codepoint-boundary-20261110-v1/inputs.

No byte decoding, endianness, BOM handling, encoding selection, CSSOM coercion,
exception/side-effect behavior, actual Firefox input adapter, tokenizer, parser,
or infinite-stream productivity is proved. The list-based implementation models
incremental semantics, not allocation costs, stack limits, or a performance
bound. EOF is invoked once by the complete adapter; an empty chunk is not EOF.
This is a manually reviewed source mapping and a checked streaming refinement,
not mechanical derivation from arbitrary specification prose.

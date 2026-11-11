# Number document transfer

This capsule transfers the accepted consume-number program through an actual `Lean.Json` document and into the accepted ParserIR backend. It adds an interchange contract, not a CSS feature or a mechanically extracted specification.

## Proven interfaces

- `ParserSchema`/`ParserArguments` describe actual Json values using the existing exact `op`/`args` node relation, constructor arities and ordered children. `TypeSchema` supplies the five base types for embedded legacy statements. These relations contain no parser-reader success predicates.
- `decodeParser_spec` is an iff for every Json value and typed ParserIR program. The result shape is checked; `nonempty` only accepts a character-list child. Expression predicates use context `[scalar]` and Boolean result. Legacy statements use an empty context and their declared base result. Both leaf schemas are alias-free and reuse the accepted actual-Json correspondence.
- `parser_json_roundtrip` covers every typed program built from the seven existing constructors: legacy, take, maximal scan, nonempty, pair, right, optional. No new parser primitive is introduced.
- `EnvelopeSchema` independently requires exact outer keys, the version string, object-valued source metadata, and the parser schema. `document_spec` is an iff for every actual Json value. `document_json_roundtrip` covers every typed parser. This separate envelope does not extend the earlier statement-document format.
- `document_lowering` composes accepted decoding with the prior `lowering_correct` theorem, preserving the entire modeled state and successful value. Failed parsing is explicitly `(none, originalState)`. Failed decoding is the outer `none`, a different result. Pair/right failure and optional rollback restore both input and the error flag.
- `accepted_number_execution` applies that contract to any program of `NumberShape`. Shape agreement alone does **not** imply CSS-number behavior.
- `number_fixture_encoded` and `number_fixture_decoded` bind the quoted actual Json value to the accepted `numberTree`. `number_fixture_relation` then transfers the prior independent `NumericResult` relation. `fixed_number_ready` retains the caller's `StartsNumber` premise. The exact projection remains the accepted Int significand, Int decimal scale, lexical type flag and optional explicit sign.

## Representation and termination

The inherited node schema accepts all four exact two-entry raw-map layouts, either field order and arbitrary cached sizes. This is deliberate: the recursive reader pattern-matches raw maps rather than assuming well-formed ordered maps. The outer envelope uses the inherited `ExactKeys` permutation relation and the actual `getObjVal?` lookup contract; key membership alone does not assert lookup on a malformed map.

The parser reader and its completeness proof recurse on actual Json/argument-list size. `node_arguments_smaller` supplies the explicit structural decrease. Parser evaluation scans arbitrary finite input lists structurally. The lowered scan uses the exact input length, connected to maximal scanning by the prior theorem. There is no arbitrary recursive depth or scan fuel in the model.

`certify` packages a successful leaf decoder value with its proved schema. Its separate result argument makes computational reduction available without placing the decoder call inside a dependent match discriminant. It introduces no axiom or semantic oracle. Runtime execution uses the decoded parser; it never selects `numberTree` based on a profile name.

## Actual files and boundary evidence

`EmitNumber.lean` serializes the typed programs using the proved encoder. `Fixture.lean` quotes the exact two file literals. The checker verifies byte identity between those literals and the `.json` files, and kernel proofs identify their Json values. The actual-file runner separately invokes `Json.parse`, the envelope decoder, and the returned parser. The parsed-file observations are not inferred merely from the quotation theorem.

The changed file replaces exponent-marker `take` with `scan`, retaining the result shape. On `1ee2`, the original retains `ee2`; the changed program consumes the input with scale 2. This is intentional different-program evidence, not a second CSS conformance claim. An independent regex/exact-integer observation generator checks both files, including both incoming error states and large exact values. Empty/non-number inputs exercise the total model; they do not satisfy the normative caller premise.

## Preserved sources and normative provenance

`PRESERVED.json` records 49 origin mappings for 36 unique Lean dependencies and four normative mapping inputs. Canonical sources come from standalone Git commit `56c09405cd45a3c9b333dcec747e39efaebc7e1b`. Parser/number/lowering inputs come from the accepted Firefox research commit `7d4e7fcd82e8557ea9d236f412930b7b3bd8d073`. Number-side imports are relocated by an explicit import-line map; overlapping core sources agree exactly after that map. No preserved definition body is changed.

The pinned CSS Syntax draft is [csswg-drafts c410ee5e, css-syntax-3/Overview.bs](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs). `SOURCE.json`, `CLAUSES.json`, and `source_map.py` retain the accepted exact consume-number, digit and starts-with-a-number excerpts, offsets and hashes. The checker re-extracts and compares them. The mapping of that prose to the existing number model remains manual.

## Explicit limits

No JSON text-parser, duplicate-text-key policy, serializer or quotation implementation theorem is claimed. Those remain separately observed toolchain boundaries. The reader's universal claims begin at `Lean.Json` values. Standard primitive character, integer, list and raw-map operations retain their Lean semantics. The numeric result does not establish native floating-point rounding, overflow, Gecko execution or memory safety.

There is no alias environment, definition list, profile dispatch or general outer-document orchestration in this envelope. Alias `use` nodes, extra `definitions`/`profile` keys and unknown versions are rejected. Source metadata is required to be an object but is not interpreted or proved to describe the program. No byte decoding, DOMString coercion, lexical token caller integration, arbitrary CSS prose translation or new CSS coverage is established here.

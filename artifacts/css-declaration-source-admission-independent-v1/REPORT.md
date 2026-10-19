# Independent declaration source-admission review

## Recommendation

Accept the limited source/interface audit and five universal optional-publication helper lemmas. No substantive blocker found. This is not acceptance of complete native parser-to-batch composition, declaration value equality, callback scheduling or CSSOM lifecycle semantics.

## Authentication and replay

The supplied FREEZE, MANIFEST and checker hashes matched. All 28 manifest inputs authenticated before execution. A fresh copy in an external temporary directory passed the source-only checker and Lean compilation. Five exact theorem names were audited; each uses only propext. REPLAY.json, COMMANDS.json, RESULT.json and AXIOMS.txt retain the result. No native compilation, browser, Git or live source mutation was performed.

## Proof reading

Read all of Publication.lean. `publish` traverses ids using filterMap and at most one Option payload for each identity. `published_ids` proves its precise identity projection by induction. `unique_publication` and `uniform_publication` inherit Nodup and Pairwise from that filtered list. `publication_capacity` derives the length bound. `admitted_source` combines those three properties and an admitted original capacity bound.

These are meaningful universal structural lemmas with arbitrary identity/payload types and arbitrary compatibility relation. They assume the source identity roster is unique/compatible and fits. They contain no payload equality, no native comparator axiom, no parser model and no claim to derive those inputs from arbitrary bytes. Option values are modeled as a pure function of identity; this is a valid interpretation of a unique fixed roster after a successful parse, not a proof about mutable callbacks themselves.

## Independent source review

Read the complete recorded setter helper and eight caller bodies. Six callers use with_one, two create default scratch and call parse_property_into. The parsed callers only reach the setter on successful parsing. The helper makes a fresh plan, prepares, invokes the before-change closure, then drains into update. Callback stability and normal completion remain external.

Read the retained parse_into branches and shared fallback helper, generated shorthand publication template, ShorthandId dispatcher/longhands traversal, source vector with_one/push/clear/drain, and metadata capacity generation. Successful generated shorthand parsing uses parse_entirely before publishing. The parse_value interface does not receive scratch. Publication visits each fixed subproperty variant once, optionally omitting disabled identities. Keyword/deferred branches use the fixed longhands list; all is stored separately. Abandoned ordinary success is cleared before deferred publication by the already accepted repair. Source push uses try_push with a debug assertion, so capacity admission is a substantive requirement, not an unconditional fallible-vector theorem.

Independently recomputed uniqueness, absence of opposing mappings within a logical group, and expansion sizes directly from TOML without treating PROVIDERS.json as an oracle. All 94 explicit shorthand rosters satisfy these conditions; font has the maximum 19 entries. The producer additionally compares ordered rosters with the retained generated receipt. This finite check binds this metadata version; it is not a universal Mako/compiler theorem. Engine gating and optional filtering cannot enlarge these inspected rosters under the retained generation contract.

## Checker limits

Authentication precedes helper imports and replay. The exact five theorem names and allowed axioms are checked. Source-check extraction handles the retained syntax; its reused Rust tokenizer is not a general Rust parser and includes unused dispatch-analysis routines. The current nine recorded bodies were read directly, so this does not block this pinned audit. String-count assertions check the current call roster, not arbitrary future source transformations. Generated-template publication correspondence is a human source audit rather than a mechanically translated proof. No semantic mutant suite is claimed or required for these elementary helper lemmas; no new broad testing was added.

## Remaining gates

1. Mechanically compose admitted source publication with the full batch algorithm and storage invariants.
2. Admit generated parser callbacks, property identity/payload construction and normal-return behavior beyond this interface audit.
3. Establish callback stability between prepare/update and actual drain/storage/native integer/heap contracts.
4. Keep arbitrary native PartialEq distinct from mathematical equality; the separate NaN audit remains applicable.

The final report accurately preserves these boundaries. No change to the sealed producer capsule is requested.

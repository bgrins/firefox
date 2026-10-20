# CSS specification source ledger pilot

This portable Python tool locks three primary HTML documents and creates a deterministic source-node and byte inventory. It does **not** extract accepted normative requirements, implement HTML5 DOM parsing, or prove CSS semantics.

## Offline replay

Requires Python 3.10+ with its standard library. The recorded replay used the Python version in receipts/RESULT.json. No network, Lean, Firefox checkout or browser is needed after copying this directory.

```
python3 -I -S verify.py
python3 -I -S check.py --output /absolute/new/output-directory
```

The destination must not exist. The checker regenerates all inventories, compares canonical decompressed JSON with the retained inventory, validates every byte interval/hash/UTF-8 boundary, and runs 16 corruption controls plus explicit positive fixtures. It preserves unknown source material rather than dropping it.

Import another compatible source lock without comparing to this release:

```
python3 -I -S importer.py --lock sources.lock.json --output /absolute/new/inventory
```

Acquire current versions into a **new** directory (network required; not part of offline replay):

```
python3 -I -S fetch.py --output /absolute/new/acquisition
```

Fetching again does not reproduce an old document revision. Review the new content/hash and make a new source lock. Failed acquisitions are recorded with status/error and make fetch.py exit1. The importer reports failed documents; the release checker requires all three declared documents acquired.

## Output contract

Each `inventory/*.json.gz` decompresses to canonical JSON. `SUMMARY.json` identifies target contexts and sizes.

- Document identity: requested/final URL, retrieval time, UTF-8 bytes, SHA256 and HTTP metadata in sources.lock.json.
- Units: an ordered, nonoverlapping complete partition `[start,end)` of original bytes. Every unit has a source-revision-qualified identity, byte digest, lexical kind and proposed content categories.
- Anchors: actual source IDs mapped to unit ordinals. Duplicate source IDs remain explicit frontiers; the selected documents have none.
- Candidate: the unique requested anchor plus its nearest preceding heading through the next heading at the same/higher rank. This is a proposed reading context, not a normative section boundary theorem.
- References: target-context links distinguish inside, same-document outside, and unresolved/external. Whole-document external links are retained as discovery frontiers, including nonnormative/support links. They are not asserted to be normative dependencies.

`INTERPRETATION-FRONTIER.json` adds separately proposed human review dependencies. It is intentionally distinct from automatically discovered hyperlinks. In particular, fragmentation's adjacent optimization section remains open even if a link extractor does not discover an incoming obligation.

## Source node meaning and limits

A node here is a lexical HTMLParser callback event: tag, text, entity, comment, declaration or explicit unclassified gap. It is not a rendered DOM node. Omitted HTML end tags, implied elements, template/foreign-content parsing and browser DOM correction are not modeled. Attributes and original byte slices remain available for independent interpretation. Parser callbacks are source-checked; unreported regions remain gaps, and overlapping callbacks fail.

Heading, prose, algorithm, table, IDL and figure labels are syntactic candidates. An ordered list is only an algorithm candidate. A note/example class marks only that source tag as informative-candidate; its full semantic scope is not inferred. All other dispositions remain unclassified. Text inside script/style can therefore receive a coarse prose label; reviewers must read source context. No candidate label grants normative status.

The byte validator checks coverage independently of category decisions. Canonical regeneration additionally binds categories and anchor extraction to this importer version. Both rely on Python, its HTMLParser/UTF-8 codec, hashing and the host runtime; there is no formal proof of these tools. Python-version changes that alter extraction must receive an explicit output review. Gzip container bytes are not the semantic comparison; canonical decompressed JSON is.

## Review and integration boundary

See REPORT.md for the bounded result. Keep this package separate from `artifacts/css-spec-lean` until interpretation and interface review. The v4 inventory schema can consume document/source-unit records, but `normative_context` and requirement bindings must stay unresolved/proposed. No accepted binding is emitted. Stable requirement identities belong to a later reviewed semantic layer; these source-unit identities intentionally all change when a document digest changes.

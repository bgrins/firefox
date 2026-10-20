# Source-lock and accounting implementation

## Delivered

A working offline importer and replay checker, with three complete primary documents and compressed deterministic inventories. No existing library, native source, WPT, browser, build or Git state was modified.

| Document | Locked bytes | Source nodes | Unique source anchors | Selected context bytes |
|---|---:|---:|---:|---|
| CSS Fragmentation3 ED | 274,435 | 6,375 | 471 | [99,200,104,879) |
| HTML semantics page | 333,092 | 19,632 | 1,624 | [283,547,326,229) |
| CSS Fonts4 ED | 1,422,027 | 49,619 | 2,247 | [537,360,540,822) |

Every one of the 2,029,554 source bytes belongs to exactly one ledger interval; intervals begin/end at UTF-8 boundaries. The three requested anchors resolve uniquely. No duplicate source ID or unclassified gap occurred in these particular imports. This establishes deterministic accounting of these fetched files, not coverage of every normative requirement or all CSS.

Sources were freshly fetched from [Fragmentation](https://drafts.csswg.org/css-break-3/#unforced-breaks), [HTML style-block updates](https://html.spec.whatwg.org/multipage/semantics.html#update-a-style-block), and [font cluster matching](https://drafts.csswg.org/css-fonts-4/#cluster-matching). Complete bytes, source URLs, successful retrieval timestamps/headers and hashes are locked. Initial sandbox DNS failures remain in FETCH-ATTEMPT-1.json; the later authorized direct fetch succeeded. The full HTML semantics page is one multipage document, not the entirety of HTML.

## Accounting versus interpretation

The importer accounts for lexical source events and bytes, not browser DOM nodes. It retains original tag attributes and all non-content material. Syntactic categories identify headings/prose/list algorithms/tables/IDL/figures/support. Explicit note/example-style classes are informative candidates; the rest remains unclassified. This intentionally does not infer inherited normative context or turn words such as “must” into accepted requirements.

The HTML target is a definition inside the style-element section. Its reading context starts at that containing heading and retains triggers, IDL and surrounding prose. The two CSS targets are headings. Their nearest-heading windows are deterministic proposals, not claims that all dependencies fall within the windows. The next semantic pass should select exact clauses with independently reviewed exceptions and obligations.

Current source binding has a useful adversarial distinction: Fragmentation Rule4 says class B while its link points to #btw-blocks. The importer preserves both raw text and link; it cannot decide which is authoritative. Also the adjacent optimization section's actual anchor is #best-breaks. It remains in INTERPRETATION-FRONTIER.json for independent review, including the reported zero-size-fragment rule. Its absence from a direct outgoing-link list would not remove the obligation.

Root's independent interpreter reported a CR2018 versus ED decoration-truncation difference. This release selects the exact ED bytes. It does not acquire or certify that historical comparison, and does not merge it into the selected interpretation. Full-source hashes must match before comparing the independent clause inventory.

## Meaningful gates

The checker freshly regenerates all three ledgers and compares canonical decompressed bytes, then validates independently traversed interval coverage, per-unit digests, unique expected identities and source binding.

The16 rejection controls are: for each document, changed source, omitted final unit, duplicate unit identity and byte gap; plus a stale input rejected before destination creation, duplicate document identity rejected before destination creation, and two source-edit invalidations. A positive fixture independently checks a non-ASCII two-byte position, entity references, a quoted `>` in a tag, comments, raw script `<`, and reconstruction. Missing target anchors remain explicit unresolved frontiers rather than disappearing or being marked accepted.

The edit exercise replaces the unique phrase “must place at least some content” with “may place at least some content” in a temporary copy. This is a synthetic semantic edit, not an actual CSSWG revision. The old lock rejects the edited file; updating the lock still rejects the old ledger. Fresh import creates a new complete revision and source-unit identities. No interpretation/theorem acceptance transfers automatically. receipts/EDIT-INVALIDATION.json records exact before/after hashes and offsets.

These gates reject corrupt accounting. They cannot reject a semantically wrong but consistently regenerated classifier or an incomplete human requirement universe. No theorem count, normative extraction or Lean acceptance is claimed.

## Portable interface and next gate

The implementation uses Python's standard library only. Its public functions are `inventory(document, bytes)`, `validate(document, bytes, ledger)` and `run(lock_path, new_output_directory)`; source acquisition is a separate explicit command. All output identities include the locked revision, and replay refuses existing output directories. Complete sources retain their own copyright/license notices. Generated inventories can be regenerated from the sources and scripts; no downloaded toolchain or build target is included.

The corresponding v4 SQL fields are document URL/hash/edition selection, source-unit span/kind, and source references. This package leaves normative-context classification, source partition interpretation, requirement guards and accepted bindings for human review. It does not execute or import the v4 demo database.

Next: compare the independently authored fragmentation clause/choice/progress inventory against this exact source and accounting window. Review #best-breaks, class definitions and progressive-relaxation context explicitly. Then conduct independent interpretation of HTML's triggers/ordering and Fonts' cluster/provider contracts. Only after reconciliation should versioned requirements and Lean definitions be attached. Hyperlink closure, complete byte accounting and semantic completeness are separate gates.

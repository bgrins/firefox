# RFST queue and outer-pass extraction

This is a small successor of the sealed extractor `6482409b`. It adds the exact queue/pass event names emitted by source capsule `a433f953`, indexes `root_node` and `normalized_node` with the existing node namespace, and adds separate `set`, `compositor` and `document` address namespaces. The raw-line parser and CLI are unchanged. The delta is retained in `EXTRACT-DELTA.patch`.

```
python3 -I -B artifacts/css-root-font-startup-trace-log-extractor-v2/extract.py CLOSED_RAW_LOG > NEW_EXTRACTED_JSON
```

Every RFST-containing raw line retains its one-based source line number, full text/newline, original order and recoverable bytes (UTF-8/surrogateescape). Fields including `pass`, `level`, `type`, `posted_before`, `skip`, `pretraverse`, `posted`, `count`, `found` and `post_required` remain strings. Hex normalization applies only to addresses in their declared namespaces. Same-valued set/compositor/document addresses do not imply the same object. A `root_node` or `normalized_node` explicitly denotes a node address; this does not by itself establish parentage, pseudo identity or lifetime.

The extractor does not carry a current pass, borrow fields from adjacent records, match enter/exit pairs, join a compositor to a style set, or assign a request to a document/traversal. Pass numbers remain local logged values. Repeated/interleaved records and address reuse require manual interpretation using the actual cohort and complete source/log context. File order is not a cross-thread happens-before proof. Queue counts do not imply selection, application or readiness. A selected target does not prove composition or installation.

Unknown events, duplicate fields, invalid bytes and multiple RFST markers are retained without identity correlation for those ambiguous rows. A partially interleaved record with only one marker can still parse; this is a bounded diagnostic extractor, not a concurrent-log repair tool. The non-hex `(nil)` spelling is not indexed; hex spellings (including `0x0`) retain the inherited mechanical normalization and do not certify a live pointer. Existing flags, node/effect/device/thread indexing and raw parsing behavior remain unchanged.

Only saved synthetic checks are performed here. No new raw trace, browser, profile, native source, index or canonical operation is included. Actual queue/pass interpretation must await the new closed log and reproduction of the single-late 46/46/46→64 observations under logging.

Actual saved check `8ae6fb/0` passes all inherited assertions plus 18 exact new event names across 20 queue/pass rows and five ambiguous-row cases. Source event inventory is checked against the pinned native delta. No actual trace has been processed by this successor.

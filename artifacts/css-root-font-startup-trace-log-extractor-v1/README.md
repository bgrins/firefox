# Read-only RFST extraction

Run after the root-owned browser session closes:

```
python3 -I -B artifacts/css-root-font-startup-trace-log-extractor-v1/extract.py PATH_TO_CLOSED_RAW_STDOUT > NEW_EXTRACTED_JSON
```

The command only reads its input and writes JSON to stdout. It records the input SHA256/byte count and retains every line containing RFST, with its original one-based file line number and full text including newline. UTF-8 surrogate escaping preserves non-UTF-8 bytes through JSON; encoding each raw field with UTF-8/surrogateescape recovers the input line bytes.

Records stay in file order. Named fields retain their exact string values, including full traversal flags, numeric task masks, optional old values and ThreadId text. Address indexes normalize hex spelling only. Node indexes join node/input_node/target_node/root/child fields; effect and device namespaces remain separate. A build-properties line supplies an explicit effect/target co-occurrence; root-published and rem-basis supply explicit device co-occurrence. Converted-font rows retain node/keyframe/value fields. No association is invented for a row that lacks a field.

Unknown events, duplicate fields, malformed records and lines with multiple RFST markers remain in the raw records. Unknown/duplicate/multiple-marker rows do not contribute identity correlations. Null pointers are not indexed. This is a compact diagnostic parser, not a general concurrent-log decoder. A partially interleaved line with only one marker can still require manual inspection.

File order is not a total native execution order. Thread IDs, node/effect/device addresses and equality of addresses do not establish lifetime identity, target cohort, delivery, phase or cause. Addresses may be reused. C++ rows do not carry thread IDs; the extractor does not borrow a nearby Rust row's thread. It does not infer that a converted value was installed or sampled, classify startup outcomes, or claim that AnimationOnly was FinalAnimationTraversal. Root must first validate the actual single-late observations and inspect complete raw lines around any inferred sequence.

Final saved check c68feb exit0 exercises exact lines/bytes, CRLF and invalid UTF-8, flags, same-device and node/effect indexes, unknown/duplicate/multiple-marker cases, no-output/null cases and JSON roundtrip. The synthetic46/64 values carry no browser evidence. No actual trace has been read, and no browser, profile, source, index or native operation is included.

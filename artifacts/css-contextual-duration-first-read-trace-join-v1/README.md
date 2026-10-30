Strict saved-trace correlation helper for the exact rem V2/lh V1/property V2 fixtures. It changes no source, fixture or execution owner. It has not analyzed an actual instrumented browser run.

The CLI takes a frozen runtime and an externally authenticated runtime manifest digest:

```sh
python3 -B artifacts/css-contextual-duration-first-read-trace-join-v1/join.py --runtime artifacts/ACTUAL-FROZEN-RUNTIME --runtime-manifest-sha256 ACTUAL-DIGEST > artifacts/NEW-EXTERNAL-JOIN.json
```

It verifies all consumed runtime bodies against FILES.json; replays the sealed trace parser over exact raw.jsonl and compares its entire output with TRACE.json; authenticates TRACE-BINDING's parser/raw/report and equal before/after generated-header hashes; checks all three captured fixture bodies against actual session 8127 bytes; and verifies the collector and nine private record envelopes/hashes/run-ID with the two original pure schema validators. The caller must separately authenticate the compiled application's provenance, source ownership/restoration and the manifest digest. A saved header receipt is joined; this helper does not read a live build header or certify the compiler used it.

All 258 authored CSS property queries must form exactly nine stable PID/window/document groups, one for each page/mode. Each group must match its entire ordered 31/36/19 role/property roster without skipping queries. Native property IDs come from the pinned configured compiler mapping. Every query must be closed, uncapped, untruncated and nonnested, with unchanged entry/exit identity; each role keeps one target/pseudo/identifier tuple and distinct roles cannot alias one target. Additional/missing/reordered/internal queries, ambiguous nesting, unknown labels and ownership changes reject correlation. A structurally valid but semantically incomplete trace is not accepted by relaxing the roster.

The numeric join covers all 204 posted CSS fields: child opacity/width samples and detail reads of duration, font or line-height. Initial standalone/setup detail reads have no posted counterparts; all 54 are retained with posted_value_joined=false. No initial observation is fabricated. Animation effect timing/progress, currentTime, driver values and membership flags remain schema-validated record data; the logger does not capture those API returns, so they are explicitly not native-joined.

The finite canonical CSS serialization domain is intentionally narrow: decimal/exponent opacity, px lengths and s durations only, with no whitespace/junk, infinities or NaN. Within that domain Python binary64 conversion implements the fixture's Number/parseFloat value, and duration is multiplied by 1000 as authored. Every recorded number must equal the conversion exactly; no tolerance hides a mismatch. This is not a general ECMAScript Number/parseFloat implementation. Alternate serialization outside this domain requires explicit review, not silent acceptance. Negative zero is indistinguishable after JSON recording.

Output preserves every authored phase's query IDs and already-produced return strings, and includes every event/full-key identity within each first-child query interval. Unknown compositor/cascade sentinel values remain explicit. Correlation is not proof that a dispatch was delivered, WillComposeStyle actually composed, a getter was a model step, or a specific queue caused staleness. Callback verdicts are retained, including ordinary FAIL; wrong mathematical values are allowed when native returns and private observations agree. No first-freshness or native acceptance verdict is inferred.

The isolated synthetic check uses the frozen uninstrumented session 8127 numerical records to manufacture a full getter stream, including its stale first observations. It tests full-roster and frozen-runtime CLI success, preserves a FAIL callback label, and rejects 27 malformed/mismatched cases including header, fixture, run-ID, caps, truncation, missing/extra/nested queries, wrong role/property/target, wrong/null values, unknown kinds, incomplete records and raw-body tampering. Two direct numeric conversions are checked. Scratch is removed. The first check 3c65f6 stopped on the test's own phase-group count (it omitted two standalone setup groups); correction 5aa8e2/619642 and full CLI check b86aed passed. No browser, native build, live state guard, Git/index operation or runtime mutation occurred.

Read-only rerun of synthetic checks (no package writes unless --write is explicitly supplied):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B artifacts/css-contextual-duration-first-read-trace-join-v1/check.py
```

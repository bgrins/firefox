# Private post-capture progress records

Small transport shared by the research-only acyclic two-hop and property-only probe V2 successors. No browser or native code is present. The write lifecycle is adapted from the reviewed duration-feedback-discriminator handler: owner-supplied absolute output directory, O_DIRECTORY/O_NOFOLLOW open, uid and0700 check, allowlisted filenames, O_EXCL/O_NOFOLLOW0600 files, close before acknowledgement. The exact delta is retained. Output records never determine numeric PASS/FAIL.

Future root-owned runner contract:

- Create a fresh private0700 records directory, record its identity, and generate a fresh run ID matching `[A-Za-z0-9_-]{16,128}`.
- Pass DURATION_PROGRESS_RECORD_DIR and DURATION_PROGRESS_RUN_ID only to the WPT child/server environment.
- Expect exactly three files for a single page: `two-hop-{literal,ordinary,animated}.json` or `property-only-{literal,ordinary,animated}.json`. A combined two-page phase expects all six. Verify file uid/mode0600/nlink1, unchanged directory identity, exact envelope run_id and handler.validate payload, then hash records into receipts.
- Retain records on ordinary assertion failure. Missing records after an initial calibration failure are incomplete collection, not an observed passive result. Never infer a clean PASS from the transport acknowledgement alone.

Request is `{kind, observation}`. The exact observation contains all four first/passive child samples and the existing sequential pre-membership, post-membership,751seek and750return snapshots. Two-hop includes middle/child identity flags; property-only includes its retained identity flag. Animated callbacks additionally include driver timing. Validator checks kind/phase order/shape/types, not convergence or expected numeric values. Incorrect widths/progress, false identities, null values and duration strings are retained for interpretation. Non-JSON tokens/overflowing numeric values are rejected before opening a file; JS serialization represents nonfinite numbers as null, which is retained.

The injected record function sends one POST only after the entire original collection and trace serialization. It awaits acknowledgement before the unchanged numeric/identity assertions. No request, new style/effect read, frame wait or mutation is inserted within sampling. The runner sees the complete stored record even if later numerical assertions PASS. A network/record failure is an observation-infrastructure failure, not a rendering finding.

Static7f8114/0 exercised six valid shapes and six exclusive roundtrips, preservation of deliberately wrong/nullable observations, and20 rejected requests/schema/ownership cases. Tests used only owned temporary directories and removed them. No WPT callback, browser, live application or canonical state was accessed. This is transport, not proof of first-flush correctness or native scheduling.

# Final escaped-terminal-quote WPT and browser binding review

**Accepted.** The complete retained pair passes the independent checker. No source, oracle, isolation or formatting concern found. This final review preserves the earlier independently approved source/proof scope and adds exact composition, WPT and raw browser binding. No production, WPT, Git, browser or build changes were made by this reviewer.

## Source and composition

The producer combined candidate SHA `54449cd1cb3ed1cd15769037919fbfb925f804fdda5956a52ccf57dbdf64409a` is bound to its sealed producer manifest. The independent source/proof review is bound to the root-supplied FREEZE and MANIFEST pins. No new native replay or broader theorem review was needed for this final task.

Two exact whole-file checks identify the live proposal: (1) producer combined candidate plus the previously accepted parity whitespace delta; (2) committed H1+H2 source plus only the closure-recognition predicate replacement. Both yield SHA `9f7dfa8368c3b3e99855d168ff24b695938a20afb08e693922a87d888b7c1355`. Formatting leaves these bytes unchanged, as independently checked against the candidate snapshot. The change preserves the parity decision, endpoint subtraction and final pop; it recognizes the escaped final quote as content and supplies the missing actual closer.

The earlier review's restricted token grammar, source admission, UTF-8/usize, provider and compiler boundaries remain unchanged. This artifact does not claim whole-parser or cascade verification. Root owns standalone upstream packaging separately; this is integration on H1+H2, not an isolated upstream build.

## WPT expectations and isolation

I read the entire final 18-case HTML and independently enumerated its names and expected decoded values in `ORACLE.json`. The checker uses a front-consuming decoder of the fixture's ordinary characters and paired escapes, independently of the repair's reverse parity predicate.

For both matching quote characters, a positive odd backslash run before a terminal quote escapes that quote: the quote belongs to the string value, and EOF still requires a closer. Even runs before a terminal quote retain a genuine closer. The test selects all four odd-run terminal-quote cases and fourteen unaffected controls. It excludes exactly the four positive-even-run EOF cases already covered by the parity repair. Zero-run, odd-run EOF, even-run closed strings, closed fallback and missing-quote fallback controls remain.

The explicit reference is a separately quoted decoded value followed by `, serif`. Preserving this suffix outside the recovered string tests the actual defect. It does not feed the same malformed input through both target and oracle. The assertions check custom-value/reference acceptance and computed font-family equality; all elements are cleaned up. Computed family-name comparison requires neither actual font availability nor timing coordination.

Normative basis is CSS Syntax's [consume a string token](https://drafts.csswg.org/css-syntax-3/#consume-string-token), independently retrieved during the preceding H1 review: the escape consumes the quoted code point as content, and later EOF returns the unterminated string token. This task adds no broader spec interpretation.

## Final raw pair

The sealed checker verifies exact per-name baseline predictions and candidate results:

- New closure WPT: **4 FAIL / 14 PASS → 18 PASS**, both harnesses OK.
- All 18 parity controls and all 38 H1 endpoint controls remain PASS.
- The broad 22-case string diagnostic changes its four remaining closure failures to PASS; all 22 pass afterward.
- Across 111 outcome keys, exactly eight status transitions occur: the four new-WPT cases and their four broad-diagnostic counterparts. All other status/expected pairs remain identical. Three existing expected syntax failures are retained.

Every raw JSONL outcome is keyed by file/subtest, with duplicate keys rejected and summary/log hashes checked. The exact WPT is bound to both runs. Within each run the before/after pin records are identical. Across runs only the intended Rust source differs among fixed inputs; the build receipt's three changes exactly match that source plus Firefox/XUL binary changes. Root's build exits zero, with the retained build log hash matching. The log contains export-tier monitor KeyError callbacks despite successful compilation/link completion. The candidate WPT process exits zero; the older expected syntax failures do not count as unexpected failures.

These are independently adjudicated root-executed shared-tree browser/build records. No new browser run or optional test expansion was performed here. Root lint/format records are retained.

## Recheck and commit roster

Authenticate the manifest and checker using the handoff hashes, then run:

```
python3 -I -S -B artifacts/css-quoted-eof-closure-final-review-v1/check.py --manifest <manifest-sha256>
```

This uses retained evidence and the Python standard library only. Commit exactly the manifest entries plus `MANIFEST.json` and `FREEZE.json`. The artifact contains no generated native binaries or Rust libraries.

# Hidden layout boundary review

Verdict: ACCEPT_BOUNDED_BOUNDARY_WPT_EVIDENCE. Combined timing rejected; historical source/build restoration authenticated. Native acceptance remains held.

## Source and oracle review

The reviewed 28 additions comprise eight leaf-first OOF cases, sixteen provider/ownership cases (including two fragmented OOF cases), and four fragmented inner-flex cases. Exact input hashes and ordered names are in `INPUTS.json`.

Every failing baseline target assertion follows successful independent visible calibration. The fixtures capture target observations before reading their visible reference, then assert the reference before the target. A reference failure would therefore prevent a target verdict; none occurred in these completed phases. “Leaf first” means before querying the OOF parent, after deliberate ancestor layout flushes.

The fragmented fixtures place their fragmentation contexts inside the hidden boundary. Their visible references explicitly establish two fragments before comparing hidden geometry; zero rectangles are not discarded. They do not assert that an externally fragmented size-contained hidden box must fragment. The containing-block transitions retain explicit offsets and compare the hidden subject with a visible containment reference. External-to-inner ownership controls keep the actual containing block inside the hidden boundary while its placeholder lies inside a nested flex box.

## Completed phases

| Phase | Full 686 rows | Added 28 rows | Calibration failures |
|---|---|---|---|
| Baseline | 645 PASS / 41 FAIL | 22 PASS / 6 FAIL | 0 |
| Principal only | 679 PASS / 7 FAIL | 22 PASS / 6 FAIL | 0 |
| OOF only | 652 PASS / 34 FAIL | 28 PASS / 0 FAIL | 0 |
| Both | 686 PASS / 0 FAIL | 28 PASS / 0 FAIL | 0 |

The six added failures are unchanged in status and exact message between these phases:

- Static OOF leaf, append/prepend: after insertion x=111 instead of 105; leaf size remains 6×8.
- Explicit-offset OOF leaf, append/prepend: after OOF parent resize the leaf remains 6×8 instead of 10×12; position is correct.
- Static flex/grid OOF provider: after insertion rectangle is [110,10,0,0] instead of [104,10,12,20].

All fragmentation, containing-block transition, external-to-inner ownership, and nested-hidden leaf additions pass. The principal candidate changes exactly 34 FAIL rows to PASS in the complete suite; all other 652 status/message pairs are unchanged. This separates the residual OOF failures from the principal-list repair in these observations; it does not establish their full native cause.

## Authentication and limits

The authentication receipts compare RUN rows and file ends with raw JSON events, validate all ordered subtest rosters, check selected source-role hashes and reviewed fixture hashes, and require before/after pin equality. All four phases have 22 file ends and one suite end. Failure classifications report the first failing assertion, not unexecuted later assertions.

No malformed fixture has been identified and no assertion was changed. Candidate source attribution, source lifetime/dirty-history correctness, performance, final restoration, isolated landing tests and final native acceptance remain separate gates. This review executes no browser, build or compiler and makes no production or Git changes.

The OOF-only phase repairs exactly seven baseline failures and preserves the other 679 status/message pairs. All 28 boundary additions pass. Timing analysis is retained separately in `COST.md`; observed hidden-query costs remain an explicit acceptance consideration.

## Four-phase result and rejected cost receipt

Across the exact 686-key roster, 645 rows pass in every phase, 34 have FAIL/PASS/FAIL/PASS, and seven have FAIL/FAIL/PASS/PASS in baseline/principal-only/OOF-only/both order. Both has 19 OK harness ends and three PASS reftest ends. This is useful separation of the two observed repairs; no WPT outcome regression occurs in this corpus.

The combined timing receipt reports stable pins and a complete observation, but `cleanupErrors` contains `PermissionError(1, 'Operation not permitted')`. The reviewed parent guard aborted before traces and entered restoration. The independent cost analyzer likewise rejects this receipt and produces no four-phase cost comparison. `COMBINED-TIMING-REJECTED.json` retains its exact hash and error. No trace execution or successful final restoration is inferred from passing WPT results.

Replay the retained raw outcome checks with:

```
python3 -I -S artifacts/css-hidden-flex-combined-boundary-review-v1/verify.py --runtime artifacts/css-hidden-flex-combined-runtime-v1
```

This checker uses pinned historical source/fixture/runtime receipts, not the current live source tree or HEAD. The cost analyzer independently regenerates the first-three-phase distributions into a fresh output path.

## Terminal restoration and original-corpus clarification

The externally pinned runtime manifest `86e59d39179a46b36f0b3c935b03cbd3b106dd1546d96286ea8ef0b0f31f4d07` authenticates all 400 payloads and the closed file roster. The driver terminated with exit 1 for its retained timing-cleanup failure. Restoration build succeeded with exit 0, no recovery errors, and exact INPUTS.before = BEFORE = FINAL equality for HEAD, staged diff, full index entries, native diff and source hashes. Root's sealed final receipt additionally records 26 restored source guards and six absent temporary test paths. This review uses historical receipts and does not require the present live HEAD to remain unchanged.

No traces ran. Process-group cleanup is not fully authenticated by a missing process scan, removed profile, or reaped direct-process status; the combined timing remains rejected. The earlier rejection receipt intentionally preserves the then-pending restoration status; `TERMINAL.json` supplies the completed restoration evidence.

The runtime report's phrase about the original 656 retaining prior outcomes refers to comparing the baseline/principal-only pair with the prior runtime. It does not mean all original 656 outcomes are unchanged in OOF-only/both: those phases also repair the original static-OOF failure, in addition to the six new OOF boundary failures. The exact four-phase matrix avoids this ambiguity.

No malformed boundary fixture or introduced WPT outcome regression was found. Native acceptance still requires the separate compact-file runtime, column-boundary investigation and explicit cost decision. Passing these 28 additions does not close arbitrary provider, lifecycle, dirty-history, or frame-graph obligations in the formal models.

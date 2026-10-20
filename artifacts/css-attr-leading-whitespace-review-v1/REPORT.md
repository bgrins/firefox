# Leading-whitespace attribute crash review

## Verdict

**Accept the scoped native repair and 26-case WPT.** No blocking defect found. The fix establishes the string origin before recording reference ranges, repairing a confirmed content-process bounds panic caused by removing a prefix afterward.

The observed installed release is Firefox 158.0, build 20261007201254. Both the scripted space case and the script-free minimal document produced content-process minidump extras with `start byte index 9 is out of bounds of var(--v)`. The plain control computed 37px. This supports a release content-crash claim for the tested binary; it does not establish memory corruption or a broader security classification.

## Verified evidence

- Original source: `18b61124b705887b6a103c015bfedec7bfdea63873248e067701c6097c90e56f`.
- Candidate source: `e3c5f24c1478ea9b1232748814b971939bf8b4895344b0717fdb3622ee7f3a20`.
- Final WPT: `858cd1e7077775790cfb40315816d5c0a450a373ca7e03d52b4abadf3a9bbdc4`.
- Independently reconciled candidate raw results: **373 PASS, two unchanged expected FAIL, 21 harness OK**. All **349 prior status/message pairs are unchanged**, and all **26 new whitespace cases pass**. The wider baseline consists of earlier candidate runs; the new WPT itself has no full pre-fix execution.
- Build and WPT receipts report terminal success and stable source/binary pins. This reviewer read and checked the retained evidence; no browser or build was launched here.
- The candidate differs from the original by exactly the prefix-token step and removal of post-scan leading trim. A separately retained upstream adaptation makes those same two edits while preserving upstream's unrelated EOF-repair implementation.

## Scope of source acceptance

The prefix step preserves comments and non-CSS whitespace, uses tokenizer byte boundaries for CRLF and UTF-8, and aligns nested-reference origins with the retained source. Non-whitespace lookahead retains tracker and comment observations across reset/cache replay. It performs no enable/query operation. NATIVE-REVIEW.md distinguishes these claims from exact equality of all cache fields or a whole-parser proof.

The WPT directly exercises raw typed attributes with distinct success/fallback expectations, including VT/NBSP negative controls. Internal comment-byte preservation and observer-state equality are not inferred from width alone. The component's remaining EOF-repair/range/representation assumptions are unchanged; no claim that every possible malformed range is now safe is made.

Upstream applicability is independently source-checked against a content-pinned tip fetch. The local patch may need context regeneration because of prior local EOF plumbing. No isolated upstream build or execution, exhaustive caller proof, or new formal theorem is supplied by this review.

## Reproduction and retained evidence

```sh
python3 -I -S artifacts/css-attr-leading-whitespace-review-v1/check_runtime.py . /private/tmp/attr-whitespace-runtime-review.json
```

This rechecks raw-row equality, stable pins, unchanged comparison results, final WPT/native hashes, release plain control, and both exact crash reasons. Source snapshots, the primary-spec excerpt, Searchfox discovery, the upstream-only patch and source checks are retained here. No compiler outputs were created, so no build directory cleanup was needed.

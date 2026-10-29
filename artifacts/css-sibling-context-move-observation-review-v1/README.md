# Independent move-boundary observation review

Saved-data replay 4132ac/0 confirms 15 PASS / 3 FAIL for the eighteen-case move page and 6 PASS for ordinary append-based reparenting, with one OK ending each. Both runs used identical captured app metadata and binary pins. Saved before/after states and application metadata match; both observation drivers report no error, empty owned-process registries and preservation success. The move child exit1 records expected test failures; it is not native acceptance or an infrastructure-failure waiver. Root owns external terminal provenance and runtime archiving.

The only failures are reparent-moveBefore sibling-count for width, opacity and inherited font-weight. All 27 records in their failure JSON independently pass topology, literal, equal-parent, repeated-read, no-animation and applicable geometry calibration. The failure occurs in the final value-comparison loop, after all three phases were calibrated. Exactly six records differ:

| Phase and target | Actual count represented | DOM count | Width | Opacity | Font weight |
| --- | --- | --- | --- | --- | --- |
| Moved: stationary old-left child | 2 | 1 | 20px vs 10px | .2 vs .1 | 200 vs 100 |
| Restored: stationary old-right child | 3 | 2 | 30px vs 20px | .3 vs .2 | 300 vs 200 |

The moved target and destination stationary target compute correctly. Initial snapshots are correct. Same-parent insertBefore/moveBefore reorder and all sibling-index callbacks pass. The source parent loses a child in both failing phases; same-parent reorder can be refreshed by destination-side invalidation, so its success does not independently certify removal-side invalidation. This is a concrete old-parent invalidation hypothesis, not a native root-cause proof. Failure of inherited font-weight as well as reset width/opacity distinguishes the observed shape from the previously repaired reset-rule-cache alias.

The three failing callbacks expose their full nine-record JSON. Passing callbacks do not export full records; their PASS status certifies the captured assertions ran, not an independently reconstructed corpus of all 162 records. No specific cache hit, missing native call, new fix count, candidate repair or formal coverage is claimed. This review performs saved-file checks only and does not rerun the historical assessor, browser or native code.

Run `python3 -I -S -B artifacts/css-sibling-context-move-observation-review-v1/analyze.py` to reproduce REVIEW.json from the pinned raw and saved state. The script never modifies runtime evidence. Initial narrower replay69cb6d passed; final4132ac additionally verifies exact ordinary roster and cross-run app/binary equality.

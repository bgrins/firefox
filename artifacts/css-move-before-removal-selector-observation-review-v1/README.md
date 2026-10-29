# Independent removal-selector observation review

Recount c74edf/0 authenticates the 26-payload runtime archive and confirms exactly nine ordinary-move PASS callbacks, nine moveBefore FAIL callbacks, and one OK ending. Root-reported terminal66118/618888/e3ad5f exited0; the WPT child exited1 for the observed assertion failures. Saved driver/result preservation succeeds, before/after states and app metadata match, the owned process group is absent and temporary root removed. No candidate was executed or accepted.

All 27 snapshots exposed by the nine failing callbacks pass independent topology, node identity/connectivity, literal width and geometry, stable-read, no-animation and selector/index calibration. Each failure occurs only in the final computed-width loop, after all phase calibrations. In the moved phase the old-parent computed width and geometry retain their initial values despite changed selector truth or index:

| Boundary | Stale width | Expected width | Calibrated selector/index |
| --- | --- | --- | --- |
| first-child, last-child, only-child, parent-empty | 10px | 30px | selector now true |
| nth-child(2), adjacent-sibling, general-sibling, parent-has | 30px | 10px | selector now false |
| sibling-index, moving first child | 20px | 10px | index2→1 |

Initial and restored snapshots agree with the intended values. Selector matches() is sampled after computed style/geometry, as recorded in the sealed fixture. Ordinary appendChild movement followed by position-preserving insertBefore restoration passes the same assertions. Passing callbacks do not export their full snapshots; their PASS is assertion execution evidence, while the 27 failing snapshots are independently reconstructed from raw messages.

This is one already-known removal-invalidation family with nine observed manifestations, not nine bugs or a new-family claim. Existing upstream moveBefore-child-list-selector-invalidation.html and bug2080017/PR63408 remain required prior art and future broad candidate controls. The data supports the separately traced skipped old-parent notification; this recount is not a native root-cause proof, model refinement, or repair validation. Sibling-index coverage adds the previously absent moving-first contrast; the earlier moved-last index controls did not shift stationary indices.

Run analyze.py with isolated Python to reproduce REVIEW.json from saved inputs. The script writes no runtime files. Raw read10dc5e, initial replay15e294, and final archive/terminal replayc74edf are recorded; no browser/build/source/index/epoch action occurred.

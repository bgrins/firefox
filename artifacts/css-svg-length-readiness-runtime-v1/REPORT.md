# SVG percentage conversion reproduction

The visible six-case diagnostic reproduces four persistent conversion errors on the restored working build. All six cases calibrate and repeat; both value-getter controls pass. Scalar rect.x and list-backed text.x behave identically.

| Operation after host200→400px | Expected | First stored result | Resolved value after layout |
| --- | --- | --- | --- |
| Read50%.value | 200 | 200 | 200 |
| Convert50% to pixels | 200px | 100px | 100, expected200 |
| Convert100px to percentage | 25% | 50% | 200, expected100 |

Each operation uses a fresh connected, visible no-viewBox SVG. The wrapper is acquired/warmed before mutation; conversion precedes any value/geometry read. Independent Python expectations, pre-flushed reference conversions and reset geometry all pass. The incorrect representation persists after layout; this is more than a stale transient getter result. Raw observations are preserved, including the separately constructed references.

This agrees with the independently replayed rational model's stale-source and stale-destination witnesses. The model assumes coherent supplied bases; the browser capture does not directly instrument their native acquisition. Source audit identifies missing layout preparation in both conversion paths, but no repair, clean-upstream/release novelty or native formal-refinement claim follows yet. The source role is the restored mixed working tree after the matrix experiment, not normalizedHEAD90 or its SVG candidate.

Session23760 exited0. Root replayed the strict validator from raw payload, authenticated all369 live source/resource/binary/absence roles and identical before/final snapshots, and rechecked index/native hashes. The50 general source guards are extended by14 exact length-source inputs in the role map. The runner preserves925 staged paths,26 native edits and both installed112 WPT identities; the owned browser group terminates and its profile is removed. No source, WPT, build or index mutation occurred. Matrix comparison history is retained in PRIOR-EXPERIMENT.json without recasting its separate acceptance state.

Next: independent results review, then a focused conversion repair and WPT covering both source-relative and destination-relative contexts. The accepted count remains113.

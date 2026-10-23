# Hidden layout cost observations

Analysis of three accepted timing receipts; the combined timing receipt is rejected for a cleanup error. This is descriptive local evidence, not a native acceptance or broad performance verdict.

`analyze-cost.py` independently checks complete observations, cleanup receipts, stable pins, timing-to-WPT source/binary identity, exact fixture bytes, row order, selected leaves, checksums and observed size counts. `COST-FIRST-THREE.json` preserves all five timing distributions for every configuration. Each phase has 84 measured batches and 4,032 leaf reads with no sampled size mismatch. Two warmup rounds are excluded; seven measured rounds rotate configuration order. Builds/phases remain in fixed baseline → principal-only → OOF-only order. There is one browser sample per phase, no reversed phase ordering or restored-baseline timing sample.

## Recovery query batch durations

Values are median [minimum–maximum] milliseconds over seven batches. Each batch sums 16 separately timed query groups, each reading one leaf for count 1 or four leaves for counts 32 and 256. These are not per-call timings or 16 independent measured rounds.

| Configuration | Baseline | Principal only | OOF only |
|---|---|---|---|
| principal/visible/1 | 0 [0–0] | 0 [0–0] | 0 [0–0] |
| principal/visible/32 | 0 [0–1] | 0 [0–1] | 0 [0–0] |
| principal/visible/256 | 0 [0–0] | 0 [0–0] | 0 [0–1] |
| principal/hidden/1 | 0 [0–0] | 0 [0–1] | 0 [0–0] |
| principal/hidden/32 | 0 [0–0] | 1 [0–2] | 0 [0–0] |
| principal/hidden/256 | 0 [0–2] | 9 [8–11] | 1 [0–1] |
| oof/visible/1 | 0 [0–0] | 0 [0–0] | 0 [0–0] |
| oof/visible/32 | 0 [0–1] | 0 [0–0] | 0 [0–0] |
| oof/visible/256 | 0 [0–0] | 0 [0–0] | 0 [0–0] |
| oof/hidden/1 | 0 [0–0] | 0 [0–0] | 0 [0–0] |
| oof/hidden/32 | 0 [0–0] | 0 [0–1] | 1 [0–2] |
| oof/hidden/256 | 1 [0–1] | 0 [0–1] | 8 [5–8] |

The 256-branch hidden principal samples are [0,0,0,0,1,2,1] ms in baseline and [9,11,8,11,10,9,8] ms with the principal repair. Hidden OOF samples are [1,1,1,1,0,0,1] ms in baseline and [7,8,5,8,8,8,7] ms with the OOF repair. All timer observations are integer milliseconds. A zero means no elapsed timer tick in the measured interval; it does not establish zero work. Ratios to zero and per-call nanosecond estimates would be misleading.

For those hidden 256-branch configurations, the mutation/outer-flush medians remain 2–3 ms. The additional measured time appears in the later leaf queries. That pattern is consistent with the source changes preserving dirty eligibility so queries force hidden layout. It does not count reflows or separate subtree marking from provider layout work; neither operation was instrumented here.

## Correctness and interpretation limits

The benchmark verifies outer dimensions and sampled 8×8 leaf sizes, and retains checksums showing the intended loops ran. It does not validate leaf positions. Its queryChecksum depends on indices and iteration counts, not returned geometry; geometryChecksum covers widths/heights only. Baseline and repaired runs therefore cannot be assumed to perform equivalent correct layout just because their size checks pass. The separate WPT failures demonstrate why previously skipped work can be observably wrong, but do not prove every extra benchmark operation is necessary or optimal.

Visible controls largely have 0 ms recovery-query medians, with occasional 1 ms observations; this resolution cannot support a general no-regression conclusion. The hidden distributions warrant an explicit cost decision and, if needed, investigation of repeated forced layouts without weakening correctness. These data alone do not establish statistical significance, browser-wide impact, or an acceptable performance budget.

## Combined timing guard

The combined phase completed its observation and reports stable pins, reaped process status −15 and profile removal, but also a nonempty cleanup-error list. The analyzer rejects it; no combined cost distribution is accepted or merged here. WPT correctness results are separately authenticated. Restoration subsequently completed with build exit 0 and exact historical BEFORE/FINAL equality. This does not override the timing cleanup rejection.

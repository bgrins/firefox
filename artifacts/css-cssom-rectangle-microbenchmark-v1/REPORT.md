# Rectangle read microbenchmark proposal

Status: executable proposal, not browser-run here and not a performance result.

## Inputs and execution

Serve `probe.html` and `benchmark.js` together. Await `window.rectangleBenchmarkPromise`; it resolves to the same JSON stored at `window.rectangleBenchmarkResults`. The script runs after an explicit body token. It makes no network requests. A root driver may append a result POST separately and retain that wrapper.

Defaults: depths 8 and 128; ordinary ancestry, transform nearest leaf, and transform nearest root; 20,000 reads per batch, seven samples each, 3,000 warmup reads per case. Six cases, 42 timed batches, 840,000 measured calls. Before/after calibrations and warmups add 18,012 calls. Hash options: `iterations` 1000–100000, `samples` 3–15, `warmup` 1000–20000, `startupMs` 0–30000. Defaults are 20000/7/3000/3000. Use identical options across binaries.

Each ancestor adds a small relative translation; the transformed ancestor adds a real CSS translation of (3,5). Exact expected small integer rectangles are checked before measurement. These fixtures avoid extreme-coordinate rounding defects. Root/leaf transformation placement targets long/short rejected-helper prefixes. DOM ancestor counts are fixture facts; exact native frame visits are source predictions, not runtime tracing.

## Measurement boundaries

All fixture construction happens before the startup delay, layout calibration, and warmup. No DOM or style writes occur between calibration and the final reads; output is written only after timing completes. Each timed loop repeatedly calls getBoundingClientRect and consumes x, y, width, and height into a checked checksum. Case order rotates across samples. There is a 10ms yield between batches, outside timing. All samples, including slow samples, are retained. Hidden-page, changed geometry, bad checksum, or nonpositive duration makes the result invalid.

This removes deliberate dirty-layout work from the measured loop. It does not prove zero engine layout work, count native helper visits, subtract JavaScript overhead, eliminate allocations/GC, isolate scheduler noise, or measure page performance. The JS mock validates invocation count and result plumbing only. Timings include API entry, flush checks, returned DOMRect allocation/property access, and checksum overhead.

Compare integer-only versus baseline, and both versus DOM-only, per case and depth. DOM-only versus baseline is a secondary control. Ordinary ancestry can replace the matrix walk; transformed ancestry retains the matrix path after some extra rejected-helper work. Deep transform-near-root is the intended worst partial-walk discriminator. Do not collapse all six into one mean or infer general browser impact. Retain per-batch data and compare medians only as a descriptive summary. For even sample counts the reported median is the upper middle observation.

Use a visible foreground tab, same machine/profile/settings, no concurrent builds or other browser tests, and record binary identity in the root driver. The fixed 3s delay is a convenience, not evidence that startup or temperature has settled. Very short batches need larger identical iteration counts across all variants. One serial variant run is exploratory; repeat runs with counterbalanced binary order before treating a small difference as a regression. No CI perf submission is proposed.

## Checks and remaining gates

`node --check benchmark.js` passed. `node mock-check.cjs benchmark.js` validates six cases, 42 batches, 840,000 measured calls and 858,012 total calls against a simple DOM mock. This is not browser geometry calibration. Root must execute and retain valid browser rows before using measurements.

The perftest and frontend skills guided measurement boundaries. No browser, main build, native source, index, or sealed predecessor was modified. The unrelated preserve-3d WPT assertion typo remains a separate possible good-first-bug in the sealed split review; it is neither filed nor part of this benchmark.

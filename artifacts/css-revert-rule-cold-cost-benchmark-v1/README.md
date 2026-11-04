# Cold-membership rule-chain benchmark

Open `benchmark.html` directly in a browser tab. It is standalone: no WPT, server, network dependencies, library, extension or privileged API. Preparation did not run the page or measure performance.

Use an A+B+D browser and an A+B+D+coldC browser with `layout.css.revert-rule.enabled=true`, the same configuration and otherwise comparable builds. Record each build label and download JSON. Repeat whole runs in alternating build order; compare distributions and raw samples, not one elapsed number. A support check rejects browsers that do not recognize the keyword. This is not a release-default exposure claim.

## Workload

One element matches N separate unlayered rules with equal selector specificity. Every block contains an opacity declaration and the same unused custom-property name with a different numeric value, making block contents distinct. A lower-layer rule supplies `opacity: var(--floor)`.

| Mode | Each unlayered rule's opacity | Expected behavior |
|---|---|---|
| literal | `var(--floor)` | First winning opacity declaration supplies the value. |
| revert-rule | `revert-rule` | Exclude N successive rule blocks, then use the lower-layer value. |
| revert-layer | `revert-layer` | First rollback excludes the unlayered declarations, then use the lower-layer value. |

N=0 is a common floor. Each update alternates the inline custom property `--floor` between 0.25 and 0.75 and immediately reads computed opacity. All three modes must alternate between those exact results. This makes the observable value change on every update without reparsing the chain stylesheet inside the measured loop. It does not by itself prove each native path was entered; an implementation may optimize repeated cascades.

Stylesheet installation and its first style flush are measured separately as setup. Four warmup writes/reads precede each timed sample. Timed work includes the custom-property write, computed-style read, JavaScript array store and deadline clock check. Value comparisons occur after timing. The result therefore measures the complete update/read workload, not isolated native lookup time. Parsing is outside that interval, but allocation/GC and other browser work can still affect it.

Counts are capped at 256, with at most eight selected counts, 15 samples and 64 updates/sample. The default is 0,16,32,64,128,256; seven samples; sixteen updates. It uses one element and no deep tree. Mode/count order rotates between rounds. Stop is serviced between samples; time guards are checked between synchronous reads (one-second sample and thirty-second run limits), so they cannot interrupt a hung browser call. Incomplete samples remain in JSON and are excluded from timing quantiles.

## Concrete cost in the candidate

The pinned cold-C source's `DeclarationSources::containing_block` restarts at the rule-tree leaf for every newly admitted Rule and scans source declaration slices with `std::ptr::eq`. With N distinct applicable Rule blocks, visiting all their positions entails a triangular number of source-block checks, plus other tree entries. For this constant-size-block workload that is Θ(N²).

Independently, the j-th Rule declaration passes the earlier `RuleExclusion` entries through the same physical property and normalized-priority comparison, then fails membership in each different earlier block. The N Rule triggers therefore induce N(N−1)/2 prior-exclusion visits. The final lower-layer value adds N cheap exclusion entries with a different priority. The exclusion vector stores O(N) entries per cascade. Repeated source occurrences or larger declaration blocks can change the constants and add further work; this fixture deliberately holds those factors small.

The A+B+D implementation does not perform those two scans for Rule. Existing declaration collection and other cascade work remain, so neither baseline nor literal controls should be described as globally constant-time. This is a source-level asymptotic argument conditional on full traversal of the stated workload, not a measured slowdown.

If the quadratic scan dominates, doubling N should approach four times the incremental Rule cost; linear work approaches twice. Fixed costs, reuse, caches, quantized clocks and noise can obscure either pattern. Inspect the Rule curves against both controls and between builds. An absent slowdown is not proof of constant complexity; a slowdown alone does not identify the responsible native function. Native profiling/counters may be needed before choosing a replacement implementation.

## Output

JSON includes complete per-sample elapsed/setup times, update counts, completion flags, mismatches, exact generated CSS, configuration, build label and browser information. Rows count setup, warmup and measured writes/reads separately; `checkedReads` counts measured value assertions. These are workload counters, not native rule-tree scans, membership checks or allocations. No native operation count is claimed. The table reports median and nearest-rank P90 microseconds per measured update, median setup milliseconds and correctness checks.

The connected offscreen element has no animation or transition. Opacity avoids requiring geometric output, but the measurement remains browser style work. Results are available as `window.rollbackBenchmark`; inspecting it during timing can disturb measurements. No performance acceptance or new bug count follows from this prepared fixture.

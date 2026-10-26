# Explicit commitStyles refresh: engineering assessment

Retain the measured stack cost as a tradeoff. It does not by itself require abandoning the correctness repair, and it does not establish universal performance safety. No obvious broad, safe skip follows from the current source representation. Complete the existing two-case implicit/additive endpoint diagnostic before acceptance; no further timing campaign or optimization is proposed now.

This review independently reparsed all six authenticated raw logs with the pinned analyzer, matched the six archived datasets, and recomputed per-process API/flush/total medians and ranges without filtering. There are324 rows:72 warmups and252 measured, across six browser processes. PROCESS-METRICS retains all six cases and three metrics separately; the source archives retain every raw sample. Runtime manifest c805288e binds actual63215. This assessment does not replace the terminal preservation review. The reviewer previously authored the benchmark/parser and port-preflight correction, not the native candidate.

## Observation

For32 effects, total medians per sixteen calls were literal [4,4] → [6,6] → [4,4]ms and variable [5,5] → [7,7] → [5,5]ms in original/candidate/restored order. The +2ms batch difference is125 microseconds per call when amortized, not a measured per-call latency distribution. Variable eight-effect totals were [1,1] → [2,2] → [1,1]ms. Literal eight-effect API medians remained1ms; its restored total was [2,1] versus [1,1] originally.

Literal32 API medians followed4→6→4ms. Variable32 API medians were [4,5] → [6,7] → [5,5]ms; flush medians were [1,0] → [0,0] → [0,0]ms. Medians of API and flush must not be added to infer median total. Small cases are dominated by observed0–1ms granularity; literal1's apparent candidate improvement is not optimization evidence. Outliers remain included. Two processes per phase and seven measured batches per case do not establish independent browser observations for every batch. Blocked A/B/A order, finite machine/sample and unretained effective generated profiles limit generalization. Reversal and repeated larger-stack differences support concern about added work without measuring a causal magnitude for a particular internal function.

## Source scaling and possible savings

Old ComposeServoAnimationRuleForEffect already collects/sorts the partial effect stack and calls UpdateBaseStyle on the committed effect. UpdateBaseStyle itself calls BuildProperties and EnsureBaseStyles. The candidate replaces that one-effect computation with UpdateProperties on every prefix effect using one full current style, retains strong references across refresh, and rechecks cascade state before unchanged composition.

New endpoint/base work is approximately the sum of each prefix effect's keyframe/property conversion and base computation, instead of only the top effect's. The32-effect benchmark calls the API on sixteen separate targets, so it can add496 lower-effect rebuilds per batch. This is a source operation count, not native instrumentation or an exact time-scaling claim. BuildProperties clones authored keyframes and performs computed-property conversion. Equality is checked afterward; equal endpoints suppress later notifications/restyles but do not skip conversion or EnsureBaseStyles. Changed endpoints can cause publication, cascade updates and layer restyles. MaybeUpdateCascadeResults is already guarded by CascadeNeedsUpdate.

This entry point is specific to explicit commitStyles, not a new per-frame recascade hook. Applications repeatedly committing styles can still pay this cost. Committing every effect in a growing size-N stack can require a triangular number of prefix refreshes; no usage-frequency claim is made.

Skipping lower effects is unsound for additive or implicit endpoints. Cached numeric values do not certify context independence of authored inputs. A literal-only skip would require reliable classification and still preserve underlying/base refresh. Property pruning must prove a contribution is overwritten under composition, neutral endpoints and cascade rules. Neither is an obvious safe condition in this patch. Reducing an allocation or consolidating reference arrays could be explored later but would not remove the conversion cost and must preserve lifetime guarantees. No speculative skip is recommended.

## Next correctness gate

The existing separate implicit diagnostic (manifest e1ebd9d9) is worthwhile: variable/literal twins require280px with an implicit additive start, refreshed lower contribution and current provider275. It snapshots inline immediately after commit and checks the frozen result after cancellation. This covers a distinct boundary from explicit additive benchmarking without a registered custom-property consumer prerequisite. Observe original/candidate/restored outcomes without weakening its oracle.

The source also confirms EnsureBaseStyles runs before unchanged-endpoint return. The selected upstream tests do not explicitly mutate ordinary underlying style after cache warming before commit; that is a coverage note, not an observed regression.

Acceptance remains root-owned, conditional on the remaining correctness gate and an explicit decision about the measured API cost. No zero-overhead requirement, universal no-regression statement, active-DAG/cycle proof, new bug count or native change is made.

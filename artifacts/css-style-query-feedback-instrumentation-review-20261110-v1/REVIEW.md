# Independent instrumentation review

Verdict: suitable for a bounded local scheduling investigation, conditional on validating trace integrity. This is diagnostic instrumentation, not a production patch or proof of timing neutrality. Reviewed patch SHA-256: `c44ee02505564eff83617d198de7522c0ea705cf9d1868cb5586ce4f2f172475`, based on `3a6a6bfe2b0d3d551b2392206179f251002cfc7e`.

`check.py` independently authenticates four Git bases and copied outputs, reconstructs the exact patch, and checks that no original lines were removed. This supports source preservation; it does not prove semantic equivalence. The reviewer did not install native files, compile, run the browser, or change Git.

## Native behavior and API checks

The additions leave existing guards, return paths, loops and state assignments intact. Animation snapshots read raw timing fields and stored target identity. `GetTargetForAnimation`, the target atom comparison, and the cached timeline snapshot's `SourceElement` accessor do not flush style or sample animation timing. Cache logging uses captured source identity, avoiding lazy `ScrollerInfo::Source` resolution. No timing getter is added and no production branching expression is evaluated twice. Header visibility and constness are consistent with the inspected declarations; no compile/API blocker was found by inspection. Actual compilation remains root's check.

The enabled diagnostic asserts the main-thread contract before shared counter access. Counters remain ordinary globals: an optimized build relies on the existing main-thread nature of these entry points, rather than enforcement by the debug assertion. No worker traversal hook was added. ScopeExit captures refer to parameters and the active method receiver; intended fixtures retain the target. An exit can be filtered out if production work changes CSS animation identity or target, so an unmatched entry is not independently evidence of a hang.

I/O and environment lookup add overhead and may perturb scheduling. The cached environment flag does not support enabling logging after its first evaluation. `unistd.h`/`getpid` make this a local Unix diagnostic. None of these receipts support performance claims or portable landing readiness.

## Event semantics

Every `StyleDocument` entry allocates a per-process call ID and increases nesting depth. Its RAII exit records the same call and depth before restoring the caller. Refresh/stale RAII scopes identify those native sampling intervals without declaring a rendering-frame epoch. Animation rebind, tick, ready, trigger and align entry/exit events cover normal and early returns. Pair events per PID, nesting stack, object and active style call; preserve all intervening events.

A changed association requires rebind entry with old `timeline != next` and corresponding exit with `timeline == next`. Ready/align/trigger restoring a resolved start or hold outside all style scopes, followed by two actual rebindings within one style call, supports finite style work following sampling. Renewed timing resolution at nonzero style depth is instead a counterexample candidate to the no-readiness-within-drain premise. Two rebindings alone do not demonstrate recurrence. Raw start/hold nullness identifies loss and restoration of timing availability, not equal numeric timing or full native-state identity.

Timeline/animation pointers identify live objects only; reuse after destruction is possible. `mAnimationIndex` is ordering metadata and can be overwritten by CSSAnimation, not an allocation serial. Partition fixtures by document and established live animation intervals. Distinct pointer counts do not count allocations. A stable pointer or unchanged nullness does not establish a full-state cycle. The trace does not identify all refresh-frame boundaries.

## Trace integrity requirements

Require strict record syntax, contiguous sequence numbers within each PID, correctly nested scopes, and complete reviewed intervals. The first 20,000 records are followed by one cap marker; later events are suppressed although scope bookkeeping continues. A capped or truncated interval cannot support absence or termination claims.

Each CSSFB record currently uses three stdio operations. Multiple processes sharing stderr may interleave fragments. Reject malformed records and sequence gaps; do not silently discard them and then infer no missing readiness event. A single bounded atomic pipe write would improve future capture, but no source change is required to interpret an intact bounded interval.

CSSFB uses stderr and QF JavaScript markers use stdout. Their common ordering is unproven until the runner's process pipe arrangement is established. Per-PID CSSFB sequence and native scope nesting are primary. Treat QF phase association as advisory where stdout/stderr order is uncertain; do not derive exact armed/frame boundaries from merged presentation alone.

## Review disposition

No native behavioral blocker found for the proposed local run. Main-thread assertion and cached source/document identifiers were incorporated during review. Animation-index identity language was corrected. Strict line and pairing checks, cap handling, pointer-lifetime limits, and stream-order qualifications are required in the runtime report. A successful bounded trace can explain repeated pending snapshots; it cannot establish general style-drain convergence or prove absence of every reentrant sampling path.

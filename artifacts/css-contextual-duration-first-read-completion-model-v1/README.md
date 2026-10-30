# First-read completion over a finite dependency chain

This isolated model separates removing queue entries, evaluating dependent values, generating new work, and deciding whether a query may return. It imports the sealed `QueueState` unchanged. No canonical library, native source, Git state, browser, or build was changed.

`Completion.lean` models nodes 0…n, with fixed root value true and each non-root value defined by copying its predecessor. Initially all non-root values are false and node 1 is Pending. A round snapshots eligible entries into an in-flight set (`begin`), evaluates that set from pre-round values, and enqueues newly inconsistent successors through the existing blocked `QueueState.request`. Unrelated queue state is carried separately. This is a concrete snapshot-frontier evaluator; its one-edge-per-round result is derived from these definitions.

`run_exact` proves the prefix of true values and the single next Pending frontier after arbitrary k rounds. `reachable_coverage` derives dirty-edge coverage for every reachable round boundary and its begun state. `ready_covered_fresh` proves that covered local inconsistencies plus absence of relevant queued/in-flight work imply the entire chain matches the fixed root. `depth_bound_completes` supplies a terminating n-round execution for this particular n-edge chain, including n=0.

For every fixed budget k, `fixed_budget_counterexample` constructs a finite acyclic chain of depth k+1 whose leaf is stale and Pending after k rounds. Thus a fixed number of extra snapshot-frontier rounds is insufficient uniformly over chain depth. This does not prove that a native traversal advances exactly one edge, or rule out a topological evaluator that resolves a whole chain in one call.

The concrete two-node witness consumes the original frontier and leaves a newly generated child Pending. Removal alone leaves an in-flight unevaluated value; a safe posting attempt also leaves the value unchanged. Arbitrarily clearing work makes `Ready` true while leaving the chain stale: coverage is essential. The unrelated-work example reaches freshness while an unrelated Pending entry remains; the obligation is scoped to the queried dependency chain, not global quiescence.

`begin_preserves_coverage` explicitly requires the previous in-flight set to be idle because `begin` replaces it. No theorem claims that `finish` preserves coverage on every arbitrary input state. Coverage is proved for the concrete reachable execution and its begin boundary. `Fresh` expresses equality for this Boolean copy chain, not numerical CSS correctness, computed serialization, property inheritance, or a general dependency graph.

## Checked evidence

Actual final run: launch 6a1840, session 77876, terminal 8b2a30/0. `run6` contains 17 named axiom audits and seven rejected false controls. Only standard `propext`, `Classical.choice`, and `Quot.sound` occur; no sorry or native reduction axiom. The final source hash is recorded in `run6/CHECK.json`. The earlier run4 checked 13 declarations/five controls; runs1–3 and5 retain actual failed development diagnostics. All six isolated scratch directories were removed. No compiled Lean artifacts are retained.

The rejected claims say: queue removal evaluates; removal leaves nothing in flight; processing the entry frontier cannot generate child work; two rounds always suffice; arbitrary clearing evaluates; a dispatch attempt evaluates; and a successful attempt makes the queue entry absent. These are semantic negatives against the actual definitions.

Replay into a fresh, previously absent output directory:

```sh
python3 -I -B -S artifacts/css-contextual-duration-first-read-completion-model-v1/replay.py replay-independent
```

The script authenticates the imported packages and pinned Lean 4.35.0-rc4 executable, uses a small temporary directory, and removes it on success or failure. Its new output is an additional replay, not a replacement for the retained run6 evidence.

## Native correspondence limits

`TRACE-BRIDGE.json` records the four joined first-read intervals. The exact runtime has nine old-fixture PASS callbacks, yet four first reads return 0.428571 while newly generated child Pending entries remain; the expected acyclic value is 6/11. The strict join authenticated 258 authored queries and 204 posted CSS values. PID/query pairs are 9699/45, 9699/81, 9701/39, and 9701/70. Entry snapshots lack the child entry; later snapshots show Pending after middle removal intent, with no logged child hint/removal/clear before return. This is bounded observation of the instrumented paths, not exhaustive native event coverage.

The trace is a useful structural analogue of `late_pending_witness`, not a refinement proof. Native removal/pre-will-compose markers do not prove evaluation or composition. Mapping native dependency closure, generations, reentrant changes, actual evaluation, scheduling eligibility, and all invalidation paths to `Covered`, `flight`, and `finish` remains external. In particular, the model does not establish native termination, delivery, or correctness of a proposed retry implementation. A pending entry may be redundant; our sufficient readiness condition is deliberately conservative.

Acyclic fixed inputs are essential to the completion theorem. The existing `css-contextual-duration-feedback-model-v1` already checks a conditional linear two-cycle and iteration non-fixedness; it is referenced rather than duplicated. CSS cycle policy remains a separate specification question. This package asserts no numeric feedback oracle, native acceptance, new bug count, or canonical proof-coverage increment.

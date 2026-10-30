# Completed size and pending font metrics

This extension makes the readiness boundary concrete without changing the CSS cycle rules. An arbitrary sequence of later requests can increase the requested demand while leaving fulfilled size available. The graph witness proves that merging size completion and metric completion into one vertex creates a cycle even when the separate computation dependencies admit a strict ranking.

`Phase.lean` imports the exact sealed `FontDemand.lean`. `request_batches_exact` and `later_requests_preserve_completed_answers` hold for arbitrary finite lists of consumer batches. `size_complete_metrics_pending` demonstrates that a metric request neither fulfills metrics nor blocks an already completed size. `served_reads_are_final` connects an answered request to the prior model's actual/final input tuples, using an explicit certificate for the fulfilled level. `completion_preserves_served_answers` preserves earlier availability as certified completion grows.

The certificate is essential: `complete` does not compute a font or establish finality. The producer must supply that proof in a refinement. Actual/final states remain fixed; later font, zoom, orientation, or used-size changes require invalidation or a new certificate. There is no claim that the existing ensured bit supplies one.

## The concrete false cycle

The source-shaped example has registered lengths `--size: 1em` and `--metric: 1ch`, literal `font-size: 20px`, and `font-weight: calc(var(--size) / 1px * 20)`. Assume these are the selected declarations and other font inputs are independent. This is an algorithm discriminator, not a new executed browser fixture.

The dependency order is size → size alias → weight → complete metrics → metric alias, with arrows here showing production order. The Lean `requires` edges point in the opposite direction, toward prerequisites. It also explicitly retains the metric alias's size prerequisite. `path_decreases` proves the general strict-ranking property for any relation and any nonempty path. Applying it proves this concrete split graph acyclic.

`project` identifies size and metrics as a single FontSize vertex. The image relation then contains FontSize → Weight → size alias → FontSize. `merging_creates_false_cycle` constructs that nonempty cycle. This is why joining stronger requirements into one active semantic DFS vertex is insufficient: the join must not retroactively make completed size depend on weight. It is not a proof that any particular native traversal currently performs this projection.

For comparison, replacing the weight dependency with the metric alias gives an actual metrics → weight → metric alias → metrics wait cycle. `genuine_metric_wait_cycle` constructs that different path. It does not prescribe inherited metrics, invalidation, or convergence. Those are experimental policy choices until the native algorithm and relevant specification boundary are resolved.

## Native boundary and policy isolation

The acyclic route can progress now: complete size, serve size-only aliases, complete the selected metric-affecting values, then certify metrics and serve the metric alias. A phase being Pending means only that its requirements are unfulfilled; it does not prove recurrence. A native cycle policy must have its own witnessed readiness recurrence and must not intercept the acyclic route merely because a stronger request is pending.

Retaining the existing custom→FontSize semantic edge and separating readiness is compatible with this model. Adding all generated ordering dependencies to the CSS SCC graph is not established by it. A DFS snapshot/restore strategy additionally needs to control custom-map, attribute-cache and builder publications, not just restore indices and lowlinks. Retaining results from a discarded unresolved suffix is not justified here.

The companion spec trace records the direct font-affecting parent-metric rule, registered computed-value substitution, and the unresolved registered-property cycle discussion. It does not stop an acyclic metric-readiness repair and does not turn an experimental cycle policy into a normative result.

## Checks

The pinned Lean4.35.0-rc4 replay compiles the prior module and this extension in an owned temporary directory. Nine statements are audited, with only standard propext/Quot.sound or no axioms. Three separate false controls are rejected by `decide`: requesting metrics fulfills them; pending metrics block completed size; completed size guarantees a changed metric read. These are false logical claims, not native mutation tests.

Run1 retained real qualification/parser errors; it supplies no proof result. Run2 passed. Run3 adds the explicit metric-alias→size edge and repeats the same proof/audit/control checks for the final source. All owned scratch directories are removed. No native code, browser, nested Lean repository, Git state or canonical coverage is changed.

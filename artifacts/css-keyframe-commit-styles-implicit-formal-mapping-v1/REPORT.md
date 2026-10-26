# Reuse: implicit additive endpoint refresh

No missing abstract refresh theorem was found. Reuse `CommitRefresh.refreshed_prefix_current` in the pinned Refresh.lean. Its cache entries are operations `Value → Value`, not sampled numeric endpoints. `refresh_at` establishes per-effect agreement for a covering task list; `compose_agrees` transports that agreement through ordered composition. The theorem already handles arbitrary finite stacks and refresh schedules, including duplicates and extra tasks, without arithmetic restrictions. No new Lean code, compilation, theorem credit, coverage credit or canonical change is warranted.

## Exact theorem inputs

Instantiate Effect with two distinct identities lower/top, Context and Value with Rat for this illustrative diagnostic, stack with [lower, top], tasks with any list covering both, current with provider c, and cache with arbitrary previous operations. Use the same initial base on both sides. Define resolve(c,lower) as `u ↦ c` and resolve(c,top) as `u ↦ interpolate(u, u + 10, p)` for the fixed sample progress p. The top's implicit start consumes the incoming lower-composed value u; it is not frozen numerically when top is refreshed. The explicit end adds10 to that same u. These are direct permitted inputs to the existing theorem; no assumption of equal composed outputs is added.

At c=275,p=1/2, fresh composition yields280. A model cache with lower fixed at225 and only top refreshed yields230. This is a **model counterexample**, not a prediction of native baseline output: actual cached lower values depend on creation/flush timing. The browser oracle remains280 and records the actual value. The already kernel-checked `top_only_insufficient` example proves the same failure mechanism with old100/current200 and top adding10 (110 versus210); the diagnostic instantiation is explanatory, not a new compiled theorem. Canonical KeyframeContext.interpolate supplies the same rational formula; this is not an IEEE/native interpolation proof.

The generic theorem is not limited to Rat. A richer instantiation can use a full animation map plus metadata and effect operations on that map. The native resolver must faithfully supply Add/Accumulate/interpolation and fallback behavior, neutral endpoints, taint, iteration and cascade state. No finite-value, progress or depth restriction is introduced here.

## Correspondence and actual remaining obligation

Archived clean-base Servo_AnimationCompose requests an underlying value for null endpoints or non-replace composition, preferring the previously composed lower map entry over Gecko_AnimationGetBaseStyle. `composite_endpoint(None, …)` clones that underlying value; an explicit Add endpoint invokes native Animate Add before interpolation. These branches support the operation-on-incoming-value mapping, but are not extracted native semantics.

The unresolved obligation is faithful native resolver/composition correspondence: refreshed retained properties, implicit endpoint formation, current progress, base fallback, ordering and error behavior. In particular, the theorem starts both sides with the same base; it does not refresh an externally stale base. When no lower map entry exists, the supplied operation/context or initial-base premise must establish current underlying style. This diagnostic instead supplies a lower replace contribution.

Full provider context freshness is also a premise, not a consequence. The existing operation-arena bridge proves scheduling under its graph/resolver assumptions, not native neutral endpoints, current ComputedStyle, animated cycles or cascade extraction. Prefix selection, lifetime, notifications and reentrancy remain outside these claims.

The next useful validation is the existing variable/literal280px diagnostic on original/candidate/restored builds. It tests native correspondence that duplicating the abstract theorem cannot establish. Only source/artifact reads and this new capsule were performed; no native, canonical, index, browser or compiler operations.

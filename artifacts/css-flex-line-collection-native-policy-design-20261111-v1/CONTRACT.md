# Proposed append-then-break policy refinement

Design only, awaiting root review. The preceding signed collector and all existing sources stay frozen. This capsule snapshots the actual old and currently patched GenerateFlexLines function; SOURCE-DELTA.patch isolates the added existing-total comparison and its comment. No native file is edited here.

Model the ordinary-item wrapping path over arbitrary full α values and a supplied size:α→Rat. Inputs are threshold T, gap G and a finite sentinel bound L. State consists of a current ordered line, its stored running total and the remaining ordered input. Each step appends the next item first. If that makes the current count greater than one, calculate `newTotal = oldTotal + size next + G`, test a break, and either move the appended last item to a fresh line or retain it. Only then update the current line total. Already emitted lines are returned in order; the implementation may use a recursive emitted prefix rather than a mutable vector, with an exact output correspondence theorem.

Old break predicate: `L ≤ newTotal ∨ T < newTotal`.

Patched predicate: `T < oldTotal ∨ L ≤ newTotal ∨ T < newTotal`.

On a break, emit the prior current line, start `[next]`, and reset total to `size next`; no preceding-line gap is charged to the new singleton. On continuation, total becomes newTotal. The first item is appended without a wrap test or an inter-item gap. Finish by emitting the nonempty current line. Empty input returns no occupied lines, consistent with the prior model's explicit projection from native empty-line storage.

The source's maximum-coordinate guard is retained in both mathematical policies, then proved redundant relative to `T < newTotal` under `T < L`. This is a source-supported simplification, not a silent deletion of the guard. Native nscoord overflow, sentinel-valued unconstrained thresholds and casts remain excluded. Exact arithmetic is Rat; connection to native sums requires independent representability/no-overflow evidence.

Main proposed theorem: for every finite ordered input, arbitrary signed sizes, T,G,L with T<L, the patched policy result equals `FlexCollect.collect size T G input`. This directly implies the independent Collected relation and all full-value partition/order/multiplicity laws. CSS-facing use additionally assumes T≥0,G≥0, as in the prior target. Proof must establish the running total equals span of current line, and that any active line whose total exceeds T is a singleton first item. It must not assume that invariant of the old policy or ban later individually large items in fitting lines.

Counterexample target: T100,G0,L1000, input[150,−50]. The old policy returns[[150,−50]], the patched policy returns[[150],[−50]], and the old output does not satisfy the unchanged Collected relation. Prove both actual model computations and relation negation, not merely failure of a proof script. This is a counterexample to the source-shaped rational policy, not machine-code verification.

Controls: later-large negative prefix[−50,150] stays together; first failed extension[80,30,−50] cannot look ahead; exact fits and zero items; positive gap with zero-size successor; gap reset on breaks; repeated/equal-size distinct identities; empty and nowrap projections; bound premise sensitivity (T≥L can make the finite-bound guard cut a line before the spec threshold). Preserve the actual added oldTotal disjunct without substituting a different singleton-size test in the executable.

Excluded source paths: DOM/frame construction, order sorting, collapsed struts/gap skipping, placeholders, forced breaks, fragmentation, indefinite/max-size threshold acquisition, all native integer/limit representation and positioning. No new SourceSolver/native bridge or general Gecko refinement claim. The unchanged prior mathematical collector is the specification authority; browser results and successful native tests are separate evidence.

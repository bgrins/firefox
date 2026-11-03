# Coalesced parent-only chain settlement

This separate Lean extension proves termination and dependency-coherent readiness for a finite, event-driven **chain** with coalesced refresh, queued application, and selected in-flight application obligations. It reuses `EndpointApplication.Version` from the existing library. It does not identify these mathematical transitions with Gecko's queue or establish native termination.

The final actual run `cd3bb8 / session 92994 / cdf9fe / exit 0` checked 27 theorem axiom audits and six genuine kernel-rejected false controls. Nine pinned imports compiled. Reported axioms are only `propext` and `Quot.sound`; there are no added axioms, `sorry`, or `native_decide`. The earlier successful 25-audit run and three failed elaboration runs with their exact source snapshots are retained. No native build or browser operation was performed.

## State and admitted transitions

Each node has endpoint and installed versions, a refresh bit R, a queued application bit A, and an optional in-flight snapshot I. Selection snapshots the latest endpoint, clears A, and creates I; it does **not** install. Selection requires an empty in-flight slot. Refresh computes from the currently installed parent, clearing R. A changed result advances the endpoint generation and sets A; an unchanged result preserves any A and I. Completion installs only a current-generation snapshot and clears I. Stale completion discards its snapshot without installing or clearing a newer A. Completion preserves R. A real change to the installed value marks the immediate child's R.

`Step.descendant` permits any genuine pending phase at any chain position. There is no prescribed root-first scheduling order, numerical monotonicity premise, or fixed pass budget. Refresh and completion are mathematical atomic steps, not claims about native callback atomicity or availability.

`localValid` conserves coverage of the newest endpoint: it is already installed, queued, or represented by the current in-flight snapshot. It also bounds generation relationships and requires equal-generation snapshots to equal the endpoint. `coherent` additionally requires every node without R to have the endpoint computed from its currently installed parent. Initial coherence is a substantive premise: an unmarked stale dependency is excluded, not repaired by assumption-free scheduling.

## Termination and readiness

For a node with `m` nodes remaining in its chain, R weighs `3m`, A weighs `3m−1`, and I weighs `3m−2`. These weights are summed over all nodes. Every enabled step strictly decreases the sum:

- Refresh consumes R and can add at most A.
- Selection replaces A with I, decreasing weight by one.
- Completion consumes I and can add at most the immediate child's R, whose weight is `3m−3`.
- A descendant step retains the prefix and decreases its suffix.

`history_budget` bounds the number of accepted steps by the initial weight. `progress` establishes either all obligations are absent or an enabled step exists. A driver that keeps choosing enabled steps until none remain therefore terminates; arbitrary idling, unavailable completion, or external work injection is outside that conclusion. Per-node weights are linear in remaining chain length; the total fully pending rank is **quadratic in depth**, not a linear total runtime bound.

`history_coherent` preserves the invariant. `stopped_values` assumes a history ending with **no enabled next step**, not merely the end of an arbitrary finite prefix. It proves that installed values equal an independently defined recursive `expected` chain from the stable root and deterministic functions. Empty A alone is not readiness: selected I can still hold an unapplied value. Nor is node-local endpoint installation global dependency coherence while an ancestor is still changing.

`finite_settlement` explicitly constructs existence of a finite all-quiet history by strong induction on the natural-valued weight, with its length bounded by initial weight. `finite_ready` combines that existence result with invariant preservation and the independent expected-chain equality. These are proved client theorems, rather than only an informal combination of progress and decreasing rank; they do not supply a native driver.

The concrete stale-snapshot example selects 64 while 46 remains installed, refreshes the endpoint to 80, discards stale completion of 64 while retaining A for 80, then selects and installs 80. The dropped-child example ends with locally quiet installed values `[2, 0]` while the independent expected chain is `[2, 4]`; it violates dependency coherence. Six false controls reject empty-A readiness, clearing newest work on stale completion, stale installation, dropping A on unchanged refresh, dropped-child global readiness, and omitting the child's refresh after a real parent change.

## Native mapping still required

The root, finite chain topology, and deterministic parent-only computation functions remain fixed throughout each history. New work is introduced only by the stated refresh/application transitions and actual installed-value changes. Generations are unbounded naturals. Retargeting, cancellation, changing functions or graph, external invalidation, overflow, cyclic feedback, composition with other effects, and multiple in-flight jobs are not modeled.

The native compositor map stores target/pseudo and cascade level with a posted bit; it does not supply this model's R/A/I or endpoint/provider generations. A native queue entry being selected or removed is not proof of installation, and an empty native map cannot be substituted for `allQuiet`. A refinement must establish exact target/reference identity, newest-work conservation, stale-reply handling, dependency-edge invalidation, scheduling and completion, provider stability, and eligibility of the parent-only functions. Existing observations motivate these obligations but do not prove them. The source eligibility review is referenced separately; no native predicate is supplied here.

Fanout is deliberately excluded. Chain depth weights do not cover multiple newly invalidated children. A possible tree extension would assign R = three times subtree size, A = R−1, I = R−2, making a parent's I outweigh the sum of child R weights. That extension is **not implemented or proved here**. Mixed `rem` and `em` dependencies can form a graph different from DOM ancestry and would need weights over the actual dependency edges, with an acyclicity argument; DOM depth alone is insufficient.

## Evidence

`CHECK.json` binds the actual run, exact tested sources and logs, import authentication, scratch absence, and failed attempts. `SOURCE-MAP.json` distinguishes source observations from model premises. `REFERENCES.json` pins the prior library, wave model, source/trace evidence, and eligibility note. These references do not turn the proof into a native simulation theorem. Re-running the successful unchanged suites is unnecessary for this documentation and seal.

# Contextual easing dependency and cache contract

The useful result is `cache_sound`: for a fixed parameter expression list, a cache that covers every structurally read context field and honestly compares those fields can reuse the old evaluated parameters. `expr_locality` proves the underlying fact by induction over expression syntax; support is collected independently of evaluation. The theorem does not assume that equal keys already imply equal results. Conservative support may include fields that arithmetic ultimately cancels or ignores.

The model includes literals, field reads, addition, multiplication, minimum and division by a constant. Parameters are lists, permitting every Bezier argument or every present linear stop component to contribute support. Context fields distinguish own font, parent font, sibling index and sibling count. The modeled sparse key stores only the fields selected by a mask. Actual selector flags, caches, restyle scheduling and Context construction are not implemented here.

Counterexamples show why dropping a second linear position, replacing own-font dependency with parent-font dependency, or tracking index instead of count cannot satisfy the general cache contract. Another counterexample gives different expressions with identical support: changing the selected declaration requires expression identity in the cache contract or separate invalidation. Matching context fields alone is insufficient. These are model mutants, not newly observed Gecko bugs.

The transition fragment deliberately separates current computed parameters from a captured effect curve. Arbitrarily many modeled context-only events preserve the capture; a new start reads the latest context. This event rule is a chosen abstraction of the restricted unchanged-end-value scenario in [CSS Transitions starting rules](https://drafts.csswg.org/css-transitions-1/#starting), not a proof that Gecko implements those rules. Cancellation, interrupted reversal, animation composition, timing and start eligibility are excluded. The false refresh control demonstrates why indiscriminately recomputing an existing effect is not the same requirement as recomputing the property.

`run-2/CHECK.json` is authoritative: 12 standalone declarations, five false propositions rejected by kernel-checked `decide`, and temporary object directory removed. The axiom audit uses only standard `propext` and `Quot.sound`; there is no `sorry` or native decision shortcut. Actual tool replay d13226/session30331 completed b7ab4e/0. Initial run-1 stopped because the Python wrapper expected the wrong wording for a correctly rejected false control; its partial logs are historical, not evidence for the final source. The final source also adds exact division-by-16 pseudo witnesses after that preliminary run.

Replay into a new absent output directory:

```sh
python3 -I -S -B artifacts/css-contextual-easing-dependency-cache-model-v1/replay.py artifacts/css-contextual-easing-dependency-cache-model-v1/run-3
```

Nat is an abstraction, not CSS floating-point arithmetic. Division is natural-number division; the concrete font witnesses divide exactly by nonzero 16. CSS type checking, fractional numbers, NaN/infinity, clamping, linear normalization, serialization and interpolation are excluded. Equal complete scalar inputs suffice for a deterministic downstream builder, but unequal modeled parameters alone do not prove different normalized curves or rendered output. Selected scope/root identity, animated self-dependencies, variables, font invalidation and lifecycle correspondence remain external obligations. No native refinement, new discovery, acceptance or canonical coverage increment is claimed; canonical 11,840 is unchanged.

# Append-then-break Flex policy

This isolated rational model compares the actual old/new `GenerateFlexLines` break predicates against the accepted signed collector. It is source-shaped proof work, not compiler extraction or verification of C++ machine execution.

`FlexPolicy.universal` proves the exact frozen UniversalTarget: for all ordered full item values and signed rational sizes, `threshold < limit` implies the patched policy equals `FlexCollect.collect`. `FlexPolicy.worker` proves the accumulator version with explicit Ready and stored-span premises. The top-level theorem establishes those premises from the empty state; it does not assume an already valid partition. `patched_collected` and `patched_partition` expose the independent relation and exact flatten/order/multiplicity consequence.

The model retains the actual conditions:

- Old: `limit ≤ newTotal ∨ threshold < newTotal`.
- Patched: `threshold < oldTotal ∨ limit ≤ newTotal ∨ threshold < newTotal`.

It appends before checking count>1, accumulates in source order `oldTotal + size next + gap`, and moves the last item to a singleton on break with total reset to its own size. The finite-bound disjunct is retained then proved redundant when threshold<limit. `ready_oversized_singleton` derives that an active line above the threshold is a singleton; this is not assumed about the old policy. `next_total` relates the stored sum to the specification span, including the commuted gap arithmetic.

`Cases.counterexample` proves the old computation [150,−50]→[[150,−50]], the patched split, and negates the unchanged Collected relation for the old output. `bound_necessary` and `no_unconditional_refinement` show the strict limit premise matters: with threshold=limit=100, even patched [50,50] splits at the finite guard. These are checked model counterexamples, not new native defects.

Replay from workspace root:

```
python3 -I -B artifacts/css-flex-line-collection-native-policy-20261111-v1/check.py --out /absolute/new/replay
```

The source-only gate checks11 modules,55 exact standard-only axiom reports and six exit1 false-proposition refusals. It pins tools/Std, target, source and predecessor copies before/after execution, uses one Lean worker with4GiB/180seconds per command, and removes compiled scratch only after observed owned-group absence. Explicit --modules is development scope only.

The five imported collector modules remain byte-exact; TRANSPORT.json authenticates them rather than counting their prior theorem inventory again. The55 audited roots here are46 policy/helper/case theorems plus nine selected definitions/target relations. All type and definition statements frozen in TARGET-INPUTS remain unchanged.

Scope: already ordered ordinary-item input; no DOM/filter/placeholder/strut handling, native vectors/memory, integer overflow, sentinel-valued unconstrained threshold, forced breaks, fragmentation, source sizing or positions. Threshold<limit is a mathematical predicate-bound assumption, not proof of native representability. CSS-facing threshold/gap nonnegativity remains the predecessor’s separate domain. Empty output projects occupied lines; nowrap_projection only cites the predecessor nowrap convention, not an execution proof of native sentinel paths. Browser/WPT results are not proof premises.

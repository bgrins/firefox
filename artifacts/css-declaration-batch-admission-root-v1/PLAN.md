# Ordinary declaration batching

The all-shorthand companion proves sequential setting. Ordinary shorthand
updates still plan against one initial destination, remove selected indices in
descending order, correct surviving indices, and execute the source-order plan.
This separate algorithm needs its own refinement theorem.

## Admission and counterexamples

The retained [source audit](../css-declaration-block-update-static-v1/REPORT.md)
checks unique identities and one mapping kind per logical group for all 94
explicit shorthand metadata lists. Filtering preserves both properties. Actual
parser output membership, callback stability, payload equality and concrete
storage correspondence remain source-provider obligations.

`explore.py` independently compares a handwritten batch algorithm with a forward
sequential setter. Its bounded domain covers five identities: two physical and
two logical members of one group, plus an ungrouped identity. It enumerates all
unique destination orders/subsets, destination priorities, admitted source
orders/subsets, equal/changed values, and source priority. All 1,962,610 cases
agree. This is theorem development evidence, not a universal or extracted-native
proof; parallel importance bits and membership are not modeled separately here.

The same script retains two counterexamples:

- Mixed source mappings: from `[physical, logical]`, setting that same pair in
  order yields `[logical, physical]` with initial-state batching, but returns to
  `[physical, logical]` with sequential setting.
- Duplicate source identity: two appends planned against an empty destination
  retain two copies; sequential setting keeps one.

Neither fabricated source is a new reachable browser bug. They explain why
source uniqueness and mapping uniformity must be explicit proof premises. The
all-specific repair uses sequential updates because its expansion mixes kinds.

## Required universal proof

1. From unique destination and source identities, prove selected original
   indices are unique and in bounds.
2. Prove descending removals equal filtering the original list by the removal
   set, preserving surviving order. Derive each corrected index as its original
   index minus the number of strictly earlier removals; prove no underflow.
3. Under source mapping uniformity, prove other source actions cannot introduce
   or remove an opposite-mapping witness for a target. Establish stability of
   each initial movement decision through sequential execution.
4. Compose replacement, movement and appending in source order; prove batch
   output equals the independent sequential setter for arbitrary admitted lists.
5. Lift the theorem to separate declarations, importance bits and identity
   membership. Permit retained membership during internal removal, then restore
   the full invariant at the public boundary. Derive the zipped lengths and
   capacity/counter premises from fresh preparation.
6. Bind generated source identity/mapping lists and actual parser publication to
   these premises; keep arbitrary value equality and callback/storage adapters
   explicit. Reuse complete native extraction with targeted mutations of removal
   direction, rank correction and bit-vector operations.

The live native input is pinned by `RESULT.json`; its exact snapshot is already
committed in `../css-all-logical-order-root-v1/declaration_block.candidate.rs`.
Replay locally with `python3 -I -S artifacts/css-declaration-batch-admission-root-v1/explore.py`.

## Initial index lemmas

`BatchIndices.lean` kernel-checks three general helpers: removing only higher
indices preserves a lower optional lookup; the number of distinct removals below
an index cannot exceed it; subtracting that count cannot underflow. The fresh
compilation and exact three axiom reports are in `INDICES-CHECK.json`.

These helpers do not yet prove complete descending-removal validity, survivor
rank correspondence, batched setter refinement or concrete storage composition.
The full component is being developed in `../css-declaration-batch-proof-v1/`.

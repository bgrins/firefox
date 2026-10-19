# Native index allocation and invalid attribute reload

## Component result

This extension contains 32 new theorems and 28 retained qualified-key theorems. Its fresh source-only replay checks nine modules including Audit and all 60 axiom lists. It addresses two distinct questions:

1. The retained native namespace-bucket allocation fragment can derive index range, uniqueness and node ownership from empty state through arbitrary modeled enter/finish/reset histories. Injective index allocation is no longer an assumed premise for that fragment.
2. An explicit invalid attribute tombstone can be overwritten by the current lazy-reload guard. A finished graph index can then be reused for the resurrected unresolved value. The corrected absent-only guard preserves a stable finished-value invariant and still permits retries when fetching/parsing never inserted an entry.

The original namespace candidate-v2 sources remain the actual source binding: custom_properties.rs `4c6bbf3ced241a0df98f90011871a4810d6306f7740e8c10411547b80e1ec92d`; properties/cascade.rs `be204d2bbdef0ec5130139eaeb56adf8fb869d09565f9b7b4c70e5ad3f61d425`. The absent-only guard is a modeled repair proposal, not an assertion that those frozen sources already contain it.

## Index invariants derived

IndexBuckets models the actual separated custom, namespace→name attribute, and non-custom maps. Its insertion theorem proves the nested map writes exactly one tagged node key. IndexAllocation models occupied-entry return, fresh count insertion, count increment, info append, stack push, stack pop/finished marker, and per-root reset.

For every history starting empty, at completed operation boundaries:

- count equals info-vector length;
- every mapped index and stack entry is below count;
- different tagged nodes cannot share a current index;
- looking up a node's index returns its own node in the info vector or the finished marker;
- another namespace cannot alias an existing qualified attribute index.

These indices are unique within the current Context epoch. Reset intentionally reuses numbers after clearing maps, info and stack; no global index identity is claimed. Arithmetic uses Nat. A separate count-increment theorem requires room below a supplied machine limit. Native allocation/capacity bounds, panic/OOM behavior and overflow admission remain external.

## Tombstones and repeated visits

The slot model preserves three distinct map cases: absent; present-invalid; present-value. Values distinguish unresolved pending content from resolved content. The native getter flattens absent and invalid into None. The current lazy load therefore revives either case when the provider returns raw content.

The repaired loader tests entry presence instead. It preserves every existing entry, including tombstones and active pending values, while a failed fetch leaves absence available for a later retry. This is exactly the intended distinction between never-loaded provider/parse failures and values explicitly invalidated by SCC handling or substitution failure.

At stable completed-visit checkpoints, a finished attribute has a present tombstone or a present resolved value. The model proves this property for arbitrary histories of corrected discovery, completed resolution/invalidation, and graph reset. It also proves the old loader violates it, that a resurrected pending value uses an occupied old index without new allocation, and that retaining the tombstone exits traversal before that index lookup.

The invariant deliberately does not apply between every source instruction. Fresh insertion updates the index map before info append; final resolution takes VarInfo.var before applying the value. Those transient states are not completed operation boundaries. Full source interleaving and evaluator admission remain open.

## Concrete observable hypothesis

The frozen reload-probe-v1 package contains ten rows (four predicted discrepancies, six controls), raw computed --out text, margins, a second independent custom declaration, DOM/CSSOM/support/calibration readbacks and a fresh primary-spec trace. No browser execution is claimed by this agent.

The witness repeats a cyclic `attr(x type(*), fallback)` inside one custom property. The first visit invalidates x; the second can reload x but reuse its finished index. Universal type syntax can then expose unresolved function tokens instead of the outer fallbacks. A noncyclic failed-substitution row exercises the same mechanism. Single references, constrained type, literal attributes, separate cycles and independent declarations discriminate the transitions.

**Read PROBE-SOURCE-TRACE-CORRECTION.md with the frozen probe.** Its original trace misidentified the visit_link branch for a parent revisiting a larger finished child index. The corrected branch still leaves the root lowlink zero and performs no re-traversal. The proof models all visit_link branches directly. The frozen witness and its expected output were not changed.

This mechanism is separate from namespace identity and from the other agent's fallback-preload/type-fallback investigations. Null-namespace inputs suffice; a native original/candidate comparison is still needed to establish historical observable behavior. No novelty or full bug acceptance is claimed here.

## Remaining native admissions

SOURCE-ADMISSION.md lists the exact operation correspondence. The index fragment's invariants do not prove Tarjan lowlink correctness, used-edge completeness, SCC membership, fallback grammar/type validity, parser/provider determinism, or final CSS results. They also do not prove that every native finished return writes a resolved value or tombstone: the modeled completion operation states that obligation explicitly.

The absent-only guard closes the demonstrated reload transition under those completion checkpoints. Whether every actual source path satisfies the full finished-value invariant remains open, including transient/reentrant evaluation, top-level resets, registered/non-custom dependency interactions and external collection implementations. No additional index aliasing defect was found in the modeled allocation fragment; that statement is not a complete traversal audit.

The earlier namespace proof, original counterexamples and original C1–C13 scope remain unchanged. This component is not a substitute for native builds, browser receipts or independent review.

## Replay

Authenticate FREEZE.json and replay.py. `python3 replay.py` verifies integrity. To rebuild sources without project oleans:

```
python3 replay.py --lean /path/to/lean-4.35.0-rc4/bin/lean --output /new/output-directory
```

The runner checks the Lean binary SHA, compiles all sources in a fresh temporary directory, checks theorem axiom lists and rejects two semantic mutants: allocating every new node at index zero, and allowing the corrected loader to overwrite explicit tombstones. Development files under work/ are excluded. No native/WPT/Git/browser/build actions were performed by this agent.

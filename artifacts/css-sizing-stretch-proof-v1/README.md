# Replaced Grid inline self-stretch selection

This source-only companion precedes the separate native repair and WPT commit. Static specification/implementation comparison suggested the defect; browser probes reproduced it before this model was written. Lean did not discover the bug.

## Contract and model

[CSS Alignment 3 stretch](https://drafts.csswg.org/css-align-3/#valdef-justify-self-stretch) requires the computed size in the relevant axis to be `auto` and neither margin to be automatic. `max-content` is a distinct computed keyword. The reviewed current draft is preserved by the round 6 sizing audit, retrieved 2026-10-18. The Grid context is restricted to a definite containing block, a non-masonry axis, and resolved explicit `stretch` alignment.

`Stretch.lean` uses a five-constructor preferred-size type, three resolved alignment values, and six independent Boolean context inputs. `selfStretch` expresses the declarative eligibility rule independently of the native branch ordering. `native` models the branch selection. `selection_refinement` establishes agreement for every one of the 960 finite contexts. Twelve audited declarations also establish no initial self-stretch for non-auto preferred sizes, both automatic-margin exclusions, preservation of ordinary auto and all other unchanged size categories, preservation of the clamp flag, and availability of a fill size when the existing clamp policy needs it. The old and repaired max-content witnesses are checked explicitly.

The `spec` record combines the normative self-stretch decision with a separately stated **preservation policy** for existing native clamp and explicit-size dispatch behavior. Those clamp rules are not claimed to formalize the Grid automatic-minimum specification. `definite`, `min-content`, and `fit-content` represent three tested non-auto/non-max-content dispatch categories; percentages, anchors, `stretch` sizing keywords, or future computed variants require an adapter argument before inclusion.

## Native bridge

`SOURCE-v1.json` binds the entire before/after `ComputeSizeWithIntrinsicDimensions` function and complete Canvas, Grid reflow, and ReflowInput caller fragments. The changed function continues to group auto and max-content for natural sizing, retains the Grid clamping branch for both, and changes only the explicit inline alignment stretch assignment. The caller snapshots are reviewed provenance, not code executed by this bridge.

`bridge.py` inserts the exact native combined-keyword declaration and complete initial inline-size branch into `adapter.cpp`. The C++ program compares all 960 context combinations at five finite coordinate triples, including padding, positive and negative margins, zero available space, and excess padding: 4,800 cases. Mock methods represent computed keyword predicates, Grid/masonry state, resolved alignment, automatic margins, and flags. Explicit-size calculation is a dispatch marker rather than a model of its arithmetic. This is bounded execution of the extracted branch, not execution of native Gecko objects or proof of C++ compiler semantics.

The minimal guard is preferable to narrowing the outer combined-keyword branch: doing the latter would also remove max-content's existing clamp handling. Block-axis behavior and min/max-size calculations remain outside the edited branch.

## Important limits

The theorem concerns **initial inline self-stretch selection**, not final geometry. Later code can promote inline fill to `Stretch` when an automatic-minimum clamp combines with block-axis stretch, and block-axis stretch can change an inline size through an aspect ratio. Those paths are deliberately preserved. “Max-content never stretches” would be an incorrect description of what this package proves.

Computed keyword retention through overrides, actual used-alignment resolution, the mappings of writing modes and automatic margins, Grid containing-block construction, and dispatch to the replaced sizing function remain manual bridge obligations. Natural dimensions, aspect-ratio arithmetic, box coordinates, rounding, min/max constraints, missing intrinsic sizes, fragmentation, masonry layout semantics, Flexbox, and final used geometry are not proved here. The independent WPT and full Firefox build provide integration evidence for the concrete repair.

## Replay

From the repository root, with the pinned Lean and C++ toolchains:

```
python3 artifacts/css-sizing-stretch-proof-v1/check.py /tmp/sizing-stretch-replay
python3 artifacts/css-sizing-stretch-proof-v1/check.py /tmp/sizing-stretch-live --live
```

The output directory must not exist. `--live` additionally checks source fragments against the working tree. The historical before snapshot permits replay after the native repair. All companion inputs and compilers are hashed before and after execution.

The checker requires an exact axiom audit: only `propext` occurs, and several finite theorems use no axioms. It rejects unchecked proof constructs. Three Lean mutations omit the auto distinction, an automatic margin, or required clamp fill; each must fail in the exact reviewed theorem bodies. Five compiled C++ mutations remove/reverse the new guard, ignore automatic margins, remove clamp fill, or retain an unconstrained clamp flag. Each must compile and then fail at its exact expected case. Nine forged diagnostic records and all five source snapshot corruptions must be rejected.

`tooling-paths-v1.txt` lists only companion sources. Replay outputs, executables, preparation receipts, and development logs are not source inputs. Development history retains the initial mutation-cardinality mistake caused by a shared expression in the old reference model; the final checker restricts its mutation to the candidate definition.

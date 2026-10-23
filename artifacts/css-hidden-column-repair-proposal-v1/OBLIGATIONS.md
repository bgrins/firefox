# Proposed obligations (uncompiled, not established theorems)

Let `dirty(f)` mean the actual `IsSubtreeDirty()` predicate (either direct dirty or dirty-descendants). Define the partial structural provider `P` only for `Col(parent = Group(parent = Table))` and `Group(parent = Table)`. Use a finite stable frame-identity graph at the entry point. Let `H(f)` be the existing in-flow ancestor walk and hidden-ancestor predicate, not a substituted provider path.

```text
oldEligible(f) := f exists and dirty(f)
newEligible(f) := f exists and (dirty(f) or (P(f) exists and dirty(P(f))))
```

1. **Exact branch refinement.** Derive candidate entry behavior from the concrete checked-parent branches, including null and malformed chains. An already-dirty frame must not require a well-formed provider. The additional path must require a column/group target and the actual table frame, not its wrapper.
2. **Conservative predicate extension.** `oldEligible → newEligible`. For a clean non-column/group, or clean target with clean/missing provider, the new method returns exactly as before. For an already-dirty target its calls and original ancestor walk are unchanged. This is a local control theorem, not universal observational equivalence of extra layout.
3. **Ancestor identity preservation.** For newly eligible targets, scheduling derives from `H(f)`, not `H(P(f))`. Include a hidden provider/intermediate ancestor witness that would be omitted by replacing `aFrame` with its table. Without a hidden ancestor and under the original caller/set-state precondition, no forcing is scheduled.
4. **Provider construction and publication.** Derive the parent chain from actual column/group/span constructors and identify the `SetColumnDimensions` writes to the queried frames. Prove the selected geometry observer consumes those frames, including any admitted span/fragment union. A declaration/accessor assertion alone does not establish every constructor/history invariant.
5. **Runtime readiness.** For the specific failing histories, show that after the ordinary flush the stale clean target has `dirty(P(f))`. This must come from source/events and the diagnostic trace; it cannot be assumed as the theorem that the repair is intended to establish. Keep a clean-table/stale-placement countermodel outside the sufficiency result until excluded by actual producers.
6. **Flush and freshness.** Under named scheduling, frame-lifetime and successful-flush contracts, show that forcing original hidden ancestors reaches table publication and that the original primary is reacquired. Preserve failure/interruption/reconstruction cases explicitly. Do not infer final geometry freshness from the eligibility Boolean.
7. **Repeated-query bound.** Conditional on completed publication clearing relevant dirtiness and no intervening invalidation, a second clean query is ineligible. Derive clearing at the actual table caller before making a runtime cost claim. The baseline predicate alone does not prove that clearing.
8. **Caller coverage.** Keep Layout primary-frame queries and the auto-visibility scroll caller distinct. Prove unchanged behavior for ordinary clean inputs; test changed scroll-column inputs. Continuation/fragmented publication remains explicitly open beyond the same-parent span relation.

Useful distinguishing source/model mutants: omit the table dirty check (repeated clean forcing); overwrite `aFrame` with provider (lost intermediate ancestor); check only direct dirty instead of subtree dirty; remove the original dirty-target alternative; accept a wrapper/unchecked arbitrary parent; and select a table from an unrelated frame. No mutations or Lean compilation have been run in this proposal.

# Source identity quotient: open admission proof

The semantic occurrence-deletion and region-intersection theorems are proved. Their instantiation with `(physical longhand, exact unimportant priority, declaration-block address)` still needs a provider/grouping theorem. A declaration-level deterministic-action premise is false and must not be introduced.

The useful stronger invariants are:

1. For a fixed receiver, physical property, flags and normalized priority, reused block pointers yield the same ordered declaration sequence and importance bits under the stylesheet read guards. Logical mapping is determined by the receiver's completed writing mode; original-property uniqueness does not imply physical uniqueness.
2. Selector specificity/proximity/source-order only alter occurrence placement, not a shared block's content. Exact priority equality includes flags, origin, context and layer. Normal and important halves retain the same block/key.
3. Every rule's important half precedes its normal half, while within a half declaration order is reversed. A source-admitted theorem must connect this to the actual complete origin/important rule-tree path, not assume a prearranged stream.
4. After the cutoff-composition repair, eligibility only shrinks as new constraints accumulate. Priority cutoff predicates are invariant under changing candidate importance. These facts are checked component lemmas. Before that repair the first property was false at the inline exception.
5. For a key excluded by a Rule event, every later distinct occurrence with the same block/key must either encounter its own corresponding Rule before any surviving value, already have been excluded, or have all relevant declarations rejected by a prior retained cutoff. Identical block order plus equal per-half eligibility and global importance order are intended to establish this; the theorem has not yet been proved.
6. Evaluation/filter outcomes and bookkeeping must be stable for those same block/key/property occurrences: variable substitution, invalid values, included flags, ignore-colors handling, dependency registration, visited filtering and lazy caches cannot be silently modeled as a pure key function. Final selected-value equivalence alone does not prove equality of intermediate audit traces or dependency observations.

Source facts already reviewed: DeclarationImportanceIterator reverses the ordered block/importance zip; DeclarationIterator filters importance and pseudo restrictions; buffering retains all longhand declarations; apply_non_prioritary_properties maps logical IDs immediately before per-property processing; Stylist::add_styles can reuse a block Arc across selectors; StyleSource identity is the declaration-block allocation, not a unique StyleRule occurrence. Locks/owners preserve pointer lifetime, but do not prove occurrence uniqueness. The direct compute_for_declarations caller has block provenance without a rule-tree node.

No universal quotient claim or full C7/C10/C13 completion follows from the current source review or finite WPT agreement.

## Additional source admission evidence

`source-identity-audit-v2/` retains parser, nested-rule and CSSOM setter snapshots. Reviewed parsing and deep cloning allocate fresh declaration blocks; ordinary CSSOM setters retain the rule's own block or substitute a freshly parsed/cloned block. This narrows the source-sharing audit but is not complete constructor/FFI closure or a semantic-occurrence quotient proof.

`apply_non_prioritary_properties` records the writing-mode dependency before `apply_one_longhand` checks seen flags, included cascade flags and rollback exclusions. Substitution occurs after those checks. A reference that physically deletes events before every observer phase therefore cannot claim exact cache-dependency trace equality. Model the pre-filter observation phase separately or explicitly prove the selected observation abstraction permits conservative dependency additions. This is a correspondence requirement, not a new computed-style defect.

`SourceCoherence` separately proves coherent full-block content from an immutable allocation-provider construction, including arbitrary concatenated provider lists. It does not alter `rawAdmitted`; connecting actual native allocation identities remains an explicit obligation. `SOURCE-GROUPING-PLAN.md` records the per-half sequence, self-disabling action and importance-order proof still required.

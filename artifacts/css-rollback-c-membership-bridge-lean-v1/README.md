# Cold C fast-bit and identity-membership bridge

This proves the representation invariant needed by the cold-membership C candidate. It extends the preceding A+B+D bridge and reuses `RepresentedControl`; it does not modify either package. The triage in `../css-rollback-c-identity-bridge-triage-v1` explains why the old `fast == priorityMap.contains(property)` invariant cannot cover C.

For one already-mapped physical longhand, `State` contains its optional three-family priority cutoff, fast membership bit, and list of rule exclusions. The list is the projection of the native global vector onto that physical property. The proved invariant is:

`fast == (cutoff entry exists || exclusion list is nonempty)`.

| Result | Checked theorem |
| --- | --- |
| Empty initialization establishes the invariant | `initial_well_formed` |
| Rule and every priority update preserve it and the representative-family validity invariant | `add_well_formed` |
| Any guarded finite update fold preserves it, including rejected declarations that leave state unchanged | `guarded_fold_well_formed` |
| First Rule has a true fast bit, no cutoff entry, and one identity exclusion | `first_rule_without_cutoff` |
| Later priority additions preserve that exclusion; Rule → Layer → Origin yields both forms of state | `later_priority_preserves_rule`, `rule_layer_origin_sequence` |
| Native-shaped update arms project to `storedAdd` | `add_matches_stored` |
| Cold membership scanning equals membership in the full identity-key list, under the explicit ownership premise | `cold_match_exact` |
| The fast bit safely gates both cutoff and identity rejection | `fast_gate_projects` |
| Inclusion, accumulated cutoffs and cold exclusions match `storedAllowed` | `longhand_gate_matches_stored` |
| With only the first Rule recorded, matching identities are rejected and other identities remain eligible | `identity_only_gate` |
| Distinct flags remain distinct after priority normalization | `full_priority_equality_retains_flags` |

`Key` is the product of the **full** normalized `Priority` and block identity. It uses structural equality, including flags; it is not equality of scalar cutoff keys or native ordering equivalence. Normalization clears the importance bit in the imported priority model while preserving origin/context, layer and flags. The existing numeric/native priority mapping premises remain unchanged.

## Explicit native premises

`contains block declaration = decide (owner declaration = block)` is a separate theorem argument. Here declarations mean the original borrowed entries, and `owner` means the reviewed block-allocation class. This package proves the scan/list representation correspondence **from** that premise. It does not prove native pointer provenance, allocation disjointness, lifetime, guard correctness, first-match lookup totality, or semantic CSS rule-occurrence uniqueness. The domain must consist of source-covered original declarations; owned substituted declarations cannot silently be substituted for those identities.

The native mapping uses `DeclarationSources::containing_block(original_declaration)` only after admitted Rule. `RuleExclusion` stores the triggering declaration's `priority.unimportant()` and recovered block, not the priority of the first node found during lookup. `block_contains` performs original-entry pointer membership. `apply_one_longhand` compares physical property and full normalized priority before that membership scan. `SOURCE-MAPPING.json` pins these exact copied sources.

The state projection is per physical longhand. Native `rule_exclusions` records for other physical properties are filtered out; updates to those other keys leave this projection unchanged. Logical mapping and its writing-mode observation occur before the exclusion guard. These source-to-model projection facts are explicit premises, not a proof of native hash maps or the full multi-property cascade.

Actual Rule keywords map to `StoredConstraint.rule key`. The distinct `StoredConstraint.priority p .rule` is a neutral algebraic constraint supported for completeness; it is not the actual C Rule arm. Non-Rule keywords create/update a cutoff entry while preserving identities. Rejected declarations must be rejected before the modeled update. The existing seen guard, action/substitution classification, provider ordering, transient context, visited/direct source selection and terminal processing retain their separate obligations.

The two proved gate/update correspondences supply the representation interface needed to reuse the existing `stored_control_deletion` theorem. No new whole-native execution or CSS occurrence-quotient theorem is claimed. The reduced ordered-block quotient, native observation audit and cold lookup coverage obligations are not discharged merely by this interface proof. No browser bug is added.

## Replay

Run `python3 artifacts/css-rollback-c-membership-bridge-lean-v1/replay.py` from the repository root. The script pins existing dependencies in `IMPORTS.json`, copies them into temporary scratch, compiles with the bundled Lean 4.35.0-rc4 compiler, retains commands/results in `lean.log` and `RESULT.json`, and removes scratch. `VALIDATION.json` identifies the actual successful invocation and theorem axiom audit. No native, browser, build, Git, old artifact or canonical-library mutation is performed.

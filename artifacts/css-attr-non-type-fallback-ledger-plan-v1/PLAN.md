# Prospective fix 137 ledger update

Title: **Include used non-type attr fallbacks in dependency cycles**.

This is a plan, not acceptance. The five live ledger files are unchanged. ENTRY-TEMPLATE.json has null commit/acceptance/signature fields and must not be copied into an accepted queue unchanged. The prior fix136 update workflow is pinned in REFERENCES.json. No canonical Lean file or coverage count changes.

## Required inputs and gates

Fill INPUT-TEMPLATE.json from actual archived files, using path plus SHA-256 references. Required future inputs are the native signed-commit receipt, preceding research receipt, acceptance record, final independent review, successful build receipt and verified post-signing epoch. Candidate and original assessments are already real and pinned here. Reported build session95572/terminal3e9f94 exited0; bind its archived receipt before acceptance rather than treating this message-derived identifier as independent validation.

Require successful signature verification for both commits, research ancestry before the native commit (normally native.parent == research.commit), and the exact three native/WPT paths, modes and blobs from the partial-commit plan/receipt. Preserve the complete candidate working bodies and remaining native dirt. Use the actual signed IDs; never substitute plan tree IDs or prospective placeholders. The root owns live ledger application and epoch/pin refresh after signing.

The saved comparison has one original and one candidate phase: new34 tests are 15 PASS/19 FAIL then34 PASS. All154 existing assertions and six reftests pass both phases; the full167-row existing regression signature is identical. Existing raw-nested attr-cycle expectations remain unchanged. This establishes19 observed repairs and15 unchanged new-fixture controls, not34 newly discovered bugs. The historical failed v2 preflight is not a browser result. No O/C/O/C or pristine-upstream run is claimed.

## Exact five-file update

| File | Required change |
| --- | --- |
| stylo-bloom-tools/CURRENT-COMMITS.json | Append finalized entry137 to new_queue; committed_native_fixes135→136. Preserve accepted_pending_native_fixes=1, on_hold=1, excluding_holds=0. Archive latest_signing in local_signing_history before replacing it with actual fix137 receipt references. Preserve latest_counter_fix and all prior queue entries. Archive latest_verified_working_epoch before setting the actual post-signing epoch and including137 in browser_binary_contains_fixes. |
| css-fix-readout-20261023/GROUPS.json | Append identical finalized entry to Attributes and custom properties; group committed/total16→17. Overall committed/accepted135→136, tracked136→137; held1 and accepted_pending0 unchanged. Set head from actual native commit. Preserve formal_library_checkpoint and its history byte-for-value. |
| stylo-bloom-tools/BUGFIX-COMMITS.md | Prepend concise signed fix137 evidence/limits paragraph; insert row137 before136 with actual native/research IDs. Update only current summary135→136 and Attributes16→17. Preserve older historical summaries and every old commit row. |
| css-fix-readout-20261023/README.md | Same current summary/group/table updates as BUGFIX-COMMITS, preserving historical sections. |
| stylo-bloom-tools/PLAN-OF-RECORD.md | Same current counts/leading evidence paragraph. Replace execution-order item1 with preservation of signed137 evidence, and leave raw-nested oracle review, pending-provider integration, registered-number investigation and Bloom milestones outstanding. Distinguish the now-fixed used-fallback lead from still-unaccepted leads. |

Paths in the table are relative to artifacts/. LEDGER-PREIMAGES.json fingerprints the inspected versions; recheck current files before applying edits and preserve intervening research-signing updates. Do not overwrite a newer ledger from an old full-file snapshot. Do not archive or rewrite prior records merely to change their historical counts.

Archive cycle_repair_queue before changing only used_attr_fallback to its finalized committed entry/receipt. Replace the all-leads REPRODUCED_NOT_ACCEPTED status with a mixed-status description; raw_nested_attr and registered_number remain unaccepted. Preserve the typed_demand_validation_checkpoint as historical evidence. Update current signing_next_action to remaining raw-nested/pending-provider work. If latest_research_signing is updated, archive its actual previous value once; do not duplicate or invent research commits already recorded by the signing step.

## Entry wording and limits

The branch classifier uses ParsedNamespace directly and shares one complete numeric parser with substitution. Parent499c0c6 already corrected numeric parsing; the branch diff therefore removes its corrected inline code. The separate upstream-self-contained.patch adapts insertion/substitution context and includes the same full primitive and exact34-case WPT. Explicitly retain that numeric overlap and the absence of upstream build/browser validation. Do not count the overlap as another bug or squash the earlier standalone fix.

Discovery attribution is source inspection and browser reproduction during formal-verification work, not a Lean proof finding. Tentative P3 CSS correctness; no security, measured performance, new canonical coverage or universal native-refinement claim. Keep existing Lean checkpoint counts unchanged:11,840 audits,12,438 cases,173 expected-false cases,2,155 source fingerprints.

After materialization, check five-file totals:136 accepted/committed,0 accepted pending, held120 excluded,137 numbered tracked; Attributes17. Compare all pre-existing queue/group entries and held120 against the pre-update versions. Verify exact new commit references/signatures, preserve the other four unfinished work areas, and refresh only the root-owned ledger pins/epoch after the live update. This artifact performs none of those mutations.

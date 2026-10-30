# CSS and Stylo continuation

HEAD ecfe313d582a335c04d80bfd360fd3a591defdb7: 149 accepted local native fix commits, plus two test-only repairs. Held fix120 and unaccepted candidates remain excluded. Goal active. No push, unsigned commit, or new native acceptance.

## Current experiment

Fresh original77 baseline completed: 49 PASS / 28 FAIL / 12 OK. Independent review verified full restoration. V3 selected-declaration repair improved cases but regressed union-plain; V4 composes selected-declaration traversal with the independently tested selected-color refinement.

Candidate77 first attempt (session31828, launch42b928, terminalf69237/1) stopped at the 27 GiB post-backup disk check before source overlay/build/browser. Full recovery verification84019/48d9f1/041d5c/0 proved unchanged source, application, index, controls and exact backup inventory. Root removed its 1,008,605,176-byte backup (019f4b/105608/0). Failed runtime2 is frozen with FILES b857593dbfb46aa57712820a373eafa0c6f0ce0830705ddc7825a44eaf536021. Six obsolete tokenizer development Cargo target directories were also removed, preserving sources, manifests, commands and results; see ../css-generated-cache-cleanup-20261030-v1.json.

Fresh retry owner css-prioritary-selection-candidate-v4, active FILES3e0000eaf9dda31d27653c70f65838d71f85676c49994c71e8302c5ec5b0f849, terminated session8402/b88cb6/06fb14 with exit1. Build exited0. Ordinary61PASS7FAIL8OK and forced-colors2PASS1FAIL2OK completed with comparison gates true; union-plain now passes. Appearance did not run: an intermediate index-state before/after equality assertion failed between lanes. The exact differing field/cause was not saved. Independent reviewer8389/508559/8aaeb3 exited0 and verified the partial observations and complete restoration; report SHAabf48c0c2aafb73e22d7b693a55b253d2e7ab18741f498f9f1f18b3582dc74bb. Root removed the exact retained1GBbackup and refreshed only the observed raw-index hash. CandidateV4 remains incomplete and unaccepted.

Signing is available again: actual59da05/0 produced and verified a1Password signature after the user's explicit request to commit all completed work. Prior failures remain evidence. Signed research checkpoint, MinMax, Log, and ready shared/A/I packaging now take priority over new experiments.

## Next actions

1. Commit the completed research checkpoint, then the independently validated MinMax and Log native+WPT patches without an intervening artifact commit between research and MinMax. Publish ready shared helpers → A union → I image with exact parent-specific patches and their WPTs. Verify actual signed commits and update the branch table. Preserve all unfinished animation/attr/selection work as clearly marked research.
2. Run the separate unused-unit-fallback probe in installed Firefox and portable Chrome, serially after restoration. Fixture FILES359e873def8991d21dea052c7dd621e9ca5dc41172444513e7ac8095c63fe923; disabled observer FILESfb9b763134c1479efbab85251eabf72d965888f89e96033eaf0a206d4984d88f. Root read full runner/report and authenticated saved inputs (c43ea1/0); peer and saved checks passed. Preserve all three WPT statuses and both phases of computed-value samples. No browser result exists yet.
3. If observations establish the unused fallback defect, evaluate a narrow selected-unit refinement. V4 PreparedCustomValue retains substituted CSS and its specified AST; derive an optional unit summary only after successful parsing/readiness, retain genuine custom/attribute edges and color handling, and avoid duplicate substitution or computation. Initial/Existing/Invalid and already-cyclic paths require explicit justification. Cover selected versus unused em/lh/rem/rlh, root/descendant, aliases, genuine cycles, CSS-wide/default/inherited values, attr taint and random state. This is a source-supported design, not an accepted fix or native proof.
4. Package validated repairs as independently reviewable native+WPT commits with prerequisites explicit. Keep tooling/model documentation in preceding research commits. Min/max and explicit-base logarithm fixes remain validated but uncommitted; union/image and selection packaging must preserve their tested dependencies.
5. After signed publication, rebind the incomplete selection experiment to the new HEAD and narrow A+I sources; do not apply an A-only whole-file postimage that drops the accepted image refinement. Diagnose the index snapshot mismatch before a complete rerun. No unsigned fallback or push.

## Formal scope and worktree

Bloom milestones1–6 are complete within their recorded bounds. CSS Lean remains a partial spec-oriented model, not all-CSS or an end-to-end Stylo proof. The selected-declaration/color model adds five theorem audits and two false controls; it does not prove native SCC scheduling/default publication. Existing finite dependency search and model boundaries remain in earlier reports.

Untracked audit v22 confirms563 expected paths:53WPT+15native/support files byte-match committed recovery blobs;495unrelated paths/metadata unchanged. No new/missing paths, no staged changes at the restored pretrial state. Ignored research/build outputs are outside this inventory. The completed trial restored held custom_properties.rs as the sole tracked edit. Recovery copies are not accepted native commits.

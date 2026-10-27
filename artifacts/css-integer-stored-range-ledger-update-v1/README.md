Candidate-only ledger updater for the fix 121 metadata fold.

Run after the actual rewrite finishes successfully, with root's genuine outer receipt:

```
python3 -I -S -B artifacts/css-integer-stored-range-ledger-update-v1/prepare.py --rewrite-map artifacts/css-integer-stored-range-history-runtime-v1/REWRITE-MAP.json --result artifacts/css-integer-stored-range-history-runtime-v1/RESULT.json --execution artifacts/css-integer-stored-range-history-runtime-v1/OUTER-EXECUTION.json --output artifacts/css-integer-stored-range-ledger-candidates-v1
```

The output directory must not exist. This writes five candidate bodies, exact before copies, a patch and a manifest only under that artifact directory. Root reviews the patch and applies it separately after checking current preimages. The helper does not write any live ledger, source, index, Git object or ref. It refuses changed ledger preimages, an incomplete 37-commit map, failed/unpublished rewrite, failed signature/final-tree flags, nonzero outer exit, or inconsistent map/result/tip. Root remains responsible for independently authenticating the actual rewrite and its root verification; reading successful receipts is not another signature verification.

The audited JSON locations map exactly fixes 121–131, 133 and 134, including companion arrays, research_commit and shared_prior_research. No global recursive replacement is used. Original signing summaries move intact into pre_fix121_rewrite_summaries; their current equivalents explicitly cite the new rewrite receipts rather than relabeling old verification. All previous/history fields and the readout historical suffix remain unchanged. Original patch/acceptance references retain their historical meaning; fix 121 gains the metadata path and a fold record. The five original full ledgers are also preserved as exact backups.

Current accepted/committed count remains 133; GROUPS.accepted is corrected from its stale 131 to 133, without adding a fix. The current model checkpoint records the signed nested HEAD 162b20fb7c53a0ab89b20875a965baee98fb66bb and full totals 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source pins. Provider host results are 19 passing native tests, with normal pending production still disabled. Metadata validation preserves 113 observations: 110 PASS and three expected FAIL, changing just one expectation. No new coverage, native refinement, browser repair or fix credit is inferred.

The current plan becomes fresh quote append candidate/original/candidate validation, followed by real winning-provider cascade/scheduler integration. Current underlying values, animated-cycle policy, dependency publication and memory reporting remain open. Historical prose and receipts are not rewritten to imply those steps have happened.

Inert replay: `python3 -I -S -B artifacts/css-integer-stored-range-ledger-update-v1/check.py`. It creates no files and invokes no Git/compiler/browser commands. The synthetic IDs exist only inside that test and are never presented as actual rewrite evidence.

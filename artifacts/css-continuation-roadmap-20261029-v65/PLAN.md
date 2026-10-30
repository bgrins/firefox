# CSS verification continuation

149 accepted native fixes remain committed across 150 tracked IDs; held repair
120 remains excluded. Two additional math candidates now have successful
reversible comparisons. Neither is installed or counted as accepted.

| Candidate | Actual comparison | Remaining publication work |
| --- | --- | --- |
| Contextual infinity in min/max | 472 callbacks; 14 target repairs; all 32 authored checks pass; 470 control/ending signatures preserved; two existing failures unchanged | Research, then calc source and two WPT files in one native commit |
| Logarithm special-value dispatch | 102 callbacks; 15 target repairs; all 24 authored checks pass; all 102 pass; 90 control/ending signatures preserved | Research, then calc source, corrected WPT and removal of five obsolete expected-failure annotations in one native commit |

The [log comparison](../css-log-clear-browser-runtime-1/CANDIDATE-ROOT-REPLAY.json)
completed as session 75102, terminal 37c78c, exit 0. Root independently replayed
both complete raw streams and checked their application/assessment bindings,
restoration and process cleanup. Source and application were restored, and the
verified 1,008,605,176-byte backup was removed. The raw Git index changed without
semantic changes; the [reconciliation](../css-log-clear-index-refresh-v1/RESULT.json)
updated only its recorded hash. Current epoch is 3a7d438b4fcce2916739d34afbb1df958bf0a41033f6e7891e9e6f3cb9091353.

## Next actions

1. Run a fresh combined min/max-and-log original/candidate comparison before
   publishing both on the branch. Both individual candidates were tested against
   accepted calc source b291d6e9. Merge their disjoint changes and preserve their
   exact test bodies. The union predicts 15 pages, 574 callbacks, 29 target
   repairs and 560 control/ending signatures; these are planned counts, not an
   observed combined run. Do not merge historical raw streams into a purported
   new baseline. Bind fresh source/application state after restoration.
2. Publish the completed research in sensible pieces, preceding each standalone
   native/WPT commit. Signing availability remains unresolved. The prepared
   MinMax [publication implementation](../css-minmax-native-publication-v1/README.md)
   and [small recovery correction](../css-minmax-native-publication-v2/README.md)
   require fresh bindings; do not reuse their old state observations blindly.
3. Update the fix ledger with the actual signed native commit IDs and explicit
   prerequisites. Current shared-branch comparisons include earlier nonfinite
   relative-length transport and the held provider; they do not establish a
   dependency-free cherry-pick or clean-upstream behavior.
4. Resume contextual easing ownership/movement and animation-only refresh work.
   Earlier 315-case comparison and isolated Servo checks remain scoped evidence,
   not native acceptance.

## Formal work and test correction

The [log dispatch model](../css-log-clear-dispatch-model-v1/README.md) passed 12
new theorem audits and rejected three false claims. Root read the model, audit
and rejection logs and authenticated all 14 package files. It proves dispatch
precedence and selected special results while leaving delegated host results
arbitrary. Native float classification, logarithm accuracy, and unresolved spec
boundaries are not proved. Canonical library coverage is unchanged.

The [native proposal](../css-log-clear-special-values-proposal-v1/README.md)
shares the helper between folding and resolution. Source/spec analysis and
browser reproduction motivated it; this is not a formal-discovery claim.
The original baseline reproduced five already-recorded WPT failures and ten
additional authored cases. Four unresolved base-zero cases remain strict
preservation controls rather than accepted conformance expectations.

Use only the [corrected v2 fixture](../css-log-clear-special-values-proposal-v2/log-clear-special-values.html).
V1 had an incorrect support-script URL that static lint/manifest checks did not
catch. The comparison plan now resolves and hashes every external script URL;
the corrected fixture ran successfully in both actual browser phases.

## Signing and cleanup

The reviewed 604-file research commit failed in the configured 1Password signer
(`failed to fill whole buffer`). Actual terminal: session 42884, chunk 20116a,
exit 1; Git returned 128. Its temporary-index operation verified unchanged HEAD,
real index, source, untracked census and canonical state before releasing the
lock. HEAD remains ecfe313d582a. No commit or automatic retry followed. See the
[failure receipt](../css-research-checkpoint-20261029-v64/result.json).

The [cleanup](../css-obsolete-build-target-cleanup-v1/RESULT.json) removed twelve
completed, noncanonical Lean review build caches: 8,578,400,256 allocated bytes
(7.99 GiB). Fresh process/open-file checks found no users; exact identities,
compiler-only contents, retained evidence and unchanged Git/canonical state
were verified. All source archives, reports and logs remain. Canonical build and
package dependencies, toolchains, the main Firefox object directory and the two
excluded historical caches were preserved. Actual terminal: 61956/885b0c/0.

All work remains local. The [untracked audit](../css-untracked-audit-user-followup-20261029.json)
verified all 563 expected paths; no unrelated files were staged or removed.

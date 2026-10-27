# Git 2.53 transaction composition: actual disposable test

Actual replay d19eee exited 0 in a newly created `/private/tmp` repository, which was removed afterward. No live repository command, index write, signer or persistent Git configuration change occurred. The probe used two unsigned empty-tree commits, an expected branch and a backup ref, with global/system configuration isolated.

The exact v2 `symref-verify HEAD` plus update of HEAD's referent fails at prepare with exit128: multiple updates for HEAD, including one via its referent, are not allowed. The expected branch, HEAD and backup remain at the old object. Adding no-deref to the branch update and replacing verification with a same-target symref-update also fail identically. The separate backup verification plus branch compare-and-swap succeeds, moves HEAD through its existing symref, and preserves the backup.

This is an evidence correction to the prior v2 source GO. The installed manual documents each individual command, but does not establish that this combination is admissible. The inert transaction mock enforced intended atomic behavior and therefore failed to detect the actual command-composition rejection. V2 must not be retried to sign 37 replacements again.

Use a reviewed publication-only recovery for the existing verified objects: re-authenticate all mapped commit objects, parents, trees, messages/authors and signatures; require exact carrier HEAD/branch and backup; recheck complete preservation; publish using backup verification plus exact branch old-value CAS; recheck symbolic branch and new HEAD immediately and after preservation. Root must serialize Git writers across this bounded window. Pre/post checks are observations, not atomic proof that HEAD could not switch between them. Retain failure state and inspect actual HEAD on an interrupted or uncertain publication; no blind retry or rollback.

This bounded probe does not prove that no other atomic strategy exists, nor does it test concurrency, signing, object recovery or the eventual live publication. The recovery source and actual receipts require separate review.

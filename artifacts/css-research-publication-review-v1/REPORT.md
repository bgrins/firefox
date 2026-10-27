# Detached research publication review

Reviewed finish-research.py SHA256 `0e998c50b440e669225ea6d51d78cf5b7c444af8ea470a876f6fd6b4a9dc1f41` and presign.py. This is read-only source review, not publication or comparison acceptance.

The cached-only research patch leaves working bodies untouched; the branch update uses compare-and-swap against the original HEAD. Exact final-tree and per-commit path/body checks cover the 170 actual artifact-only files in the three signed receipts. All 49 admitted modified native paths and 15 untracked native paths occur in the epoch pins. The five current ledgers are pinned as both roles and committed research; all still match their admitted bodies. There is no identified native patch overwrite or stale ledger pin at this review point.

Before execution, add root/nested index-flag checks: the imported semantic_index and verify_current helpers do not include ls-files -v flags. Compare both pre-publication sets with the admitted flag hashes, then preserve every preexisting root flag record after publication and the entire nested flag set. The root full hash will change because new research files become tracked. Current root/nested hashes match admission in the read-only observation.

Also mirror presign.py's ambient GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES rejection and exact symbolic-ref branch check before mutations. CAS failure must leave the staged artifact patch intact for explicit reconciliation; do not reset unrelated staging or change working bodies.

The driver must be complete and absent before publication; independently reviewed final comparison results remain a separate acceptance gate. Missing outer-session exit status must continue to be reported as unobserved, not fabricated from PID absence.

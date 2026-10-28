# Experimental normalization installer review

Bounded source rereview: clear to seal for a root-controlled experimental installation. No execution, native mutation, build, browser, Git/index or epoch query was performed by the reviewer. This is not acceptance of normalization semantics or proof of recovery under arbitrary process crashes/filesystem failures.

Initial review found index state could be silently adopted and control publication fell outside rollback. The revised code checks root/nested snapshots before writing, preserves semantic index fields except intentional working_diff, exact raw index and saved flags, and requires the full tracked working diff to be exactly the existing two plus seven new source paths. Source inodes and base hashes are rechecked before each in-place write; rollback checks source identity and authorized body before restoration.

ROLE/OWNED are parsed directly from the captured control bytes, with prior candidate/committed-head/build2 role requirements. All three controls are compared against captured preimages before atomic replacement inside the same try as source writes. A publication failure takes the guarded rollback path. Rollback requires the complete restored preservation snapshot equal to before and unchanged root/nested flags. Control originals and previous epoch are saved separately. The new epoch remains compiled:false, accepted:false and explicitly labels the experimental container contract and unresolved logical scheduling defect.

The reviewed container helper also now preserves Zoom::unzoom's ONE/zero behavior while dividing in f64. This addresses the concrete zero-zoom finding in css-registered-zoom-normalization-source-review-v1. It does not adjudicate the complete container semantic contract.

Review reads:adda3e/0 initial;66049b/0 transaction revision;33f61d/0 zero guard; eaf816/0 final closure. Final exact inputs are bound in INPUT-PINS.json; the parent owns package sealing and execution. No scratch/native tests were run by this reviewer.

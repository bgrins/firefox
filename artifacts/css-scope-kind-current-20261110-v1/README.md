# Include implicit-scope host context in shared cascade keys

Equal sheet contents and equal raw positions are insufficient when one stylesheet's implicit scope is its owner parent and the other's is the shadow host. The compiler uses that distinction when selecting rule buckets. Resolving the receiving root later does not repair a bucket chosen using the donor's context.

The repair records matches_shadow_host for each effective sheet in the cache key. Recording follows the disabled/media early returns and aligns with the effective contents vector. Constructed roots are classified through the same native method as compilation. Root identities remain receiver-relative; the key does not require two shadow trees to share the same root node. The existing media snapshot publication and index vector are preserved.

This adds one bool per effective sheet and conservatively separates contexts even for sheets without implicit scopes. No performance measurement or complete cache memory-accounting repair is claimed. Default cache ownership restrictions remain relevant: the accompanying model does not prove correctness for every experimental sharing configuration.

## Validation

The baseline is explicitly the preceding completed index-candidate run, not a new browser execution. Its binary, source and test hashes were checked again before applying this patch. BASELINE-REUSE.json identifies the copied raw stream and result: 12 PASS / 2 FAIL, four OK endings. Both remaining failures are host-context cases; the index cases and media controls pass.

The patch was composed onto the current index source and forward/reverse checked without fuzz in a temporary directory. The candidate binaries build exited zero, retaining the known nonfatal Mach progress reporter exception in its log. Rustfmt passed; the exact unchanged WPT resources had already passed WPT lint in the preceding evidence commit. The candidate passed all 14 assertions with four OK harness endings, preserving the previous 12 passes. Build/source/test and post-run binary fingerprints are retained.

The installed Nightly comparison in the preceding index artifact reproduces both host-context failures, both index failures and four shared-media failures. That is Nightly exposure, not a release-channel claim. Both WPTs calibrate resource loading and include an independent URL control; neither accesses cssRules or depends on moveBefore.

The Scope and Vectors proofs retained in css-scope-index-current-20261110-v1 establish the stronger content/position/host-context key's sufficiency in the abstract model. Its fresh replay checked 34 theorems and rejected 12 false propositions. The native implementation is reviewed against that model; there is no Rust refinement proof, complete selector semantics or memory-safety theorem. The specification oracle is the omitted scope-start rule retained by the preceding artifact.

## Delivery

The native commit contains only stylist.rs, implicit-scope-root-kind.html and its CSS support file. The index WPT stays with the separate index fix. This patch uses the current media/index predecessor; historical standalone variants establish the defects' independence, not arbitrary upstream cherry-pick compatibility. No isolated latest-upstream build is claimed.

Run `python3 -I -B check.py` to authenticate the saved evidence and verify the exact callback comparison. REFERENCES.json pins the preceding proof, specification, Nightly and WPT lint records. No additional build directory or persistent profile was created; the existing local objdir is retained for manual testing.

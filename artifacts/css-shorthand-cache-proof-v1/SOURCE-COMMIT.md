# Source-only proof companion

This local research commit precedes the standalone Gecko/WPT fix. It contains the Lean model, replay/validation tools and identities of the exact before/after native snapshots. Generated compiler objects, process logs and browser reports remain local artifacts; the manifests retain their identities.

The full gate requires the accompanying native fix in the worktree and the pinned Lean4.35.0-rc4 macOS toolchain under artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64. Run materialize.py to reconstruct authenticated native snapshots from the recorded parent commit and current worktree, then run check.py with a new output directory. The snapshots remain generated artifacts, avoiding duplicate full native files in the source commit. Source checks intentionally reject earlier or changed native code. The Lean file itself can be checked independently with that Lean version and Std.

ROOT-REVIEW-v1.json records the independent replay. PROOF-v1.json fingerprints the original local gate, including generated files intentionally omitted from this source commit. Its freeze replay needs those retained local outputs; use check.py to produce a new gate run from source.

This is a manually connected bounded model, not extracted Rust verification. Fixed expansion environments, source-identity stability, and supplied cascade eligibility remain explicit premises. The native patch is independently applicable without this research commit.

# Used attribute fallback signing checkpoint

Fix 137 is signed as `aa3f0588538800300df20a2f7de40ce8ac2ffec1`, with only two Rust files and the exact tested WPT. Tooling is in `c43e47f8857bbbdad868541e6e55ac597a907368`; native/browser validation immediately precedes the fix in `38c1b6093c7bf87034ad583e2c84c2277f34ccfb`. All signatures and the remaining working diff were verified.

The original/candidate comparison changes 15 PASS + 19 FAIL to 34 PASS. All 154 existing assertions and six reftests remain passing. Native build, isolated WPT lint and repository WPT lint passed. Independent review verifies exact raw lifecycle, fixture identities, source/binary/BuildID binding and cleanup. This is one additional CSS correctness bug; no new canonical Lean coverage or native-refinement proof is claimed. The standalone upstream export retains numeric-overlap and untested-upstream-build limitations.

The five ledgers now report 136 accepted committed fixes, with held fix 120 excluded. Recovery snapshot `artifacts/css-unfinished-work-checkpoint-20261027-v6` preserves 129 unfinished paths relative to its exact base, with 133 source hashes and reversible patch transport verified. Those experiments remain in the working tree.

The reviewed raw-nested proposal and explicit correction of two historical WPT oracles are signed separately in `809b431f5fb335fa26caf2d7a7e07b6e8f76ac36`. Its 29-case new WPT still needs a controlled browser comparison. Pending-provider integration, registered-number dependencies and scoped Bloom/CSS milestones remain active.

After the final checkpoint commit, use this directory's CURRENT-EPOCH.json as the authoritative continuation state; synchronize the two active native runtime epoch files only after final signature/source/index checks. Current normal binaries contain fix 137. Earlier typed-demand GTest results remain historical; this signing step does not claim a fresh GTest run. All work stays local.

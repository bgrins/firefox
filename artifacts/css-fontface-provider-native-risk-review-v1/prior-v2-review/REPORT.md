# Candidate v2 addendum

Approved as the proposed source-level revision, pending actual build/runtime gates. The earlier review seal is unchanged.

Authenticated all 108 inputs of integration-v1 using its independently supplied INPUTS/FREEZE hashes. Its 16 native candidates exactly equal the original proposal retained in the parent review. Verified v2 preformat against those bytes: the only implementation change is using a retained GetData rule when previousEntry is null and cloning it when an entry exists. Its intent comment is updated. All other preformat files are byte-identical.

Read every format.patch hunk: only indentation and line wrapping change, including signatures and call arguments. Independently verified non-whitespace byte equality for all 16 preformat/final files and regenerated native.patch and format.patch from the retained snapshots. No formatter/compiler was invoked by this review.

The no-wrapper path retains the original parse semantics: GetData selects owned mDescriptors after HasRule rejection; generated descriptor set() parses entirely before assignment; invalid input preserves the old descriptor and family retry; constructor failure still resets all descriptors. No preparation/worker dispatch occurs without previousEntry. The existing-entry branch retains detached parsing, preparation, reentry checks and status-preserving wrapper publication. Moving a retained RefPtr back to mDescriptors does not change the underlying rule in the no-wrapper branch.

Exact native.patch, format.patch and FontFaceImpl.cpp identities are in AUTHENTICATION.json and the retained NATIVE-PINS.json. Root reports 38 failures/30 passes on the 68-case baseline plus two existing regression failures; these are external baseline status, not evidence that v2 compiles or fixes them. No production files were edited here. The original macOS compile/API findings and worker/platform/shutdown limits remain unchanged.

Replay: `python3 artifacts/css-fontface-provider-macos-compile-review-v1/v2-addendum/check.py`.

# Actual-header candidate integer conversion check

The exact candidate lambda from repair-v2 compiled against the existing Gecko headers and passed2,100,046 input checks under undefined-behavior and integer sanitizers. Compile/run exits are0; compiler and runtime stderr are empty. Session13610 completed successfully. The executable, dependency file and debug-symbol directory were hashed and removed.

The test compares against a separately written quotient/remainder oracle, checks integer identity and admissible sign symmetry, preserves the old helper result on the exhaustive ordinary domain[-1048576,1048576] and selected neighborhoods through±2^24, and samples every residue class around the large browser witnesses and signed32 endpoints. There are877 intended result differences from the old float conversion in those sampled large domains. This is not an exhaustive signed32 or IEEE proof.

The candidate conversion uses signed64 bias ±30 followed by C++ truncating division by60. Inputs503316540 and−503316540 now return±8388609. No Gecko source was edited, no browser was run, and no repair was accepted. Full native compilation and paired WPT validation remain necessary; earlier unzoom/ancestor arithmetic remains outside this helper check.

# Fix 124: additive-symbol-resolved-weight-ordering

Calculated additive-symbol weights are compared through storage representation rather than numeric meaning. A shared local resolver applies the nonnegative weight range consistently to admission, strict ordering and export, preserving specified serialization.

The standalone candidate passes all 32 landing subtests and its eight-row rendering reference. It repairs 11 observed outcomes in the isolated phase. The four-phase comparison checks 76 subtests and five references per phase; the combined result retains all twelve improvements with no prior PASS loss or changed retained-failure diagnostics. The single remaining reference failure is unchanged and metadata-expected. All builds and lint pass; root and independent terminal review verify complete restoration.

Source/spec tracing identified representation-dependent ordering; calibrated browser tests reproduced the mismatch. Conditional Lean ordering laws and symbolic post-clamp checks support the repair, with numeric resolution/native/compiler correctness remaining separate premises.

The exact five-path Gecko/WPT patch is copied unchanged from the tested proposal. Research, proofs and tooling belong in a preceding commit. No pending Integer/Sign or other counter repair is a semantic prerequisite. Working-stack installation and signed commits remain pending. CSS parsing, CSSOM and counter rendering correctness; no demonstrated security impact.

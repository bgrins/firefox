# Fix 123: counter-range-calculated-bound-export

Calculated counter-style range bounds can crash during counter rendering. The repair validates each finite endpoint before publication and resolves stored bounds during membership checks, retaining their specified representation.

The standalone candidate passes all 28 landing subtests and its eight-row rendering reference. It repairs 1 observed outcomes in the isolated phase. The four-phase comparison checks 76 subtests and five references per phase; the combined result retains all twelve improvements with no prior PASS loss or changed retained-failure diagnostics. The single remaining reference failure is unchanged and metadata-expected. All builds and lint pass; root and independent terminal review verify complete restoration.

Source inspection identified the boxed-versus-inline Integer mismatch; browser diagnostics reproduced the unwrap panic. Lean supplies abstract admission/export laws under explicit resolution/publication premises, not an automatic parser or FFI refinement.

The exact five-path Gecko/WPT patch is copied unchanged from the tested proposal. Research, proofs and tooling belong in a preceding commit. No pending Integer/Sign or other counter repair is a semantic prerequisite. Working-stack installation and signed commits remain pending. Content-process crash with ordinary constant CSS math on the tested branch; prioritize reproduction and crash repair. No release-browser or memory-safety impact established.

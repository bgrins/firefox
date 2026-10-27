# Accepted fix 112: integer offset and scroll geometry

Accepted as one shared conversion defect. The exact two-file patch changes only Element.cpp and its 32-case WPT. Exact 8388609 CSS-pixel geometry was published as 8388610 through float conversion; signed offset positions and offset/scroll dimensions are repaired.

The candidate passes all 32 new cases and preserves 109 controls: 137 PASS and four unchanged expected FAIL overall, with exactly eight baseline failures repaired. Both builds, lint, cleanup, original-source restoration and rebuilt binaries pass root and independent review. Eighty historical baseline controls were reused only after raw-log and source/resource authentication; their earlier report-order rejection remains recorded.

The 21 arithmetic proofs and actual-header sanitizer checks support the final conversion under explicit source correspondence. They do not verify earlier geometry, unzoom, compiler correctness or the whole CSS specification. Discovery came from source/numeric investigation; the proofs followed it. Client rounding remains separate because its tie rule differs.

No security or measured performance impact is established. The patch applies independently on the retained upstream base; a clean-upstream browser run was not performed. The accepted native/WPT commit is pending signing. Working-tree installation is recorded separately when completed; no commit ID is invented here.

# Preserve the sign of accumulated flex size violations

Locally validated native/WPT repair, uncommitted pending signing. Tentative P3 extreme-size layout correctness. Source review found the narrow totalViolation accumulator; release and local browser reproduction preceded the Lean model. No security severity or measured performance improvement is claimed.

The sizing algorithm uses the sign of the sum of min/max corrections to decide which flexible items to freeze. A positive sum beyond signed32 can select maximum violations even when all corrections are minimum violations. The retained WPT puts a small subject before large min-constrained siblings, avoiding unrelated extreme-coordinate clipping. Its 28 cases cover all four flex directions, small controls, three/four/five/seven large siblings, and 357/359 scaled siblings.

The candidate widens the accumulator and freeze-helper parameter to AuCoord64, promotes both operands before each subtraction, uses typed-zero comparisons, and updates the diagnostic format. It preserves the existing branch order, item updates and final-iteration fallback. The standalone patch contains only nsFlexContainerFrame.cpp and the new WPT.

Validation:

- Unchanged local build: 16 FAIL / 12 PASS, harness OK (session 58541, terminal 37a6fe, exit 1).
- Candidate build: session 43197, terminal e604c1, exit 0. The initial build caught an ambiguous mixed-coordinate equality; its source/log/terminal are retained, and the final patch also fixes the debug-only zero comparison.
- Candidate browser suite: all 28 new subtests pass; 20 files and 211 subtests give 231 successful checks (session 88766, terminal e4f0b9, exit 0). The suite includes existing min/max-freeze controls and both earlier fixes' full preservation suite.
- Final scoped clang-format and WPT lint: session 99137, terminal cc450c, exit 0; no errors or warnings.
- All three pending native/WPT patches apply and reverse independently against HEAD and in all six orders, reproducing the current source exactly. See ../css-flex-three-independent-patches-20261111-v1/RESULT.json. This establishes patch independence, not clean-upstream runtime independence.

The independent v1 review covers the native delta, WPT formula and scoped formal target. The formal model is still under development: v2 strengthens checked-old arithmetic to check each subtraction, not only running sums. No correctness theorem is yet accepted. Its progress property concerns one sign-selection pass; exact native helper correspondence additionally needs the final-iteration/count-history boundary recorded by the reviewer. Wraparound controls describe a model mutation, not C++ signed-overflow semantics.

No gap, auto-margin storage, positioning or fragment repair is included. The current combined source SHA is cc649bb12d69438bcc84f67e77dcafa25f58a574475f8235211cc6da3de9822c. Existing two-fix receipts remain historical, and their tests pass in the new build. No Try, push, signing retry or unrelated build cleanup occurred.

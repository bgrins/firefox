# Independent finite Round arithmetic review

No final-binary32 counterexample was found. The tested v2 algorithm remains a reasonable arithmetic prerequisite; this review does not accept it as a native fix or close the separate contextual-consumer work. The strongest qualification is that reconstructed binary64 bounds are **not always exact**. Correctness must concern the final binary32 result, not exactness of every intermediate multiple.

For value 1 and step 3 times the minimum positive binary32 subnormal (bits 3f800000/00000003), the exact truncating remainder is two minimum subnormals. Both reconstructed binary64 bounds become1, even though the exact adjacent multiples differ. All four candidate results are nevertheless correct: both exact multiples round to binary32 value 1. The negative counterpart behaves symmetrically. WITNESSES.json preserves this example, the historical one-third-step discrepancy, signed-zero ties, and finite-to-infinity output rounding. This is a limit of an intermediate-exactness claim, not an observed candidate bug.

## Executed checks

The actual sealed v2 scalar helper bodies were authenticated, extracted unchanged and compiled with rustc 1.92.0 at optimization level 2. No Gecko source or build output was changed. The temporary executable was removed.

| Coverage | Operand pairs |
|---|---:|
| Exhaustive subnormal magnitudes value 0..255, step 1..255, both operand signs | 261,120 |
| Every finite exponent pair, four selected mantissa pairs, both value signs | 520,200 |
| Seeded uniform bit patterns, excluding nonfinite values and zero steps | 99,196 |
| Near integer/half-step boundaries, including quotient 2^23,2^24,2^29,2^53 | 228,864 |
| Explicit subnormal/normal, overflow and signed-zero transitions | 100 |
| Total, including repetitions between batches | 1,109,480 |

Four strategies give **4,437,920 comparisons**, with **zero candidate mismatches** and **656,404 old-implementation mismatches**. There are 207,055 tested pairs with quotient magnitude at least 2^53, 266,398 with a subnormal operand, and 5,834 exact half-step ties. Oracle outputs include 631,731 negative-zero and 6,492 infinity cases. The binary32 truncating remainder agrees with the exact dyadic remainder for every tested pair.

The expanded oracle uses integers in units of 2^-149. Signed integer division selects exact mathematical multiples; a separate integer nearest-even encoder rounds only the selected result to binary32, including subnormals and overflow. It does not compute the candidate's binary64 reconstruction. 8,192 outputs were independently cross-checked against the predecessor's exact-Fraction oracle and binary-search encoder. The old implementation supplies a substantial negative control. Seven additional compiled witness pairs agree, including the collapsed-bounds and negative-zero examples.

This is exhaustive only for the stated low-subnormal subdomain, not all binary32 input pairs. Output and input digests, the deterministic generator, coverage counts and compiler identity are in RESULT.json. The helper starts after operand/type resolution and is not a CalcNode/native or browser execution.

## Conditional numerical reasoning

This is a hand argument, not a kernel proof or verified Rust refinement. It assumes binary32/binary64 nearest-even arithmetic and conversion, exact finite truncating remainder behavior, gradual underflow, and no transformations that alter those operations. It is intended to expose the precision boundary rather than replace compilation and browser validation.

1. A finite nonzero binary32 remainder is representable exactly. For magnitude A at least positive step B, write them on the step's binary quantum. Integer remainder has fewer bits than B's at-most 24-bit significand. For A<B the remainder is A. Returning A when remainder is zero therefore avoids quotient overflow and preserves the input zero sign.
2. If A<B, the two bounds are zero and B, with the appropriate signs. If B>=4A, the nearest-choice comparison has a wide separation. Otherwise the comparable-exponent subtraction is exact in binary64. Thus a rounded distance cannot reverse the nearest selection at its tie boundary. The explicit copysign retains negative zero for a zero upper bound.
3. For A>=B, let e=floor(log2(A)), d=floor(log2(B)), k=e-d. If k<=27, both exact adjacent multiples lie on a quantum no finer than 2^(d-23) and have magnitude less than 2^(e+2). They therefore require at most k+25<=52 significant bits. Binary64's53 bits represent the reconstructed bounds and relevant distances exactly, including nearest ties. Subnormals have a coarser quantum than this bound and do not invalidate it.
4. If k>=28, B<2^(e-27). Both exact bounds are within B of A. The nearest binary32 rounding boundary is at least 2^(e-25) away from an exactly represented nonzero A (the conservative power-of-two lower-side case). Binary64 reconstruction errors are far smaller: two operations contribute at most 2^(e-51). Both reconstructed bounds and exact bounds therefore round back to the original binary32 A. Any loss of distinction between the bounds or distance comparison cannot change the final result in this case.
5. Binary32 magnitudes and adjacent multiples cannot overflow binary64, and their smallest quantum is far above binary64 underflow. Output overflow is handled by the final cast; the exact oracle tests its rounding threshold independently. Returning signed exact inputs and applying copysign before bound selection are necessary parts of this reasoning.

The case split explains why merely finding a rounded-away remainder in binary64 is insufficient to refute this algorithm. It also avoids a blanket claim that using a wider type automatically prevents double rounding. The exactness and final-rounding-margin premises are the substantive requirements.

## Scope and next action

The special NaN, zero-step and infinity branches and accepted 125/126/128 bodies remain the authenticated v2 predecessor scope; this new audit targets finite operands. It does not establish target-dependent compiler/fmod behavior, flush-to-zero behavior, all contexts, parser simplification equivalence, dependency invalidation, timing-function storage, or targetless API policy. No performance claim is made.

Proceed with the already proposed arithmetic-only configured/linked candidate and exact original 14 plus four exposure/calibration tests when root schedules them. The current original-browser diagnostic has executed: all sixteen exposure/control snapshots pass. Only the future deferral-induced route into the defective arithmetic remains predicted and unexecuted. The historically observed context-dependent Round defect is already known and is not a new counted bug. Integrating relative stepped deferral still needs its separate consumer work.

Replay audit.py and witnesses.py only in a fresh copy, because they regenerate their local receipts. No canonical source, index, epoch, binary, sealed predecessor or Git ref was changed.

# Uninstrumented hidden flex repair experiment

All four variants completed15WPT files and656subtests after installing exact HEAD
bytes for all20 modified native files. Five builds, including restoration, passed.
WPT lint reported no errors or warnings.

| Source variant | PASS | FAIL |
| --- | ---: | ---: |
| Committed baseline | 621 | 35 |
| Principal-child repair | 655 | 1 |
| Original four-field measurement key | 629 | 27 |
| Original key plus principal-child repair | 647 | 9 |

The repair changes34 failures to passes with the full key and18 with the original
key. There are no pass-to-fail changes and no file-status changes. All124new test
names match the retained ordered rosters; all656 identities match across phases.
The original-key pair preserves eight caption/padding failures caused by removing
those required key inputs. This demonstrates independence from fixes98/101 for
the repaired release-derived cases; it is not a full upstream runtime claim.

One newly tested static absolute-child failure is identical across all variants:
a hidden in-flow sibling insertion gives[110,10,0,0] instead of[104,10,12,8]. The
principal repair does not reach the container-owned absolute child list. Separate
source review proposes an absolute-reflow invalidation repair; no acceptance of
that proposal follows from this run. The failed test remains in the evidence.

The experiment restored all original native and temporary-test state. BEFORE and
FINAL match for HEAD,index and25native pins. The restoration build exited zero;
no byte-identical binary claim is made. Root rechecked all25live source hashes on
22October after resuming, and observed the original process terminal with exit0.
The source/build again contains the preserved prototypes, not either candidate.

The scoped subtree proof and browser results are complementary. This experiment
does not prove arbitrary dirty histories, native lifetime, external OOF ownership,
fragmentation or performance. Remaining gates include actual fragmentation/cost
checks, separate OOF repair validation, final packaging and acceptance.

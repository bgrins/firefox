# Standalone v4 driver review

Verdict: **GO for the reversible standalone runtime experiment.** Final driver and all 400 prepared input hashes match. No build, browser, Git operation or production edit was executed by this reviewer.

The experiment must temporarily install the four reviewed v4 traversal sources plus pre-fix102 DOMRect (`7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5`). The v4 capsule's DOMRect is already fix102 (`340a676…`) and cannot serve this purpose. The candidate pre102 snapshot matches the independently retained historical integer-only source hash. The producer separately records the Git-parent acquisition; this review does not execute Git to repeat it.

The historical oracle is deliberately 70 PASS / 4 FAIL with exit1. Its own four untransformed cases all pass. The separate transformed-edge suite contains two passes and two unexpected failures, and the remaining 66 existing cases include two expected failures. Matching these outcomes is the intended independence test, not an instruction to turn every failure into PASS or to relabel unexpected failures as expected.

The driver authenticates prepared inputs, five original sources, HEAD, exact staged diff and complete stage entries before mutation. It rejects non-artifact staging or staged files inside the runtime output directory. The temporary WPT must be absent initially. Candidate and source-before snapshots are distinct from the standalone/ runtime output directory; the initial candidate/ collision identified by root is corrected in the reviewed final driver.

Within try/finally, it installs the one temporary WPT, runs lint, installs all five candidate files, runs format/build and confirms exact candidate bytes. Runtime captures source/test/metadata/harness/binary hashes before and after, unique keyed subtests, complete file ends and suite completion. Exact equality to all 74 historical status/expected pairs and 23 file outcomes preserves the oracle; exit1 is explicitly checked.

The finally block restores all five captured originals, including fix102 DOMRect, removes the temporary WPT and rebuilds if source installation began. It records and checks source/fixed-native restoration, HEAD and both staged-content hashes. No stage/reset/checkout/commit command is present. Restoration is intended for Python exceptions and handled interrupts; it cannot guarantee completion after process kill or power failure. No broader recovery guarantee is claimed.

This GO covers this controlled reversible runtime experiment only. Source applicability and a successful future run do not establish an isolated upstream build or universal frame/provider/graphics correctness. This run specifically tests independence from fix102 on the current retained tree. No timing measurements are requested or needed here.

## Final reviewed inputs

Driver SHA256: `5811759c90c8ef16e025a152618075f812187d5d64bc4d0e06a03214e36e66b5`. INPUTS SHA256: `527dbf449b80d114c79f0fe81f81ac9b1ddbad13eac6416603871f846777f943`. The prepared set contains 400 pins, 229 expected staged paths and 20 fixed native inputs. All hashes were checked without invoking Git. The driver's own launch preflight must still verify current HEAD/stage identities. All four candidate traversal files equal the sealed v4 proposal; the fifth is the exact pre102 DOMRect. The copied oracle matches historical rows, ends and exit byte-for-byte as JSON values. Root's identified output-directory collision is fixed: candidate/ holds source inputs; standalone/ receives results.

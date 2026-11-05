# Proposed C delivery with owner-map dedup

`C-after-163.patch` is a five-file production proposal explicitly depending on #163, `e63fc6b1892bc13f4d0f6583e4efc4b58d1e54db` (A+B+D). It is not independently cherry-pickable onto the retained pre-project base. Keep supporting research in a preceding commit; this patch contains no tooling, docs, native diagnostic instrumentation, harness copies or benchmarks.

The source bodies are exact cac13 owner-map dedup cascade plus the unchanged fd5ded C stylist caller. Tests are the exact existing frozen C72 and substitution20 fixtures and the D48→D64 expansion. This adds 108 callbacks; the combined A16+B16+D64+C72+substitution20 roster is 188. Canvas2 and six diagnostic occurrence tests remain outside this strict minimum. These callback counts are not separate bug counts.

Configured rustfmt and byte-exact zero-fuzz forward/reverse application succeeded against immutable #163 blobs. Current HEAD blobs have identical patch preimages for all five paths. Temporary patch scratch was removed. This package does not itself run or accept native correctness or performance; the root-owned combined experiment and independent restoration records must close before adoption. No live source, index or probe was modified.

The existing untracked logical/physical WPT already matches the intended delivery bytes. The substitution test is absent from the working tree. The tracked inline-exclusion test still contains the committed D48 bytes; its exact current body is preserved under `preserved-working-tests/` before proposing the D64 replacement. No differing untracked probe needed preservation in this five-file scope. This check does not inventory unrelated WPT probes.

The prerequisite and retained-base limits are detailed in `../css-revert-rule-c-delivery-prerequisites-v1/REVIEW.md`. This proposal updates that review's d329 source to cac13 only. It does not silently rebase or bundle unrelated repairs, and it does not claim isolated validation on current upstream. The same explicit #163 prerequisite remains necessary for this exact implementation and D test expansion.

# Independent standalone v4 runtime review

**PASS for the tested traversal candidate without DOMRect fix102.** This closes the specific runtime dependency gate left by the v4 shared-build review. It is not an isolated upstream build, universal CSSOM correctness proof or new performance measurement.

## Independent reconstruction

After root reported experiment89714 terminal exit0 and complete restoration, the independently prepared analyzer read the raw WPT stream. It reconstructs 74 unique subtest keys, 23 unique completed file outcomes and one suite end. The result exactly matches the previously authenticated integer-only oracle, including expected statuses and exit1.

| Partition | Result |
|---|---|
| Four traversal/untransformed-edge cases | 4 PASS |
| Separate transformed-edge/DOMRect cases | 2 PASS, 2 unexpected FAIL |
| Other 66 existing subtests | 64 PASS, 2 expected FAIL |

The two unexpected failures are the horizontal/vertical large transformed-edge witnesses for the deliberately removed fix102. They remain expected-PASS tests that fail; they were not relabeled expected failures. The two unrelated expected failures remain rotated SVG text Element/Range equivalence and trailing-surrogate Range indexing. File outcomes match the historical oracle exactly. Candidate WPT exit1 is the intended outcome under this split, not a harness success masquerading as all-pass.

## Source, build and restoration

The checker authenticates all 400 prepared input hashes against retained snapshots and immutable siblings. The four installed traversal files match the previously reviewed v4 roles; the temporary DOMRect is exact pre102 hash `7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5`, not the v4 capsule's already-fixed DOMRect. All runtime source/test/metadata/harness hashes are stable before/after, with contemporaneous Firefox/XUL binary identities retained. Historical executables are not archived or independently rebuilt by this review.

Candidate and restoration builds both exit0. Format and WPT lint exit0. The finally path restores all five originals, including DOMRect hash `340a676a79f33faa6f6243bd1c5af4c4bba99310142ee0b24a6ecbf2da1bfc9e`, removes the temporary WPT and confirms the 20 other fixed native files unchanged. A separate current-byte read in this review matches all 25 historical final native pins.

INPUTS, BEFORE and FINAL agree on historical HEAD `99a9ca84f08370c1797720db8688bcb3747f6985`, staged-diff hash and full stage-entry hash. The driver protected the 229 staged artifact paths. Later authorized artifact signing is expected to change live HEAD/index; this review does not require them to remain at their old values and performed no Git operation. Preservation here concerns recorded staged content/entries, not byte identity of the physical index file.

## Scope and decision

The candidate's four own precision cases pass with pre102 DOMRect, and all other keyed outcomes retain their exact old integer-only results. The separate DOMRect failures discriminate that fix102 was truly absent. This supports runtime independence from fix102 on the retained current source tree. It does not establish independence from every other shared-tree change; upstream patch application and isolated upstream execution remain different claims.

No timing run occurred here. The previous v4 runtime review's qualified performance advancement and disclosed deep-root cost tradeoff remain unchanged. Native/provider/frame-lifetime and legacy numeric-restart admissions are not discharged by finite browser results.

This reviewer executed only artifact/source reads and Python analysis: no compiler, browser, full build, native edit or Git command. Final evidence authentication is recorded separately; the independent analyzer derives outcomes directly from raw records, without invoking the producer's result summarizer.

## Final evidence binding

Authenticated the producer's postprocessing capsule FILES `ae43eed36c8cf69e3c47aa96bd4ee91ff5355bc5a8d97bdde4be12e7b936870f` (124 payloads). Independently matched all 115 captured runtime files to root's terminal originals. The analyzer now reads that immutable capture and reconstructs the same result; it does not import or execute the producer analyzer. Runtime-local prepared inputs are resolved within the capture, so later authorized main-tree changes do not alter the historical source roles. Other immutable research dependencies remain explicit siblings. This is a reproducible retained-evidence review, not a self-contained archive of historical browser binaries.

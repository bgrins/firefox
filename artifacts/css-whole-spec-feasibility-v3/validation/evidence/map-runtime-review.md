# Independent paired runtime review

Accept the bounded runtime gate for the pinned two-site map/cascade candidate. This review reconstructs raw test identities and outcomes independently of the producer parser; it does not run Firefox or establish a universal native theorem.

## Observations

The original phase reports 78 PASS and four FAIL. The candidate reports 82 PASS. Each phase has exactly nine distinct harness OK results and one suite end. All 82 `(test, subtest)` identities match the independently retained expected roster, with no duplicate or missing result. The only changed outcomes are the four expected map-taint cases listed in RESULT.json. The other 78 outcomes (five diagnostic controls, 32 attr-security entries and 41 enumeration/defaulting controls) are unchanged.

The new nine-case test has unconditional prerequisites for registration, parent computed tokens, parent URL behavior, child computed tokens and final image behavior. An unsupported prerequisite fails its test rather than silently skipping its final assertion. No missing prerequisites can turn the four failures into passing results.

The older attr-security.html registers 32 tests. Its 29 `test_attr` registrations conditionally execute their assertion when the substituted value is empty or CSS.supports accepts it. Thus 32 PASS means no reported regression in this test, not 32 independently demonstrated supported security mechanisms. Its shorthand and two registered-property helper cases execute assertions unconditionally. This test intentionally includes unsupported proposals such as string(); no new support claim follows.

## Source and binary association

The original phase reuses the prior combined enumeration build. The copied BUILD-ASSOCIATION hash matches PAIR.json and binds the copied BUILD-MATRIX hash, successful combined build and original Firefox/XUL hashes. Both original native sources and binaries are unchanged across original execution. The candidate build starts and ends with exact candidate source hashes; its successful exit and full log are retained. Both binary hashes change, and the resulting binaries remain unchanged through candidate execution. Candidate sources also remain unchanged across execution. PAIR.json records 54 protected input pins. These are shared-workspace build associations, not an isolated upstream build or a reproducible compiler theorem.

Original map: 9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d.
Original cascade: 7cf543c5f258c577568df72b892dd0a39e97578b59390752e8c63a77ee501a8c.
Candidate map: 58c66ad3893b79282538386480db8ea6475b49e6744f4d74ffdf3b68ae8d9d86.
Candidate cascade: 714f7d9a36d25206fb1721a9c3eafef32ad55cfd8b1be82be7d4ff04ea733d55.

The candidate build log contains four `KeyError: 'export'` monitor tracebacks. It nevertheless reports successful compilation/link and exits zero; the candidate executes successfully. This review does not call the build warning-free. The source-only input capsule was authenticated before reading its inputs; no producer module was imported for result reconstruction.

## Boundaries

This accepts the observed source/binary/test pair only. Native source/spec and standalone patch reviews remain separate. Formatting or later source changes require explicit identity revalidation. Historical raw evidence is copied, not overwritten. The checker authenticates this review before running its independent raw parser; no browser, build or external checkout is needed. Source/compiler correctness, arbitrary attribute flows and animation taint are not proved here.

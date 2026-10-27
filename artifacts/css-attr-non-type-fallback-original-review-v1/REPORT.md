# Original non-type fallback run review

The stored original run is internally consistent. An independent parser verified one complete suite, 14 unique test starts and ends, no duplicate subtest identities, and exactly the capsule's 34 new subtest names in their declared order. The new fixture produced 19 FAIL and 15 PASS. The other 154 subtests and six reftests passed. Raw events contain no ERROR/CRITICAL logs or crash events. All eight testharness documents completed OK.

The original WPT process returned 1 because assertions failed; the observation wrapper accepted the complete observation. This is not candidate acceptance. The parent's reported terminal execution is session 54979, chunk 1bf2c9, wrapper exit 0; this review independently checks stored RESULT.json rather than observing that tool session.

## Failure interpretation

| Group | Failures | Observed first failing assertion |
|---|---:|---|
| Missing/invalid primitive or bare primary, self or mutual property cycles, including namespace and token controls | 14 | Custom property expected guaranteed-invalid serialization `""`, observed `red` |
| Same attribute with raw and number syntax | 1 | Expected `""`, observed `"red" "red" red` |
| Bare/number mutation tests | 2 | Initial absent-attribute state expected `""`, observed `red` |
| Registered length with used font-size/line-height fallback | 2 | Registered property expected initial `11px`, observed `23px`/`31px` |

These observations support the specific used-fallback cycle defect. A failing test callback stops at its first failed assertion: its consuming-color check, other mutual participant check, later attribute mutations, and remaining registered-property checks are not independently observed here. In particular, the two mutation failures establish the initial state failure, not failure after mutation. The 15 passing controls include direct var and typed-attribute cycles, valid primaries that exclude unused fallbacks, empty raw strings, namespace lookup, raw function text, and valid primary font/line-height controls.

The existing attr-cycle fixture and metadata are unchanged. Its 37 PASS results preserve the existing oracle; they do not establish current Editor's Draft conformance for nested raw attributes. A separate proposal must explicitly change and justify any obsolete oracle.

## Identity and preservation

The runtime fixture, capsule capture, and pinned repair-v3 fixture share SHA-256 `6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3`. All retained owned input bytes match OWNED-INPUT-PINS.json. Capsule manifest `fc8e9a7cc39e37f17177627386574f7dc18bf69e3e3a700b9509b127fcdd53e1` authenticates all capsule payloads. Assessment SHA-256 is `49d7c867e4b4255e169ae05d41becb73cd121bba8b126d02d02443c475a397b3`.

The saved epoch SHA matches COMMAND and ASSESSMENT. Its two relevant source hashes exactly match the original policy role, not the candidate role. Its normal Firefox/XUL hashes match NORMAL-BINARIES.json. BuildID `20261027145735` and revision `4ebfb9861c95d33290f5fb472fddd78de241d043` agree between captured application metadata and raw suite run_info. Application metadata is byte-equivalent before/after, including link lstat identity/type, link target text, resolved path, target identity and bytes. PRE and POST are identical, including root and nested index observations.

CLEANUP records the owned process group absent and temporary root removed. Two mozrunner directory names listed there describe remaining entries before recursive temporary-root removal; they are not a claim that directories remain afterwards. This review relies on saved cleanup/preservation evidence, and makes no current live-process or live-tree claim while the candidate build proceeds.

The replayable audit reads only stored artifacts and writes this review's AUDIT.json and INPUTS.json. No browser, build, native, index, HEAD, epoch or canonical edits were performed. No additional accepted bug or normative coverage credit is claimed.

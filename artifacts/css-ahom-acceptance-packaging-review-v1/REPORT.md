# Ahom repair acceptance and packaging review

## Disposition

The narrow encoding/coordinate repair is supported by the retained exact-source, native-provider, kernel and paired-browser evidence. This audit found no additional correctness blocker for that repair. Root's fresh full offline provider/breaker replay has now passed (ROOT-FULL-REPLAY-v2.json, process 9241, exit 0); this audit independently checked its log identity and both native/kernel result objects against the frozen evidence. No further technical gate was found for narrow acceptance. Root's explicit scoped acceptance record remains to be written. Authentication or an encoding/kernel-only replay would not have substituted for that complete native replay.

Review independence is limited: this worker produced the candidate replay capsule and earlier normative adjudication. This follow-up independently parses the root-owned WPT evidence and checks its source/patch bindings, but is a producer audit of its own formal/native capsule. Root is the independent reviewer and replay owner. The original capsule's use of “independent” refers to its role relative to root's native/browser work, not an additional independent review of this follow-up.

## Causal source review

The complete `Utf16` handler preserves decoded scalars by using Rust `char::encode_utf16` instead of truncating each `u32` to `u16`. Its initial and subsequent seek advances now use the actual `Utf16::char_len`. The same representation and width convention therefore feed the complex provider and subsequent cache consumption. Actual iterator cloning/restoration, provider selection, cache subtraction, return position, EOF handling and all source outside this implementation remain unchanged. The Cargo checksum differs only at `files["src/line.rs"]`; package identity and other file entries are unchanged.

The new representation needs one or two units per admitted scalar. Supplementary complex runs can allocate more storage than the old incorrectly truncated representation; BMP encoding and scalar widths remain unchanged. This is no allocation-performance theorem. Existing vector allocation failure behavior, Rust standard encoding, integer/container representation and provider semantics remain boundaries.

The first returned internal complex boundary must be positive, in range and scalar-aligned; subsequent returned boundaries must progress. These are existing provider contracts, not newly validated by this patch. A first boundary of zero would not be reached by a search initialized after the first scalar. Actual complex-run admission excludes surrogate values; the replacement-character fallback is not a proof of preserving arbitrary malformed UTF-16. Correcting this handler does not settle the separate complex-run end-boundary issue.

The three-file patch reproduces the paired candidate bytes when applied to copied paired-original source snapshots and reverses exactly. The WPT bytes also equal `wpt-final-v1.html`. Root's separate retained checks establish exact apply/reverse at historical base and HEAD. This audit did not use Git or claim an isolated historical Firefox build.

## WPT oracle and raw evidence

Independent parsing authenticates both 53-pin receipts and every retained source/resource/metadata snapshot. The only changed pair pins are ICU line source, Cargo checksum, Firefox and XUL. All 364 status identities match between runs. The eight failures are exactly Ahom + normal breaking + narrow width + before-LF/nested-before-LF, across both pre-wrap/pre-line and none/capitalize. All eight become PASS. The remaining 356 statuses are unchanged: 305 new-test passes, the test's OK status, 46 regression passes and four regression OK statuses. No expected-status conversion hides the failures.

The test has 24 suffix calibration controls and 288 partition cases plus one asynchronous setup test: 313 subtests total. Scalar-aware Range endpoints do not split surrogate pairs. Calibration requires positive single-character widths and a pair at least two pixels wider than either single; the chosen midpoint fits either Han character and excludes their pair. The expected suffix wrapping depends on width and word-break policy, not candidate output. It does not assert Ahom dictionary segmentation, total line count or prefix font metrics. Generic fallback fonts are deliberately measured; platform portability is not established by one macOS run. Calibration failures fail the test rather than skipping coverage.

The final WPT's initial/default none transform, normal overflow wrapping and inherited identical span styles are sufficient for this fixture. Explicit default declarations and more specific help links could improve readability, but changing them would require new exact-byte test binding; they are not an acceptance blocker here. The invalidated candidate-v1 binary receipt is excluded. Only the strict paired receipts and their verified rebuilt binaries support the result.

## Normative and upstream adjudication

The retained current CSS Text 3 Editor's Draft, fetched on 2026-10-19, requires inline boundaries to be ignored for text-processing adjacency. Preserved LF in pre-wrap/pre-line creates a forced break while wrapping remains enabled. The following Han pair stays wholly inside one Text node under every partition. No grapheme, surrogate or differently styled typographic unit is split. Under identical styles, splitting the earlier prefix cannot remove this UA's calibrated suffix opportunity. **Verdict: REACHED for these fixture preconditions.** The argument does not turn UAX14 LB31 into a universal Thai-language CSS mandate; CSS tailoring and provider choices remain explicit.

Primary references: [text adjacency](https://drafts.csswg.org/css-text-3/#text-encoding), [white-space](https://drafts.csswg.org/css-text-3/#white-space-property), [segment breaks](https://drafts.csswg.org/css-text-3/#line-break-transform), [line-breaking details](https://drafts.csswg.org/css-text-3/#line-break-details), [normal word breaking](https://drafts.csswg.org/css-text-3/#valdef-word-break-normal), [UAX14 LB31](https://www.unicode.org/reports/tr14/#LB31). Exact primary documents and verified anchors are retained in `ahom-lf-adjudication-v1`; this audit uses those dated captures, not an uncaptured claim about a later specification revision.

Official retained GitHub records distinguish [PR 8143](https://github.com/unicode-org/icu4x/pull/8143), cache-consumption optimization, from [PR 8144](https://github.com/unicode-org/icu4x/pull/8144), the borrowed-slice refactor that removes the truncating handler and uses encoding-specific widths. PR 8144's structural removal addresses both diagnosed mechanisms. The local patch is a narrow backport of the correction, not a cherry-pick of that broader eleven-file upstream change. Neither this review nor the capsule executes the witness at the upstream commit. PR 8574's later final-run-boundary change is separate. Describe this as an upstream-fixed vendored mechanism, not a new unfixed ICU4X defect.

## Exact formal and native scope

| Evidence | Established | Boundary |
|---|---|---|
| Eleven encoding/coordinate lemmas | Mathematical encoding length, BMP preservation, supplementary roundtrip/bounds, arbitrary finite run/prefix coordinates and progress | Not universal Rust stdlib/compiler or mutable iterator refinement; valid scalar interpretation required |
| Complete source binding | Exactly five declared replacements inside the full Utf16 implementation; real char_len retained | Source review binds the intended model; no automatic proof of every Rust execution |
| Fifteen-module, 80-report kernel witness | Exact full modeled Append/provider/publication path and restored second-CJK opportunity for the concrete witness | Three provider answers are freshly checked against native; the general segmentation provider remains external |
| Offline ICU and complete native bridge | Fixed six encoding cases, five Gecko queries, six LF traces and unchanged 1,284 streams per original/language-candidate breaker | Finite correspondence, explicit C++/locale/dictionary/string/refcount/platform adapters |
| Paired browser gate | Eight targeted observable improvements; 46 existing regression passes unchanged | Combined project build, not release/clean-base/cross-platform evidence |

The repaired concrete glyph vectors remain `0101001` for whole/after-LF and `0101111` for before-LF. The second-CJK bit is restored, but LF and initial-boundary bits still differ. The original raw partition-equality obligation therefore remains refuted. The original language proof's universal source/provider/caller/consumer obligations remain open as recorded; this narrow acceptance cannot be used to mark them complete or to infer all-CSS conformance.

## Packaging and remaining gate

`replay-paths.txt` is the exact 7,497-file existing complete candidate closure: 7,495 manifest inputs plus manifest/freeze. It contains about 135 MB of source/evidence, mainly duplicate immutable provider/vendor trees. `companion-paths.txt` adds the 21-file primary-spec adjudication closure, this report/guide and root's completed full-replay receipt/log. These are exact coherent inventories for the existing replay, not a claim of globally minimal deduplication. A smaller replacement package would require source equivalence and a fresh complete replay.

No generated build/development-build directories, compiled objects or binaries belong in that inventory. The dictionary and compiled-in Rust data files are source/provider inputs and remain. Tool executables, their distributions, system libicucore and the macOS SDK/frameworks remain explicit external toolchain requirements.

Root's freshly relocated complete replay passed, including all 7,495 authenticated source inputs, baseline provider rebuild, candidate provider rebuild and candidate kernel witness. Root can now record narrow acceptance of the three-file backport and commit the companion first. No additional broad finite matrix is proposed. Any future deduplication, full language proof completion or cross-platform expansion remains separate work.

Read-only `git ls-files` returned no tracked paths in either frozen capsule or this review directory at handoff. The inventory preserves the existing replay layout; Git can deduplicate identical blobs without changing that layout.

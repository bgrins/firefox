# Independent review: sticky explicit inset versus auto alias

## Recommendation

**Accept the native repair and its WPT; HOLD full formal-companion acceptance pending correction of tested-source identity.** No mathematical defect or native patch defect was found. The formal capsule substitutes the final formatted candidate for the distinct source actually used by the browser build, while reporting that both exact sources were executed. The original contract requires preserving and replaying all three source roles; formatting equivalence does not waive this requirement.

The review changed only its own artifact. It used the frontend review skill and layout reviewer guidance, read the current primary CSS rules and Searchfox numeric source, and independently checked retained browser evidence. It did not change production/WPT files or Git, run Firefox or a Firefox build, or push anything.

## Blocking source-identity finding

| Source role | Browser/build artifact | Sealed proof capsule |
|---|---|---|
| Before | `38d14faa60bfe3180e87904f5085fdbbee5aa47746a38df77f4edb50360af40c` | Same |
| Actually tested candidate | `51e60438c405a4163cd0f8c43a669ee712d06dc6d202ccefa7519b968ea7925c` | **`2a0794213ffad4d35d96b915b0fc858e2bfb18ddf74b20e4884a2d6b6f0f3b4b`** |
| Final formatted candidate | `2a0794213ffad4d35d96b915b0fc858e2bfb18ddf74b20e4884a2d6b6f0f3b4b` | Same |

`capsule/inputs/candidate.cpp` and `candidate-formatted.cpp` are byte-identical. This is already present in the authenticated producer, not a review-copy error. `SOURCE-PINS.json` also lists the same final hash for both roles, although SOURCE-CONTRACT names the distinct tested hash. The producer's source pin file is authenticated as data but is not enforced against checkpoint/CANDIDATE or BUILD identities. The source extractor's whole-file and formatting checks therefore compare identical candidates, and its six correct configurations execute only two distinct bodies. All six numerical runs pass, but they do not establish the three exact source identities claimed by REPORT/SOURCE-CONTRACT.

`SOURCE-IDENTITY-FINDING.json` preserves the exact comparison. The retained native artifact still contains the real tested source, whose difference from the final candidate is solely whitespace in the return expression. This supports native review; it does not repair the formal artifact's false transfer claim.

Required correction: preserve proof-v2 and this review, create a new producer version with the actual tested `51e60438…` candidate, regenerate the body/byte bindings and source roster, and enforce each source role against its independently retained native receipt. Replay the real original/tested/final variants at both optimization levels, the complete corpus, mutants and integrity gates. Add a negative control that replaces the tested input with the formatted input and re-seals ordinary manifest data: the independent source-role gate must reject it. Update documentation only after the exact three-source replay succeeds. Full acceptance remains pending that correction.

## Native and specification review

The complete `ComputeStickySideOffset` helper already distinguishes auto after anchor resolution from an explicit LengthPercentage. Its old explicit branch returns the numeric result directly. That numeric result can equal `NS_AUTOOFFSET`, because this code is also `nscoord_MAX`. Downstream sticky code then treats a very large explicit inset as unconstrained.

The repair retains the actual-auto branch and clamps only the numeric result to `NS_AUTOOFFSET - 1`. It introduces no frame lookup, allocation, lifetime change, new resolver call or evaluation of the numeric value for auto. The requested side and percentage basis are forwarded unchanged. The sole added arithmetic is a representable constant subtraction; `std::min` compares signed nscoord values. Returning its scalar value does not outlive either temporary. All lower resolved values, including negative values and zero, remain unchanged. On the ordinary resolved range, the maximum changes by one app unit; the Lean proof correctly requires an upper bound for that claim.

The current [positioning rules](https://drafts.csswg.org/css-position-3/#stickypos-insets) distinguish unconstrained auto from numeric insets, reduce an insufficient end inset to fit the border box, and constrain non-auto sides subject to containing-block containment. [CSS numeric range rules](https://drafts.csswg.org/css-values-4/#numeric-types) allow limited implementation precision/ranges and conversion to supported numeric values. Reserving an internal numeric code is consistent with those rules; converting an explicit numeric side into auto is not justified by numeric clamping. Retained primary pages and fetch metadata are under spec/.

Searchfox inspection of `ServoStyleConstsInlines.h` independently follows the real numeric path. Pure lengths use `LengthPercentage::ToLength` → `StyleCSSPixelLength::ToAppUnits` → `DefaultLengthToAppUnits`, which clamps its upper/lower endpoints. Percentage/calc resolution uses `DefaultPercentLengthToAppUnits` → `NSToCoordTruncClamped`; the retained actual nsCoord header likewise clamps the endpoints. `StyleCalcLengthPercentage::Resolve` delegates CSS-pixel evaluation to Rust before conversion. These sources explain the upper endpoint's reachability and support the chosen representation. This is source review, not a proof of floating-point conversion, Rust calc or NaN handling.

The real `ComputeCBDependentValue` overload asserts that an unconstrained basis has no percentage. The maximum-basis harness rows are interpreted as pure lengths. The facade does not execute `HasPercent` or the real numeric resolver; those preconditions remain explicit. Anchor-resolved auto can arise from provider semantics rather than the author's literal syntax, so all no-alias statements refer to actual auto after that provider.

## WPT, native evidence and independence

The exact patch `4be581a216c84dc29887c54ee719edcafae40482b36926a2e8c03c0234e6cf0e` changes only `ComputeStickySideOffset` and adds the WPT. Independent exact-context apply/reverse checks pass against retained Git source at both `92a6fddf18e5828b17d7491a34663a0d5a9c12ad` and `976279105b2e78b8666a959eb3f25c9176cefaf8`. The repaired helper matches the final candidate exactly; all other base bytes are preserved. These are source applicability checks, not isolated-base builds.

The WPT exercises all four sides, two scroll offsets, ordinary lengths, values around the implementation boundary, a large length, calc and percentage. The opposite side is explicitly zero. That detail makes its geometry independent of the separate missing-auto normalization repair: neither side relies on treating an absent opposite inset correctly. The border box and containing block are small, so the independent geometric sentinel defect is also outside the fixture. The containing block, target size, scrollport, actual scroll, sticky computed position, explicit tested side and zero opposite side are calibrated. Large authored values saturate far beyond the small containing-block limit, so the oracle does not require exact support for those enormous lengths.

`native_audit.py` independently reconstructs all 80 named expectations and compares the raw WPT events to the receipts. All 32 baseline failures occur in the four overflow-producing values across four sides and two scroll offsets, with exact observed failure coordinates matching the alias prediction. All become PASS; 48 controls stay PASS. The test and metadata are unchanged across the pair, within-run pins are stable, only StickyScrollContainer.cpp/XUL/firefox differ across runs, and each harness ends OK. The original wrapper's incorrect 24-failure count and earlier auto-opposite fixture remain preserved as development evidence, not credited as the final pair.

The retained candidate regression suite has 1,328 passing subtests, three passing reftests and five OK harnesses. The build receipt and terminal log show success despite a recorded progress-monitor KeyError; native final lint and WPT lint report zero problems. The browser build used the distinct preformat `51e60438…` source; the format transfer is independently checked. Combined-worktree regression passes do not imply isolated-base browser validation.

Separate retained probes show the issue on installed Firefox 158 and the shared build: eight failures among 32 calibrated cases each. Those are earlier actual browser observations, not browser executions performed by this reviewer. The fix does not claim a crash, memory corruption, exfiltration or performance improvement.

## Formal and replay review

All supplied outer/capsule seals were authenticated before producer code was imported, including independent closed-file/directory traversals: 476 outer files and 28 capsule inputs. Fresh manifest-only copied replay passes the implemented scope: 31 named audits, 236 cases retaining the original 216, six native configurations, five paired compiled/Lean mutants, and eleven rejected provider/schema inputs. The six configurations have the source-role defect described above. Existing mathematical results do not depend on that false documentation claim.

The twelve original encoding results remain unchanged. Their no-alias, round-trip, monotonicity, range and preservation statements have appropriate premises. The source-shaped observer includes the actual-auto branch and complete side/query/resolve/basis observations. Constant subtraction is bounded explicitly. Native source interpretation, ABI, provider storage and object lifetime are admitted; finite calibration is not presented here as a fully mechanized C++ semantics proof. The integer result does not prove downstream sticky limits, scheduling, view-timeline consumers or all CSS.

Ten independently written kernel results additionally check signed32/no-alias behavior, exact endpoint output and trace, auto skipping, preservation of the complete nonalias observation, the exact one-unit delta, idempotence, zero/negative values, explicit-versus-auto distinction, signed minimum behavior and the necessity of the upper-bound premise. Four false-proposition controls test rejection of the opposite conclusions. A development tactic missed a numeral min reduction; its failed source/log is preserved and the completed proof uses omega. No failed development check is counted as a passing result.

The producer's 26 integrity and two custom-axiom/sorry controls were freshly repeated. Independent review closure controls separately challenge nested caches even when the outer manifest is re-sealed. The original nested seals remain external pins. Exact axiom rosters permit only propext, Quot.sound and Classical.choice. The producer pins its entire installed Lean bin/lib tree and compiler header closure; those libraries are trusted compiled dependencies. Runtime/loader/OS, Python, compiler dynamic libraries, tool correctness and the documented whitespace/colon-free dependency-file path profile remain trust boundaries.

## Rechecking

`python3 -I -S check.py --authenticate-only` authenticates both closed rosters. `python3 -I -S check.py --out /absolute/new/external/directory` additionally reruns retained native evidence checks, source-role finding, the producer replay, independent kernel proofs and semantic negative controls. A successful checker execution means the evidence reproduces; its verdict remains **HOLD-tested-source-identity**. It must not be presented as full companion acceptance.

Only owned compiler products and disposable relocation copies are cleaned, after their hashes and commands are retained. The original producer and native artifacts remain unchanged.

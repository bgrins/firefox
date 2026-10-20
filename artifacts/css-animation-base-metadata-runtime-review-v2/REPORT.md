# Strengthened base-animation metadata runtime review

**Accepted scoped runtime gate.** Candidate has189 PASS and 14 harness OK, with four repaired observations and185 unchanged. This sibling preserves the sealed v1 review; no new execution was performed by this reviewer.

## Strengthened baseline

The only test change is an extra target read after all control/reference style flushes and before changing currentTime. Both its payload and background-image must equal the first captured target observation. Exact probe SHA256: `3c3f231171b914e38fc60bacdc967aa34605a6b545ee5e4f2b9818131564b5d6`.

The new baseline has the same eight ordered identities: four same-payload implicit start/end cases fail in both taint directions; two changed-payload and two explicit-replacement controls pass. All four failures remain at the final `Immediate effect URL taint` assertion. Therefore both new pre-seek assertions, then the sought observation, pass in each failing case. The control/reference flush sequence does not repair the captured result; changing time within the same discrete half is followed by correct output.

This closes v1's particular competing explanation that those intervening flushes alone account for recovery. It does not uniquely prove the entire internal scheduling chain or inspect the precise moment mBaseValues becomes correct.

## Source and oracle review

The candidate SHA256 `cee5ea606d98c23cd609b9f09f87f97d871530de059ac7e31478c025fe87cc13` adds metadata comparison only in EnsureBaseStyles' existing new-map scan. Ordinary AnimationValue inequality remains first. The extra accessor calls require a custom property key and two nonnull values. Existing null/non-null inequality already distinguishes missing versus present old values, so one-null cases do not enter the new calls. Removed old-only keys remain outside this scan, as before; this fixture retains the same property and base requirement.

The original normative trace in v1 remains applicable: missing endpoint uses current underlying value; registered strings interpolate discretely; taint survives registered substitution; tainted URL use is invalid. The probe uses distinct base versus explicit initial strings, so no equal-endpoint interpolation shortcut supplies the expectation. It mutates normal declarations without setKeyframes, distinguishing this route from endpoint retention.

Setting currentTime completes pending pause synchronously. A computed-style query must expose updated animation-dependent style; there is no requirement to wait for an animation frame to see the correct result. The liveness section's explanatory examples are nonnormative, while the underlying effect-value algorithm and liveness requirement support this interpretation. See [Web Animations effect values](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-effect), [setting current time](https://drafts.csswg.org/web-animations-1/#setting-the-current-time-of-an-animation), [model liveness](https://drafts.csswg.org/web-animations-1/#model-liveness), and [attribute security](https://drafts.csswg.org/css-values-5/#attr-security).

## Independently reconstructed final paired gate

The driver joins three retained reference sets: fresh strengthened eight-case baseline, the endpoint candidate's101 rows, and its later80-row setKeyframes regression. This is a joined reference, not a fresh 189-case original run. Candidate execution contains all 189 identities and 14 harnesses. The independent checker reconstructs duplicate-free exact identity sets, all raw statuses, all harness outcomes and exactly the four expected improvements. It reproduces the full row records in PAIR.json from raw input.

Base RUN 63 pins associate the fresh baseline with endpoint build binaries and its exact formatting transfer. The before/after pin sets differ exactly in KeyframeEffect.cpp and the two rebuilt binaries. setKeyframes.html is an additional regression input beyond those 63pins; root captured its matching historical digest during candidate build before candidate raw output existed, and recorded equality after completion. The supplemental pair digest matches the final PAIR.json. No broader metadata/support closure than the existing regression receipt is implied.

## Scope

This review owns source/oracle and retained runtime association. Separate source/repair review and formal review cover their declared scopes. It does not prove global animation equality, all metadata, removed-key scheduling, numeric/additive taint, arbitrary multiple-effect histories, complete native scheduler refinement or isolated upstream runtime. No browser, build, live source or Git operation was performed by this reviewer.


The 189 rows are: inheritance 12 + 7; base 8; endpoint 6 + 6; attr-security 32; touching-boundary 7; map-taint 9; enumeration 7 + 10 + 2; CSSOM 1 + 2; setKeyframes 80. Every row is PASS in the candidate. Existing attr-security cases retain their own conditional assertion guards: a subtest PASS is not evidence that every guarded branch executed. No new assertion-level telemetry or broader coverage claim is inferred.

Build exit 0 is retained with successful candidate execution. The build log also contains four `KeyError: 'export'` monitor traces; this is not a warning-free build claim. Format exit 0 produced the exact pinned candidate. No benchmark or baseline performance comparison was performed.

The historical 80-row regression used the pre-format endpoint source. Its only source-pin difference from the fresh baseline is the exact previously recorded whitespace transfer; the independent checker reconstructs that full-file hash transformation again. All overlapping regression pins then agree, and its single additional test pin matches the before/after supplemental receipt. The review accepts the recorded acquisition/stability provenance; it does not independently observe past filesystem states or rehash current live binaries.

**Recommendation:** the strengthened oracle and paired runtime gate support the narrow candidate. Final native acceptance remains composed with the separate exact source/standalone and formal reviews; this artifact does not substitute for them. The identified pre-seek ambiguity is resolved for this fixture, with source/internal-scheduler limitations retained.

Replay `python3 -I -S artifacts/css-animation-base-metadata-runtime-review-v2/review.py`; it reads only the exact retained external INPUTS.json closure and prints RESULT.json's reconstructed data. The integrity checker validates this artifact's own sealed files. The initially overstrict review assertion comparing historical and current source pins was corrected to apply the explicit authenticated endpoint whitespace transfer; no evidence or browser result changed.

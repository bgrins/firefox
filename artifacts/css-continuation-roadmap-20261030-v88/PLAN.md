# CSS and Stylo verification — V88

The eight-source snapshot experiment compiled and all nine WPT callbacks passed with four OK endings. Compared with the frozen original run, three named failures became passes and all six preservation controls stayed unchanged. The saved strict equality gate remains false because it compares all baseline callback/end signatures, including the three improved cases; that historical verdict is preserved. Separate root verification replayed the results, verified all eight source preimages and the original application, checked process cleanup, and confirmed removal of the 1,008,605,176-byte backup. This is a successful bounded admission experiment, not a native fix acceptance.

The previous one-line admission experiment remains rejected because it changed timing on unrelated outline updates. The first snapshot attempt remains a compiler failure with no browser run; the corrected attempt adds the missing uint16_t enum forward declaration. Generated bindings and the native build now succeeded for the eight-source proposal.

Installed Firefox 158 also reproduced the three masked-duration failures with six preservation controls passing. Its first runner had a cleanup failure after a browser relaunch; root separately verified and stopped only the owned group and removed its private profile. The original failed cleanup and unknown outer tool exit remain recorded. The executed recovery checked user.js absence; it did not audit every deployment preference.

A second cross-browser experiment exposes the input-policy boundary:

| Contextual fade, animated font held at 32px | Firefox 158 effect duration / opacity | Chrome 156 effect duration / opacity |
|---|---|---|
| Initial authored 16px | 1000ms / .75 | 1000ms / .75 |
| Authored 16→24px | 1000ms / .75 | 1500ms / .5 |
| Authored 16→32px | 1000ms / .75 | 2000ms / .375 |

The after-change values persist from the first opacity read through three sampled frames. Literal controls and independently recomputed reference checks pass; both isolated runs and cleanup completed. CSS serialization differs separately: Firefox reports 2s for the contextual fade throughout, while Chrome reports 1s initially and 1.5s/2s after the respective changes. These observations do not prove Chrome's internal input path or normative correctness. The native candidate has not run this partial 24px page.

The focused specification trace reaches the ordinary computed-font→em→duration correspondence, whose direct reading favors composed 2s even initially. It does not resolve the complete generation/update timing-input context. Observed initial 1s preservation is therefore empirical. The snapshot-only source predicts a 1500ms cached input but a 2000ms applied duration for the partial 24px case; the passing nine-case suite cannot discriminate because its final base and animated fonts coincide.

## Next work

1. Complete the signed research checkpoint using the verified restored state, then publish the already validated min/max and logarithm changes as separate native+WPT commits with fresh admission. V81 failed 1Password signing; no unsigned fallback or old-owner retry is planned. Accepted native fixes remain 149 across 150 tracked IDs, excluding held 120 and two test-only repairs.
2. Run original baselines for the three preservation callbacks and the three animation-taint callbacks, then compare candidate behavior. Preservation covers fresh descendant rem conversion, collection recreation, and duration-list/Auto changes with script ownership. Taint must preserve required var() fallback; the current CSS Variables draft retains that restriction. No result is claimed for either new fixture.
3. Run the partial 24px observation against the native candidate. The separately reviewed duration-only variant threads the compared list into timing construction while keeping composed keyframes, other timing fields and script overrides. It is uncompiled and unexecuted. Its taint behavior, CSS serialization and normative timing policy remain unresolved. Prepare CSSWG clarification before presenting this policy change as standards-correct.
4. Measure verification overhead using equivalent builds and the manual performance probe. It reports mutation/style-read wall time and final-value checks; internal recascade/manager CPU attribution requires profiling. A future runner may retain a verified candidate application dependency closure to avoid rebuilding for every probe, then remove it when no longer needed. A copied app with external links is insufficient.
5. Continue descendant first-read completion independently. The snapshot does not implement a parent barrier or establish fresh parent/root inputs. Integrate the staged driver and exact-target animation preparation, preserving dependency notification and publication order. Fixed pass counts and matching values are not completion certificates.
6. Extend the formal model where these observations expose missing assumptions. The isolated lifecycle model has 13 audited claims and six rejected false controls: cache freshness does not imply applied timing equals the captured input. The new partial-font case makes that distinction concrete. No native refinement or canonical CSS-model coverage increment is claimed.

The restored checkout is at ecfe313d582a335c04d80bfd360fd3a591defdb7. The latest audit accounts for 563 expected untracked paths: 68 project bodies match committed recovery objects and 495 unrelated metadata entries are unchanged. Staging is empty; the held custom-properties provider is the sole tracked edit. Application revision 20ab is bound through authenticated build provenance and binary pins, not read from application.ini. Root reconciliation changed only the raw-index observation in the canonical epoch.

[Work table](WORK-TABLE.md) · [Exact evidence](EVIDENCE.json) · [Pinned sources](REFERENCES.json).

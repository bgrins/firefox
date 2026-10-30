# Partial authored font change — unexecuted observation page

`observe.html` is a standalone research page. It does not assign a PASS/FAIL verdict to contextual timing, install a WPT, post to a receiver or launch a browser. Existing nine-case and preservation fixtures are unchanged. Root can load identical page/script bytes in the original build, snapshot build, installed stock Firefox and Chrome using separate owned profiles and recorded binary/source provenance.

Four independent iframe trajectories run serially and are removed before the next starts: contextual authored font16→24, literal16→24, contextual16→32, literal16→32. Every target has a constant32px font CSS animation with fixed2s duration, plus a fade. Contextual fade duration is `calc(1em / 16px * 1s)`; literal controls change1s→1.5s or1s→2s. Both effects are CSS-paused and held at750ms. There is no script duration override. The 32px case preserves the previously investigated convergence condition; this is a new collection page, not a byte-identical replay of the earlier WPT.

The discriminating case keeps final authored24px distinct from composed32px. `finalFont` and `authoredInitialFont` record authored declarations, not a queried internal base ComputedStyle. Actual `font`, `cssDuration`, effect specified/computed duration, progress, currentTime and playState are retained independently. No conversion of computed CSS duration into applied timing is assumed.

| Interpretation to distinguish | Partial24 contextual fade duration / progress / opacity | Converging32 |
|---|---|---|
| Retained initial timing | 1000 / .75 / .75 | 1000 / .75 / .75 |
| Fresh pre-own timing | 1500 / .5 / .5 | 2000 / .375 / .375 |
| Fresh composed timing | 2000 / .375 / .375 | 2000 / .375 / .375 |

These are conditional numerical predictions for linear fading at750ms, not normative assertions or executed outcomes. In the frozen snapshot proposal, `Gecko_UpdateAnimations` freshly recascades the base duration input, `DoUpdateAnimations` compares it with the owned snapshot, but `UpdateAnimations` still supplies composed UIReset to the manager. With an initial1000 snapshot and fresh1500 base key, that path admits an update using composed2000, then seeds1500. Actual task admission, traversal and initial values still require observation. The original normal-restyle equality skip suggests retained timing; the prior stock/Chrome32px observations and cross-engine source research do not establish their partial24px result. CSS serialization may also differ between engines even when effect output agrees. The pre-own/composed timing-policy question remains unresolved.

Read order is explicit. Immediately after acquisition, names/time/state are recorded; each ready promise is awaited before its currentTime is set. Three setup frames precede initial details. After the single `.final` class mutation, the first getter reads only opacity. Three further animation-frame callbacks each read only opacity. Only then do details read opacity, font-size, animation-duration and the two effects' timing APIs, in that order. Membership/current names and exact retained animation/effect identities are collected afterward, followed by a second details snapshot. No extra seek, rescue or membership read precedes the first observation. Getters are sequential; later timing or font reads do not describe an atomic first-read state. Frames are observations, not native passes or convergence guarantees.

JSON is exposed in the `#observations` script element, the visible preformatted report and `window.partialBaseObservations`. After `status` becomes `complete` or `incomplete`, save the entire `#observations.textContent` plus page/script hashes and external run metadata. `complete` means all four collections finished without JavaScript/acquisition errors, not that any numerical check passed. Each trajectory retains its stage, partial samples and error. A blocked ready promise or frame can leave status `running`; an external owner watchdog is required, and an unfinished run must not be promoted to complete evidence. The page has no execution owner or browser identity attestation; userAgent is descriptive only.

Reference checks run only after that iframe has been removed. They report constant-font/fixed-font-duration, held times, sample roster and identities. Only literal cases have numeric fade-duration/progress/output calibration. Contextual1000/1500/2000/null timing values receive no policy verdict. Wrong observations remain in JSON, and checks never abort collection. Nonfinite numbers serialize as explicit tagged objects instead of silently becoming null. Setup failure may leave missing snapshots; the partial result remains visible. There is no intentional failing assertion used as transport.

Pure preparation checks:

```sh
node --check artifacts/css-contextual-duration-partial-base-observation-v1/observe.js
node artifacts/css-contextual-duration-partial-base-observation-v1/check.js
```

They exercise literal references, preservation of distinct contextual outcomes, missing/reordered samples, identity/time errors and partial acquisition failure without a DOM or browser. They are not a rendering or WPT result. Frontend skill/performance guidance informed serial frames and the explicitly intentional style reads. No native, Git, index, app or canonical state is changed.

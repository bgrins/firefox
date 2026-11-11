# Composition baseline: eleven expected failures

All eleven extra failures exactly match unconditional expected: FAIL entries at pinned revision `4d1607b92c59814d3bd4e234fec8fb917dc3c735`. They were observed on the retained baseline, before the ComposeProperties extraction. This is triage of known failing coverage, not eleven new bugs or new branch fixes.

| Group | Observations | Classification / next question |
| --- | --- | --- |
| Opacity clamping | Eight rows in clamping-001.tentative.html: expected0, actual1. Four companion rows expecting1 pass. | Known upstream behavior with explicit metadata. Metadata history identifies bug2066417, “Opacity clamping rollback”, commit b4f027ffe395c129063106a76fe845d1555838d2 (D323334). The same change made clamping tests tentative. Do not reopen as a newly discovered bug without reviewing the rollback's policy rationale. |
| Discrete align-content | Fails at the first iteration midpoint: expected flow-end, actual flex-end. | Keyword/computed-serialization expectation mismatch precedes iteration accumulation. Metadata addition belongs to bug2075789 / WPT PR62982, a broad alignment keyword metadata update. Next question, if pursued, is current keyword serialization support; this callback does not establish a repeat-accumulation arithmetic defect. |
| Incompatible calc-size bases | Fails the first-iteration width-at0 versus width-at50 inequality: both1350px. | Existing expected failure, consistent with unsupported/rejected calc-size endpoints, but this read-only triage does not establish that cause. Check CSS.supports and retained getKeyframes values before investigating accumulation. The test never reaches its third-iteration accumulation assertion. |
| Incompatible clip rects | First-iteration midpoint and third-iteration start assertions pass; third-iteration midpoint expects rect(auto,150px,150px,30px), gets rect(auto,50px,50px,10px). | Most focused arithmetic lead, with a direct matching native rejection path. Still already expected-failing coverage, not a newly counted bug. Resolve the WAAPI/SMIL operation contract before changing code. |

## Clip source chain and equation

`ClipRect` uses `LengthOrAuto` components. `GenericLengthPercentageOrAuto` derives Animate; the derive rejects mismatched variants and constructs matching zero-field Auto without an error. Thus Auto with Auto can succeed at the component layer.

`impl Animate for ClipRect` in `servo/components/style/properties/helpers/animated_properties.mako.rs` then adds a specific guard: after component animation, an Interpolate procedure returns the component, but any other procedure returning auto produces Err. The rectangle's component calls use `?`, so one equal-auto result rejects the entire rectangle. Its existing comment explicitly links the guard to SMIL tests.

`accumulate_endpoint` in `servo/ports/geckolib/glue.rs` calls `last_value.animate(endpoint, Procedure::Accumulate { count })`. Failure produces no accumulated value (or retains the previous composited endpoint), and `compose_animation_segment` falls back to the original endpoint when needed. This is a source explanation matching the observed result; no instrumented experiment or modified build was run for this triage.

For the test end rectangle E=(auto,50,50,10), iteration index2 seeks E accumulated twice onto itself. The WPT expects (auto,3×50,3×50,3×10). The current ClipRect guard rejects equal-auto Accumulate, retains E, and the discrete midpoint chooses that unaccumulated end rectangle. The test's numeric-start versus auto-end mismatch at iteration-start still correctly avoids accumulation; broad fallback changes are unnecessary to explain this case.

## Why not just delete the guard

Pinned `dom/smil/test/db_smilCSSFromBy.js` expressly expects noEffect when adding rectangles with equal auto components, including a mixed numeric/auto pair. Pinned `db_smilCSSFromTo.js` permits interpolation when auto appears at matching positions. These are concrete compatibility constraints, not merely an uncertain native comment.

The decisive next question is whether the rejection belongs specifically to Add/from-by SMIL semantics, rather than every non-interpolation procedure including WAAPI iteration Accumulate, and how SMIL actually selects Procedure for those operations. Verify that mapping and current normative rules before choosing an operation-specific or caller-specific change. The smallest subsequent experiment would distinguish equal-auto Add, equal-auto Accumulate count2, and mismatched auto/length, retaining the existing SMIL from-by and from-to controls. No experiment is added or run here.

## Catalogue boundary and evidence

Searched the authoritative `css-all-work-readout-20261110-v17/README.md` and current verification roadmap with the recorded terms. No matching delivered clip-auto or opacity-clamping repair appears in that bounded catalogue search. Catalogue #15 concerns extreme iteration identity versus saturated accumulation counts and is a different mechanism. This is not a search of every historical artifact or all Bugzilla reports. Metadata histories are enough to classify all11 as already-known failing coverage, but are not proof of current open/closed bug status or a dedicated clip bug identifier.

SOURCES.json pins test, metadata, native and SMIL/derive source copies. FAILURES.json preserves exact observed messages. INPUTS.json binds the baseline result and catalogue/roadmap used; catalogue-search.txt and metadata history receipts record provenance. The checker verifies pinned bytes and exact metadata membership. All source/WPT files are preserved; no live edits, metadata changes, builds, browser runs, or catalogue increments were made.
